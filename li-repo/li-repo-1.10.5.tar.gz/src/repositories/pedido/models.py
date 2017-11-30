# -*- coding: utf-8 -*-
import datetime
from decimal import Decimal
import hashlib
import json
import random
import re

from django.db import models
from django.db.models import F, Count, Sum, Max
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save

from repositories import custom_models
from django.db.models import Q

from jsonfield import JSONField


class BoletoNaoPodeSerEmititdo(Exception):
    pass


class PedidoVendaSituacaoManager(models.Manager):
    def ordenados(self):
        situacao_1 = []
        situacao_2 = []
        situacao_3 = []
        for situacao in PedidoVendaSituacao.objects.filter(ativo=True):
            # TODO: MUDAR CLASSE
            """Retorna a classe (CSS) da situação"""
            if situacao.id == 4: #Pago
                situacao.situacao_classe = 'label-success'
            elif situacao.id == 9: #Efetuado
                situacao.situacao_classe = 'label-warning'
            elif situacao.id == 11: #Enviado
                situacao.situacao_classe = 'label-primary'
            elif situacao.id == 14: #Entregue
                situacao.situacao_classe = 'label-default'
            elif situacao.id == 8: #Cancelado
                situacao.situacao_classe = 'label-important'
            elif 'pagamento' in situacao.nome.lower():
                situacao.situacao_classe = 'label-color-2'
            elif len(re.findall(r'\w+', situacao.nome)) > 1:
                situacao.situacao_classe = 'label-color-1'
            else:
                situacao.situacao_classe = 'label-info'

            # Separando em blocos
            if situacao.id == 8 or situacao.id == 14 or situacao.id == 11 or situacao.id == 4 or situacao.id == 9:
                situacao.color = '#c7e3ff'
                situacao_1.append(situacao)
            elif 'pagamento' not in situacao.nome.lower():
                situacao.color = '#d8ecff'
                situacao_2.append(situacao)
            else:
                situacao.color = '#e7f3fe'
                situacao_3.append(situacao)
        return situacao_1 + situacao_2 + situacao_3


class PedidoVendaSituacao(models.Model):
    """Situação de pedido de venda."""
    SITUACAO_PEDIDO_PENDENTE = 1
    SITUACAO_AGUARDANDO_PAGTO = 2
    SITUACAO_PAGTO_EM_ANALISE = 3
    SITUACAO_PEDIDO_PAGO = 4
    SITUACAO_PAGTO_EM_DISPUTA = 6
    SITUACAO_PAGTO_DEVOLVIDO = 7
    SITUACAO_PEDIDO_CANCELADO = 8
    SITUACAO_PEDIDO_EFETUADO = 9
    SITUACAO_PEDIDO_ENVIADO = 11
    SITUACAO_PRONTO_RETIRADA = 13
    SITUACAO_PEDIDO_ENTREGUE = 14
    SITUACAO_PEDIDO_EM_SEPARACAO = 15
    SITUACAO_PAGTO_CHARGEBACK = 16

    id = custom_models.BigAutoField(db_column="pedido_venda_situacao_id", primary_key=True)
    nome = models.CharField(db_column="pedido_venda_situacao_nome", max_length=64)
    codigo = models.CharField(db_column="pedido_venda_situacao_codigo", max_length=64)
    aprovado = models.BooleanField(db_column="pedido_venda_situacao_aprovado", default=False)
    cancelado = models.BooleanField(db_column="pedido_venda_situacao_cancelado", default=False)
    final = models.BooleanField(db_column="pedido_venda_situacao_final", default=False)
    padrao = models.BooleanField(db_column="pedido_venda_situacao_padrao", default=False)
    notificar_comprador = models.BooleanField(db_column="pedido_venda_situacao_notificar_comprador", default=False)
    ativo = models.BooleanField(db_column="pedido_venda_situacao_ativo", default=False)
    data_criacao = models.DateTimeField(db_column="pedido_venda_situacao_data_criacao", auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column="pedido_venda_situacao_data_modificacao", auto_now=True, null=True)

    conta = models.ForeignKey('plataforma.Conta', related_name='pedido_venda_situacoes', null=True, default=None)
    contrato = models.ForeignKey('plataforma.Contrato', related_name='pedido_venda_situacoes', null=True, default=None)

    @classmethod
    def obter_situacao_cancelado(cls):
        return PedidoVendaSituacao.objects.get(pk=PedidoVendaSituacao.SITUACAO_PEDIDO_CANCELADO)

    def nome_situacao(self):
        """Na listagem dos pedidos no ADMIN deve ser
        retirado o 'Pedido' da string"""
        r = '(Pedido|[ ]?Pagamento|Pronto\ para)'
        if re.search(r, self.nome):
            return re.sub(r, '', self.nome).title().strip()
        return self.nome

    class Meta:
        db_table = u"pedido\".\"tb_pedido_venda_situacao"
        verbose_name = u'Situação do pedido de venda'
        verbose_name_plural = u"Situações de pedidos de vendas"
        ordering = ['nome']
        unique_together = (("conta", "nome"),)

    def __unicode__(self):
        return self.nome


class PedidoVendaTipo(models.Model):
    """Tipo de pedido de venda."""
    id = custom_models.BigAutoField(db_column="pedido_venda_tipo_id", primary_key=True)
    nome = models.CharField(db_column="pedido_venda_tipo_nome", max_length=64)

    class Meta:
        db_table = u"pedido\".\"tb_pedido_venda_tipo"
        verbose_name = u'Tipo de pedido de venda'
        verbose_name_plural = u"Tipos de pedidos de vendas"
        ordering = ['nome']

    def __unicode__(self):
        return self.nome


class PedidoVendaEndereco(models.Model):
    """Endereço de um pedido de venda. Esta é basicamente uma cópia da tabela
    de endereço do CRM.

    Esta cópia dos dados serve como cache para que não altere o endereço caso
    o cliente altere qualquer depois de criar o pedido de venda.
    """
    ENDERECO_TIPOS = [
        ("pf", u"Pessoa Física"),
        ("pj", u"Pessoa Jurídica"),
    ]

    id = custom_models.BigAutoField(db_column="pedido_venda_endereco_id", primary_key=True)
    tipo = models.CharField(db_column="pedido_venda_endereco_tipo", max_length=64, choices=ENDERECO_TIPOS)
    cpf = models.CharField(db_column="pedido_venda_endereco_cpf", max_length=11, null=True)
    rg = models.CharField(db_column="pedido_venda_endereco_rg", max_length=20, null=True)
    cnpj = models.CharField(db_column="pedido_venda_endereco_cnpj", max_length=14, null=True)
    razao_social = models.CharField(db_column="pedido_venda_endereco_razao_social", max_length=255, null=True)
    ie = models.CharField(db_column="pedido_venda_endereco_ie", max_length=20, null=True)
    nome = models.CharField(db_column="pedido_venda_endereco_nome", max_length=255, null=False, blank=False)
    endereco = models.CharField(db_column="pedido_venda_endereco_endereco", max_length=255, null=False, blank=False)
    numero = models.CharField(db_column="pedido_venda_endereco_numero", max_length=10, null=False, blank=False)
    complemento = models.CharField(db_column="pedido_venda_endereco_complemento", max_length=255, null=True)
    referencia = models.CharField(db_column="pedido_venda_endereco_referencia", max_length=255, null=True)
    bairro = models.CharField(db_column="pedido_venda_endereco_bairro", max_length=128, null=False, blank=False)
    cidade = models.CharField(db_column="pedido_venda_endereco_cidade", max_length=128, null=False, blank=False)
    estado = models.CharField(db_column="pedido_venda_endereco_estado", max_length=2, null=False, blank=False)
    cep = models.CharField(db_column="pedido_venda_endereco_cep", max_length=8, null=False, blank=False)
    pais = models.CharField(db_column="pedido_venda_endereco_pais", max_length=128, null=True)

    conta = models.ForeignKey("plataforma.Conta", related_name="pedido_venda_enderecos")
    contrato = models.ForeignKey("plataforma.Contrato", related_name="pedido_venda_enderecos")

    class Meta:
        db_table = u"pedido\".\"tb_pedido_venda_endereco"
        verbose_name = u'Endereço do pedido de venda'
        verbose_name_plural = u"Endereços de pedidos de vendas"
        ordering = ['id']

    def __unicode__(self):
        return unicode(self.id)

    def save(self, *args, **kwargs):
        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id
        super(PedidoVendaEndereco, self).save(*args, **kwargs)

    @property
    def completo(self):
        complemento = self.complemento and (" - %s" % self.complemento) or ""
        return "%s, %s%s - %s, %s / %s - CEP: %s" % (
            self.endereco, self.numero, complemento, self.bairro,
            self.cidade, self.estado, self.cep)

    def codigo_ibge(self):
        """Retorna o código IBGE da cidade"""
        from repositories.domain.models import Cidade

        if not self.cidade:
            return None
        try:
            cidade = Cidade.objects.filter(
                Q(cidade_alt__in=[self.cidade.upper(), self.cidade])|
                Q(cidade__in=[self.cidade.upper(), self.cidade]),
                uf=self.estado
            )[0]
        except IndexError:
            return '0000000'
        else:
            return cidade.uf_munic


class PedidoVendaManager(models.Manager):
    def _com_relacionados(self, select=None, prefetch=None):
        select_related = ['situacao', 'tipo'] + (select or [])
        prefetch_related = ['envios', 'pagamentos'] + (prefetch or [])
        return self.select_related(*select_related).prefetch_related(*prefetch_related)

    def buscar(self, conta_id, *args, **kwargs):
        return self._com_relacionados().filter(conta_id=conta_id, *args, **kwargs)

    def get_by_numero(self, conta_id, numero, *args, **kwargs):
        select_related = ['cliente', 'cupom']
        prefetch_related = ['itens', 'itens__produto']
        return self._com_relacionados(select=select_related, prefetch=prefetch_related).get(conta_id=conta_id, numero=numero)


class PedidoVenda(models.Model):
    """Pedido de venda."""

    MAXIMO_DIAS_PEDIDO = 6

    SITUACOES_PAGAS = [4]
    SITUACOES_DISPONIVEIS = [11, 13, 14]
    SITUACOES_INTERNAS = [15]
    SITUACOES_CONCLUIDAS = (SITUACOES_PAGAS + SITUACOES_DISPONIVEIS +
                            SITUACOES_INTERNAS)
    SITUACOES_AGUARDANDO_PAGAMENTO = [2, 3, 9]
    SITUACOES_CANCELADAS = [6, 7, 8]
    TODAS_SITUACOES = (SITUACOES_CONCLUIDAS + SITUACOES_AGUARDANDO_PAGAMENTO +
                       SITUACOES_CANCELADAS)

    objects = PedidoVendaManager()

    id = custom_models.BigAutoField(db_column='pedido_venda_id', primary_key=True)
    numero = models.BigIntegerField(db_column='pedido_venda_numero', null=False, db_index=True)
    consolidado = models.BooleanField(db_column='pedido_venda_consolidado', default=False)

    telefone_principal = models.CharField(db_column='pedido_venda_telefone_principal', max_length=11, null=True)
    telefone_comercial = models.CharField(db_column='pedido_venda_telefone_comercial', max_length=11, null=True)
    telefone_celular = models.CharField(db_column='pedido_venda_telefone_celular', max_length=11, null=True)

    valor_subtotal = models.DecimalField(db_column='pedido_venda_valor_subtotal', max_digits=16, decimal_places=4, null=True)
    valor_envio = models.DecimalField(db_column='pedido_venda_valor_envio', max_digits=16, decimal_places=4, null=True)
    valor_total = models.DecimalField(db_column='pedido_venda_valor_total', max_digits=16, decimal_places=4, null=True)
    valor_desconto = models.DecimalField(db_column='pedido_venda_valor_desconto', max_digits=16, decimal_places=4, null=True)
    peso_real = models.DecimalField(db_column='pedido_venda_peso_real', max_digits=16, decimal_places=3, null=True)

    data_criacao = models.DateTimeField(db_column='pedido_venda_data_criacao', auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column='pedido_venda_data_modificacao', auto_now=True)
    data_expiracao = models.DateTimeField(
        db_column='pedido_venda_data_expiracao', null=True, default=None)
    cliente_obs = models.TextField(
        db_column='pedido_venda_cliente_obs', null=True, default=None)

    # Relacionada a Nota Fiscal
    conteudo_json = JSONField(db_column="pedido_venda_conteudo_json", null=True)
    numero_nota_fiscal = models.BigIntegerField(
        db_column="pedido_venda_numero_nota_fiscal", null=True)

    _endereco_entrega = models.OneToOneField('pedido.PedidoVendaEndereco', db_column='pedido_venda_endereco_entrega_id', related_name='+', null=False)
    _endereco_pagamento = models.OneToOneField('pedido.PedidoVendaEndereco', db_column='pedido_venda_endereco_pagamento_id', related_name='+', null=False)

    tipo = models.ForeignKey('pedido.PedidoVendaTipo', db_column='pedido_venda_tipo_id', related_name='pedidos')
    situacao = models.ForeignKey('pedido.PedidoVendaSituacao', db_column='pedido_venda_situacao_id', related_name='pedidos')
    cliente = models.ForeignKey('cliente.Cliente', related_name='pedidos')
    conta = models.ForeignKey('plataforma.Conta', related_name='pedidos_vendas', on_delete=models.CASCADE)
    contrato = models.ForeignKey('plataforma.Contrato', related_name='pedidos_vendas')
    cupom = models.ForeignKey("marketing.CupomDesconto", db_column='cupom_desconto_id', related_name='pedidos', null=True)
    envios = models.ManyToManyField('configuracao.Envio', through='pedido.PedidoVendaFormaEnvio', related_name='pedidos')
    pagamentos = models.ManyToManyField('configuracao.FormaPagamento', through='pedido.PedidoVendaFormaPagamento', related_name='pedidos')

    # A referência e o serviço são usados para identificar que este pedido
    # foi criado por algum serviço externo e depois importado na Loja Integerada
    # ou que ele foi criado na Loja Integrada e depois exportado para outro local.
    referencia = models.TextField(db_column='pedido_venda_referencia', null=True, default=None)

    utm_campaign = models.CharField(max_length=255, db_column='pedido_venda_utm_campaign', null=True)

    # Integracao Anymarket
    id_anymarket = models.IntegerField(db_column="pedido_venda_id_anymarket", null=True, blank=True)

    # nota fiscal do pedido de venda
    nota_fiscal = models.ForeignKey('pedido.NotaFiscal',
                                    db_column='pedido_venda_nota_fiscal_id',
                                    null=True)


    class Meta:
        db_table = u"pedido\".\"tb_pedido_venda"
        verbose_name = u'Pedido Venda'
        verbose_name_plural = u'Pedidos de Venda'
        ordering = ['id']
        unique_together = (("conta", "numero"), )
        get_latest_by = 'id'

    def __unicode__(self):
        return unicode(self.id)

    def save(self, *args, **kwargs):
        if not self.numero and self.conta_id:
            self.numero = self.conta.proximo_numero_pedido()

        if not self.tipo_id:
            self.tipo = PedidoVendaTipo.objects.get(pk=1)

        if not self.situacao_id:
            self.situacao = PedidoVendaSituacao.objects.get(padrao=True)

        if self.cliente:
            self.telefone_principal = self.cliente.telefone_principal
            self.telefone_comercial = self.cliente.telefone_comercial
            self.telefone_celular = self.cliente.telefone_celular

        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id

        super(self.__class__, self).save(*args, **kwargs)

    def criar_endereco(self, tipo, endereco):
        """Cria um endereço para o pedido baseado em um endereço do cliente."""
        from repositories.cliente.models import ClienteEndereco

        # O tipo de endereço só pode ser pagamento ou entrega e o objeto deve
        # ser uma instância do endereço do cliente.
        assert tipo in ['entrega', 'pagamento']
        assert isinstance(endereco, ClienteEndereco)

        campos = ['tipo', 'cpf', 'rg', 'cnpj', 'razao_social', 'ie', 'nome',
                  'endereco', 'numero', 'complemento', 'referencia', 'bairro',
                  'cidade', 'estado', 'cep', 'pais']
        valores = {}
        for campo in campos:
            valores[campo] = getattr(endereco, campo)
            if campo in ['tipo', 'cpf', 'rg', 'cnpj', 'razao_social', 'ie']:
                if not getattr(endereco, campo):
                    valores[campo] = getattr(endereco.cliente.endereco, campo)

        try:
            novo_endereco = PedidoVendaEndereco.objects.filter(
                conta=self.conta, **valores)[0]
        except IndexError:
            novo_endereco = PedidoVendaEndereco(conta=self.conta)
            for campo, valor in valores.items():
                setattr(novo_endereco, campo, valor)
            novo_endereco.save()
        return novo_endereco

    @property
    def telefone(self):
        """Retorna o primeiro telefone que tiver sido preenchido, ou um dos que
        foi preenchido nesta ordem: telefone_celular, telefone_principal e
        telefone_comercial.
        """
        return self.telefone_celular or self.telefone_principal or self.telefone_comercial

    def situacao_classe(self):
        # TODO: MUDAR CLASSE
        """Retorna a classe (CSS) da situação"""
        if self.situacao_id == 4: #Pago
            return 'label-success'
        elif self.situacao_id == 9: #Efetuado
            return 'label-warning'
        elif self.situacao_id == 11: #Enviado
            return 'label-primary'
        elif self.situacao_id == 14: #Entregue
            return 'label-default'
        elif self.situacao_id == 8: #Cancelado
            return 'label-important'
        elif 'pagamento' in self.situacao.nome.lower():
            return 'label-color-2'
        elif len(re.findall(r'\w+', self.situacao.nome)) > 1:
            return 'label-color-1'
        else:
            return 'label-info'

    def logar(self, codigo, descricao, **kwargs):
        return None

    @property
    def pagamento(self):
        """Retorna a primeira relação de FormaPagamento do pedido."""
        if not hasattr(self, '_pagamento'):
            try:
                self._pagamento = self.pagamentos.all()[0]
            except IndexError:
                self._pagamento = None
        return self._pagamento

    def marcar_pagamento_externo(self):
        pagamento = self.pedido_venda_pagamento()
        pagamento.pagamento_externo = True
        pagamento.save()
        return pagamento

    def pedido_venda_pagamento(self):
        """Retorna a primeira relação de PedidoVendaFormaPagamento do pedido."""
        if not hasattr(self, '_pedido_venda_pagamento'):
            try:
                self._pedido_venda_pagamento = PedidoVendaFormaPagamento \
                    .objects.get(pedido=self, conta=self.conta)
            except PedidoVendaFormaPagamento.DoesNotExist:
                self._pedido_venda_pagamento = None
        return self._pedido_venda_pagamento

    @property
    def pedido_envio(self):
        """Retorna a primeira relação de PedidoVendaFormaEnvio do pedido."""
        if not hasattr(self, '_pedido_envio'):
            try:
                self._pedido_envio = self.pedido_envios.all()[0]
            except IndexError:
                self._pedido_envio = None
        return self._pedido_envio

    def envio(self):
        """Retorna a primeira relação de FormaEnvio do pedido."""
        if not hasattr(self, '_envio'):
            try:
                self._envio = self.envios.all()[0]
            except IndexError:
                self._envio = None
        return self._envio

    @property
    def prazo_entrega(self):
        prazo_envio = self.prazo_envio or 0
        entrega = 0
        if self.pedido_envio:
            entrega = self.pedido_envio.prazo or 0
        return prazo_envio + entrega

    @property
    def prazo_envio(self):
        """Retorna o maior prazo de envio de todos os itens do pedido."""
        return self.itens.aggregate(prazo=Max('disponibilidade')).get('prazo')

    @property
    def nao_iniciado(self):
        """Indica se o pagamento do pedido já foi iniciado."""
        return self.situacao.padrao

    @property
    def cancelado(self):
        """Indica se o pedido está cancelado."""
        return self.situacao.cancelado

    @property
    def finalizado(self):
        """Indica se o pedido está finalizado."""
        return self.situacao.cancelado

    def situacao_anterior(self):
        """Retorna a situação exatamente anterior a situação atual. Caso não
        tenha situação anterior, retorna None."""
        historico_situacoes = self.historico.all().order_by('-data')
        if historico_situacoes.count() > 1:
            return historico_situacoes[1]
        return None

    def calcular_porcentagem(self, valor_1, valor_2):
        """
        Calcula a porcentagem e retorna o valor.
        """
        valor = Decimal(valor_1) * Decimal(valor_2) / Decimal('100')
        return Decimal('%0.2f' % valor)

    @property
    def endereco_entrega_completo(self):
        return self.endereco_entrega.completo

    @property
    def endereco_pagamento_completo(self):
        return self.endereco_pagamento.completo

    def _set_endereco_entrega(self, endereco):
        """Ao definir um endereço de entrega é possível definir como um
        endereço do cliente ou como um endereço do pedido.
        """
        from repositories.cliente.models import ClienteEndereco

        if isinstance(endereco, PedidoVendaEndereco):
            self._endereco_entrega = endereco
        elif isinstance(endereco, ClienteEndereco):
            self._endereco_entrega = self.criar_endereco('entrega', endereco)
        else:
            raise TypeError(u'O endereço deve ser do tipo Endereco ou PedidoVendaEndereco. %s foi enviado.' % type(endereco))

    def _get_endereco_entrega(self):
        return self._endereco_entrega

    endereco_entrega = property(_get_endereco_entrega, _set_endereco_entrega)

    def _set_endereco_pagamento(self, endereco):
        """Ao definir um endereço de pagamento é possível definir como um
        endereço do cliente ou como um endereço do pedido.
        """
        from repositories.cliente.models import ClienteEndereco

        if isinstance(endereco, PedidoVendaEndereco):
            self._endereco_pagamento = endereco
        elif isinstance(endereco, ClienteEndereco):
            self._endereco_pagamento = self.criar_endereco('pagamento', endereco)
        else:
            raise TypeError(u'O endereço deve ser do tipo Endereco ou PedidoVendaEndereco. %s foi enviado.' % type(endereco))

    def _get_endereco_pagamento(self):
        return self._endereco_pagamento

    endereco_pagamento = property(_get_endereco_pagamento, _set_endereco_pagamento)

    def adicionar_item(self, produto, quantidade):
        """Cria um novo item no pedido de venda com o produto e a
        quantidade informada.
        """
        return PedidoVendaItem.objects.create(produto=produto, produto_pai=produto.pai,
                                              quantidade=quantidade, pedido=self, conta=self.conta)

    def adicionar_envio(self, envio, frete_escolhido=None, objeto=None):
        """Adiciona uma nova forma de envio para o pedido."""
        return PedidoVendaFormaEnvio.objects.create(
            valor=frete_escolhido.get('valor'), objeto=objeto,
            envio=envio, pedido=self, conta=self.conta,
            mensagem_correios=frete_escolhido.get('msg_erro'),
            prazo=frete_escolhido.get('prazo'))

    def remover_envios(self):
        """Remove todos os envios para este pedido."""
        return PedidoVendaFormaEnvio.objects.filter(pedido=self, conta=self.conta).delete()

    def adicionar_pagamento(self, pagamento, valor=None, valor_pago=None,
                            transacao_id=None, identificador_id=None,
                            conteudo=None, banco_id=None, json=None):
        """Adiciona uma nova forma de pagamento para o pedido."""
        return PedidoVendaFormaPagamento.objects.create(valor=valor,
                                                        valor_pago=valor_pago, transacao_id=transacao_id,
                                                        identificador_id=identificador_id, conteudo=conteudo,
                                                        banco_id=banco_id, pagamento=pagamento, pedido=self,
                                                        conta=self.conta, conteudo_json=json)

    def remover_pagamentos(self):
        """Remove todos os pagamentos para este pedido."""
        return PedidoVendaFormaPagamento.objects.filter(pedido=self, conta=self.conta).delete()


class NotaFiscal(models.Model):
    """A nota fiscal de uma venda efetuada na loja."""

    id = custom_models.BigAutoField(db_column="nota_fiscal_id",
                                    primary_key=True)
    # url para visualização da nota
    url = models.URLField(db_column='nota_fiscal_url', null=True)
    # numero da nota fiscal
    numero = models.IntegerField(db_column='nota_fiscal_numero')
    # data da geração da nota fiscal
    data = models.DateTimeField(db_column='nota_fiscal_data')
    # access key da nota enviada pelo parceiro gerador da nota
    access_key = models.CharField(max_length=128, db_column='nota_fiscal_access_key')
    # série da nf
    serie = models.IntegerField(db_column='nota_fiscal_serie')
    # indica se a nota já foi enviada para o anymarket
    enviada = models.BooleanField(db_column='nota_fiscal_enviada',
                                  default=False)

    class Meta:
        db_table = u"pedido\".\"tb_nota_fiscal"
        verbose_name = u'Nota fiscal de uma venda'
        verbose_name_plural = u"Notas fiscais de pedidos de venda."
        ordering = ['id']


class PedidoVendaItem(models.Model):
    """Itens de um pedido de venda.

    Para criar um novo item de venda é preciso enviar produto, produto_pai,
    quantidade, pedido e conta. A partir dos dados do produto os outros campos
    serão preenchidos.
    """
    id = custom_models.BigAutoField(db_column="pedido_venda_item_id", primary_key=True)
    linha = models.IntegerField(db_column="pedido_venda_item_linha")

    quantidade = models.DecimalField(db_column="pedido_venda_item_quantidade", max_digits=16, decimal_places=3)
    preco_cheio = models.DecimalField(db_column="pedido_venda_item_preco_cheio", max_digits=16, decimal_places=4)
    preco_custo = models.DecimalField(db_column="pedido_venda_item_preco_custo", max_digits=16, decimal_places=4, null=True)
    preco_promocional = models.DecimalField(db_column="pedido_venda_item_preco_promocional", max_digits=16, decimal_places=4, null=True)
    preco_venda = models.DecimalField(db_column="pedido_venda_item_preco_venda", max_digits=16, decimal_places=4)
    preco_subtotal = models.DecimalField(db_column="pedido_venda_item_preco_subtotal", max_digits=16, decimal_places=4)

    tipo = models.CharField(db_column="pedido_venda_item_produto_tipo", max_length=255, null=True)
    sku = models.CharField(db_column="pedido_venda_item_sku", max_length=255)
    nome = models.CharField(db_column="pedido_venda_item_nome", max_length=255)

    # Variação é um campo que armazena um json com os dados de um dicionário de
    # variações do produto, se o produto tem variação: Cor = Azul e Tamanho = P
    # o valor armazenado é: '{"Cor": "Azul", "Tamanho": "P"}'.
    _variacao = models.TextField(db_column="pedido_venda_item_variacao", null=True)
    peso = models.DecimalField(db_column="pedido_venda_item_peso", max_digits=16, decimal_places=3, default=None, null=True)
    altura = models.IntegerField(db_column="pedido_venda_item_altura", default=None, null=True)
    largura = models.IntegerField(db_column="pedido_venda_item_largura", default=None, null=True)
    profundidade = models.IntegerField(db_column="pedido_venda_item_comprimento", default=None, null=True)
    disponibilidade = models.IntegerField(db_column="pedido_venda_item_disponibilidade", null=True)

    pedido = models.ForeignKey('pedido.PedidoVenda', db_column='pedido_venda_id', related_name='itens', on_delete=models.CASCADE)
    pedido_forma_envio = models.ForeignKey('pedido.PedidoVendaFormaEnvio', db_column="pedido_venda_envio_id", related_name='pedido_venda_itens', null=True)
    produto = models.ForeignKey("catalogo.Produto", related_name='pedido_venda_itens', on_delete=models.PROTECT)
    produto_pai = models.ForeignKey("catalogo.Produto", db_column='produto_id_pai', related_name='filhos_pedido_venda_itens', null=True, on_delete=models.PROTECT)
    conta = models.ForeignKey('plataforma.Conta', related_name='pedido_venda_itens')
    contrato = models.ForeignKey('plataforma.Contrato', related_name='pedido_venda_itens')

    class Meta:
        db_table = u"pedido\".\"tb_pedido_venda_item"
        verbose_name = u'Itens de um pedido de venda'
        verbose_name_plural = u"Itens dos pedidos de vendas"
        ordering = ['id']

    def __unicode__(self):
        return unicode(self.id)

    def save(self, *args, **kwargs):
        if not self.linha:
            linha = self.pedido.itens.aggregate(linha=Max('linha')).get('linha') or 0
            self.linha = linha + 1

        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id

        super(PedidoVendaItem, self).save(*args, **kwargs)

    @property
    def produto_tipo(self):
        return self.tipo

    def _get_variacao(self):
        """Retornar o valor de variação. Normalmente é um dicionário."""
        try:
            return json.loads(self._variacao)
        except TypeError:
            return self._variacao

    def _set_variacao(self, value):
        """Transforma o valor em um JSON. Envie um dicionário ou None."""
        self._variacao = json.dumps(value)

    variacao = property(_get_variacao, _set_variacao)

    def _popular_de_produto(self, produto):
        """"Através do produto, popula todos os dados necessário para o item
        do pedido de venda ser 'autônomo'.
        """
        self.preco_custo = produto.preco.custo
        self.preco_cheio = produto.preco.cheio
        self.preco_promocional = produto.preco.promocional
        self.preco_venda = min([x for x in [produto.preco.cheio, produto.preco.promocional] if x])
        self.preco_subtotal = self.preco_venda * self.quantidade

        self.tipo = produto.tipo
        self.sku = produto.sku
        self.peso = produto.peso
        self.altura = produto.altura
        self.largura = produto.largura
        self.profundidade = produto.profundidade
        self.disponibilidade = produto.estoque.disponibilidade()

        if produto.pai:
            self.nome = produto.pai.nome
            variacao = {}
            for pro_gra_var in produto.produto_grades_variacoes.all():
                variacao[pro_gra_var.grade.nome] = pro_gra_var.variacao.nome
            self.variacao = variacao or None
        else:
            self.nome = produto.nome

    def reduzir_estoque(self, motivo=None):
        return self.produto.estoque.reduzir(pedido_venda=self, motivo=motivo)

    def imagem(self):
        """
        Imagem do produto caso o produto tenha ou não imagem associada a grade
        """
        TIPO_OPCAO = 'atributo_opcao' # Produto.TIPO_OPCAO
        produto = self.produto

        if produto.tipo == TIPO_OPCAO:
            imagem = produto.imagem()

            if not imagem:
                pai = produto.pai if produto.pai else produto
                variacoes = produto.produto_grades_variacoes.all().values_list('variacao', flat=True)
                imagens = pai.produto_grades_imagens.filter(variacao_id__in=variacoes)

                if imagens:
                    imagem = imagens[0].imagem

            return imagem


class PedidoVendaItemReserva(models.Model):
    """Itens reservados por pedidos feitos na loja."""
    id = custom_models.BigAutoField(db_column="pedido_venda_item_reserva_id", primary_key=True)
    quantidade = models.IntegerField(db_column="pedido_venda_item_reserva_quantidade", null=False)

    pedido = models.ForeignKey('pedido.PedidoVenda', db_column='pedido_venda_id', related_name='reservas', on_delete=models.CASCADE)
    pedido_item = models.ForeignKey('pedido.PedidoVendaItem', db_column='pedido_venda_item_id', related_name='reservas', on_delete=models.CASCADE)
    produto = models.ForeignKey("catalogo.Produto", db_column='produto_id', related_name='reservas', on_delete=models.PROTECT)
    produto_pai = models.ForeignKey("catalogo.Produto", db_column='produto_id_pai', related_name='filhos_reservas', null=True, on_delete=models.PROTECT)
    conta = models.ForeignKey('plataforma.Conta', db_column='conta_id', related_name='pedido_venda_itens_reservas')
    contrato = models.ForeignKey('plataforma.Contrato', db_column='contrato_id', related_name='pedido_venda_itens_reservas')

    class Meta:
        db_table = u"pedido\".\"tb_pedido_venda_item_reserva"
        verbose_name = u'Item reservado para o pedido'
        verbose_name_plural = u"Itens reservados para o pedido"
        ordering = ['id']

    def __unicode__(self):
        return unicode(self.id)

    def save(self, *args, **kwargs):
        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id
        super(PedidoVendaItemReserva, self).save(*args, **kwargs)


class PedidoVendaFormaEnvio(models.Model):
    """Forma de envio de um pedido de venda."""
    id = custom_models.BigAutoField(db_column="pedido_venda_envio_id", primary_key=True)
    objeto = models.CharField(db_column="pedido_venda_envio_objeto", max_length=32, null=True, blank=True)
    valor = models.DecimalField(db_column="pedido_venda_envio_valor", max_digits=16, decimal_places=2, null=True)
    data_criacao = models.DateTimeField(db_column="pedido_venda_envio_data_criacao", auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column="pedido_venda_envio_data_modificacao", auto_now=True)
    mensagem_correios = models.TextField(db_column="pedido_venda_envio_mensagem_correios", null=True, default=None)
    prazo = models.IntegerField(db_column='pedido_venda_envio_prazo', null=True, default=None)

    pedido = models.ForeignKey('pedido.PedidoVenda', db_column='pedido_venda_id', related_name='pedido_envios')
    envio = models.ForeignKey('configuracao.Envio', related_name='pedidos_envio')
    conta = models.ForeignKey('plataforma.Conta', related_name='pedido_venda_envios')
    contrato = models.ForeignKey('plataforma.Contrato', related_name='pedido_venda_envios')

    class Meta:
        db_table = u"pedido\".\"tb_pedido_venda_envio"
        verbose_name = u'Forma de envio de um pedido de venda'
        verbose_name_plural = u"Formas de envios dos pedidos de vendas"
        ordering = ['id']

    def __unicode__(self):
        return unicode(self.id)

    def save(self, *args, **kwargs):
        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id
        super(PedidoVendaFormaEnvio, self).save(*args, **kwargs)


class PedidoVendaFormaPagamento(models.Model):
    """Forma de pagamento de um pedido de venda."""
    id = custom_models.BigAutoField(db_column="pedido_venda_pagamento_id", primary_key=True)
    valor = models.DecimalField(db_column="pedido_venda_pagamento_valor", max_digits=16, decimal_places=2, null=True)
    valor_pago = models.DecimalField(db_column="pedido_venda_pagamento_valor_pago", max_digits=16, decimal_places=2, null=True)
    transacao_id = models.CharField(db_column="pedido_venda_pagamento_transacao_id", max_length=64, null=True)
    identificador_id = models.CharField(db_column="pedido_venda_pagamento_identificador_id", max_length=64, null=True)
    conteudo = models.TextField(db_column="pedido_venda_pagamento_conteudo", null=True)
    conteudo_json = JSONField(db_column="pedido_venda_pagamento_conteudo_json", null=True)
    data_criacao = models.DateTimeField(db_column="pedido_venda_pagamento_data_criacao", auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column="pedido_venda_pagamento_data_modificacao", auto_now=True)
    pagamento_externo = models.BooleanField(db_column="pedido_venda_pagamento_pagamento_externo", null=False, default=False)

    banco = models.ForeignKey('configuracao.Banco', db_column='banco_id', related_name='banco', null=True, default=None)
    pagamento_banco = models.ForeignKey('configuracao.PagamentoBanco', db_column='pagamento_banco_id', related_name='pedidos_banco', null=True, default=None)
    pedido = models.ForeignKey('pedido.PedidoVenda', db_column='pedido_venda_id', related_name='pedido_pagamentos')
    pagamento = models.ForeignKey('configuracao.FormaPagamento', related_name='pedidos_pagamento')
    conta = models.ForeignKey('plataforma.Conta', related_name='pedido_venda_pagamentos')
    contrato = models.ForeignKey('plataforma.Contrato', related_name='pedido_venda_pagamentos')

    class Meta:
        db_table = u"pedido\".\"tb_pedido_venda_pagamento"
        verbose_name = u'Forma de pagamento de um pedido de venda'
        verbose_name_plural = u"Formas de pagamentos dos pedidos de vendas"
        ordering = ['id']
        unique_together = (("transacao_id", "identificador_id"), )

    def __unicode__(self):
        return unicode(self.id)

    def save(self, *args, **kwargs):
        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id
        super(PedidoVendaFormaPagamento, self).save(*args, **kwargs)

    @property
    def transacao(self):
        if self.transacao_id:
            return self.transacao_id
        if self.identificador_id:
            return self.identificador_id
        return None

class PedidoVendaSituacaoHistorico(models.Model):
    """Histórico de situações de um pedido de venda.

    O alterado_por pode receber três valores básicos:
        cliente - Quando foi o cliente que alterou.
        gateway - Quando a alteração foi feita pelo gateway de pagamento.
        usuario - Sempre que o usuário alterar a situação.
        sistema - Quando não é possível identificar quem fez a alteração.
    """
    ALTERADO_POR_CLIENTE = 'cliente'
    ALTERADO_POR_GATEWAY = 'gateway'
    ALTERADO_POR_USUARIO = 'usuario'
    ALTERADO_POR_SISTEMA = 'sistema'

    CHOICES_ALTERADO_POR = [
        (ALTERADO_POR_CLIENTE, u'Cliente'),
        (ALTERADO_POR_GATEWAY, u'Gateway'),
        (ALTERADO_POR_USUARIO, u'Usuário'),
        (ALTERADO_POR_SISTEMA, u'Sistema'),
    ]

    id = custom_models.BigAutoField(db_column="pedido_venda_situacao_historico_id", primary_key=True)
    data = models.DateTimeField(db_column="pedido_venda_situacao_historico_data", auto_now=True)
    alterado_por = models.CharField(db_column="pedido_venda_situacao_historico_alterado_por", max_length=64, null=True, choices=CHOICES_ALTERADO_POR)
    alterado_por_nome = models.CharField(db_column="pedido_venda_situacao_historico_alterado_por_nome", max_length=128, null=True)
    obs = models.TextField(db_column='pedido_venda_situacao_historico_obs', null=True, default=None)

    situacao_inicial = models.ForeignKey('pedido.PedidoVendaSituacao', db_column="pedido_venda_situacao_id_inicial", related_name='pedido_venda_situacao_inicial_historico')
    situacao_final = models.ForeignKey('pedido.PedidoVendaSituacao', db_column="pedido_venda_situacao_id_final", related_name='pedido_venda_situacao_final_historico')
    pedido = models.ForeignKey('pedido.PedidoVenda', db_column='pedido_venda_id', related_name='historico', on_delete=models.CASCADE)
    conta = models.ForeignKey('plataforma.Conta', related_name='pedido_venda_situacao_historico')
    contrato = models.ForeignKey('plataforma.Contrato', related_name='pedido_venda_situacao_historico')

    class Meta:
        db_table = u"pedido\".\"tb_pedido_venda_situacao_historico"
        verbose_name = u'Histórico de situações de um pedido de venda'
        verbose_name_plural = u"Histórico de situações dos pedidos de vendas"
        ordering = ['id']

    def __unicode__(self):
        return unicode(self.id)

    def save(self, *args, **kwargs):
        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id
        super(PedidoVendaSituacaoHistorico, self).save(*args, **kwargs)


class Carrinho(models.Model):
    id = custom_models.BigAutoField(db_column="carrinho_id", primary_key=True)

    token = models.CharField(db_column="carrinho_token", null=False, max_length=64)
    data_criacao = models.DateTimeField(db_column="carrinho_data_criacao", auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column="carrinho_data_modificacao", auto_now=True)

    cliente = models.ForeignKey('cliente.Cliente', db_column="cliente_id", null=True, related_name="carrinhos")
    conta = models.ForeignKey('plataforma.Conta', db_column="conta_id", related_name="carrinhos")
    contrato = models.ForeignKey('plataforma.Contrato', related_name="carrinhos")

    class Meta:
        db_table = u"pedido\".\"tb_carrinho"
        verbose_name = u"Carrinho"
        verbose_name_plural = u"Carrinhos"
        unique_together = ("token", "conta", "contrato")

    def save(self, *args, **kwargs):
        if not self.token:
            import string
            texto = ''.join(random.sample(string.letters + string.digits, 10))
            agora = datetime.datetime.now()

            salt = '%s.:.%s.:.%s' % (texto, self.conta_id, agora)
            self.token = hashlib.md5(salt).hexdigest()

        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id

        super(Carrinho, self).save(*args, **kwargs)


class CarrinhoProduto(models.Model):
    id = custom_models.BigAutoField(db_column="carrinho_produto_id", primary_key=True)

    produto = models.ForeignKey('catalogo.Produto', db_column="produto_id", related_name="carrinhos_produto")
    quantidade = models.IntegerField(db_column="carrinho_produto_quantidade", default=1)
    carrinho = models.ForeignKey('pedido.Carrinho', db_column="carrinho_id", related_name="carrinho_produtos")

    conta = models.ForeignKey('plataforma.Conta', db_column="conta_id", related_name="carrinho_produtos")
    contrato = models.ForeignKey('plataforma.Contrato', related_name="carrinho_produtos")

    class Meta:
        db_table = u"pedido\".\"tb_carrinho_produto"
        verbose_name = u"Produto no carrinho"
        verbose_name_plural = u"Produtos no carrinho"
        unique_together = ("produto", "carrinho", "conta")

    def save(self, *args, **kwargs):
        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id
        super(CarrinhoProduto, self).save(*args, **kwargs)


@receiver(pre_save, sender=PedidoVendaItem)
def pedido_venda_item_pre_save(sender, instance, raw, *args, **kwargs):
    if not instance.id and instance.produto:
        instance._popular_de_produto(instance.produto)


@receiver(pre_save, sender=PedidoVenda)
def pedido_venda_pre_save(sender, instance, raw, *args, **kwargs):
    if (instance.situacao_id in
            PedidoVenda.SITUACOES_AGUARDANDO_PAGAMENTO):
        dias_delta = PedidoVenda.MAXIMO_DIAS_PEDIDO
        instance.data_expiracao = (datetime.datetime.now() +
                                   datetime.timedelta(days=dias_delta))
    else:
        instance.data_expiracao = None
