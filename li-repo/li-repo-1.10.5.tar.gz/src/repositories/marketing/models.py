# -*- coding: utf-8 -*-
import datetime
import hashlib
import json
import time
import logging
from decimal import Decimal
from jsonfield import JSONField

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.text import slugify

from repositories import custom_models
from repositories.libs import utils


logger = logging.getLogger(__name__)


class CupomDesconto(models.Model):
    """Cupom de desconto."""
    TIPO_VALOR_FIXO = 'fixo'
    TIPO_PORCENTAGEM = 'porcentagem'
    TIPO_FRETE_GRATIS = 'frete_gratis'

    CHOICES_CUPOM_TIPOS = [
        (TIPO_VALOR_FIXO, u'Valor fixo'),
        (TIPO_PORCENTAGEM, u'Porcentagem'),
        (TIPO_FRETE_GRATIS, u'Frete grátis'),
    ]

    id = custom_models.BigAutoField(db_column="cupom_desconto_id", primary_key=True)
    descricao = models.TextField(db_column="cupom_desconto_descricao")
    codigo = models.CharField(db_column="cupom_desconto_codigo", max_length=32)
    valor = models.DecimalField(db_column='cupom_desconto_valor', max_digits=16, decimal_places=2, null=True)
    tipo = models.CharField(db_column="cupom_desconto_tipo", max_length=32, choices=CHOICES_CUPOM_TIPOS)
    cumulativo = models.BooleanField(db_column="cupom_desconto_acumulativo", default=False)
    quantidade = models.IntegerField(db_column="cupom_desconto_quantidade")
    quantidade_por_cliente = models.IntegerField(db_column="cupom_desconto_quantidade_por_usuario", null=True, blank=True)
    quantidade_usada = models.IntegerField(db_column="cupom_desconto_quantidade_utilizada", default=0)
    validade = models.DateTimeField(db_column="cupom_desconto_validade", null=True, blank=True)
    valor_minimo = models.DecimalField(db_column='cupom_desconto_valor_minimo', max_digits=16, decimal_places=2, null=True, blank=True)
    data_criacao = models.DateTimeField(db_column="cupom_desconto_data_criacao", auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column="cupom_desconto_data_modificacao", auto_now=True)
    ativo = models.BooleanField(db_column="cupom_desconto_ativo", default=False)
    aplicar_no_total = models.BooleanField(db_column='cupom_desconto_aplicar_no_total', default=False, null=False)

    conta = models.ForeignKey('plataforma.Conta', related_name='cupons')
    contrato = models.ForeignKey('plataforma.Contrato', related_name='cupons')

    class Meta:
        db_table = u"marketing\".\"tb_cupom_desconto"
        verbose_name = u'Cupom de desconto'
        verbose_name_plural = u"Cupons de desconto"
        ordering = ['codigo']
        unique_together = (("conta", "codigo"),)

    def __unicode__(self):
        return self.codigo

    def save(self, *args, **kwargs):
        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id
        if self.codigo:
            self.codigo = self.codigo.upper()
        return super(CupomDesconto, self).save(*args, **kwargs)

    def clean(self, *args, **kwargs):
        if not utils.validar_tipo_desconto(self.tipo, self.valor):
            raise ValidationError(u'O valor do desconto não pode ser maior que 100%.')
        super(CupomDesconto, self).clean(*args, **kwargs)

    def logar(self, codigo, descricao, **kwargs):
        return None
        # descricao = u'%s (cupom_desconto_id=%s)' % (descricao, self.id)
        # return NoSQLLog(codigo=codigo, conta_id=self.conta_id,
        #                 descricao=descricao, **kwargs).save()

    def verificar_validade(self, cliente, valor_subtotal=None, exclude=None):
        """Retorna True se o cupom pode ser usado, False caso contrário.
        aceita o exclude para não usar o pedido recem criado na query"""
        hoje = datetime.datetime.now()
        if (self.validade and self.validade < hoje) or self.quantidade <= 0:
            return False
        if self.quantidade_por_cliente and cliente:
            if exclude:
                usados = cliente.pedidos.filter(cupom=self).exclude(pk=exclude.id).count()
            else:
                usados = cliente.pedidos.filter(cupom=self).count()
            if self.quantidade_por_cliente <= usados:
                return False
        if self.valor_minimo and valor_subtotal and self.valor_minimo > valor_subtotal:
            return False
        return True

    def calcular_porcentagem(self, valor_1, valor_2):
        """
        Calcula a porcentagem e retorna o valor.
        """
        return valor_1 * Decimal('%0.2f' % valor_2) / Decimal('100')

    def calcular_desconto(self, valor_subtotal, valor_frete=None):
        """Calcula o valor de desconto que será aplicado. Caso o valor seja
        maior que o valor subtotal, ele é limitado para o valor do subtotal.
        """
        if not isinstance(valor_subtotal, Decimal):
            raise ValueError(u'O valor_subtotal é %s, deveria ser um Decimal.' \
                             % type(valor_subtotal))

        if valor_frete and not isinstance(valor_frete, Decimal):
            raise ValueError(u'O valor_frete é %s, deveria ser um Decimal.' \
                             % type(valor_frete))

        if self.tipo == self.TIPO_FRETE_GRATIS and valor_frete is None:
            raise ValueError(
                u'O valor_frete deve ser enviado sempre que o tipo de frete ' \
                u'é %s %s.' % (self.TIPO_FRETE_GRATIS, type(valor_frete)))
        if self.aplicar_no_total and valor_frete and self.tipo == self.TIPO_PORCENTAGEM:
            return self.calcular_porcentagem(valor_subtotal + valor_frete, self.valor)

        if self.tipo == self.TIPO_PORCENTAGEM:
            desconto = (valor_subtotal / Decimal('100.0')) * self.valor
        elif self.tipo == self.TIPO_VALOR_FIXO:
            desconto = self.valor
        elif self.tipo == self.TIPO_FRETE_GRATIS:
            desconto = valor_frete

        return desconto


class SEO(models.Model):
    """S.E.O."""
    id = custom_models.BigAutoField(db_column="seo_id", primary_key=True)
    tabela = models.CharField(db_column="seo_tabela", max_length=64)
    linha_id = models.IntegerField(db_column="seo_linha_id")
    data_criacao = models.DateTimeField(db_column="seo_data_criacao", auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column="seo_data_modificacao", auto_now=True)
    title = models.CharField(db_column="seo_title", max_length=255, null=True, blank=True)
    keyword = models.CharField(db_column="seo_keyword", max_length=255, null=True, blank=True)
    description = models.CharField(db_column="seo_description", max_length=255, null=True, blank=True)
    robots = models.CharField(db_column="seo_robots", max_length=32, null=True)

    idioma = models.ForeignKey('domain.Idioma', related_name="seos", default='pt-br')
    conta = models.ForeignKey("plataforma.Conta", related_name="seos")
    contrato = models.ForeignKey("plataforma.Contrato", related_name="seos")

    class Meta:
        db_table = u"marketing\".\"tb_seo"
        verbose_name = u"S.E.O."
        verbose_name_plural = u"S.E.O."
        ordering = ["data_criacao"]

    def __unicode__(self):
        return str(self.id)

    def save(self, *args, **kwargs):

        if self.conta_id and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id
        elif not self.conta_id and not self.contrato_id:
            self.contrato_id = 1
        super(SEO, self).save(*args, **kwargs)


class NewsletterAssinatura(models.Model):
    """Assinatura de newsletter."""
    id = custom_models.BigAutoField(db_column="newsletter_assinatura_id", primary_key=True)
    email = models.CharField(db_column="newsletter_assinatura_email", max_length=256)
    nome = models.CharField(db_column="newsletter_assinatura_nome", max_length=256, null=True)
    ativo = models.BooleanField(db_column="newsletter_assinatura_ativo", default=True)

    conta = models.ForeignKey("plataforma.Conta", related_name="newsletter_assinaturas")
    contrato = models.ForeignKey("plataforma.Contrato", related_name="newsletter_assinaturas")
    cliente = models.OneToOneField("cliente.Cliente", related_name="newsletter_assinatura", default=None)

    class Meta:
        db_table = u"marketing\".\"tb_newsletter_assinatura"
        verbose_name = u"Assinatura de newsletter"
        verbose_name_plural = u"Assinaturas de newsletter"
        ordering = ["email"]
        unique_together = (("email", "conta"),)

    def __unicode__(self):
        return self.email

    def save(self, *args, **kwargs):
        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id
        super(NewsletterAssinatura, self).save(*args, **kwargs)

    @property
    def primeiro_nome(self):
        if self.nome:
            return self.nome.split()[0]


class XML(models.Model):
    """XML do marketing."""

    XMLS_URLS = {
        'buscape': 'http://negocios.buscapecompany.com.br/',
        'googlemerchant': 'http://www.google.com.br/merchants',
        'kuantokusta': 'http://www.kuantokusta.com.br/areareservada/registo.php',
        'muccashop':'http://www.muccashop.com.br/anuncie/',
        'hookit': 'http://hookit.cc/',
        'shoppinguol': 'http://central.shopping.uol.com.br/'
    }

    id = custom_models.BigAutoField(db_column="xml_id", primary_key=True)
    nome = models.CharField(db_column="xml_nome", max_length=128)
    codigo = models.CharField(db_column="xml_codigo", max_length=128, unique=True)
    ativo = models.BooleanField(db_column="xml_ativo", default=False)
    contrato = models.ForeignKey("plataforma.Contrato", related_name='xmls', null=True, default=None)
    url_cadastro = models.URLField(db_column='xml_url_cadastro', null=True)
    chamada = models.TextField(db_column='xml_chamada', null=True)

    conteudo_json = JSONField(db_column="xml_conteudo_json", null=True)
    oculto = models.BooleanField(db_column="xml_oculto", default=False)

    class Meta:
        db_table = u"marketing\".\"tb_xml"
        verbose_name = u"XML"
        verbose_name_plural = u"XMLs"
        ordering = ["nome"]

    def __unicode__(self):
        return self.nome

    @classmethod
    def ativos(cls):
        return cls.objects.filter(ativo=True)


class XmlConfiguracaoManager(models.Manager):
    def ativos(self, conta_id):
        xmls_ativos = XML.objects.filter(ativo=True, oculto=False)
        for xml in xmls_ativos:
            try:
                xml.configuracao = XmlConfiguracao.objects.get(conta_id=conta_id, xml=xml)
            except XmlConfiguracao.DoesNotExist:
                xml.configuracao = None
        return xmls_ativos


class XmlConfiguracao(models.Model):
    """Configuração do XML."""
    id = custom_models.BigAutoField(db_column="xml_configuracao_id", primary_key=True)
    ativo = models.BooleanField(db_column="xml_configuracao_ativo", default=False)
    url = models.CharField(db_column="xml_configuracao_url", max_length=128)
    todos_os_produtos = models.BooleanField(db_column="xml_configuracao_todos_os_produtos", default=False)

    xml = models.ForeignKey('marketing.XML', related_name="configuracoes")
    produtos = models.ManyToManyField("catalogo.Produto", related_name="xmls_configuracoes", through='marketing.XmlProduto')
    conta = models.ForeignKey("plataforma.Conta", related_name="xmls_configuracoes")
    contrato = models.ForeignKey("plataforma.Contrato", related_name="xmls_configuracoes")

    conteudo_json = JSONField(db_column="xml_configuracao_conteudo_json", null=True)

    objects = XmlConfiguracaoManager()

    class Meta:
        db_table = u"marketing\".\"tb_xml_configuracao"
        verbose_name = u"Configuração do XML"
        verbose_name_plural = u"Configurações dos XMLs"
        unique_together = (("url", "conta"),)

    def __unicode__(self):
        return self.url

    def gerar_url(self):
        return (hashlib.md5('%s..:..%s' % (time.time(), self.conta.id)).hexdigest())[:5]

    def save(self, *args, **kwargs):
        if self.xml.codigo != 'bpmais':
            if not self.url and self.ativo:
                self.url = self.gerar_url()

        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id

        super(XmlConfiguracao, self).save(*args, **kwargs)

    def alterar_url(self):
        self.url = self.gerar_url()
        self.save()


class XmlProduto(models.Model):

    id = custom_models.BigAutoField(db_column="xml_produto_id", primary_key=True)

    configuracao = models.ForeignKey('marketing.XmlConfiguracao', db_column="xml_configuracao_id")
    produto = models.ForeignKey('catalogo.Produto', db_column="produto_id")

    class Meta:
        db_table = u'marketing\".\"tb_xml_produto'
        verbose_name = u'Produto XML'
        verbose_name_plural = u'Produtos XML'


class Banner(models.Model):
    """Banners da loja."""
    TIPOS_BANNER = [
        ('imagem', u'Imagem'),
        ('produto', u'Produto'),
        ('produto', u'Produto'),
    ]

    LOCAIS_PUBLICACAO_BANNER = [
        ('fullbanner', u'Full banner'),
        ('tarja', u'Banner tarja'),
        ('vitrine', u'Banner vitrine'),
        ('sidebar', u'Banner lateral do Full banner'),
        ('esquerda', u'Banner lateral'),
        ('minibanner', u'Mini banner'),
        # Por enquanto ainda não existe banner na direita.
        # ('direita', 'Banner lateral direita'),
    ]

    PAGINAS_PUBLICACAO_BANNER = (
        ('Gerais',
         (
             ('todas', u'Todas as páginas'),
             ('categoria', u'Todas as categorias'),
             ('marca', u'Todas as marcas'),
             ('produto', u'Todos os produtos'),
         )
         ),
        ('Somente na(s)',
         (
             ('pagina_inicial', u'Página inicial'),
             ('busca', u'Página de busca'),
             ('extra', u'Páginas extras'),
             ('somente_categoria', u'Categorias selecionadas'),
             ('somente_marca', u'Marcas selecionadas'),
         )
         )
    )

    ORDENACOES_BANNER = [
        ('aleatorio', u'Aleatório'),
        ('ordenado', u'Ordenado'),
    ]

    id = custom_models.BigAutoField(db_column="banner_id", primary_key=True)
    nome = models.CharField(db_column="banner_nome", max_length=128)
    titulo = models.CharField(db_column="banner_titulo", max_length=512, null=True, blank=True)
    codigo = models.CharField(db_column="banner_codigo", max_length=128)
    tipo = models.CharField(db_column="banner_tipo", max_length=32)
    ativo = models.CharField(db_column="banner_ativo", max_length=128)
    local_publicacao = models.CharField(db_column="banner_local_publicacao", max_length=32, choices=LOCAIS_PUBLICACAO_BANNER)
    pagina_publicacao = models.CharField(db_column="banner_pagina_publicacao", max_length=90)
    caminho = models.CharField(db_column="banner_caminho", max_length=128, null=True)
    link = models.CharField(db_column="banner_link", max_length=256, null=True, blank=True)
    ordenacao = models.CharField(db_column="banner_ordenacao", max_length=32, choices=ORDENACOES_BANNER, null=True)
    ordem = models.IntegerField(db_column="banner_ordem", null=True)
    limite = models.IntegerField(db_column="banner_limite", null=True)
    data_inicio = models.DateTimeField(db_column="banner_data_inicio", auto_now_add=True)
    data_fim = models.DateTimeField(db_column="banner_data_fim", auto_now=True)
    largura = models.IntegerField(db_column="banner_largura", default=None, null=True)
    altura = models.IntegerField(db_column="banner_altura", default=None, null=True)
    mapa_imagem = models.TextField(db_column="banner_mapa_imagem", default=None, null=True, blank=True)
    target = models.CharField(db_column="banner_target", max_length=32, null=True, default=None)

    conteudo_json = JSONField(db_column="banner_conteudo_json", null=True)

    conta = models.ForeignKey("plataforma.Conta", related_name="banners")
    contrato = models.ForeignKey("plataforma.Contrato", related_name="banners")

    class Meta:
        db_table = u"marketing\".\"tb_banner"
        verbose_name = u"Banner"
        verbose_name_plural = u"Banners"
        ordering = ["ordem"]
        unique_together = (("codigo", "conta"),)

    def __unicode__(self):
        return self.nome

    def save(self, *args, **kwargs):
        if self.tipo == 'imagem':
            self.ordenacao = None
            self.limite = None
        elif self.tipo == 'produto':
            self.caminho = None
            self.link = None
        if not self.codigo and self.nome:
            self.codigo = slugify(self.nome)

        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id

        super(self.__class__, self).save(*args, **kwargs)

    def logar(self, codigo, descricao, **kwargs):
        return None
        # descricao = u'%s (banner_id=%s)' % (descricao, self.id)
        # return NoSQLLog(codigo=codigo, conta_id=self.conta_id,
        #                 descricao=descricao, **kwargs).save()


class FreteGratis(models.Model):
    """O Frete Grátis é uma forma de máscara as formas de envio existentes.

    Sempre que um pedido tem a possibilidade de Frete Grátis, o menor valor
    de envio assume o papel de Frete Grátis. O Frete Grátis sempre é baseado
    em faixas de CEP.

    O campo faixas é um campo JSON que tem como conteúdo uma lista de
    listas de faixas, onde cada lista interna é um início e fim de uma faixa.
    Por exemplo: `[[59150000, 59880999], [1000000, 1999999]]`
    """
    id = custom_models.BigAutoField(db_column="frete_gratis_id", primary_key=True)
    nome = models.CharField(db_column="frete_gratis_nome", max_length=256, null=False)
    codigo = models.CharField(
        db_column="frete_gratis_codigo", max_length=256, null=False, db_index=True)
    ativo = models.BooleanField(db_column="frete_gratis_ativo", default=False, db_index=True)
    valor_minimo = models.DecimalField(
        db_column="frete_gratis_valor_minimo", max_digits=16, decimal_places=2,
        null=False, db_index=True)
    _faixas = models.TextField(db_column="frete_gratis_faixas", null=True, default=None)

    conta = models.ForeignKey("plataforma.Conta", related_name="fretes_gratis")
    contrato = models.ForeignKey("plataforma.Contrato", related_name="fretes_gratis")

    class Meta:
        db_table = u"marketing\".\"tb_frete_gratis"
        verbose_name = u"Frete grátis"
        verbose_name_plural = u"Fretes grátis"
        ordering = ["nome"]
        unique_together = (("codigo", "conta"),)

    def __unicode__(self):
        return self.nome

    def save(self, *args, **kwargs):
        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id
        super(FreteGratis, self).save(*args, **kwargs)

    def _set_faixas(self, faixas):
        try:
            self._faixas = json.dumps(faixas)
        except:
            self._faixas = None

    def _get_faixas(self):
        try:
            return json.loads(self._faixas)
        except:
            return self._faixas

    faixas = property(_get_faixas, _set_faixas)


class Tag(models.Model):

    LOCAL_PUBLICACAO = [
        ('cabecalho', u'Cabeçalho'),
        ('rodape', u'Rodapé'),
    ]

    id = custom_models.BigAutoField(db_column='tag_id', primary_key=True)
    nome = models.CharField(db_column='tag_nome', max_length=32)
    url_imagem = models.CharField(db_column="tag_url_imagem", max_length=255, null=True)
    url_cadastro = models.CharField(db_column="tag_url_cadastro", max_length=255, null=True)
    local_publicacao = models.CharField(db_column="tag_local_publicacao", max_length=255, choices=LOCAL_PUBLICACAO)
    campos = JSONField(db_column='tag_campos_json')
    descricao = models.TextField(db_column='tag_descricao', null=True)
    chamada = models.TextField(db_column='tag_chamada', null=True)
    em_producao = models.BooleanField(db_column="tag_em_producao", default=True)

    # Fun, fun fun!

    tag_global = models.TextField(db_column="tag_global", null=True, blank=True)
    index = models.TextField(db_column="tag_index", null=True, blank=True)
    catalogo = models.TextField(db_column="tag_catalogo", null=True, blank=True)
    produto = models.TextField(db_column="tag_produto", null=True, blank=True)
    carrinho = models.TextField(db_column="tag_carrinho", null=True, blank=True)
    pedido = models.TextField(db_column="tag_pedido", null=True, blank=True)
    pedido_pago = models.TextField(db_column="tag_pedido_pago", null=True, blank=True)

    data_criacao = models.DateTimeField(db_column="tag_data_criacao", auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column="tag_data_modificacao", auto_now=True)


    class Meta:
        db_table = u"marketing\".\"tb_tag"
        verbose_name = u"Tag"
        verbose_name_plural = u"Tags"


    def campos_json(self):
        return json.dumps(self.campos)

    def propriedades(self):
        if 'campos' not in self.campos:
            return {}
        campos = self.campos['campos']
        campos_json = {}
        for i, x in enumerate(campos):
            campos_json['{}'.format(x['field'])] = {'type': 'string', 'title': x['label'], 'format': x['input'], 'propertyOrder': i}
        return campos_json

    def placeholders(self):
        if 'campos' not in self.campos:
            return {}
        campos = self.campos['campos']
        return dict([(x['field'], x['placeholder']) for x in campos])


    @classmethod
    def listar_tags_pagina(cls, conta, pagina):
        SQL = """
        SELECT t.tag_local_publicacao as local_publicacao, t.tag_id as tag_id, t.tag_global, tc.tag_configuracao_dados, tag_%s as tag from marketing.tb_tag as t JOIN marketing.tb_tag_configuracao as tc ON (t.tag_id = tc.tag_id)
        WHERE conta_id=%s and (t.tag_%s IS NOT NULL OR t.tag_global IS NOT NULL) and (tc.tag_configuracao_dados IS NOT NULL);
        """ % (pagina, conta.id, pagina)
        tags = cls.objects.raw(SQL)
        return {
            'rodape': [x for x in tags if x.local_publicacao == 'rodape'],
            'cabecalho': [x for x in tags if x.local_publicacao == 'cabecalho'],
        }


class TagConfiguracao(models.Model):

    id = custom_models.BigAutoField(db_column='tag_configuracao_id', primary_key=True)
    dados = JSONField(db_column='tag_configuracao_dados', null=True)
    ativa = models.BooleanField(db_column='tag_configuracao_ativa', default=False)

    tag = models.ForeignKey(Tag, related_name='configuracoes')
    conta = models.ForeignKey("plataforma.Conta", related_name="tag_configuracoes")
    contrato = models.ForeignKey("plataforma.Contrato", related_name="tag_configuracoes")

    class Meta:
        db_table = u"marketing\".\"tb_tag_configuracao"
        verbose_name = u"Tag configuração"
        verbose_name_plural = u"Tags configurações"
        unique_together = ('tag', 'conta')

    def save(self, *args, **kwargs):
        if not self.contrato_id:
            self.contrato_id = self.conta.contrato_id
        super(TagConfiguracao, self).save(*args, **kwargs)


@receiver(post_save, sender=Banner)
def banner_post_save(sender, instance, created, raw, **kwargs):
    if created:
        # instance.logar('LPN19001', u'Banner criado.')
        pass
    else:
        # instance.logar('LPN19002', u'Banner editado.')
        pass


@receiver(post_delete, sender=Banner)
def banner_post_delete(sender, instance, **kwargs):
    # Removendo o banner anterior.
    if not instance.caminho.startswith('0/%s/' % instance.conta.CONTA_TESTE_ID):
        utils.delete_uploaded_file(instance.caminho)
        # Logando a remoção.
        # instance.logar('LPN19003', u'Banner removido.')
