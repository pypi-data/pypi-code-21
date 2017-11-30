# -*- coding: utf-8 -*-
import hashlib
import json
import random
import re
import logging
import string
import hmac
from datetime import timedelta, datetime
from jsonfield import JSONField
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.db import models, transaction, IntegrityError, connection
from django.db.models import Q, Max
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.urlresolvers import reverse

from repositories.libs import utils
from repositories.libs.utils import LOGRADOUROS
from repositories import custom_models

from repositories.libs import novo_template_definicoes

logger = logging.getLogger(__name__)

try:
    from django.apps import apps
    get_model = apps.get_model
except Exception:
    from django.db.models.loading import get_model

IMPORT_STATUS_RECEIVED = "received"
IMPORT_STATUS_PROCESSING = "processing"
IMPORT_STATUS_FAIL = "fail"
IMPORT_STATUS_PARTIAL = "partial"
IMPORT_STATUS_SUCCESS = "success"

IMPORT_STATUS = [
    (IMPORT_STATUS_RECEIVED, u"Arquivo recebido"),
    (IMPORT_STATUS_PROCESSING, u"Em processamento"),
    (IMPORT_STATUS_FAIL, u"Falha"),
    (IMPORT_STATUS_PARTIAL, u"Importado Parcialmente"),
    (IMPORT_STATUS_SUCCESS, u"Sucesso"),
]


LOG_IMPORT_CREATED = "created"
LOG_IMPORT_UPDATED = "updated"

LOG_IMPORT = [
    (LOG_IMPORT_CREATED, u"Produto criado"),
    (LOG_IMPORT_UPDATED, u"Produto atualizado"),
]


def hash(valor):
    try:
        valor = valor.encode('utf-8')
    except:
        pass
    return hashlib.md5(valor).hexdigest()


class UsuarioJaExiste(Exception):
    pass


class ContaJaExiste(Exception):
    pass


class Pagina(models.Model):
    """Página do CMS."""
    id = custom_models.BigAutoField(db_column="pagina_id", primary_key=True)
    url = models.CharField(db_column="pagina_url", max_length=500)
    titulo = models.CharField(db_column="pagina_titulo", max_length=500)
    conteudo = models.TextField(db_column="pagina_conteudo")
    posicao = models.IntegerField(db_column="pagina_posicao", null=True)
    ativo = models.BooleanField(db_column="pagina_ativo", default=False)
    data_criacao = models.DateTimeField(db_column="pagina_data_criacao", auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column="pagina_data_modificacao", auto_now=True)

    conta = models.ForeignKey("plataforma.Conta", related_name="paginas")
    contrato = models.ForeignKey("plataforma.Contrato", related_name="paginas")

    class Meta:
        db_table = u"plataforma\".\"tb_pagina"
        verbose_name = u"Página"
        verbose_name_plural = u"Páginas"
        ordering = ["posicao", "titulo"]
        unique_together = (("conta", "url"),)

    def __unicode__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id
        super(Pagina, self).save(*args, **kwargs)


class URL(models.Model):
    """URLs dos recursos do sistema.

    Define uma URL para um recurso da loja. Todas as URLs são únicas para a
    loja. Cada recurso deve ter pelo menos uma URL principal, caso não tenha,
    a URL mais nova é assumida como principal.
    """
    URL_REGEX = r'^[a-zA-Z0-9-_\.\/]+$'

    id = custom_models.BigAutoField(db_column="url_id", primary_key=True)
    data_criacao = models.DateTimeField(db_column="url_data_criacao", auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column="url_data_modificacao", auto_now=True)
    url = models.CharField(db_column="url_canonical_url", max_length=1024, null=False)
    principal = models.BooleanField(db_column="url_principal", default=True)

    produto = models.ForeignKey("catalogo.Produto", related_name="urls", null=True, on_delete=models.CASCADE)
    categoria = models.ForeignKey("catalogo.Categoria", related_name="urls", null=True, on_delete=models.CASCADE)
    marca = models.ForeignKey("catalogo.Marca", related_name="urls", null=True, on_delete=models.CASCADE)
    pagina = models.ForeignKey("plataforma.Pagina", related_name="urls", null=True, on_delete=models.CASCADE)

    conta = models.ForeignKey("plataforma.Conta", related_name="urls")
    contrato = models.ForeignKey("plataforma.Contrato", related_name="urls")

    class Meta:
        db_table = u"plataforma\".\"tb_url"
        verbose_name = u"URL"
        verbose_name_plural = u"URLs"
        ordering = ["-data_criacao"]
        unique_together = (("url", "conta", "contrato"),)

    def __unicode__(self):
        return self.url

    def save(self, *args, **kwargs):
        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id
        super(URL, self).save(*args, **kwargs)

    def url_principal(self):
        if self.principal:
            return self
        try:
            return URL.objects.get(
                principal=True, produto=self.produto, categoria=self.categoria,
                marca=self.marca, pagina=self.pagina, conta=self.conta)
        except URL.DoesNotExist:
            return self

    @classmethod
    def validar_url(cls, conta, url):
        # A URL deve obedecer a um padrão pré-definido.
        if not url or not re.match(cls.URL_REGEX, url):
            logger.debug('Regex nao bateu.')
            return False

        try:
            if not url.startswith('/'):
                url = "/{}".format(url)
            url = cls.objects.get(conta=conta, url=url)
        except cls.DoesNotExist:
            logger.debug('Tudo ok.')
            return True
        else:
            logger.debug('URL já existe.')
            # Url principal, deixa quieto.
            if url.principal:
                return False
            else:
                # Se for antiga, vish, remove e deixa criar!
                url.delete()
                return True


class Atividade(models.Model):
    id = custom_models.BigAutoField(db_column="atividade_id", primary_key=True)
    nome = models.CharField(db_column="atividade_nome", max_length=255)
    descricao = models.CharField(db_column="atividade_descricao", max_length=1024)

    class Meta:
        db_table = u"plataforma\".\"tb_atividade"
        verbose_name = u"Atividade da loja"
        verbose_name_plural = u"Atividades das lojas"
        ordering = ["nome"]

    def __unicode__(self):
        return self.nome


class Certificado(models.Model):
    """Tipo de certificados a venda."""
    # objects = caching.base.CachingManager()

    id = custom_models.BigAutoField(db_column="certificado_id", primary_key=True)
    ativo = models.BooleanField(db_column="certificado_ativo", default=True)
    nome = models.CharField(db_column="certificado_nome", max_length=64)
    codigo = models.CharField(db_column="certificado_codigo", max_length=64, unique=True)
    fornecedor = models.CharField(db_column="certificado_fornecedor", max_length=128)
    fornecedor_site = models.CharField(db_column="certificado_fornecedor_site", max_length=256, null=True)
    descricao = models.TextField(db_column="certificado_descricao", null=True, default=None)
    valor = models.DecimalField(db_column="certificado_valor", max_digits=16, decimal_places=2)
    validade_anos = models.IntegerField(db_column="certificado_validade_anos")

    crt_intermediario = models.TextField(db_column="certificado_crt_intermediario", null=True)
    crt_raiz = models.TextField(db_column="certificado_crt_raiz", null=True)
    contrato = models.ForeignKey('plataforma.Contrato', related_name="certificados")

    class Meta:
        db_table = u"plataforma\".\"tb_certificado"
        verbose_name = u"Certificado"
        verbose_name_plural = u"Certificados"
        ordering = ["valor"]

    def __unicode__(self):
        return self.nome


class Visita(models.Model):
    """Gerencia as visitas que ainda estão ativas atualmente nas lojas."""
    class Meta:
        db_table = u"plataforma\".\"tb_visita"
        verbose_name = u"Visita atual nas lojas"
        verbose_name_plural = u"Visitas atuais nas lojas"

    id = custom_models.BigAutoField(db_column="visita_id", primary_key=True)
    chave = models.CharField(db_column='visita_chave', max_length=32, unique=True)
    dominio = models.CharField(db_column='visita_dominio', max_length=255)
    expirado = models.BooleanField(db_column='visita_expirado', default=False)
    primeiro_acesso = models.DateTimeField(db_column='visita_primeiro_acesso')
    ultimo_acesso = models.DateTimeField(db_column='visita_ultimo_acesso')
    pageviews = models.BigIntegerField(db_column='visita_pageviews')
    trafego = models.BigIntegerField(db_column='visita_trafego')

    def __unicode__(self):
        return unicode(self.id)


class Usuario(models.Model):
    """Usuário do sistema."""
    INDICE_TIPOS = ['cliente', 'staff', 'admin', 'admin_global']

    # Esta lista tem que ser em ordem para que os tipos sejam usados como chave
    TIPOS = [
        (INDICE_TIPOS[3], u'Administrador global'),
        (INDICE_TIPOS[2], u'Administrador do Contrato'),
        (INDICE_TIPOS[1], u'Funcionário do Contrato'),
        (INDICE_TIPOS[0], u'Cliente'),
    ]

    id = custom_models.BigAutoField(db_column="usuario_id", primary_key=True)
    nome = models.CharField(db_column="usuario_nome", max_length=128)
    email = models.EmailField(db_column="usuario_email")
    _senha = models.CharField(db_column="usuario_senha", max_length=128)

    tipo = models.CharField(db_column="usuario_tipo", max_length=32, null=False, choices=TIPOS, default=INDICE_TIPOS[0])
    feedback = models.BooleanField(db_column="usuario_feedback", default=True)
    cancelado = models.BooleanField(db_column="usuario_cancelado", default=False)
    confirmado = models.BooleanField(db_column="usuario_confirmado", default=False)

    data_criacao = models.DateTimeField(db_column="usuario_data_criacao", auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column="usuario_data_modificacao", auto_now=True, null=True)
    data_ultimo_login = models.DateTimeField(db_column="usuario_data_ultimo_login", null=True, default=None)

    chave = custom_models.UUIDField(db_column="usuario_chave")
    contas = models.ManyToManyField('plataforma.Conta', related_name="usuarios", through="plataforma.ContaUsuario")
    contrato = models.ForeignKey('plataforma.Contrato', related_name="usuarios")

    class Meta:
        db_table = u"plataforma\".\"tb_usuario"
        verbose_name = u"Usuário"
        verbose_name_plural = u"Usuários"
        ordering = ["id"]
        unique_together = ('email', 'contrato')

    def __unicode__(self):
        return self.nome

    def get_senha(self):
        return self._senha

    def set_senha(self, valor):
        self._senha = hash(valor)

    senha = property(get_senha, set_senha)

    @property
    def primeiro_nome(self):
        if self.nome:
            return self.nome.split()[0]

    def verificar_tipo(self, tipo):
        try:
            indice_procurado = self.INDICE_TIPOS.index(tipo)
            indice_atual = self.INDICE_TIPOS.index(self.tipo)
        except ValueError:
            return False

        if indice_procurado <= indice_atual:
            return True
        return False

    def tipos(self):
        try:
            indice = self.INDICE_TIPOS.index(self.tipo) + 1
        except ValueError:
            indice = 1
        return self.INDICE_TIPOS[:indice]

    @property
    def admin_global(self):
        return self.verificar_tipo('admin_global')

    @property
    def admin(self):
        return self.verificar_tipo('admin')

    @property
    def staff(self):
        return self.verificar_tipo('staff')

    @property
    def cliente(self):
        return self.verificar_tipo('cliente')

    def has_perm(self, perm):
        if self.contrato.tipo_revenda and not perm.startswith('admin'):
            return True

        dict_permissoes = dict(settings.PERMISSOES)
        if perm in dict_permissoes:
            ator = dict_permissoes[perm]
            if ator == '*' or ator in self.tipos():
                return True
        return False

    @classmethod
    def gerar_senha_aleatoria(self):
        letras = 'abcdefghjkmnpqrstuvwxyz23456789'
        return ''.join([random.choice(letras) for x in range(6)])

    def logar(self, codigo, descricao, **kwargs):
        return None
        # descricao = u'%s (usuario_id=%s)' % (descricao, self.id)
        # try:
        #     conta_id = self.contas.all()[0].id
        # except IndexError:
        #     conta_id = 0

        # return NoSQLLog(codigo=codigo, conta_id=conta_id,
        #                 descricao=descricao, **kwargs).save()

    @classmethod
    def autenticar(self, email=None, senha=None, contrato_id=None, conta_id=None, by_token=None):

        try:
            if by_token is not None and by_token is True:
                usuario = self.objects.get(email__iexact=email, contrato_id=contrato_id)
            else:
                usuario = self.objects.get(email__iexact=email, _senha=hash(senha),
                                           cancelado=False, contrato_id=contrato_id)

        except self.DoesNotExist:
            return False
        else:
            if conta_id:
                try:
                    conta = Conta.objects.get(pk=conta_id)
                except Conta.DoesNotExist:
                    return False

                validade = conta.data_criacao + relativedelta(hours=+24)

                if conta.situacao != 'ATIVA' or validade < datetime.now():
                    if not usuario.confirmado:
                        raise UsuarioNaoConfirmado

            usuario.data_ultimo_login = datetime.now()
            usuario.save()
            return usuario

    def chave_confirmacao(self):
        return hash('%s.:.%s' % (self.id, self.email))

    def chave_alteracao(self):
        data = self.data_ultimo_login or self.data_criacao
        data = data.strftime('%Y-%m-%d %H:%M:%S')
        salt = '%s.:.%s.:.%s.:.%s' % (self.id, self.email, self.senha, data)
        return hash(salt)

    # FIXME: A conta não precisa ser passada.
    def enviar_email_confirmacao(self, request, pro=False):
        """Envia um email para o usuário confirmar que o seu email existe."""

        chave_confirmacao = self.chave_confirmacao()

        url_confirmacao = 'https://app.%s/public/usuario_email_confirmar/%s/%s' % \
                          (self.contrato.dominio, self.id, chave_confirmacao)

        context = {'url_confirmacao': url_confirmacao, 'pro': pro}

        utils.enviar_email(
            request,
            template_file='lojista/confirmando_email',
            context=context,
            usuario_id=self.id,
            salva_evidencia=False,
            countdown=3)

        return True

    def confirmar_email(self):
        self.confirmado = True
        self.save()
        # self.logar('LPN01002', u'Email do usuário foi confirmado.')

    def reenviar_senha(self, request):
        """Envia um email para o usuário com os passos para redefinir a sua senha."""
        chave_alteracao = self.chave_alteracao()

        url_alteracao = 'https://%s/public/usuario_senha_redefinir/%s/%s' % \
                        (self.contrato.url_aplicacao, self.id, chave_alteracao)

        context = {'url_alteracao': url_alteracao}

        utils.enviar_email(
            request,
            template_file='lojista/redefinir_senha',
            context=context,
            usuario_id=self.id,
            salva_evidencia=False)

        return True

    def alterar_senha(self, nova_senha):
        self.senha = nova_senha
        self.save()
        # self.logar('LPN01005', u'Senha do usuário foi alterada.')

    def intercom_user_hash(self):
        return hmac.new(
            settings.INTERCOM_API_SECRET,
            str(self.id), digestmod=hashlib.sha256).hexdigest()


class UsuarioNaoConfirmado(Exception):
    pass


class Conta(models.Model):
    """Conta do sistema."""
    CONTA_TIPO = [
        ("PF", u"Pessoa Física"),
        ("PJ", u"Pessoa Jurídica")
    ]

    # na unha
    CONTA_TESTE_APELIDO = 'temanovo'
    CONTA_TESTE_ID = 31
    CONTA_COPIA_ID = CONTA_TESTE_ID

    TIPO_LISTAGEM = [
        ('alfabetica', u'Ordem Alfabética'),
        ('ultimos_produtos', u'Últimos produtos'),
        ('destaque', u'Produtos em Destaque'),
        ('mais_vendidos', u'Produtos mais vendidos')
    ]
    LIMITE_TEMAS_ANTIGO = 53600

    MODOS_LOJA = [
        (u'loja', u'Loja virtual'),
        (u'catalogo_sem_preco', u'Catálogo sem preço'),
        (u'catalogo_com_preco', u'Catálogo com preço'),
        (u'orcamento_sem_preco', u'Orçamento sem preço'),
        (u'orcamento_com_preco', u'Orçamento com preço'),
    ]

    DADOS_CLIENTE_TESTE = {
        'nome': 'Cliente do suporte',
        'email': 'cliente.suporte@lojaintegrada.com.br',
        'senha': 'clientesuporte1q2w3e',
        'sexo': 'm',
        'telefone_principal': '11849433516',
        'telefone_comercial': '11849433516',
        'telefone_celular': '11986215001',
        'newsletter': True,
        'data_nascimento': '11/01/1991',
        'teste': True
    }

    MODO_LOJA = 'loja'

    MODOS_COM_PRECO = ['loja', 'catalogo_com_preco', 'orcamento_com_preco']
    MODOS_COM_VENDA = ['loja', 'orcamento_com_preco', 'orcamento_sem_preco']
    MODOS_COM_ORCAMENTO = ['orcamento_com_preco', 'orcamento_sem_preco']
    GOOGLE_MOSTRAR_REMARKETING = ['marca_listar', 'categoria_listar', 'index', 'buscar', 'produto_detalhar']
    MODO_COM_CLIENTES = ['loja']
    PLANO_INDICE_MINIMO_MODO_LOJA = 0
    DIAS_CANCELAMENTO_MINIMO = 30

    # Dados do elasticsearch
    FATOR_PONTUACAO_INDICE = 0.5

    APELIDOS_RESERVADOS = [
        'admin', 'administrador', 'apploja', 'integrado',
        'lojaintegrada', 'lojasintegradas', 'lojaintegrado',
        'manutencao', 'nixus', 'temporario', 'facebook', 'lojas',
        'lojailocal', 'ilocal', r'.*\-facebook'
    ]

    URL_SERVICOS = {
        'facebook': 'http://www.facebook.com/%s',
        'twitter': 'http://twitter.com/%s',
        'pinterest': 'http://pinterest.com/%s',
        'instagram': 'http://instagram.com/%s',
        'google_plus': 'http://plus.google.com/%s',
        'youtube': 'http://youtube.com/%s',
    }

    # relacionado a edição do tema
    NOVO_TEMPLATE_APELIDO = 'v1'

    COMPONENTES_CONFIGURACOES = novo_template_definicoes.COMPONENTES_CONFIGURACOES
    LINHAS_PADRAO_COLUNA = novo_template_definicoes.LINHAS_PADRAO_COLUNA
    DISPOSICOES_LAYOUT = novo_template_definicoes.DISPOSICOES_LAYOUT
    LAYOUT_BASE = novo_template_definicoes.LAYOUT_BASE
    CONTA_SITUACOES = [
        ('ATIVA', 'Loja ATIVA'),
        ('BLOQUEADA', 'Loja BLOQUEADA'),
        ('CANCELADA', 'Loja CANCELADA')
    ]

    id = custom_models.BigAutoField(db_column="conta_id", primary_key=True)
    apelido = models.CharField(db_column="conta_apelido", max_length=32)
    logo = models.CharField(db_column="conta_logo", max_length=128, null=True, default=None)
    situacao = models.CharField(db_column="conta_situacao", max_length=32, null=False, default='ATIVA', choices=CONTA_SITUACOES)
    data_criacao = models.DateTimeField(db_column="conta_data_criacao", auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column="conta_data_modificacao", auto_now=True, null=True)
    data_cancelamento = models.DateTimeField(db_column="conta_data_cancelamento", null=True)
    verificada = models.BooleanField(db_column="conta_verificada", default=False)

    tema_id = models.IntegerField(db_column="tema_id", null=True, default=None)

    tema = models.CharField(db_column="conta_loja_tema", max_length=128, default="v1")
    dominio = models.CharField(db_column="conta_loja_dominio", max_length=128, null=True, default=None)
    nome = models.CharField(db_column="conta_loja_nome", max_length=128, null=True, default=None)
    nome_loja_title = models.CharField(db_column="conta_loja_nome_title", max_length=128, null=True, default=None)
    telefone = models.CharField(db_column="conta_loja_telefone", max_length=20, null=True, default=None)
    whatsapp = models.CharField(db_column="conta_loja_whatsapp", max_length=20, null=True, default=None)
    skype = models.CharField(db_column="conta_loja_skype", max_length=128, null=True, default=None)
    endereco = models.CharField(db_column="conta_loja_endereco", max_length=128, null=True, default=None)
    email = models.CharField(db_column="conta_loja_email", max_length=128, null=True, default=None)
    css = models.TextField(db_column="conta_loja_css", default=None, null=True, blank=True)
    descricao = models.TextField(db_column="conta_loja_descricao", null=True, default=None)

    loja_tipo = models.CharField(db_column="conta_loja_tipo", max_length=2, choices=CONTA_TIPO, null=True, default=None)
    loja_cpf_cnpj = models.CharField(db_column="conta_loja_cpf_cnpj", max_length=15, null=True, default=None)
    loja_razao_social = models.CharField(db_column="conta_loja_razao_social", max_length=128, null=True, default=None)
    loja_nome_responsavel = models.CharField(db_column="conta_loja_nome_responsavel", max_length=128, null=True, default=None)

    loja_layout = models.TextField(db_column="conta_loja_layout", null=True, default=None)
    ultimo_pedido = models.IntegerField(db_column="conta_loja_ultimo_pedido", default=0)
    tipo_listagem = models.CharField(db_column="conta_loja_tipo_listagem_produto", max_length=32, null=False, choices=TIPO_LISTAGEM, default="alfabetica")
    quantidade_destaque = models.IntegerField(db_column='conta_loja_quantidade_destaque', null=False, default=24)
    ranking_json = JSONField(db_column='conta_ranking_json', null=False, default=None)
    produtos_linha = models.IntegerField(db_column='conta_loja_produtos_linha', null=False, default=4)
    banner_ebit = models.TextField(db_column='conta_loja_banner_ebit', null=True, blank=True)
    selo_ebit = models.TextField(db_column='conta_loja_selo_ebit', null=True, blank=True)
    selo_google_safe = models.BooleanField(db_column="conta_loja_selo_google_safe", null=False, default=False)
    selo_norton_secured = models.BooleanField(db_column="conta_loja_selo_norton_secured", null=False, default=False)
    selo_seomaster = models.BooleanField(db_column="conta_loja_selo_seomaster", null=False, default=True)
    comentarios_produtos = models.BooleanField(db_column="conta_loja_comentarios_produtos", default=True)
    blog = models.URLField(db_column="conta_loja_blog", max_length=256, null=True)
    favicon = models.TextField(db_column="conta_loja_favicon", default=None, blank=True)
    # redes sociais
    facebook = models.CharField(db_column="conta_loja_facebook", max_length=128, null=True, default=None)
    twitter = models.CharField(db_column="conta_loja_twitter", max_length=128, null=True, default=None)
    pinterest = models.CharField(db_column="conta_loja_pinterest", max_length=128, null=True, default=None)
    instagram = models.CharField(db_column="conta_loja_instagram", max_length=128, null=True, default=None)
    google_plus = models.CharField(db_column="conta_loja_google_plus", max_length=128, null=True, default=None)
    youtube = models.CharField(db_column="conta_loja_youtube", max_length=128, null=True, default=None)
    pedido_valor_minimo = models.DecimalField(
        db_column='conta_pedido_valor_minimo', max_digits=16, decimal_places=3, blank=True)
    ultimo_acesso = models.DateTimeField(
        db_column="conta_ultimo_acesso", default=None, null=True)
    modo = models.CharField(
        db_column="conta_loja_modo", max_length=32, null=False, default="loja")
    ultima_exportacao = models.DateTimeField(
        db_column="conta_ultima_exportacao", null=True)
    utm_campaign = models.CharField(max_length=255, db_column='conta_utm_campaign', null=True)
    utm_source = models.CharField(max_length=255, db_column='conta_utm_source', null=True)
    utm_medium = models.CharField(max_length=255, db_column='conta_utm_medium', null=True)
    utm_term = models.CharField(max_length=255, db_column='conta_utm_term', null=True)
    principal_redirect = models.CharField(max_length=64, db_column='conta_principal_redirect', null=True)
    conteudo_json = JSONField(db_column='conta_conteudo_json', null=True, default=None)

    email_webmaster_verificado = models.NullBooleanField(db_column="conta_email_webmaster_verificado", null=True, default=False)

    gerenciar_cliente = models.BooleanField(db_column='conta_gerenciar_cliente', default=False, null=False)
    chave = custom_models.UUIDField(db_column="conta_chave")
    wizard_finalizado = models.BooleanField(db_column="conta_wizard_finalizado", default=False)
    manutencao = models.BooleanField(db_column="conta_loja_manutencao", default=False)

    habilitar_facebook = models.BooleanField(db_column='conta_habilitar_facebook', default=False)
    habilitar_mercadolivre = models.BooleanField(db_column='conta_habilitar_mercadolivre', default=False)
    habilitar_mobile = models.BooleanField(db_column='conta_habilitar_mobile', default=True)

    origem_pro = models.BooleanField(db_column="conta_origem_pro", null=False, default=False)

    atividades = models.ManyToManyField('plataforma.Atividade', through="plataforma.ContaAtividade", related_name="contas")
    atividades.help_text = u''

    valor_produto_restrito = models.BooleanField(db_column="conta_valor_produto_restrito", null=False, default=False)

    beta_tester = models.BooleanField(db_column="conta_beta_tester", null=False, default=False)
    versao_indexacao = models.CharField(db_column='conta_versao_indexacao', max_length=100, default=None, null=True)

    contrato = models.ForeignKey('plataforma.Contrato', related_name="contas")

    class Meta:
        db_table = u"plataforma\".\"tb_conta"
        verbose_name = u"Conta"
        verbose_name_plural = u"Contas"
        ordering = ["id"]
        get_latest_by = "data_criacao"
        unique_together = ('apelido', 'contrato')

    def __unicode__(self):
        return self.dominio or self.apelido

    # Legacy property `nome_loja`.
    @property
    def nome_loja(self):
        return self.nome

    # Legacy setter `nome_loja`.
    @nome_loja.setter
    def nome_loja(self, value):
        self.nome = value

    # Legacy property `loja_manutencao`.
    @property
    def loja_manutencao(self):
        return self.manutencao

    # Legacy setter `loja_manutencao`.
    @loja_manutencao.setter
    def loja_manutencao(self, value):
        self.manutencao = value

    # def clean(self, *args, **kwargs):
    #     if self.apelido and len(self.apelido) < 5:
    #         raise ValidationError({'apelido': 'O apelido tem que ter 5 ou mais caracteres.'})
    #     if self.apelido in self.APELIDOS_RESERVADOS:
    #         raise ValidationError({'apelido': 'O apelido não pode ser usado pois está reservado.'})
    #     super(Conta, self).clean(*args, **kwargs)

    def logar(self, codigo, descricao, **kwargs):
        return None
        # return NoSQLLog(codigo=codigo, conta_id=self.id,
        #                 descricao=descricao, **kwargs).save()

    def endereco_loja(self):
        """Transforma o endereço json para os campos apropriados"""
        if not self.endereco:
            return ''
        try:
            return json.loads(self.endereco)
        except:
            return {}

    def endereco_is_json(self):
        try:
            json.loads(self.endereco)
        except:
            return None
        else:
            return True

    def endereco_loja_formatado(self, complemento=True, cep=True):
        endereco = self.endereco_loja()
        if not endereco:
            return self.endereco
        saida = endereco.get('endereco')
        # retirando virgla
        if saida.endswith(','):
            saida = saida[:-1]
        if endereco.get('numero'):
            saida += ', %s' % endereco.get('numero')
        if endereco.get('complemento') and complemento:
            saida += ' - %s' % endereco.get('complemento')
        if endereco.get('bairro'):
            saida += ', %s' % endereco.get('bairro')
        if endereco.get('cidade'):
            saida += ', %s' % endereco.get('cidade')
        if endereco.get('estado'):
            saida += ', %s' % endereco.get('estado')
        if endereco.get('cep') and cep:
            saida += ' - %s' % utils.formatar_cep(endereco.get('cep'))
        return saida

    def endereco_loja_google_maps(self):
        return self.endereco_loja_formatado(complemento=False, cep=False)

    @property
    def md5_data_criacao(self):
        return hash(self.data_criacao.strftime('%Y-%m-%d %H:%M:%S'))

    @property
    def email_contato(self):
        if self.email:
            return self.email
        elif len(self.usuarios.all()):
            return self.usuarios.all()[0].email
        else:
            return None

    @property
    def tem_certificado_ativo(self):
        return ContaCertificado.objects.filter(situacao='ativo', conta_id=self.id).exists()

    @property
    def email_pedido(self):
        return '"%s" <nao-responder@%s>' % (self.nome_loja or '', self.contrato.dominio)

    @property
    def email_sistema(self):
        return '"%s" <nao-responder@%s>' % (self.nome_loja or '', self.contrato.dominio)

    @property
    def email_loja(self):
        return '"%s" <nao-responder@%s>' % (self.nome_loja or '', self.contrato.dominio)

    @property
    def email_webmaster(self):
        if self.dominio_sem_www:
            return 'webmaster@{}'.format(self.dominio_sem_www)
        return None

    @property
    def url_dominio(self):
        """Verifica se existe um dominio caso não existe retorna o apelido
        + lojaintegrada.com.br"""
        if self.dominio:
            return self.dominio
        else:
            return self.url_subdominio

    def url_subdominio_facebook(self):
        """Retorna a url do facebook para o subdominio/contrato"""
        return "%s-facebook.%s" % (self.apelido, self.contrato.dominio)

    @property
    def url_subdominio(self):
        """Retorna sempre o subdomínio da loja integrada."""
        return "%s.%s" % (self.apelido, self.contrato.dominio)

    def favicon_ico(self):
        if not self.favicon:
            return False
        if self.favicon.upper().endswith('.ICO'):
            return True
        return False

    @property
    def url_subdominio_facebook(self):
        """Retorna a url do facebook para o subdominio/contrato"""
        return "%s-facebook.%s" % (self.apelido, self.contrato.dominio)

    @property
    def dominio_sem_www(self):
        if self.dominio:
            return ".".join(self.dominio.split(".")[1:])
        return None

    def save(self, *args, **kwargs):
        if not self.apelido and not self.id:
            self.apelido = self.gerar_apelido_aleatorio()
        if self.dominio and 'lojaintegrada.com.br' in self.dominio:
            apelido = self.dominio.split('.')
            if apelido[0].startswith('www'):
                self.apelido = apelido[1]
            else:
                self.apelido = apelido[0]
            self.dominio = None
        if not self.apelido:
            raise IntegrityError(u'Apelido inválido')
        self.apelido = self.apelido.lower()

        if not self.contrato_id:
            self.contrato_id = 1
        if isinstance(self.loja_layout, dict):
            self.loja_layout = json.dumps(self.loja_layout)
        if isinstance(self.endereco, dict):
            self.endereco = json.dumps(self.endereco)
        super(self.__class__, self).save(*args, **kwargs)

    @classmethod
    def gerar_apelido_aleatorio(self):
        letras = 'abcdefghijklmnopqrstuvwxyz0123456789'
        salt = ''.join([random.choice(letras) for x in range(5)])
        return 'nova-loja-%s' % salt

    def dominios_alternativos(self):
        return self.dominios.filter(principal=False)

    def numero_pedido_minimo(self):
        minimo = self.pedidos_vendas.all().only('numero') \
            .aggregate(minimo=Max('numero')).get('minimo')
        if not minimo:
            return 1
        return minimo

    def ultimo_pedido_criado(self):
        ultimo = self.pedidos_vendas.all() \
            .only('numero') \
            .aggregate(ultimo=Max('numero')) \
            .get('ultimo')
        if not ultimo:
            return 0
        return ultimo

    @classmethod
    def verificar_apelido_reservado(cls, apelido):
        """Retorna True caso o apelido seja reservado, False caso contrário."""
        if settings.DEBUG:
            return False
        for apelido_reservado in cls.APELIDOS_RESERVADOS:
            if re.match(apelido_reservado, apelido):
                return True
        return False

    def chave_reativacao(self):
        data = self.ultimo_acesso or self.data_criacao
        data = data.strftime('%Y-%m-%d %H:%M:%S')
        salt = '%s.:.%s.:.%s.:.' % (self.id, self.situacao, data)
        return hash(salt)

    def dominio_principal(self):
        try:
            return self.dominios.get(principal=True)
        except Dominio.DoesNotExist:
            return None

    def adicionar_dominio_alternativo(self, fqdn, principal=False):
        from repositories.configuracao.models import Dominio
        # Verifica se deve ser principal
        try:
            existencia = Dominio.objects.only('id').get(conta_id=self.id, principal=True)
        except Exception:
            principal = True
        finally:
            dominio = Dominio(fqdn=fqdn, principal=principal, conta=self)

            if principal is True:
                Conta.objects.only('id', 'fqdn').filter(id=self.id).update(dominio=fqdn)

            dominio.save()
            return dominio

    def principais_pagamentos(self, configuracoes_pagamento, bancos_deposito):
        bandeira_cartoes = []
        bandeira_bancos = []
        outras_bandeiras = []
        for pagamento in configuracoes_pagamento:
            pagamentos = pagamento.principais_pagamentos()
            cartoes = pagamentos.get('cartoes', [])
            outros = pagamentos.get('outros', [])
            bancos = pagamentos.get('bancos', [])
            outras_bandeiras += outros
            bandeira_cartoes += cartoes
            bandeira_bancos += bancos
        outras_bandeiras = list(set(outras_bandeiras))
        bandeira_cartoes = list(set(bandeira_cartoes))
        bandeira_bancos = list(set(bandeira_bancos))

        # bancos so se foram em contas pagas
        # TODO: REVER
        # if self.plano_id > 1:
        #     for banco in bancos_deposito:
        #         # Esta duplicando a bandeira de BOLETO no rodape.
        #         if banco.nome == 'boleto-bancario':
        #             nome = 'boleto'
        #         else:
        #             nome = banco.nome
        #         bandeira_bancos.append(slugify(nome))
        #     bandeira_bancos = list(set(bandeira_bancos))

        todas_bandeiras = set(bandeira_cartoes + bandeira_bancos + outras_bandeiras)
        return todas_bandeiras

    def verificar_pedido_minimo(self, valor):
        """Verificar se pelas configurações da conta o pedido é válido"""
        if not self.pedido_valor_minimo:
            return {'status': 'valido'}
        if valor >= self.pedido_valor_minimo:
            return {'status': 'valido'}
        from repositories.libs.utils import formatar_decimal_br
        resto = formatar_decimal_br(self.pedido_valor_minimo - valor)
        return {
            'status': 'invalido',
            'mensagem': u'Ainda faltam R$ %s para que' \
                        u' o pedido possa ser finalizado' % resto,
        }

    def tem_versao_mobile(self):
        # até o mês de fevereiro vai ser gratis
        # depois colocar lógica para ver se a conta
        # tem ou não tem versão mobile
        return self.habilitar_mobile

    @classmethod
    def assinar(cls, request, email, nome, senha, plano=None, contrato_id=None,
                utm_campaign=None, utm_source=None, utm_medium=None,
                utm_term=None, origem_pro=False):
        if not contrato_id:
            contrato_id = 1

        if origem_pro is None:
            origem_pro = False

        try:
            usuario = Usuario(email=email, nome=nome, senha=senha, contrato_id=contrato_id)
            usuario.save()
        except Exception as e:
            logger.error(e)
            raise UsuarioJaExiste

        try:

            conta = cls(
                contrato_id=contrato_id, utm_campaign=utm_campaign,
                utm_source=utm_source, utm_medium=utm_medium,
                utm_term=utm_term, origem_pro=origem_pro)
            conta.save()

            # É necessário vincular a conta ao usuário aqui para que na
            # alteração do plano seja enviado um email para o usuário.
            conta_usuario = ContaUsuario(conta=conta, usuario=usuario, administrador=True)
            conta_usuario.save()
        except Exception as e:
            logger.error(e)
            raise ContaJaExiste

        usuario.enviar_email_confirmacao(request, pro=origem_pro)

        return conta

    def proximo_numero_pedido(self):
        """Incrementa o último número de pedido no banco e o retorna."""
        proximo_pedido = self.ultimo_pedido + 1

        from repositories.pedido.models import PedidoVenda
        try:
            minimo = self.pedidos_vendas.only('numero').get(numero=proximo_pedido)
        except PedidoVenda.DoesNotExist:
            pass
        else:
            proximo_pedido = self.ultimo_pedido_criado() + 1

        self.ultimo_pedido = proximo_pedido
        self.save()
        return self.ultimo_pedido

    def tem_redes_sociais(self):
        redes = ['facebook', 'google_plus', 'twitter',
                 'youtube', 'instagram', 'pinterest']
        if self.blog:
            return True
        for rede in redes:
            if getattr(self, rede):
                return True
        return False

    def tem_selos_rodape(self):
        try:
            certificado_ssl = self.conta_certificado
        except ContaCertificado.DoesNotExist:
            certificado_ssl = None
        return self.selo_ebit or self.selo_google_safe or \
               self.selo_norton_secured or \
               self.selo_seomaster or certificado_ssl

    @property
    def usuario(self):
        try:
            conta_usuario = ContaUsuario.objects.filter(conta=self).order_by('-administrador')[0]
            return conta_usuario.usuario
        except IndexError:
            return None

    def atualizar_exportacao(self):
        self.ultima_exportacao = datetime.now()
        self.save()

    def endereco_conta_formato(self):
        # Formato
        # Rua Cláudio Soares, 72 cj 1211 - Pinheiros
        # CEP 05422-030 - São Paulo/SP
        return "%s, %s - %s\n CEP %s - %s/%s" % \
               (self.endereco_logradouro or '', self.endereco_complemento or '',
                self.endereco_bairro or '', self.endereco_cep or '',
                self.endereco_cidade or '', self.endereco_estado or '')

    def _parser_endereco(self):
        """Pega o endereço da conta e tenta trazer o tipo, logradouro e
        número separados.
        """
        if not self.endereco_logradouro:
            return None, None, None

        tipo = self.endereco_logradouro.split()[0].upper()
        tipo = ''.join([x for x in tipo if x in string.ascii_uppercase])
        if len(tipo) > 4 or len(tipo) <= 1:
            if tipo in LOGRADOUROS:
                tipo = LOGRADOUROS[tipo]
            else:
                tipo = u'RUA'

        if tipo not in LOGRADOUROS.values():
            tipo = u'RUA'

        logradouro = self.endereco_logradouro
        if ',' in logradouro:
            numero = logradouro.split(',')[-1].strip()
            logradouro = u' '.join(logradouro.split(',')[:-1])
        else:
            numero = logradouro.split()[-1].strip()
            logradouro = u' '.join(logradouro.split()[:-1])

        if not re.search('\d', numero):
            numero = u'S/N'

        return tipo, logradouro[:50], numero[:10]

    def layout(self):

        # try:
        #     if self.tema_id is not None and self.tema_layout_parametros:
        #         return self.tema_layout_parametros
        # except:
        #     pass

        if not self.loja_layout:
            return self.LAYOUT_BASE

        return json.loads(self.loja_layout)

    def configuracao_componente(self):
        configuracao = self.layout().get('configuracao', {})
        return dict([(k.replace('-', '_'), v) for k, v in configuracao.items()])

    def novo_template(self):
        """Retorna True se a conta estiver
        usando o novo template"""
        return self.tema == self.NOVO_TEMPLATE_APELIDO

    def hash_list(self, lista):
        return '_'.join(sorted([x for sub in lista for x in sub]))

    def layout_forms(self):
        """Transforma o JSON em dados válidos
        para o forms"""
        dados_layout = self.layout()

        cabecalho = dados_layout.get('cabecalho', {})
        rodape = dados_layout.get('rodape', {})
        coluna = dados_layout.get('coluna', {})
        fullbanner = dados_layout.get('fullbanner')
        secao_banner = dados_layout.get('banner')
        configuracao = dados_layout.get('configuracao', {})

        # Assumindo sempre que é somente 1 componente por linha.
        coluna_linhas = ''.join(("%s," % x[0]) for x in coluna.get('linhas', []))

        disposicao_linhas = dados_layout.get(
            'conteudo', {}
        ).get('linhas', []) + dados_layout.get(
            'banner', {}
        ).get('linhas', [])
        disposicao_linhas = self.hash_list(disposicao_linhas)
        disposicao = None

        # Necessário?
        for k, v in self.DISPOSICOES_LAYOUT.items():
            disposicao_usada = v.get('conteudo', {}).get('linhas', []) + \
                               v.get('banner', {}).get('linhas', [])
            disposicao_usada = self.hash_list(disposicao_usada)
            if disposicao_linhas == disposicao_usada:
                disposicao = k
                break

        initial_data = {
            'menu': dados_layout.get('menu'),
            'menu_conteudo': dados_layout.get('menu_conteudo'),
            'menu_lateral_expandido': dados_layout.get('menu_lateral_expandido'),
            'cabecalho': cabecalho.get('disposicao'),
            'rodape': rodape.get('disposicao'),
            'coluna': coluna.get('posicao', 'sem'),
            'coluna_linhas': coluna_linhas,
            'disposicao': disposicao,
            'tamanho': dados_layout.get('tamanho'),
            'newsletter': dados_layout.get('newsletter', {}),
        }

        if 'listagem_produto' in configuracao:
            listagem_produto = configuracao['listagem_produto']

            if 'caixa' in listagem_produto:
                initial_data['caixa'] = listagem_produto['caixa']

            if 'destaque' in listagem_produto:
                initial_data['destaque'] = listagem_produto['destaque']

        initial_data.update(dict([(k, v) for k, v in configuracao.items()]))
        return initial_data

    @property
    def url_facebook(self):
        if self.facebook:
            return self.URL_SERVICOS.get('facebook') % self.facebook
        return None

    @property
    def url_twitter(self):
        if self.twitter:
            return self.URL_SERVICOS.get('twitter') % self.twitter
        return None

    @property
    def url_pinterest(self):
        if self.pinterest:
            return self.URL_SERVICOS.get('pinterest') % self.pinterest
        return None

    @property
    def url_instagram(self):
        if self.instagram:
            return self.URL_SERVICOS.get('instagram') % self.instagram
        return None

    @property
    def url_youtube(self):
        if self.youtube:
            return self.URL_SERVICOS.get('youtube') % self.youtube
        return None

    @property
    def url_google_plus(self):
        if self.google_plus:
            return self.URL_SERVICOS.get('google_plus') % self.google_plus
        return None

    @property
    def url_blog(self):
        return self.blog

    def cancelar(self, dados_cancelamento=None):
        """Cancela uma conta e remove seus domínios."""
        from repositories.configuracao.models import Dominio
        Dominio.objects.filter(conta_id=self.id).delete()

        self.situacao = 'CANCELADA'
        self.data_cancelamento = datetime.now()
        self.save()

    def reativar(self):
        self.situacao = 'ATIVA'
        self.data_cancelamento = None
        self.save()

    class CancelamentoInvalido(Exception):
        pass

    def verificar_modo(self):
        return self.modo

    def mostrar_preco(self):
        """Retorna verdadeiro se a loja foi configurada para mostrar o preço"""
        return self.verificar_modo() in self.MODOS_COM_PRECO

    def pode_vender(self):
        """Retorna True se a loja pode vender"""
        return self.verificar_modo() in self.MODOS_COM_VENDA

    def orcamento(self):
        return (self.verificar_modo() in self.MODOS_COM_ORCAMENTO) or None

    def pode_ter_clientes(self):
        return (self.verificar_modo() in self.MODO_COM_CLIENTES) or None

    def copiar_dados_teste(self):
        """ Copia os dados de teste"""
        try:
            conta_original = Conta.objects.get(apelido=self.CONTA_TESTE_APELIDO)
        except Conta.DoesNotExist:
            return None
        return conta_original.copiar_dados_loja(self)

    def copiar_dados_loja(self, loja):
        """Copia alguns dos dados da loja para a loja que foi informada
        via argumento"""

        def _get_foreign_keys(model):
            """Retorna todas as Foreign Keys/OneToOne do modelo"""
            from django.db.models.fields.related import RelatedField
            return ([x[0] for x in model._meta.get_fields_with_model()
                     if isinstance(x[0], RelatedField) and x[0].name != 'conta'
                     and x[0].name != 'id'])

        conta_id = self.id
        chaves_estrangeiras_alteradas = {}
        tree_ids = {}
        # se o wizard ja foi finalizado
        if loja.wizard_finalizado:
            return None
        modelos = [
            'catalogo.Marca',
            'catalogo.Produto.pai',
            'catalogo.ProdutoGrade', 'catalogo.ProdutoGradeVariacao',
            'domain.Imagem', 'catalogo.ProdutoImagem.produto',
            'catalogo.ProdutoPreco.produto', 'catalogo.ProdutoEstoque.produto',
            'plataforma.Pagina', 'marketing.Banner']

        with transaction.atomic():
            for model_string in modelos:
                split_model = model_string.split('.')
                schema, model = split_model[0], split_model[1]
                modelo = get_model(schema, model)
                if len(split_model) == 3:
                    linhas = modelo.objects.filter(
                        conta_id=conta_id
                    ).order_by(split_model[2])
                else:
                    linhas = modelo.objects.filter(
                        conta_id=conta_id
                    )

                for linha in linhas:
                    id_antigo = linha.pk
                    nome_chave_primaria = '%s_%s' % (linha._meta.pk.db_column,
                                                     id_antigo)
                    linha.pk = None
                    for field in _get_foreign_keys(linha):
                        valor_do_campo = getattr(linha, '%s' % field.name)
                        if not valor_do_campo:
                            continue
                        name_field = '%s_id_%s' % (field.name, valor_do_campo.id)
                        if isinstance(valor_do_campo, linha.__class__):
                            name_field_parent = '%s_%s' % (
                                linha._meta.pk.column,
                                valor_do_campo.id)
                            if name_field_parent in chaves_estrangeiras_alteradas:
                                setattr(
                                    linha, '%s_id' % field.name,
                                    chaves_estrangeiras_alteradas[name_field_parent])
                        else:
                            nome_do_campo = name_field.replace('_pai', '')
                            if nome_do_campo in chaves_estrangeiras_alteradas:
                                setattr(
                                    linha, '%s_id' % field.name,
                                    chaves_estrangeiras_alteradas[nome_do_campo])

                    # injetando a nova conta
                    linha.conta_id = loja.id
                    linha._copia = True

                    linha.save()
                    chaves_estrangeiras_alteradas[nome_chave_primaria] = linha.pk
                    # connectando de volta
                    # post_save.connect(produto_post_save, sender=Produto)

    @classmethod
    def painel_resumo(cls, conta_id):
        """Traz todos os dados de resumo para o painel.

        Faz as queries de conta_uso e deixa os dados guardados na sessão.

        Os dados são guardados durante 15 minutos na sessão, caso este dados seja
        consultado nesses 15 minutos, ele é retornado diretamente da sessão, após
        os 15 minutos ele é consultado novamente do banco.

        Use forcar=True para forçar a atualização dos dados diretamente do banco
        independente se o tempo do cache ainda estiver válido.

        - ultima_atualizacao -> Data e hora da última atualização.
        - uso_data_inicio -> Data de início do resumo de uso da conta.
        - uso_data_fim -> Data de fim do resumo de uso da conta.
        - visitas -> Total de visitas no período.
        - porcentagem_visitas -> Porcentagem de visitas em relação ao plano atual.
        - trafego -> Total trafegado no período.
        - porcentagem_trafego -> Porcentagem trafegado em relação ao plano atual.
        - produtos -> Qunatidade total de produtos.
        - vendas -> Qunatidade total de vendas nos últimos 30 dias.
        - vendas_aprovadas -> Qunatidade total de vendas aprovadas nos últimos 30 dias.
        - vendas_canceladas -> Qunatidade total de vendas canceladas nos últimos 30 dias.
        - vendas_pendentes -> Qunatidade total de vendas pendentes nos últimos 30 dias.
        - porcentagem_vendas_aprovadas -> Porcentagem de vendas aprovadas nos últimos 30 dias.
        - porcentagem_vendas_canceladas -> Porcentagem de vendas canceladas nos últimos 30 dias.
        - porcentagem_vendas_pendentes -> Porcentagem de vendas pendentes nos últimos 30 dias.
        """

        resumo = {}

        inicio = datetime.now().date() - timedelta(days=30)
        fim = datetime.now()

        sql = '''SELECT (COUNT(*)) AS "total",
               (COUNT(CASE WHEN "pedido"."tb_pedido_venda"."pedido_venda_situacao_id" IN (4, 11, 13, 14, 15, 17) THEN 1 ELSE NULL END)) AS "aprovadas",
               (COUNT(CASE WHEN "pedido"."tb_pedido_venda"."pedido_venda_situacao_id" IN (8) THEN 1 ELSE NULL END)) AS "canceladas",
               (COUNT(CASE WHEN "pedido"."tb_pedido_venda"."pedido_venda_situacao_id" IN (2, 3, 9) THEN 1 ELSE NULL END)) AS "pendentes"
        FROM "pedido"."tb_pedido_venda"
        WHERE (
            "pedido"."tb_pedido_venda"."conta_id" = %s  AND
            "pedido"."tb_pedido_venda"."pedido_venda_situacao_id" IS NOT NULL AND
            "pedido"."tb_pedido_venda"."pedido_venda_data_criacao" BETWEEN %s and %s
        )'''
        cursor = connection.cursor()
        cursor.execute(sql, [conta_id, inicio, fim])
        vendas = cursor.fetchone()

        resumo['vendas'] = vendas[0]
        resumo['vendas_aprovadas'] = vendas[1]
        resumo['vendas_canceladas'] = vendas[2]
        resumo['vendas_pendentes'] = vendas[3]
        if resumo['vendas'] > 0:
            resumo['porcentagem_vendas_aprovadas'] = float(resumo['vendas_aprovadas']) / resumo['vendas'] * 100.0
            resumo['porcentagem_vendas_canceladas'] = float(resumo['vendas_canceladas']) / resumo['vendas'] * 100.0
            resumo['porcentagem_vendas_pendentes'] = float(resumo['vendas_pendentes']) / resumo['vendas'] * 100.0
        else:
            resumo['porcentagem_vendas_aprovadas'] = \
                resumo['porcentagem_vendas_canceladas'] = \
                resumo['porcentagem_vendas_pendentes'] = 0.0
        return resumo


class ContaCertificado(models.Model):
    """Gerencia os Certificados SSL instalados na Loja integrada."""
    SITUACAO_ATIVO = u"ativo"
    SITUACAO_PENDENTE = u"pendente"
    SITUACAO_AGUARDANDO_APROVACAO = u"aguardando_aprovacao"
    SITUACAO_VENCIDO = u"vencido"
    SITUACAO_INVALIDO = u"invalido"
    SITUACAO_CANCELADO = u"cancelado"

    CONTA_CERTIFICADO_SITUACAO = [
        (SITUACAO_ATIVO, u"Ativo"),
        (SITUACAO_PENDENTE, u"Pendente"),
        (SITUACAO_AGUARDANDO_APROVACAO, u"Aguardando aprovação"),
        (SITUACAO_VENCIDO, u"Vencido"),
        (SITUACAO_INVALIDO, u"Inválido"),
        (SITUACAO_CANCELADO, u"Cancelado")
    ]

    id = custom_models.BigAutoField(db_column="conta_certificado_id", primary_key=True)
    dominio = models.CharField(db_column="conta_certificado_dominio", max_length=128)
    key = models.TextField(db_column="conta_certificado_key", null=True)
    csr = models.TextField(db_column="conta_certificado_csr", null=True)
    crt = models.TextField(db_column="conta_certificado_crt", null=True)
    data_inicio = models.DateTimeField(db_column="conta_certificado_data_inicio", auto_now_add=True)
    data_expiracao = models.DateTimeField(db_column="conta_certificado_data_expiracao", null=True)
    situacao = models.CharField(db_column="conta_certificado_situacao", max_length=32, choices=CONTA_CERTIFICADO_SITUACAO, default=SITUACAO_PENDENTE)

    nc_compra_id = models.IntegerField(db_column="conta_certificado_namecheap_compra_id", null=True)
    nc_certificado_id = models.IntegerField(db_column="conta_certificado_namecheap_certificado_id", null=True)
    nc_transacao_id = models.IntegerField(db_column="conta_certificado_namecheap_transacao_id", null=True)

    certificado = models.ForeignKey('plataforma.Certificado', related_name='contas', on_delete=models.CASCADE)
    conta = models.ForeignKey('plataforma.Conta', related_name='conta_certificado', on_delete=models.CASCADE)
    contrato = models.ForeignKey('plataforma.Contrato', related_name="contas_certificados")

    class Meta:
        db_table = u"plataforma\".\"tb_conta_certificado"
        verbose_name = u"Certificado SSL"
        verbose_name_plural = u"Certificados SSL"

    def __unicode__(self):
        return unicode(self.id)

    def save(self, *args, **kwargs):
        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id
        super(ContaCertificado, self).save(*args, **kwargs)

    @property
    def email_apovador(self):
        return 'webmaster@%s' % self.conta.dominio_sem_www


class ContaAtividade(models.Model):
    """Relação de atividade de um conta."""
    id = custom_models.BigAutoField(db_column="id", primary_key=True)

    conta = models.ForeignKey('plataforma.Conta', related_name="conta_atividades")
    atividade = models.ForeignKey('plataforma.Atividade', related_name="contas_atividade")
    contrato = models.ForeignKey('plataforma.Contrato', related_name="contas_atividades")

    class Meta:
        db_table = u"plataforma\".\"tb_conta_atividade"
        verbose_name = u"Atividade da conta"
        verbose_name_plural = u"Atividades da contas"
        unique_together = (("conta", "atividade"),)

    def save(self, *args, **kwargs):
        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id
        super(ContaAtividade, self).save(*args, **kwargs)


class ContaUsuario(models.Model):
    """Relação entre conta e usuário."""
    id = custom_models.BigAutoField(db_column="conta_usuario_id", primary_key=True)
    conta = models.ForeignKey('plataforma.Conta', db_column="conta_id", related_name="conta_usuarios", on_delete=models.CASCADE)
    usuario = models.ForeignKey('plataforma.Usuario', db_column="usuario_id", related_name="contas_usuario", on_delete=models.CASCADE)
    administrador = models.BooleanField(db_column="conta_usuario_administrador", default=False)
    contrato = models.ForeignKey('plataforma.Contrato', related_name="contas_usuarios")

    class Meta:
        db_table = u"plataforma\".\"tb_conta_usuario"
        unique_together = ('conta', 'usuario')

    def __unicode__(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id
        super(self.__class__, self).save(*args, **kwargs)


class ContaUsuarioConvite(models.Model):
    """Convites para usuários se juntarem a uma conta."""
    id = custom_models.BigAutoField(db_column="conta_usuario_convite_id", primary_key=True)
    email = models.EmailField(db_column="conta_usuario_convite_email")
    chave = models.CharField(db_column="conta_usuario_convite_chave", max_length=64)
    data_criacao = models.DateTimeField(db_column="conta_usuario_convite_data_criacao", auto_now_add=True)

    conta = models.ForeignKey('plataforma.Conta', db_column="conta_id", related_name="convites")
    usuario = models.ForeignKey('plataforma.Usuario', db_column="usuario_id", related_name="convites", default=None, null=True)
    contrato = models.ForeignKey('plataforma.Contrato', related_name="convites")

    class Meta:
        db_table = u"plataforma\".\"tb_conta_usuario_convite"
        verbose_name = u"Convite"
        verbose_name_plural = u"Convites"
        ordering = ["id"]
        unique_together = ('conta', 'email')

    def __unicode__(self):
        return '%s - %s' % (self.conta, self.email)

    def save(self, *args, **kwargs):
        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id
        super(self.__class__, self).save(*args, **kwargs)

    @classmethod
    def convidar_usuario(cls, request, conta, email=None, usuario=None):

        if not email:
            email = usuario.email

        convite = cls.objects.create(
            conta=conta, email=email, usuario=usuario,
            contrato=conta.contrato)

        url_aceitar_convite = reverse('public_convite_aceitar', args=[convite.chave])
        url_recusar_convite = reverse('public_convite_recusar', args=[convite.chave])

        context = {
            'url_aceitar_convite': url_aceitar_convite,
            'url_recusar_convite': url_recusar_convite
        }

        utils.enviar_email(
            request,
            template_file='loja/convidar_usuario',
            context=context,
            to_email=email,
            salva_evidencia=False
        )

    def recusar(self):
        self.delete()

    def aceitar(self, nome=None, senha=None):
        try:
            with transaction.atomic():
                usuario = self.usuario
                if not self.usuario:
                    usuario = Usuario.objects.create(
                        nome=nome, senha=senha, email=self.email,
                        contrato=self.conta.contrato,
                        confirmado=True)

                ContaUsuario.objects.create(
                    conta=self.conta, usuario=usuario)

                self.delete()
                return usuario
        except IntegrityError:
            return False


@receiver(pre_save, sender=ContaUsuarioConvite)
def convite_pre_save(sender, instance, raw, **kwargs):
    if not instance.chave:
        agora = datetime.now()
        instance.chave = hash('%s%s' % (instance.email, agora))


class ImpossivelVerificarRetencaoIRRF(Exception):
    pass


class Observacao(models.Model):
    id = custom_models.BigAutoField(db_column="observacao_id", primary_key=True)
    tabela = models.CharField(db_column="observacao_tabela", max_length=64)
    linha_id = models.BigIntegerField(db_column="observacao_linha_id")
    conteudo = models.TextField(db_column="observacao_conteudo", null=True)
    usuario = models.ForeignKey('plataforma.Usuario', db_column="usuario_id", related_name="observacoes", on_delete=models.CASCADE)
    encaminhada = models.BooleanField(db_column="observacao_encaminhada", default=False)
    data_criacao = models.DateTimeField(db_column='observacao_data_criacao', auto_now_add=True)
    conta = models.ForeignKey('plataforma.Conta', db_column="conta_id", related_name='observacoes')
    contrato = models.ForeignKey('plataforma.Contrato', db_column="contrato_id", related_name='observacoes')

    class Meta:
        db_table = u"plataforma\".\"tb_observacao"
        verbose_name = u'Observação'
        verbose_name_plural = u"Observações"
        ordering = ['id']


class Parceiro(models.Model):
    CATEGORIAS_PARCEIRO = [
        ('design', u'Design'),
        ('consultoria', u'Consultoria'),
        ('email_marketing', 'Email marketing'),
        ('catalogo', u'ERP'),
        ('marketing_digital', u'Marketing digital'),
        ('servico', u'Serviço'),
        ('outros', u'Outros'),

    ]

    id = custom_models.BigAutoField(db_column='parceiro_id', primary_key=True)
    nome = models.CharField(db_column='parceiro_nome', max_length=128, unique=True)
    nome_responsavel = models.CharField(db_column='parceiro_nome_responsavel', max_length=128, unique=True)
    categoria = models.CharField(max_length=64, db_column='parceiro_categoria', null=False, choices=CATEGORIAS_PARCEIRO)
    ativo = models.BooleanField(db_column="parceiro_ativo", default=False)
    data_contrato = models.DateTimeField(db_column="parceiro_data_contrato", null=True)
    url = models.CharField(max_length=256, db_column="parceiro_url", null=False)
    logo = models.CharField(max_length=256, db_column="parceiro_logo", null=False)
    descricao = models.TextField(db_column="parceiro_descricao", null=True)
    telefone = models.CharField(u'Telefone principal', db_column="parceiro_telefone", max_length=11, null=True, default=None)
    email = models.EmailField(db_column="parceiro_email")

    class Meta:
        db_table = u"plataforma\".\"tb_parceiro"
        verbose_name = u"Parceiro"
        verbose_name_plural = u"Parceiros"
        ordering = ['nome']

    def __unicode__(self):
        return self.nome


class Email(models.Model):
    """Emails que são enviados pelo sistema."""

    id = custom_models.BigAutoField(db_column='email_id', primary_key=True)
    de = models.CharField(db_column='email_de', max_length=256, null=False)
    para = models.CharField(db_column='email_para', max_length=256, null=False)
    responder_para = models.CharField(db_column='email_responder_para', max_length=256, null=True)

    conteudo_html = models.TextField(db_column='email_conteudo_html', null=False)
    conteudo_txt = models.TextField(db_column='email_conteudo_txt', null=True)
    assunto = models.CharField(db_column='email_tipo', max_length=128, null=False)
    lido = models.BooleanField(db_column="email_lido", default=False)
    erro = models.TextField(db_column="email_erro", null=True)
    data_criacao = models.DateTimeField(db_column="email_data_criacao", auto_now_add=True)
    prioridade = models.IntegerField(db_column='email_prioridade', default=1)

    conta = models.ForeignKey('plataforma.Conta', db_column="conta_id", related_name="emails", null=True, default=None)
    usuario = models.ForeignKey('plataforma.Usuario', db_column="usuario_id", related_name="emails", null=True, default=None)
    cliente = models.ForeignKey('cliente.Cliente', db_column="cliente_id", related_name="emails", null=True, default=None)
    template = models.ForeignKey('plataforma.EmailTemplate', db_column="email_template_id", related_name="emails", null=True, default=None)
    contrato = models.ForeignKey('plataforma.Contrato', related_name="emails")

    class Meta:
        db_table = u"plataforma\".\"tb_email"
        verbose_name = u"Email"
        verbose_name_plural = u"Emails"
        get_latest_by = "data_criacao"

    def __unicode__(self):
        return self.template.codigo

    def save(self, *args, **kwargs):
        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id
        super(self.__class__, self).save(*args, **kwargs)

    @classmethod
    def resumo_envio(cls, template_id, data_inicio, data_fim):

        emails = cls.objects.filter(
            data_criacao__gte=data_inicio,
            # isso não é legal... não lembro como resolvi
            # isso antes (Jefferson)
            data_criacao__lte=data_fim + timedelta(days=1),
            template_id=template_id
        )

        emails = utils.contar_objetos(emails)
        for data in utils.range_datas(data_inicio, data_fim):
            if data not in emails.keys():
                emails[data] = 0
        return emails


class EmailTemplate(models.Model):
    """Templates dos emails enviados pelo sistema."""
    EMAIL_ENVIO = [
        ('sistema_contato', u'Plataforma - contato'),
        ('sistema_suporte', u'Plataforma - suporte'),
        ('lojista_contato', u'Lojista - contato'),
        ('lojista_suporte', u'Lojista - suporte'),
        ('lojista_vendas', u'Lojista - vendas'),
        ('cliente', u'Cliente'),
    ]

    id = custom_models.BigAutoField(db_column='email_template_id', primary_key=True)
    ativo = models.BooleanField(db_column='email_template_ativo', default=True)
    codigo = models.CharField(db_column='email_template_codigo', max_length=256)
    descricao = models.TextField(db_column='email_template_descricao', null=True)
    assunto = models.CharField(db_column='email_template_assunto', max_length=512, null=False)
    conteudo_html = models.TextField(db_column='email_template_conteudo_html', null=False)
    conteudo_txt = models.TextField(db_column='email_template_conteudo_txt', null=True)

    de = models.CharField(db_column="email_template_de", max_length=256, null=False, choices=EMAIL_ENVIO)
    # O campo `para` recebe sempre uma lista codificada em JSON com todos
    # os destinatários.
    para = models.CharField(db_column="email_template_para", max_length=256, null=False, choices=EMAIL_ENVIO)
    responder_para = models.CharField(db_column="email_template_responder_para", max_length=256, null=True, choices=EMAIL_ENVIO)

    data_criacao = models.DateTimeField(db_column="email_template_data_criacao", auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column="email_template_data_modificacao", auto_now=True)

    contrato = models.ForeignKey('plataforma.Contrato', related_name="emails_templates", null=True, default=1)

    class Meta:
        db_table = u"plataforma\".\"tb_email_template"
        verbose_name = u"Template de email"
        verbose_name_plural = u"Templates de emails"
        ordering = ['codigo']
        unique_together = (('codigo', 'contrato'),)

    def __unicode__(self):
        return self.codigo


class Contrato(models.Model):
    """Contrato do sistema."""
    TIPO_REVENDA = 'revenda'
    TIPO_WHITELABEL = 'whitelabel'
    TIPOS = [
        (TIPO_REVENDA, u'Revenda'),
        (TIPO_WHITELABEL, u'Whitelabel'),
    ]
    VENCIMENTOS = [(None, u' - Vazio - ')] + [(x, u'Dia %s' % x) for x in range(1, 29)]
    TIPO_PESSOA = [
        ("PF", u"Pessoa Física"),
        ("PJ", u"Pessoa Jurídica")
    ]

    MESES_VALIDADE = [
        (6, u'6'), (12, u'12'), (18, u'18'), (24, u'24'), (32, u'32')
    ]

    id = custom_models.BigAutoField(db_column="contrato_id", primary_key=True)

    ativo = models.BooleanField(u'Ativo?', db_column="contrato_ativo", default=True)

    data_inicio = models.DateField(u'Data de início do contrato', db_column='contrato_data_inicio')
    validade_meses = models.IntegerField(u'Tempora de validade', db_column='contrato_validade_meses', default=12, choices=MESES_VALIDADE)

    colecao_id = models.IntegerField(u'ID da Coleção', db_column='colecao_id', default=1)

    tipo = models.CharField(u'Tipo', db_column="contrato_tipo", max_length=32, choices=TIPOS, default=TIPO_REVENDA)
    dia_vencimento = models.IntegerField(u'Dia do vencimento da fatura', default=None, null=True, choices=VENCIMENTOS, db_column='contrato_dia_vencimento', blank=True)
    cadastro_restrito = models.BooleanField(u'Cadastro restrito pelo administrador?', db_column="contrato_cadastro_restrito", default=False)

    minimo_mensal_valor = models.DecimalField(db_column="contrato_minimo_mensal_valor", max_digits=16, decimal_places=2, null=0.00)
    minimo_mensal_inicio_em_meses = models.IntegerField(db_column="contrato_minimo_mensal_inicio_em_meses", null=True, default=0)

    razao_social = models.CharField(u'Razão social', db_column="contrato_razao_social", max_length=255)
    tipo_pessoa = models.CharField(u'Tipo de pessoa', db_column="contrato_tipo_pessoa", max_length=2, choices=TIPO_PESSOA, null=True, default='PJ')
    cpf_cnpj = models.CharField(u'CNPJ', db_column="contrato_cpf_cnpj", max_length=15, null=True, default=None)
    nome_responsavel = models.CharField(u'Responsável financeiro', db_column="contrato_nome_responsavel", max_length=128, null=True, default=None)
    email_nota_fiscal = models.CharField(u'Email do financeiro', db_column="contrato_email_nota_fiscal", max_length=128, null=True, default=None,
                                         help_text=u'Será usado para envio de fatura e boleto quando existente.')
    telefone_principal = models.CharField(u'Telefone principal', db_column="contrato_telefone_principal", max_length=11, null=True, default=None)
    telefone_celular = models.CharField(u'Telefone celular', db_column="contrato_telefone_celular", max_length=11, null=True, default=None)
    endereco_logradouro = models.CharField(u'Endereço', db_column="contrato_endereco_logradouro", max_length=128, null=True, default=None)
    endereco_numero = models.CharField(u'Número', db_column="contrato_endereco_numero", max_length=32, null=True, default=None)
    endereco_complemento = models.CharField(u'Complemento', db_column="contrato_endereco_complemento", max_length=128, null=True, default=None)
    endereco_bairro = models.CharField(u'Bairro', db_column="contrato_endereco_bairro", max_length=50, null=True, default=None)
    endereco_cep = models.CharField(u'CEP', db_column="contrato_endereco_cep", max_length=8, null=True, default=None, help_text=u'Somente números.')
    endereco_cidade = models.CharField(u'Cidade', db_column="contrato_endereco_cidade", max_length=50, null=True, default=None)
    endereco_cidade_ibge = models.IntegerField(u'Código da cidade no IBGE', db_column="contrato_endereco_cidade_ibge", null=True, default=None, help_text=u'Somente números.')
    endereco_estado = models.CharField(u'Estado', db_column="contrato_endereco_estado", max_length=2, null=True, default=None)
    comentario = models.TextField(u'Outras informações', db_column="contrato_comentario", null=True, default=None, blank=True,
                                  help_text=u'Preencha com alguma informação relevante do contrato ou outros meios de contato como celular, skype, email alternativo, etc...')

    nome = models.CharField(u'Nome da plataforma', db_column="contrato_nome", max_length=255)
    codigo = models.CharField(u'Código interno', db_column="contrato_codigo", max_length=255, help_text=u'Exemplo: plataforma-exemplo', unique=True)
    dominio = models.CharField(u'Domínio', db_column="contrato_dominio", max_length=255)
    url_institucional = models.CharField(u'Site institucional', db_column="contrato_url_institucional", max_length=255)

    url_termo = models.CharField(u'URL Termo de uso', db_column="contrato_url_termo", max_length=255, null=True)
    headtags = models.TextField(u'Headtags', db_column="contrato_headtags", default=None, null=True, blank=True)

    parametros = JSONField(u'Parametros do contrato', db_column="contrato_parametros", null=True, help_text=u'Os parametros informados vão sobreescrever os do contrato principal.')

    certificado_ssl = models.TextField(u'Certificado SSL', db_column="contrato_certificado_ssl", default=None, null=True, blank=True,
                                       help_text=u'Certificado SSL WildCard para *.dominioexemplo.com.br em formato PEM. Sugestão de compra: https://www.namecheap.com/security/ssl-certificates/wildcard.aspx')

    chave = custom_models.UUIDField(db_column="contrato_chave")

    html = models.TextField(u'Código HTML', db_column='contrato_html', default=None, null=True, blank=True)

    class Meta:
        db_table = u"plataforma\".\"tb_contrato"
        verbose_name = u"Contrato"
        verbose_name_plural = u"Contratos"
        ordering = ["id"]

    @property
    def usar_filtros(self):
        """
        É para aparecer as configurações de Filtros avançados?
        """
        return True
        # return self.codigo == 'lojailocal'

    def __unicode__(self):
        return self.nome

    @property
    def url_aplicacao(self):
        return u'app.%s' % self.dominio

    @property
    def email_contato(self):
        return u'nao-responder@%s' % self.dominio

    @property
    def email_suporte(self):
        return u'ouvidoria@%s' % self.dominio

    @property
    def email_nao_responder(self):
        return u'nao-responder@%s' % self.dominio

    @property
    def suporta_cobranca(self):
        return self.tipo_revenda

    @property
    def tipo_revenda(self):
        return self.tipo == self.TIPO_REVENDA

    @property
    def tipo_whitelabel(self):
        return self.tipo == self.TIPO_WHITELABEL

    @property
    def static_url(self):
        if settings.ENVIRONMENT == "local":
            return "{}whitelabel/{}/".format(
                settings.STATIC_URL,
                self.codigo
            )
        else:
            return '{}{}/static/whitelabel/{}/'.format(
                settings.MEDIA_URL,
                settings.ENVIRONMENT,
                self.codigo
            )

    @property
    def email_cobranca(self):
        """Retorna o email de cobrança, tenta usar o email_nota_fiscal,
        caso não exista, usa o campos email da conta, se não existir usa o
        email do usuário, sempre retirando qualquer sublinhado (_) do conteúdo.
        """
        if self.email_nota_fiscal:
            email = self.email_nota_fiscal
        else:
            email = self.email_contato

        def limpar_sublinhados(s):
            return s.replace('_', '-')

        return limpar_sublinhados(email)

    def mostrar_parceiros(self):
        """
        Para verificar se é para mostrar ou não
        o menu de parceiros.
        """
        if self.tipo == self.TIPO_WHITELABEL:
            if self.id == settings.DEFAULT_CONTRATO_ID:
                return True
            else:
                return False
        else:
            return True

    @property
    def configuracao(self):
        if hasattr(self, '_configuracao') and self._configuracao:
            return self._configuracao

        contrato_padrao = Contrato.objects.get(pk=settings.DEFAULT_CONTRATO_ID)
        self._configuracao = contrato_padrao.parametros or {}
        if self._configuracao:
            self._configuracao.update(self.parametros)
        return self._configuracao

    def pagseguro_configuracao(self):
        return self.configuracao.get('pagseguro')

    def credenciais_facebook(self):
        """Retorna uma tupla com o app_id, app_secret do contrato
        caso o mesmo não existe retorna o padrão da Loja Integrada
        """
        fb = self.configuracao.get('facebook')
        return fb['app_id'], fb['app_secret']

        # if self.facebook_app_id and self.facebook_app_secret:
        #     return self.facebook_app_id, self.facebook_app_secret
        # return settings.FACEBOOK_APP_ID, settings.FACEBOOK_APP_SECRET

    def credenciais_pagseguro(self, aplicacao=None):
        """Retorna as credenciais do pagseguro para o contrato
        se for passado uma aplicação tenta retornar as credenciais da mesma
        caso contrario retorna a primeira do contrato

        para manter a retrocompatibilidade, retorno uma tupla
        contendo o app_id, app_secret
        """
        configuracao_pagseguro = self.pagseguro_configuracao()
        return (configuracao_pagseguro.get('app_id'),
                configuracao_pagseguro.get('app_secret'))

    def _parser_endereco(self):
        """Pega o endereço do contrato e tenta trazer o tipo, logradouro e
        número separados.
        """
        if not self.endereco_logradouro:
            return None, None, None

        tipo = self.endereco_logradouro.split()[0].upper()
        tipo = ''.join([x for x in tipo if x in string.ascii_uppercase])
        if len(tipo) > 4 or len(tipo) <= 1:
            if tipo in LOGRADOUROS:
                tipo = LOGRADOUROS[tipo]
            else:
                tipo = u'RUA'

        if tipo not in LOGRADOUROS.values():
            tipo = u'RUA'

        logradouro = self.endereco_logradouro
        if ',' in logradouro:
            numero = logradouro.split(',')[-1].strip()
            logradouro = u' '.join(logradouro.split(',')[:-1])
        else:
            numero = logradouro.split()[-1].strip()
            logradouro = u' '.join(logradouro.split()[:-1])

        if not re.search('\d', numero):
            numero = u'S/N'

        return tipo, logradouro[:50], numero[:10]


class Index(models.Model):
    id = custom_models.BigAutoField(db_column='index_id', primary_key=True)
    status = models.IntegerField(db_column='index_status', default=1, null=False)
    data_atualizacao = models.DateTimeField(db_column='index_data_atualizacao', auto_now=True)
    mensagem_erro = models.TextField(db_column='index_mensagem_erro')

    produto = models.ForeignKey('catalogo.Produto', db_column='produto_id')
    categoria = models.ForeignKey('catalogo.Categoria', db_column='categoria_id')
    conta = models.ForeignKey('plataforma.Conta', db_column='conta_id')
    plano = models.ForeignKey('faturamento.Plano', db_column='plano_id')
    categoria_global = models.ForeignKey('catalogo.CategoriaGlobal', db_column='cateogria_global_id')

    class Meta:
        db_table = u"plataforma\".\"tb_index"
        verbose_name = u"Indice"
        verbose_name_plural = u"Indices"
        ordering = ["id"]


class ProductImportHistory(models.Model):
    """
    Classe ProductImportHistory.

    Para guardar o histórico de importações da Conta,
    através do arquivo excel modelo.
    """
    id = models.AutoField(
        db_column="historico_importacao_id",
        primary_key=True
    )
    account = models.ForeignKey(
        Conta,
        verbose_name='Conta',
        db_column="conta_id",
        help_text=u'Número da Loja'
    )

    contract = models.ForeignKey(
        Contrato,
        verbose_name='Contrato',
        db_column='contrato_id',
        help_text=u'Número do Contrato'
    )

    date_created = models.DateTimeField(
        db_column="historico_importacao_data_criacao",
        verbose_name=u'Data da Criação',
        auto_now_add=True,
        auto_now=False,
        help_text=u'Data da importação do arquivo'
    )

    date_start = models.DateTimeField(
        db_column="historico_importacao_data_inicio",
        verbose_name=u'Data de Início',
        help_text=u'Data do início da importação do arquivo',
        null=True,
        blank=True
    )

    date_end = models.DateTimeField(
        db_column="historico_importacao_data_final",
        verbose_name=u'Data da Finalização',
        help_text=u'Data da finalização da importação do arquivo',
        null=True,
        blank=True
    )

    status = models.TextField(
        db_column='historico_importacao_status',
        verbose_name=u'Status da Importação',
        choices=IMPORT_STATUS,
        default=IMPORT_STATUS_RECEIVED,
        help_text=u'O status da importação do arquivo. '
                  u'"Falha" significa que nenhum Produto foi importado. '
                  u'"Importação Parcial" significa que nem todos os produtos'
                  u'do arquivo foram importados. "Sucesso" significa '
                  u'que todos os produtos no arquivo foram importados.'
    )
    log = models.TextField(
        db_column='historico_importacao_mensagem',
        verbose_name=u'Log da importação',
        null=True,
        blank=True,
        help_text=u'Mensagem sobre o status da importação,'
    )
    error_file = models.TextField(
        db_column='historico_importacao_arquivo_erro',
        verbose_name=u'Arquivo com Erros',
        null=True,
        blank=True,
        help_text=u'Arquivo Excel contendo as linhas que não '
                  u'foram importadas devido a erros.'
    )
    original_file = models.TextField(
        db_column='historico_importacao_arquivo_original',
        verbose_name=u'Arquivo Original',
        null=True,
        blank=True,
        help_text=u'Arquivo Excel enviado pela Loja.'
    )
    total_quantity = models.IntegerField(
        db_column='historico_importacao_quantidade_total',
        verbose_name=u'Linhas Excel',
        help_text=u'Total de Linhas no arquivo Excel enviado',
        null=True,
        blank=True,
    )
    success_quantity = models.IntegerField(
        db_column='historico_importacao_quantidade_sucesso',
        verbose_name=u'Linhas importadas',
        help_text=u'Linhas do Excel importadas com sucesso',
        null=True,
        blank=True,
    )
    error_quantity = models.IntegerField(
        db_column='historico_importacao_quantidade_erro',
        verbose_name=u'Linhas com Erro',
        help_text=u'Linhas do Excel com erros',
        null=True,
        blank=True,
    )

    def __unicode__(self):
        return "{}: {}".format(
            self.date_created.strftime("%c"),
            self.get_status_display()
        )

    class Meta:
        # app_label = 'repositories_plataforma'
        db_table = u"plataforma\".\"tb_importacao_historico"
        verbose_name = u'Histórico das Importação',
        verbose_name_plural = u'Histórico das Importações',
        ordering = ['date_created']
        unique_together = ['account', 'contract', 'original_file']


class ProductImportRelation(models.Model):

    id = models.AutoField(
        db_column="produto_importacao_id",
        primary_key=True
    )
    account = models.ForeignKey(
        Conta,
        verbose_name='Conta',
        db_column="conta_id",
        help_text=u'Número da Loja'
    )

    importacao = models.ForeignKey(
        ProductImportHistory,
        db_column='historico_importacao_id',
        help_text=u'Importação que gerou/atualizou o Produto'
    )

    contract = models.ForeignKey(
        Contrato,
        verbose_name='Contrato',
        db_column='contrato_id',
        help_text=u'Número do Contrato'
    )

    product = models.ForeignKey(
        'catalogo.Produto',
        verbose_name='Produto',
        db_column='produto_id',
        help_text=u'Produto'
    )

    status = models.TextField(
        db_column='produto_importacao_status',
        verbose_name=u'Resultado da Importação',
        choices=LOG_IMPORT,
        default=LOG_IMPORT_CREATED,
    )

    class Meta:
        # app_label = 'repositories_plataforma'
        db_table = u"plataforma\".\"tb_importacao_produto"
        verbose_name = u"Relação de Produto por Importacao"
        verbose_name_plural = u"Relação de Produtos por Importacao"

    def __unicode__(self):
        return "{}: {} ({})".format(
            self.importacao,
            self.product,
            self.status
        )


class Feature(models.Model):
    """Defines a state of a feature implemented in the platform."""

    STATUS_CHOICES = [
        ('disabled', 'Disabled'),
        ('local', 'Local'),
        ('development', 'Development'),
        ('staging', 'Staging'),
        ('production', 'Production'),
        ('beta', 'Beta'),
        ('PRO0', 'Plano Gratuito'),
        ('PRO1', 'Plano Pro 1'),
        ('PRO2', 'Plano Pro 2'),
        ('PRO3', 'Plano Pro 3'),
        ('PRO4', 'Plano Pro 4')
    ]

    STATUS_SORTED = [
        'local', 'development', 'staging', 'beta', 'production',
        'PRO0', 'PRO1', 'PRO2', 'PRO3', 'PRO4'
    ]

    id = models.AutoField(db_column='feature_id', primary_key=True)
    name = models.TextField(db_column='feature_name')
    code = models.TextField(db_column='feature_code')
    status = models.TextField(db_column='feature_status',
                              choices=STATUS_CHOICES)

    class Meta:
        db_table = u"plataforma\".\"tb_feature"
        verbose_name = u"Feature"
        verbose_name_plural = u"Features"

    @classmethod
    def is_enabled(cls, feature, store, plan=None):
        """Returns True if a feature is enabled.

        If the feature is in beta it is only enabled for beta testers.
        """
        feature = cls.objects.get(code=feature)

        if feature.status == 'disabled':
            return False

        # The beta testers has all beta features enabled.
        if feature.status == 'beta' and store.beta_tester:
            return True

        feature_index = cls.STATUS_SORTED.index(feature.status)

        if plan:
            environment_index = cls.STATUS_SORTED.index(
                "PRO{}".format(plan-1))

            # O valor do Lojista deve ser maior que a Feature
            if environment_index >= feature_index:
                return True
        else:        
            environment_index = cls.STATUS_SORTED.index(settings.ENVIRONMENT)
            
            # O valor da Feature deve ser maior que o Environment
            if feature_index >= environment_index:
                return True

        return False
