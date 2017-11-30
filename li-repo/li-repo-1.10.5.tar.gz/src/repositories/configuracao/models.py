# -*- coding: utf-8 -*-
import datetime
from decimal import Decimal
import hashlib
import time
import caching.base
import tldextract

from jsonfield import JSONField
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.utils.text import slugify
from repositories import custom_models


def hash(valor):
    try:
        valor = valor.encode('utf-8')
    except:
        pass
    return hashlib.md5(valor).hexdigest()


class PesoTotalNaoInformado(Exception):
    pass


class CEPNaoInformado(Exception):
    pass


class FormaDeEnvioNaoCompativel(Exception):
    pass


class ConfiguracaoManager(models.Manager):
    def configuracoes_ativas(self, conta_id=None):
        ativo_conta_sql = 'SELECT envio_configuracao_ativo ' \
                          'FROM configuracao.tb_envio_configuracao ' \
                          'WHERE envio_id = tb_envio.envio_id ' \
                          'AND tb_envio_configuracao.conta_id = %s'
        return super(ConfiguracaoManager, self).get_queryset() \
            .filter(ativo=True, conta__isnull=True) \
            .extra(select={'ativo_conta': ativo_conta_sql},
                   select_params=[conta_id])


class Envio(models.Model):
    """Formas de envios."""
    CODIGO_CORREIOS = ['sedex', 'pac', 'e_sedex', 'sedex_10', 'sedex_hoje',
                       'sedex_cobrar']

    TIPO_CORREIOS_API = 'correios_api'
    TIPO_FAIXA_CEP = 'faixa_cep'
    TIPO_MERCADOENVIOS_API = 'mercadoenvios_api'
    TIPOS = [
        (TIPO_CORREIOS_API, u'API dos Correios'),
        (TIPO_FAIXA_CEP, u'Faixa de CEP e peso'),
        (TIPO_MERCADOENVIOS_API, u'API do Mercado Envios'),
    ]
    ORDEM_XLS = ['regiao', 'cep_inicio', 'cep_fim', 'peso_inicio', 'peso_fim',
                 'valor', 'prazo_entrega', 'ad_valorem', 'kg_adicional']
    CABECALHO_XLS = {
        'regiao': u'Região',
        'cep_inicio': u'Faixa inicial',
        'cep_fim': u'Faixa final',
        'peso_inicio': u'Peso inicial',
        'peso_fim': u'Peso final',
        'valor': u'Valor',
        'prazo_entrega': u'Prazo Entrega',
        'ad_valorem': u'AD Valorem',
        'kg_adicional': u'Kilograma adicional'
    }

    id = custom_models.BigAutoField(db_column="envio_id", primary_key=True)
    nome = models.CharField(db_column="envio_nome", max_length=128)
    codigo = models.CharField(db_column="envio_codigo", max_length=128)
    tipo = models.CharField(db_column="envio_tipo", max_length=128,
                            choices=TIPOS, null=False, default=TIPO_FAIXA_CEP)
    ativo = models.BooleanField(db_column="envio_ativado", default=False)
    imagem = models.CharField(db_column="envio_imagem", max_length=255, default=None, null=True)
    posicao = models.IntegerField(db_column='envio_posicao', default=1000, null=False)

    conta = models.ForeignKey("plataforma.Conta", related_name="formas_envios", null=True, default=None)
    contrato = models.ForeignKey("plataforma.Contrato", related_name="formas_envios", null=True)

    class Meta:
        app_label = "configuracao"
        db_table = u"configuracao\".\"tb_envio"
        verbose_name = u"Forma de envio"
        verbose_name_plural = u"Formas de envios"
        ordering = ["posicao", "nome"]
        unique_together = (("nome", "codigo", "conta"),)

    def __unicode__(self):
        return self.nome

    objects = ConfiguracaoManager()

    def save(self, *args, **kwargs):
        if self.nome and not self.codigo:
            self.codigo = slugify(self.nome)
        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id
        super(self.__class__, self).save(*args, **kwargs)

    def url_imagem(self):
        if self.tipo == self.TIPO_CORREIOS_API:
            return '%spainel/img/formas-de-envio/%s-logo.png' % (
                settings.STATIC_URL, self.codigo)
        elif self.tipo == self.TIPO_FAIXA_CEP and not self.conta_id:
            return '%spainel/img/formas-de-envio/%s-logo.png' % (
                settings.STATIC_URL, self.codigo)
        elif self.imagem:
            return '%s%s' % (settings.MEDIA_URL, self.imagem)
        return None

    def url_imagem_rodape(self):
        if self.tipo == self.TIPO_CORREIOS_API:
            return '%spainel/img/formas-de-envio/%s-logo.png' % (
                settings.STATIC_URL, self.codigo)
        elif self.tipo == self.TIPO_FAIXA_CEP and not self.conta_id:
            return '%simg/formas-de-envio/rodape-%s-logo.png' % (
                settings.STATIC_URL, self.codigo)
        elif self.imagem:
            return '%s%s' % (settings.MEDIA_URL, self.imagem)
        return None

    @property
    def configuracao(self):
        configuracao = EnvioConfiguracao.objects.filter(conta=self.conta, forma_envio=self)
        if configuracao:
            return configuracao[0]
        return EnvioConfiguracao()

    def calcular_frete_trasportadora(self, cep_destino, peso_total, conta_id=None):
        """Calcula o frete de um envio do tipo faixa_cep.

        O cep_destino deve ser uma string com 8 caracteres e o peso_total um
        Decimal com o peso em kg.
        """
        # vamos pegar a faixa de cep
        # verificamos pelo inicio e fim de CEP
        # depois diminuimos a faixa final(sempre maior) pela inicial
        # e ordenamos pelo resultado inverso
        if self.tipo != 'faixa_cep':
            raise FormaDeEnvioNaoCompativel(
                u'Tipo "%s" da forma de envio não é compativel.' % self.tipo)

        if not peso_total:
            peso_total = Decimal(0)
            # raise PesoTotalNaoInformado(u'Peso total não informado.')

        if not isinstance(peso_total, Decimal):
            raise ValueError(u'peso deve ser Decimal, foi enviado %s.' % type(peso_total))

        if isinstance(cep_destino, (str, unicode)):
            cep_destino = ''.join([x for x in cep_destino if x.isdigit()])
            if not cep_destino:
                raise CEPNaoInformado('O CEP não foi informado')
            cep_destino = int(cep_destino)

        faixa_cep = EnvioFaixaCEP.objects.filter(
            conta_id=conta_id, cep_inicio__lte=cep_destino,
            cep_fim__gte=cep_destino, forma_envio=self) \
            .extra(select={'total': 'envio_faixa_cep_cep_fim - envio_faixa_cep_cep_inicio'}) \
            .order_by('total')

        # caso não ache a faixa
        # saimos sem fazer nada
        if not faixa_cep:
            return {}

        # pegamos só o primeiro resultado e sua região.
        faixa_cep = faixa_cep[0]
        regiao = faixa_cep.regiao
        prazo = (self.configuracao.prazo_adicional or 0) + faixa_cep.prazo_entrega

        # soma total do peso dos produtos passados
        faixa_peso = EnvioFaixaPeso.objects.filter(
            conta_id=conta_id, peso_inicio__lte=peso_total,
            peso_fim__gte=peso_total, regiao=regiao).order_by('valor')

        if self.codigo == 'retirar_pessoalmente':
            valor_frete = 0
            prazo = 1
        else:
            # nao tem faixa de peso
            if faixa_peso:
                adicional = 0
                faixa_peso = faixa_peso[0]
            else:
                if not regiao.kg_adicional:
                    return {}
                faixa_peso = EnvioFaixaPeso.objects.filter(
                    conta_id=conta_id, peso_fim__lte=peso_total,
                    regiao=regiao).order_by('-peso_fim')
                if not faixa_peso:
                    return {}
                faixa_peso = faixa_peso[0]
                adicional = regiao.kg_adicional * (peso_total - faixa_peso.peso_fim)

            if not faixa_peso.valor:
                # gratis uhull!
                valor_frete = 0

            valor_frete = faixa_peso.valor + adicional
            # A taxa deve ser calculada sempre depois da definição do valor do frete.
            valor_frete += self.configuracoes.get(
                conta_id=conta_id, forma_envio_id=self.id) \
                .taxa_calculada(valor_frete)

            # Calculando ad valorem no total do frete
            # TODO O Ad valorem precisa do valor total do pedido
            # if regiao.ad_valorem:
            #    valor_frete += ((valor_total/Decimal(100.0)) * regiao.ad_valorem)

        params = {
            'valor_frete': valor_frete,
            'forma_envio': self.nome,
            'regiao': faixa_cep.regiao.nome,
            'imagem': self.imagem,
            'id': self.id,
            'faixa_cep': faixa_cep.id,
            'cep_inicio': faixa_cep.cep_inicio,
            'cep_fim': faixa_cep.cep_fim,
            'prazo': prazo
        }

        if self.codigo != 'retirar_pessoalmente':
            params['faixa_peso'] = faixa_peso.id
            params['peso_inicio'] = faixa_peso.peso_inicio
            params['peso_fim'] = faixa_peso.peso_fim

        return params

    @property
    def correios(self):
        return self.codigo in self.CODIGO_CORREIOS or \
               self.tipo == self.TIPO_CORREIOS_API

    def configurar(self, conta, cep_origem):
        """Configura e habilita a forma de envio com um cep de origem para uma conta.

        Este método só pode ser usado para configurar as formas de envio que não
        precisam de contrato.
        """

        try:
            configuracao = EnvioConfiguracao.objects.get(
                conta=conta, forma_envio=self)
        except EnvioConfiguracao.DoesNotExist:
            configuracao = EnvioConfiguracao(conta=conta, forma_envio=self)

        try:
            contrato = EnvioContrato.objects.get(forma_envio=self, contratado=False)
        except EnvioContrato.DoesNotExist:
            pass
        else:
            configuracao.codigo_servico = contrato.codigo
        if self.tipo == 'correios_api':
            configuracao.cep_origem = cep_origem
        configuracao.ativo = True
        configuracao.save()
        return configuracao

    def exportar_dados_envio(
            self, limite=None, cabecalho=True, conta_id=None,
            limite_regioes=None):
        from repositories.libs.utils import formatar_cep
        saida = []
        if cabecalho:
            saida.append(self.CABECALHO_XLS)

        # regioes = self.regioes.prefetch_related('faixas_cep', 'faixas_peso').all()
        regioes = EnvioRegiao.objects \
            .prefetch_related('faixas_cep', 'faixas_peso') \
            .filter(conta_id=conta_id, forma_envio=self)
        if limite_regioes:
            regioes = regioes[:limite_regioes]

        # regioes = self.configuracoes.get(conta_id=conta_id)\
        #     .regioes.prefetch_related('faixas_cep', 'faixas_peso').all()
        primeira_linha = True
        for regiao in regioes:
            # verificando limite
            if limite:
                faixas_cep = regiao.faixas_cep.all()[:limite]
                faixas_peso = regiao.faixas_peso.all()[:limite]
            else:
                faixas_cep = regiao.faixas_cep.all()
                faixas_peso = regiao.faixas_peso.all()
            for faixa_cep in faixas_cep:
                for faixa_peso in faixas_peso:
                    if primeira_linha:
                        primeira_linha = False
                        ad_valorem = regiao.ad_valorem
                        kg_adicional = regiao.kg_adicional
                    else:
                        ad_valorem = kg_adicional = None

                    row = {
                        'regiao': regiao.nome,
                        'cep_inicio': formatar_cep(faixa_cep.cep_inicio),
                        'cep_fim': formatar_cep(faixa_cep.cep_fim),
                        'peso_inicio': faixa_peso.peso_inicio,
                        'peso_fim': faixa_peso.peso_fim,
                        'valor': faixa_peso.valor,
                        'prazo_entrega': faixa_cep.prazo_entrega,
                        'ad_valorem': ad_valorem,
                        'kg_adicional': kg_adicional,
                        'id': regiao.id
                    }
                    saida.append(row)
            primeira_linha = True
        return saida


class EnvioConfiguracao(models.Model):
    """Configuração das formas de envios."""
    TAXA_TIPOS = [
        ('fixo', u'Valor fixo (R$)'),
        ('porcentagem', u'Porcentagem (%)')
    ]

    id = custom_models.BigAutoField(db_column="envio_configuracao_id", primary_key=True)
    ativo = models.BooleanField(db_column="envio_configuracao_ativo", default=False)
    cep_origem = models.CharField(db_column="envio_configuracao_cep_origem", max_length=8, null=True)
    codigo_servico = models.CharField(db_column="envio_configuracao_codigo_servico", max_length=20, null=True)
    com_contrato = models.BooleanField(db_column="envio_configuracao_com_contrato", default=False)
    codigo = models.CharField(db_column="envio_configuracao_codigo", max_length=128, null=True)
    senha = models.CharField(db_column="envio_configuracao_senha", max_length=128, null=True)
    mao_propria = models.BooleanField(db_column="envio_configuracao_mao_propria", default=False)
    valor_declarado = models.BooleanField(db_column="envio_configuracao_valor_declarado", default=False)
    aviso_recebimento = models.BooleanField(db_column="envio_configuracao_aviso_recebimento", default=False)
    prazo_adicional = models.IntegerField(db_column="envio_configuracao_prazo_adicional", null=True)
    taxa_tipo = models.CharField(db_column="envio_configuracao_taxa_tipo", choices=TAXA_TIPOS, max_length=32, null=True)
    taxa_valor = models.DecimalField(db_column="envio_configuracao_taxa_valor", max_digits=16, decimal_places=2, null=True, blank=True)
    valor_minimo = models.DecimalField(db_column='envio_configuracao_valor_minimo', max_digits=16, decimal_places=2, null=True, blank=True)
    data_criacao = models.DateTimeField(db_column="envio_data_criacao", auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column="envio_data_modificacao", auto_now=True)

    forma_envio = models.ForeignKey('configuracao.Envio', db_column="envio_id", related_name="configuracoes", on_delete=models.CASCADE)
    conta = models.ForeignKey("plataforma.Conta", related_name="formas_envios_configuracoes")
    contrato = models.ForeignKey("plataforma.Contrato", related_name="formas_envios_configuracoes")

    class Meta:
        db_table = u"configuracao\".\"tb_envio_configuracao"
        verbose_name = u"Configuração da forma de envio"
        verbose_name_plural = u"Configurações das formas de envios"
        ordering = ["id"]
        unique_together = (("conta", "forma_envio"),)

    def __unicode__(self):
        return self.cep_origem or ''

    def save(self, *args, **kwargs):
        if not self.com_contrato:
            try:
                self.codigo_servico = EnvioContrato.objects.filter(
                    forma_envio_id=self.forma_envio_id, contratado=False)[0].codigo
            except IndexError:
                self.codigo_servico = ''

        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id
        if self.forma_envio.conta_id and self.forma_envio.conta_id == self.conta_id:
            self.forma_envio.ativo = self.ativo
            self.forma_envio.save()

        super(EnvioConfiguracao, self).save(*args, **kwargs)

    def logar(self, codigo, descricao, **kwargs):
        return None
        # return NoSQLLog(codigo=codigo, conta_id=self.conta_id,
        #                 descricao=descricao, **kwargs).save()

    def taxa_calculada(self, preco=None):
        if preco is None:
            preco = 0
        if not self.taxa_valor:
            return 0
        if self.taxa_tipo == 'fixo':
            return self.taxa_valor
        elif self.taxa_tipo == 'porcentagem':
            return (Decimal(preco) / Decimal('100.0')) * self.taxa_valor

    def exportar_dados_envio(self, *args, **kwargs):
        parametros = kwargs
        parametros['conta_id'] = self.conta_id
        return self.forma_envio.exportar_dados_envio(*args, **parametros)


class EnvioRegiao(models.Model):
    id = custom_models.BigAutoField(db_column="envio_regiao_id", primary_key=True)
    pais = models.CharField(db_column="envio_regiao_pais", max_length=128, null=False, default='Brasil')
    nome = models.CharField(db_column="envio_regiao_nome", max_length=128, null=False)
    ad_valorem = models.DecimalField(db_column="envio_regiao_ad_valorem", max_digits=16, decimal_places=2, default=0, null=True)
    kg_adicional = models.DecimalField(db_column="envio_regiao_kg_adicional", max_digits=16, decimal_places=2, default=0, null=True)

    forma_envio = models.ForeignKey('configuracao.Envio', db_column="envio_id", related_name="regioes", on_delete=models.CASCADE)
    forma_envio_configuracao = models.ForeignKey('configuracao.EnvioConfiguracao', db_column="envio_configuracao_id", related_name="regioes", on_delete=models.CASCADE)
    conta = models.ForeignKey("plataforma.Conta", related_name="formas_envios_regioes")
    contrato = models.ForeignKey("plataforma.Contrato", related_name="formas_envios_regioes")

    class Meta:
        db_table = u"configuracao\".\"tb_envio_regiao"
        verbose_name = u"Região da forma de envio"
        verbose_name_plural = u"Regiões das formas de envio"
        ordering = ["pais", "nome"]
        unique_together = (("pais", "nome", "forma_envio"),)

    def save(self, *args, **kwargs):
        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id
        super(EnvioRegiao, self).save(*args, **kwargs)


class EnvioFaixaCEP(models.Model):
    id = custom_models.BigAutoField(db_column="envio_faixa_cep_id", primary_key=True)
    cep_inicio = models.IntegerField(db_column="envio_faixa_cep_cep_inicio", null=False)
    cep_fim = models.IntegerField(db_column="envio_faixa_cep_cep_fim", null=False)
    prazo_entrega = models.IntegerField(db_column="envio_faixa_cep_prazo_entrega", default=0, null=False)

    regiao = models.ForeignKey('configuracao.EnvioRegiao', db_column="envio_regiao_id", related_name="faixas_cep", on_delete=models.CASCADE)
    forma_envio = models.ForeignKey('configuracao.Envio', db_column="envio_id", related_name="faixas_cep")
    forma_envio_configuracao = models.ForeignKey('configuracao.EnvioConfiguracao', db_column="envio_configuracao_id", related_name="faixas_cep")
    conta = models.ForeignKey("plataforma.Conta", related_name="formas_envios_faixas_cep")
    contrato = models.ForeignKey("plataforma.Contrato", related_name="formas_envios_faixas_cep")

    class Meta:
        db_table = u"configuracao\".\"tb_envio_faixa_cep"
        verbose_name = u"Faixa de CEP para região"
        verbose_name_plural = u"Faixas de CEPs para regiões"
        ordering = ["cep_inicio"]
        unique_together = (("cep_inicio", "cep_fim", "regiao"),)

    def save(self, *args, **kwargs):
        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id
        super(EnvioFaixaCEP, self).save(*args, **kwargs)


class EnvioContrato(models.Model):
    """Contratos das formas de envio."""
    id = custom_models.BigAutoField(db_column="envio_contrato_id", primary_key=True)
    codigo = models.IntegerField(db_column="envio_contrato_servico_codigo")
    descricao = models.CharField(db_column="envio_contrato_descricao", max_length=50)
    contratado = models.BooleanField(db_column="envio_contrato_contratado", default=False)

    forma_envio = models.ForeignKey('configuracao.Envio', db_column="envio_id", related_name="contratos")
    contrato = models.ForeignKey("plataforma.Contrato", related_name="envio_contrato_contrato_fk")

    class Meta:
        db_table = u"configuracao\".\"tb_envio_contrato"
        verbose_name = u"Contrato da forma de envio"
        verbose_name_plural = u"Contratos das formas de envios"
        ordering = ["codigo"]

    def __unicode__(self):
        return self.descricao


class EnvioFaixaPeso(models.Model):
    id = custom_models.BigAutoField(db_column="envio_faixa_peso_id", primary_key=True)
    peso_inicio = models.DecimalField(db_column="envio_faixa_peso_peso_inicio", max_digits=16, decimal_places=3, null=False)
    peso_fim = models.DecimalField(db_column="envio_faixa_peso_peso_fim", max_digits=16, decimal_places=3, null=False)
    valor = models.DecimalField(db_column="envio_faixa_peso_valor", max_digits=16, decimal_places=2, default=0, null=False)

    regiao = models.ForeignKey('configuracao.EnvioRegiao', db_column="envio_regiao_id", related_name="faixas_peso", on_delete=models.CASCADE)
    forma_envio = models.ForeignKey('configuracao.Envio', db_column="envio_id", related_name="faixas_peso")
    forma_envio_configuracao = models.ForeignKey('configuracao.EnvioConfiguracao', db_column="envio_configuracao_id", related_name="faixas_peso")
    conta = models.ForeignKey("plataforma.Conta", related_name="formas_envios_faixas_peso")
    contrato = models.ForeignKey("plataforma.Contrato", related_name="formas_envios_faixas_peso")

    class Meta:
        db_table = u"configuracao\".\"tb_envio_faixa_peso"
        verbose_name = u"Faixa de peso para região"
        verbose_name_plural = u"Faixas de pesos para regiões"
        ordering = ["peso_inicio"]
        unique_together = (("peso_inicio", "peso_fim", "regiao"),)

    def save(self, *args, **kwargs):
        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id
        super(EnvioFaixaPeso, self).save(*args, **kwargs)


class Banco(models.Model):
    id = custom_models.BigAutoField(db_column="banco_id", primary_key=True)
    nome = models.CharField(db_column="banco_nome", max_length=128)
    imagem = models.CharField(db_column='banco_imagem', max_length=256)
    codigo = models.CharField(db_column='banco_codigo', max_length=3)

    class Meta:
        db_table = u"configuracao\".\"tb_banco"
        verbose_name = u'Banco'
        verbose_name_plural = u'Bancos'
        ordering = ['nome']

    @property
    def url_imagem(self):
        if self.imagem:
            if not self.imagem.startswith('http'):
                return '%spainel/img/formas-de-pagamento/%s' % \
                       (settings.STATIC_URL, self.imagem)
            return self.imagem
        return None

    @property
    def url_imagem_loja(self):
        if self.imagem:
            if not self.imagem.startswith('http'):
                return '%simg/formas-de-pagamento/%s' % \
                       (settings.STATIC_URL, self.imagem)
            return self.imagem
        return None

    def __unicode__(self):
        return self.nome

    def natural_key(self):
        return self.nome


class FormaPagamentoManager(models.Manager):

    def configuracoes_ativas(self, conta_id=None):
        return super(FormaPagamentoManager, self).raw(
            """SELECT
                    pg.pagamento_id,
                    pg.pagamento_nome,
                    pg.pagamento_codigo,
                    pg.pagamento_ativado,
                    pgc.pagamento_configuracao_id,
                    pgc.pagamento_configuracao_usuario,
                    pgc.pagamento_configuracao_senha,
                    pgc.pagamento_configuracao_token,
                    pgc.pagamento_configuracao_assinatura,
                    pgc.pagamento_configuracao_codigo_autorizacao,
                    pgc.pagamento_configuracao_ativo,
                    pgc.pagamento_configuracao_json,
                    pgc.conta_id
               FROM configuracao.tb_pagamento as pg
               LEFT OUTER JOIN configuracao.tb_pagamento_configuracao as pgc on (pgc.pagamento_id = pg.pagamento_id AND pgc.conta_id=%s)
               WHERE pg.pagamento_ativado = true""",
            [conta_id]
        )


class FormaPagamento(models.Model):
    """Forma de pagamento."""

    CODIGOS_GATEWAYS = ['pagseguro', 'bcash', 'mercadopago', 'paypal', 'koin']

    PRINCIPAIS_FORMAS_PAGAMENTO = {
        'bcash': {
            'cartoes': ['visa', 'mastercard', 'hipercard', 'amex'],
            'bancos': ['banco-itau', 'bradesco', 'banco-do-brasil'],
            'outros': ['boleto']
        },
        'pagarme': {
            'cartoes': ['visa', 'mastercard'],
        },
        'pagseguro': {
            'cartoes': ['visa', 'mastercard', 'hipercard', 'amex'],
            'bancos': ['banco-itau', 'bradesco', 'banco-do-brasil'],
            'outros': ['boleto']
        },
        'paypal': {
            'cartoes': ['visa', 'mastercard', 'amex']
        },
        'mercadopago': {
            'cartoes': ['visa', 'mastercard', 'amex', 'elo'],
            'outros': ['boleto']
        },
        'koin': {
            'outros': ['boleto']
        }
    }

    id = custom_models.BigAutoField(db_column="pagamento_id", primary_key=True)
    nome = models.CharField(db_column="pagamento_nome", max_length=128)
    codigo = models.CharField(db_column="pagamento_codigo", max_length=128, unique=True)
    ativo = models.BooleanField(db_column="pagamento_ativado", default=False)
    valor_minimo_parcela = models.DecimalField(
        db_column='pagamento_parcela_valor_minimo_parcela', max_digits=16,
        decimal_places=2, null=True)
    valor_minimo_parcelamento = models.DecimalField(
        db_column='pagamento_parcela_valor_minimo', max_digits=16,
        decimal_places=2, null=True)
    plano_indice = models.IntegerField(db_column='pagamento_plano_indice', default=1)
    posicao = models.IntegerField(db_column='pagamento_posicao', default=1000, null=False)

    conta = models.ForeignKey("plataforma.Conta", related_name="formas_pagamentos", null=True, default=None)
    contrato = models.ForeignKey("plataforma.Contrato", related_name="formas_pagamentos", null=True, default=None)
    _pedidos = models.ManyToManyField('pedido.PedidoVenda', through='pedido.PedidoVendaFormaPagamento', related_name='_pedidos')

    class Meta:
        app_label = "configuracao"
        db_table = u"configuracao\".\"tb_pagamento"
        verbose_name = u"Forma de pagamento"
        verbose_name_plural = u"Formas de pagamentos"
        ordering = ["posicao", "nome"]

    def save(self, *args, **kwargs):
        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id
        super(FormaPagamento, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.nome

    @property
    def url_imagem(self):
        return '%spainel/img/formas-de-pagamento/%s-logo.png' % (settings.STATIC_URL, self.codigo)

    def principais_pagamentos(self):
        return self.PRINCIPAIS_FORMAS_PAGAMENTO.get(self.codigo, {})

    def criar_configuracao_vazia(self, conta_id):
        """ Cria uma configuracao vazia para a forma de pagamento
        util até agora em só um caso"""
        configuracao = FormaPagamentoConfiguracao.objects.create(
            conta_id=conta_id, forma_pagamento_id=self.id)
        return configuracao

    # objects = models.Manager()
    objects = FormaPagamentoManager()


class FormaPagamentoConfiguracao(models.Model):
    """Configuração da forma de pagamento."""
    TIPO_VALOR_FIXO = 'fixo'
    TIPO_PORCENTAGEM = 'porcentagem'

    id = custom_models.BigAutoField(db_column="pagamento_configuracao_id", primary_key=True)
    usuario = models.CharField(db_column="pagamento_configuracao_usuario", max_length=128, null=True)
    senha = models.CharField(db_column="pagamento_configuracao_senha", max_length=128, null=True)
    token = models.CharField(db_column="pagamento_configuracao_token", max_length=128, null=True)
    token_expiracao = models.DateTimeField(db_column="pagamento_configuracao_token_expiracao", null=True)
    assinatura = models.CharField(db_column="pagamento_configuracao_assinatura", max_length=128, null=True)
    codigo_autorizacao = models.CharField(db_column="pagamento_configuracao_codigo_autorizacao", max_length=128, null=True)
    usar_antifraude = models.NullBooleanField(db_column='pagamento_configuracao_usar_antifraude', null=True, default=False)
    aplicacao = models.CharField(db_column="pagamento_configuracao_aplicacao_id", max_length=128, null=True, default=None)
    ativo = models.BooleanField(db_column="pagamento_configuracao_ativo", default=False)
    eh_padrao = models.BooleanField(db_column="pagamento_configuracao_eh_padrao", default=False)
    mostrar_parcelamento = models.BooleanField(db_column='pagamento_coonfiguracao_mostrar_parcelamento', default=False, null=False)
    maximo_parcelas = models.IntegerField(db_column="pagamento_configuracao_quantidade_parcela_maxima", default=None, null=True)
    parcelas_sem_juros = models.IntegerField(db_column="pagamento_configuracao_quantidade_parcela_sem_juros", default=None, null=True)
    desconto = models.BooleanField(db_column="pagamento_configuracao_desconto", default=False, null=False)
    desconto_tipo = models.CharField(db_column="pagamento_configuracao_desconto_tipo", max_length=32, default=TIPO_PORCENTAGEM)
    desconto_valor = models.DecimalField(db_column='pagamento_configuracao_desconto_valor', max_digits=16, decimal_places=2, null=True)
    juros_valor = models.DecimalField(db_column='pagamento_configuracao_juros_valor', max_digits=16, decimal_places=2, null=True)
    email_comprovante = models.EmailField(db_column='pagamento_configuracao_email_comprovante', null=True)
    informacao_complementar = models.TextField(db_column='pagamento_configuracao_informacao_complementar', null=True)
    aplicar_no_total = models.BooleanField(db_column='pagamento_configuracao_desconto_aplicar_no_total', null=False, default=False)
    valor_minimo_aceitado = models.DecimalField(db_column='pagamento_configuracao_valor_minimo_aceitado', max_digits=16, decimal_places=2, null=True)
    valor_minimo_parcela = models.DecimalField(db_column='pagamento_configuracao_valor_minimo_parcela', max_digits=16, decimal_places=2, null=True)
    ordem = models.IntegerField(db_column='pagamento_configuracao_ordem', default=0)

    json = JSONField(db_column='pagamento_configuracao_json', null=True, default=None)

    forma_pagamento = models.ForeignKey('configuracao.FormaPagamento', db_column="pagamento_id", related_name="configuracoes")
    conta = models.ForeignKey("plataforma.Conta", related_name="formas_pagamentos_configuracoes")
    contrato = models.ForeignKey("plataforma.Contrato", related_name="formas_pagamentos_configuracoes")

    data_criacao = models.DateTimeField(db_column='pagamento_configuracao_data_criacao', auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column='pagamento_configuracao_data_modificacao', null=True, auto_now=True)

    class Meta:
        db_table = u"configuracao\".\"tb_pagamento_configuracao"
        verbose_name = u"Configuração da forma de pagamento"
        verbose_name_plural = u"Configurações das formas de pagamentos"
        ordering = ["id"]
        unique_together = (("conta", "forma_pagamento"),)

    def __unicode__(self):
        return unicode(self.id)

    def save(self, *args, **kwargs):
        self.desconto_tipo = self.TIPO_PORCENTAGEM

        if self.maximo_parcelas != 0 and self.parcelas_sem_juros > self.maximo_parcelas:
            self.parcelas_sem_juros = self.maximo_parcelas

        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id

        # Se o email adicionado for igual ao email da conta, não precisa
        # adicionar, ele será pego sempre da conta.
        if (self.email_comprovante and self.conta_id and
                    self.conta.email == self.email_comprovante):
            self.email_comprovante = None

        super(FormaPagamentoConfiguracao, self).save(*args, **kwargs)

    def logar(self, codigo, descricao, **kwargs):
        return None
        # return NoSQLLog(codigo=codigo, conta_id=self.conta_id,
        #                 descricao=descricao, **kwargs).save()

    def principais_pagamentos(self):
        return self.forma_pagamento.principais_pagamentos()

    def total_parcelas(self):
        # Paypal sempre vai usar o maximo de parcelas
        # já que não existe parcelas com juros.
        if self.parcelas_sem_juros > 1:
            return self.parcelas_sem_juros
        elif self.maximo_parcelas > 1:
            return self.maximo_parcelas
        else:
            return None

    def calcular_porcentagem(self, valor_1, valor_2):
        """
        Calcula a porcentagem e retorna o valor.
        """
        return valor_1 * Decimal('%0.2f' % valor_2) / Decimal('100')

    def credenciais_pagseguro(self):
        """Retorna o app_id, app_key do PagSeguro de acordo
        com a instalação do lojista"""
        return self.contrato.credenciais_pagseguro(aplicacao=self.aplicacao)

    @classmethod
    def parcelamento(cls, conta_id=None, configuracoes_pagamento=None):
        try:
            pagamento_com_mais_parcelas_sem_juros = FormaPagamentoConfiguracao.objects.only('forma_pagamento_id').filter(
                mostrar_parcelamento=True, conta_id=conta_id, forma_pagamento_id__in=[x['meio_pagamento']['id'] for x in configuracoes_pagamento]
            ).exclude(parcelas_sem_juros__isnull=True).order_by('-parcelas_sem_juros')[0]
        except IndexError:
            return None
        parcelas = Parcela.objects.filter(forma_pagamento_id=pagamento_com_mais_parcelas_sem_juros.forma_pagamento_id)
        if not parcelas:
            return None

        pagamento_com_mais_parcelas_sem_juros.parcelas = parcelas
        return pagamento_com_mais_parcelas_sem_juros

    def valor_minimo_parcelamento(self):
        """
        Retorna o valor minimio do parcelamento, se existir uma configuração
        do usuário (Atualmente só disponivel para o Paypal) irá retornar ela,
        caso contrario retorna o padrão para a forma de pagamento
        """
        if self.valor_minimo_parcela and self.valor_minimo_parcela > 0:
            return self.valor_minimo_parcela
        return self.forma_pagamento.valor_minimo_parcela

    def bancos_ativos(self):
        return Banco.objects.filter(bancos_pagamentos__conta=self.conta)

    @property
    def pagamento_bancos_ativos(self):
        return PagamentoBanco.objects.filter(pagamento=self.forma_pagamento, conta=self.conta_id, ativo=True)

    def habilitado(self, plano_indice):
        try:
            plano_indice = int(plano_indice)
        except ValueError:
            plano_indice = 1
        return self.ativo and self.forma_pagamento.ativo and self.configurado and self.forma_pagamento.plano_indice <= plano_indice

    @property
    def configurado(self):
        try:
            try:
                bancos = self.pagamento_bancos_ativos[0]
            except IndexError:
                bancos = None
            return (self.usuario or
                    self.senha or
                    self.assinatura or
                    self.token or
                    self.codigo_autorizacao or
                    bancos or self.json)
        except AttributeError:
            return False


class BoletoCarteira(models.Model):
    id = custom_models.BigAutoField(db_column="boleto_carteira_id", primary_key=True)

    numero = models.CharField(db_column="boleto_carteira_numero", max_length=32, null=False)
    nome = models.CharField(db_column="boleto_carteira_nome", max_length=128, null=False)
    convenio = models.BooleanField(db_column="boleto_carteira_convenio", default=False, null=False)
    ativo = models.BooleanField(db_column="boleto_carteira_ativo", default=False, null=False)

    banco = models.ForeignKey('configuracao.Banco', db_column="banco_id", related_name='carteiras')

    class Meta:
        db_table = u"configuracao\".\"tb_boleto_carteira"
        verbose_name = u'Carteira de boleto'
        verbose_name_plural = u'Carteiras de boletos'
        unique_together = (('banco', 'numero', 'convenio'),)

    def __unicode__(self):
        return self.nome


class Parcela(caching.base.CachingMixin, models.Model):
    objects = caching.base.CachingManager()

    id = custom_models.BigAutoField(db_column="pagamento_parcela_id", primary_key=True)
    numero_parcelas = models.IntegerField(db_column="pagamento_parcela_numero_parcelas")
    fator = models.DecimalField(db_column="pagamento_parcela_fator", max_digits=16, decimal_places=6, null=True)

    forma_pagamento = models.ForeignKey('configuracao.FormaPagamento', db_column="pagamento_id", related_name="parcelas")

    class Meta:
        db_table = u"configuracao\".\"tb_pagamento_parcela"
        verbose_name = u'Parcela'
        verbose_name_plural = u"Parcelas"
        ordering = ['id']


class PagamentoBanco(models.Model):

    id = custom_models.BigAutoField(db_column="pagamento_banco_id", primary_key=True)
    agencia = models.CharField(db_column="pagamento_banco_agencia", max_length=11, null=False)
    numero_conta = models.CharField(db_column="pagamento_banco_conta", max_length=11, null=False)
    poupanca = models.BooleanField(db_column="pagamento_banco_poupanca", default=True, null=False)
    operacao = models.CharField(db_column="pagamento_banco_variacao", max_length=10, null=True)
    favorecido = models.CharField(db_column="pagamento_banco_favorecido", max_length=256)
    cpf = models.CharField(db_column="pagamento_banco_cpf", max_length=11, null=True)
    cnpj = models.CharField(db_column="pagamento_banco_cnpj", max_length=14, null=True)
    ativo = models.BooleanField(db_column="pagamento_banco_ativo", null=False, default=False)

    banco = models.ForeignKey('configuracao.Banco', db_column="banco_id", related_name='bancos_pagamentos')
    conta = models.ForeignKey('plataforma.Conta', related_name='pagamento_bancos')
    pagamento = models.ForeignKey('configuracao.FormaPagamento', db_column="pagamento_id", related_name='bancos')
    contrato = models.ForeignKey("plataforma.Contrato", related_name="pagamento_bancos")

    class Meta:
        db_table = u"configuracao\".\"tb_pagamento_banco"
        verbose_name = u'Banco para depósito'
        verbose_name_plural = u'Bancos para depósito'
        unique_together = (('banco', 'conta'),)

    def __unicode__(self):
        return unicode(self.nome)

    def __repr__(self):
        return slugify(self.nome)

    @property
    def imagem(self):
        return self.banco.url_imagem
    url_imagem = imagem

    @property
    def imagem_loja(self):
        return self.banco.url_imagem_loja
    url_imagem_loja = imagem_loja

    @property
    def nome(self):
        # if self.banco:
        #     return self.banco.nome
        # return self.nome
        return self.banco.nome
    nome_banco = nome

    @property
    def cpf_cnpj(self):
        return self.cpf or self.cnpj or None

    def save(self, *args, **kwargs):
        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id
        super(PagamentoBanco, self).save(*args, **kwargs)


class EdicaoTema(models.Model):
    id = custom_models.BigAutoField(db_column='edicao_tema_id', primary_key=True)
    ativo = models.BooleanField(db_column='edicao_tema_ativo', default=True)
    nome = models.CharField(db_column='edicao_tema_nome', max_length=64)
    css = models.TextField(db_column='edicao_tema_css', null=True, default=None)
    json = models.TextField(db_column='edicao_tema_json', null=True, default=None)
    data_criacao = models.DateTimeField(db_column="data_criacao", auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column="data_modificacao", auto_now=True, null=True)

    conta = models.OneToOneField('plataforma.Conta', db_column='conta_id')
    contrato = models.ForeignKey('plataforma.Contrato', related_name="edicoes_temas")

    def save(self, *args, **kwargs):
        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id
        super(EdicaoTema, self).save(*args, **kwargs)

    class Meta:
        db_table = u"configuracao\".\"tb_edicao_tema"
        verbose_name = u'Edição Tema'
        verbose_name_plural = u'Edições Tema'
        ordering = ['nome']


class Dominio(models.Model):
    """Lista de domínios habilitados para uma conta."""
    id = custom_models.BigAutoField(db_column="dominio_id", primary_key=True)
    fqdn = models.CharField(db_column="dominio_fqdn", max_length=128, null=False, unique=True)
    principal = models.BooleanField(db_column="dominio_principal", default=False, db_index=True)
    verificado = models.BooleanField(db_column="dominio_verificado", default=False, db_index=True)

    data_criacao = models.DateTimeField(db_column="dominio_data_criacao", auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column="dominio_data_modificacao", auto_now=True, null=True)

    conta = models.ForeignKey("plataforma.Conta", db_column="conta_id", related_name="dominios")
    contrato = models.ForeignKey('plataforma.Contrato', related_name="dominios")

    class Meta:
        db_table = u"configuracao\".\"tb_dominio"
        verbose_name = u"Domínio de uma conta"
        verbose_name_plural = u"Domínios de uma conta"
        ordering = ["principal", "verificado", "fqdn"]
        get_latest_by = "data_modificacao"

    def __unicode__(self):
        return self.fqdn

    def _partes_fqdn(self):
        """Retorna um objeto com os atributos domin, subdomin e tld."""
        return tldextract.extract(self.fqdn)

    @property
    def subdominio(self):
        return self._partes_fqdn().subdomain

    @property
    def dominio(self):
        partes_fqdn = self._partes_fqdn()
        return u'%s.%s' % (partes_fqdn.domain, partes_fqdn.tld)

    def definir_como_principal(self):
        self.conta.dominios.all().update(principal=False)

        self.conta.dominio = self.fqdn
        self.conta.save()

        self.principal = True
        self.save()
        return self

    def save(self, *args, **kwargs):
        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id

        super(Dominio, self).save(*args, **kwargs)


@receiver(post_delete, sender=Dominio)
def dominio_post_delete(sender, instance, **kwargs):
    quantidade_dominios = instance.conta.dominios.count()
    if not quantidade_dominios:
        instance.conta.dominio = None
        instance.conta.selo_google_safe = False
        instance.conta.selo_norton_secured = False
        instance.conta.save()


class Facebook(models.Model):
    id = custom_models.BigAutoField(db_column='conta_facebook_id', primary_key=True)
    access_token = models.TextField(db_column='conta_facebook_oauth_token')
    pagina = models.CharField(db_column='conta_facebook_pagina_id', max_length=255)
    usuario = models.CharField(db_column='conta_facebook_usuario_id', max_length=255)
    expires = models.DateTimeField(db_column='conta_facebook_oauth_token_expires')
    app_id = models.CharField(db_column='conta_facebook_app_id', max_length=255)
    app_secret = models.CharField(db_column='conta_facebook_app_secret', max_length=255)
    pro = models.BooleanField(db_column='conta_facebook_pro', default=False)
    contrato = models.ForeignKey('plataforma.Contrato', related_name="contas_facebook")

    conta = models.ForeignKey('plataforma.Conta', db_column='conta_id', related_name='contas_facebook')

    class Meta:
        db_table = u'configuracao\".\"tb_facebook'
        verbose_name = u'Conta Facebook'
        verbose_name_plural = u'Contas Facebook'
        ordering = ['id']

    def save(self, *args, **kwargs):
        if self.expires and not isinstance(self.expires, datetime.datetime):
            self.expires = datetime.datetime.fromtimestamp(time.time() + int(self.expires))
        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id
        super(Facebook, self).save(*args, **kwargs)

    @property
    def expired(self):
        if self.expires and datetime.datetime.now() > self.expires:
            return True
        return False


class ConfiguracaoFacebook(models.Model):

    id = custom_models.BigAutoField(db_column='conta_configuracao_facebook_id', primary_key=True)
    comentarios_produtos = models.BooleanField(db_column='conta_configuracao_facebook_comentarios_produtos', default=False)
    usuario = models.CharField(db_column='conta_configuracao_facebook_user_admin', max_length=255)
    pagina = models.TextField(db_column='conta_configuracao_facebook_pagina')
    compartilhar_compra = models.BooleanField(db_column='conta_configuracao_facebook_compartilhar_compra', default=False)
    publicar_novos_produtos = models.BooleanField(db_column='conta_configuracao_facebook_publicar_novos_produtos', default=False)
    contrato = models.ForeignKey('plataforma.Contrato', related_name="configuracoes_facebook")

    conta = models.ForeignKey('plataforma.Conta', db_column='conta_id', related_name='configuracoes_facebook')

    class Meta:
        db_table = u'configuracao\".\"tb_configuracao_facebook'
        verbose_name = u'Configuração Facebook'
        verbose_name_plural = u'Configurações Facebook'
        ordering = ['id']

    def save(self, *args, **kwargs):
        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id
        super(ConfiguracaoFacebook, self).save(*args, **kwargs)


class CodigoHTML(models.Model):

    LOCAIS_PUBLICACAO = [
        ('cabecalho', 'Cabeçalho'),
        ('rodape', u'Rodapé'),
    ]

    PAGINAS_PUBLICACOES = [
        ('todas', u'Todas as páginas'),
        ('loja/index', u'Página inicial - Home'),
        ('loja/produto_detalhar', u'Página do produto'),
        ('loja/categoria_listar', u'Página da categoria'),
        ('loja/carrinho_index', u'Página do carrinho'),
        ('loja/checkout_index', u'Página de checkout'),
        ('loja/checkout_finalizacao', u'Página de finalização do pedido'),
    ]

    TIPOS_DADOS = [
        ('html', 'HTML'),
        ('css', 'Cascade Style Sheet (CSS)'),
        ('javascript', 'JavaScript'),
    ]

    DESCRICAO_CABECALHO_PADRAO = 'Código do cabecalho'
    DESCRICAO_RODAPE_PADRAO = 'Código do rodapé'

    id = custom_models.BigAutoField(db_column="codigo_html_id", primary_key=True)
    descricao = models.CharField(db_column="codigo_html_descricao",
                                 max_length=32, verbose_name=u"Descrição")
    local_publicacao = models.CharField(db_column="codigo_html_local_publicacao", max_length=32, choices=LOCAIS_PUBLICACAO,
                                        verbose_name=u"Local publicação", default="rodape")
    pagina_publicacao = models.CharField(db_column="codigo_html_pagina_publicacao", max_length=32, choices=PAGINAS_PUBLICACOES,
                                         verbose_name=u"Página publicação")
    data_criacao = models.DateTimeField(db_column="codigo_html_data_criacao", auto_now_add=True,
                                        verbose_name=u"Data criação")
    data_modificacao = models.DateTimeField(
        db_column="codigo_html_data_modificacao", auto_now=True, null=True)
    conteudo = models.CharField(
        db_column="codigo_html_conteudo", null=False, blank=False,
        max_length=15000, help_text='Tamanho máximo de 15000 caracteres')
    tipo = models.CharField(
        db_column="codigo_html_tipo", max_length=16, null=False,
        blank=False, choices=TIPOS_DADOS, default="html")

    conta = models.ForeignKey('plataforma.Conta', related_name='codigos_html')
    contrato = models.ForeignKey('plataforma.Contrato', related_name='codigos_html')

    class Meta:
        db_table = u"configuracao\".\"tb_codigo_html"
        verbose_name = u'HTML Customizado'
        verbose_name_plural = u'HTMLs Customizados'
        unique_together = ('conta', 'descricao')

    def save(self, *args, **kwargs):
        if not self.contrato_id and self.conta:
            self.contrato_id = self.conta.contrato_id
        super(CodigoHTML, self).save(*args, **kwargs)


class Token(models.Model):

    id = custom_models.BigAutoField(db_column="token_id", primary_key=True)
    descricao = models.CharField(db_column="token_descricao", max_length=32, null=False)
    token = models.CharField(db_column="token_token", max_length=20, null=False, unique=True)

    conta = models.ForeignKey('plataforma.Conta', related_name='tokens')
    contrato = models.ForeignKey('plataforma.Contrato', related_name='tokens')

    class Meta:
        db_table = u"configuracao\".\"tb_token"
        verbose_name = u'Token de acesso'
        verbose_name_plural = u'Tokens de acesso'

    def save(self, *args, **kwargs):
        if not self.contrato_id and self.conta:
            self.contrato_id = self.conta.contrato_id
        if not self.token or hasattr('_renovar', self):
            self.token = self.gerar_token()
        super(Token, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.token

    def gerar_token(self):
        """Gera o token de acesso
        usa o id do token + id da conta e data de modificação"""
        return hash('%s..%s..%s..%s' % (self.conta_id, self.id, self.conta.data_modificacao, datetime.datetime.now()))[:20]

