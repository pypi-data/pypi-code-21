# -*- coding: utf-8 -*-

from django.db import models
from repositories import custom_models
from repositories.libs import utils


class Logradouro(models.Model):

    nome_local = models.CharField(db_column='nome_local', max_length=128, primary_key=True)
    uf = models.CharField(db_column="uf_log", max_length=2, null=True)
    cep_log = models.IntegerField(db_column="cep8_log", null=True)
    cep_ini = models.IntegerField(db_column="cep8_ini", null=True)
    cep_fim = models.IntegerField(db_column="cep8_fim", null=True)
    tipo = models.CharField(db_column="tipo_log", max_length=256, null=True)
    logradouro = models.CharField(db_column="logradouro", max_length=256, null=True)
    bairro = models.CharField(db_column="bairro", max_length=256, null=True)
    complemento = models.CharField(db_column="complemento", max_length=256, null=True)

    class Meta:
        db_table = u'tb_logradouro'


class Imagem(models.Model):
    """Imagens."""
    TIPO_LOGO = 'logo'
    TIPO_PRODUTO = 'produto'
    TIPO_BANNER = 'banner'
    TIPO_MARCA = 'marca'
    TIPO_UPLOAD = 'upload'
    TIPOS = [
        (TIPO_LOGO, u'Logo'),
        (TIPO_PRODUTO, u'Produto'),
        (TIPO_BANNER, u'Banner'),
        (TIPO_MARCA, u'Marca'),
        (TIPO_UPLOAD, u'Upload')
    ]

    id = custom_models.BigAutoField(db_column="imagem_id", primary_key=True)
    tabela = models.CharField(db_column="imagem_tabela", max_length=64, null=True)
    campo = models.CharField(db_column="imagem_campo", max_length=64, null=True)
    linha_id = models.IntegerField(db_column="imagem_linha_id", null=True)
    data_criacao = models.DateTimeField(db_column="imagem_data_criacao", auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column="imagem_data_modificacao", auto_now=True)

    nome = models.CharField(db_column="imagem_nome", max_length=255, null=True)
    alt = models.CharField(db_column="imagem_alt", max_length=512, null=True)
    title = models.CharField(db_column="imagem_title", max_length=512, null=True)
    mime = models.CharField(db_column="imagem_mime", max_length=256, null=True)

    caminho = models.CharField(db_column="imagem_caminho", max_length=255, null=True)

    tipo = models.CharField(db_column="imagem_tipo", max_length=32,
                            choices=TIPOS, default=u'produto')
    processada = models.BooleanField(db_column="imagem_processada", default=False)
    conta = models.ForeignKey("plataforma.Conta", related_name="imagens")
    contrato = models.ForeignKey("plataforma.Contrato", related_name="imagens")

    _produtos = models.ManyToManyField('catalogo.Produto', through='catalogo.ProdutoImagem', related_name='_produtos')

    class Meta:
        db_table = u"plataforma\".\"tb_imagem"
        verbose_name = u"Imagem"
        verbose_name_plural = u"Imagens"
        ordering = ["data_criacao"]

    def __unicode__(self):
        return self.caminho

    @property
    def original(self):
        return self.caminho

    def save(self, *args, **kwargs):
        # Para que o usuário não fique sem visualizar nada enquanto a imagem é
        # redimensionada, o caminho da imagem é definido como todos os outros
        # valores da imagem.

        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id

        # if self.conta.apelido == self.conta.CONTA_TESTE_APELIDO:
        #     self.tipo = 'imagem_teste'

        super(Imagem, self).save(*args, **kwargs)

    def delete_from_s3(self):
        """Remove esta imagem do S3."""
        if self.caminho:
            utils.delete_from_s3(self.caminho)

    def delete(self, *args, **kwargs):

        if not self.caminho.startswith('0/%s/' % self.conta.CONTA_TESTE_ID):
            self.delete_from_s3()
        super(Imagem, self).delete(*args, **kwargs)

    @property
    def imagem(self):
        """Retorna True caso o tipo de arquivo seja imagem."""
        if not self.mime:
            return True
        return self.mime.startswith('image')

    @property
    def extensao(self):
        return self.caminho.split('.')[-1]

    @property
    def filename(self):
        return self.caminho.split('/')[-1]

    def tamanhos(self):
        lista_tamanhos = ['icone', 'grande', 'media', 'pequena']
        saida = {}
        for tamanho in lista_tamanhos:
            saida[tamanho] = getattr(self, tamanho, None)
        return saida


class Moeda(models.Model):

    """Moedas."""
    id = models.CharField(db_column="moeda_id", max_length=3, primary_key=True)
    nome = models.CharField(db_column="moeda_nome", max_length=64)

    class Meta:
        db_table = u"tb_moeda"
        verbose_name = u"Moeda"
        verbose_name_plural = u"Moedas"
        ordering = ["nome"]

    def __unicode__(self):
        return self.nome


class Pais(models.Model):

    """Países."""
    id = models.CharField(db_column="pais_id", max_length=3, primary_key=True)
    nome = models.CharField(db_column="pais_nome", max_length=64)
    numero = models.CharField(db_column="pais_numero", max_length=3)
    codigo = models.CharField(db_column="pais_codigo", max_length=2, unique=True)

    class Meta:
        app_label = "domain"
        db_table = u"tb_pais"
        verbose_name = u"País"
        verbose_name_plural = u"Países"
        ordering = ["nome"]

    def __unicode__(self):
        return self.nome


class Estado(models.Model):

    """Estados."""
    id = custom_models.BigAutoField(db_column="estado_id", primary_key=True)
    uf_id = models.IntegerField(db_column="uf_id", unique=True)
    nome = models.CharField(db_column="estado_nome", max_length=100)
    uf = models.CharField(db_column="estado_uf", max_length=2)

    pais = models.ForeignKey('domain.Pais', related_name="estados")

    class Meta:
        db_table = u"tb_estado"
        verbose_name = u"Estado"
        verbose_name_plural = u"Estados"
        ordering = ["nome"]

    def __unicode__(self):
        return self.nome


class Cidade(models.Model):
    """Cidades."""
    id = custom_models.BigAutoField(db_column="cidade_id", primary_key=True)
    cidade = models.CharField(db_column="cidade", max_length=100)
    cidade_alt = models.CharField(db_column="cidade_alt", max_length=100)
    uf = models.CharField(db_column="uf", max_length=2)
    uf_munic = models.IntegerField(db_column="uf_munic")
    munic = models.IntegerField(db_column="munic")

    estado = models.ForeignKey('domain.Estado', db_column="uf_id", to_field="uf_id",
                               related_name="cidades")

    class Meta:
        db_table = u"tb_cidade"
        verbose_name = u"Cidade"
        verbose_name_plural = u"Cidades"
        ordering = ["cidade"]

    def __unicode__(self):
        return self.nome

    def get_object(self):
        dict = self.__dict__
        dict.pop("_django_version", None)
        dict.pop("_state", None)
        return dict


class Idioma(models.Model):

    """Idiomas."""
    id = models.CharField(db_column="idioma_id", max_length=5, primary_key=True)
    nome = models.CharField(db_column="idioma_nome", max_length=64)

    pais = models.ForeignKey('domain.Pais', related_name="idiomas", default=None, null=True)

    class Meta:
        db_table = u"tb_idioma"
        verbose_name = u"Idioma"
        verbose_name_plural = u"Idiomas"
        ordering = ["nome"]

    def __unicode__(self):
        return self.nome


class ApiAplicacao(models.Model):
    """Aplicação para conectar a API."""
    id = custom_models.BigAutoField(db_column="api_aplicacao_id", primary_key=True)
    chave = custom_models.UUIDField(db_column="api_aplicacao_chave", unique=True)
    nome = models.CharField(db_column="api_aplicacao_nome", max_length=255)
    data_criacao = models.DateTimeField(db_column="api_aplicacao_data_criacao", auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column="api_aplicacao_data_modificacao", auto_now=True, null=True)

    class Meta:
        db_table = u"plataforma\".\"tb_api_aplicacao"
        verbose_name = u"Aplicação da API"
        verbose_name_plural = u"Aplicações da API"
        ordering = ["nome"]

    def __unicode__(self):
        return self.nome
