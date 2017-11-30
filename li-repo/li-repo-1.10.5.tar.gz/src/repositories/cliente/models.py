# -*- coding: utf-8 -*-
import datetime
import hashlib
import random
import re
import logging

from django.core.exceptions import MultipleObjectsReturned, ValidationError
from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save
from django.dispatch import receiver
from repositories import custom_models
from repositories.libs import utils

logger = logging.getLogger(__name__)


def hash(valor, tipo='md5'):
    return getattr(hashlib, tipo)(valor).hexdigest()


class ClienteGrupo(models.Model):
    """Grupo de clientes."""
    id = custom_models.BigAutoField(db_column="cliente_grupo_id", primary_key=True)
    nome = models.CharField(db_column="cliente_grupo_nome", max_length=128)
    padrao = models.BooleanField(db_column="cliente_grupo_padrao", default=False)

    conta = models.ForeignKey("plataforma.Conta", related_name="grupos", on_delete=models.CASCADE, null=True, blank=True)
    contrato = models.ForeignKey("plataforma.Contrato", related_name="grupos")

    class Meta:
        db_table = u"cliente\".\"tb_cliente_grupo"
        verbose_name = u"Grupo de cliente"
        verbose_name_plural = u"Grupo de clientes"
        ordering = ["conta", "nome"]
        unique_together = (("conta", "nome"),)

    def __unicode__(self):
        return self.nome

    def save(self, *args, **kwargs):
        if self.padrao:
            c = ClienteGrupo.objects.filter(conta=self.conta, padrao=True)
            if c:
                c.update(padrao=False)

        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id
        # se nao tiver conta(grupo padrao por exemplo)
        # usa o contrato 1 da Loja Integrada
        if not self.conta and not self.contrato_id:
            self.contrato_id = 1

        super(ClienteGrupo, self).save(*args, **kwargs)

    def criar_endereco_vazio(self):
        return ClienteEndereco.criar_endereco_vazio(self.id)

    @classmethod
    def grupo_padrao(cls):
        return ClienteGrupo.objects.get(nome='Padrão', conta_id__isnull=True)


class Cliente(models.Model):
    """Clientes da loja virtual."""

    CLIENTE_SITUACAO_APROVADO = 'aprovado'
    CLIENTE_SITUACAO_NEGADO = 'negado'
    CLIENTE_SITUACAO_PENDENTE = 'pendente'

    id = custom_models.BigAutoField(db_column="cliente_id", primary_key=True)
    email = models.EmailField(db_column="cliente_email", max_length=255)
    senha = models.CharField(db_column="cliente_senha", max_length=64)
    nome = models.CharField(db_column="cliente_nome", max_length=255, null=True)
    sexo = models.CharField(db_column="cliente_sexo", max_length=1, null=True)
    telefone_principal = models.CharField(db_column="cliente_telefone_principal", max_length=11, null=True)
    telefone_comercial = models.CharField(db_column="cliente_telefone_comercial", max_length=11, null=True)
    telefone_celular = models.CharField(db_column="cliente_telefone_celular", max_length=11, null=True)
    newsletter = models.BooleanField(db_column="cliente_newsletter", default=True)
    data_nascimento = models.DateField(db_column="cliente_data_nascimento", null=True)
    data_criacao = models.DateTimeField(db_column="cliente_data_criacao", auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column="cliente_data_modificacao", auto_now=True)
    facebook_id = models.CharField(db_column='cliente_facebook_usuario_id', max_length=64, default=None, null=True)
    teste = models.BooleanField(db_column="cliente_teste", default=False, null=False)
    grupo = models.ForeignKey('cliente.ClienteGrupo', db_column="cliente_grupo_id", related_name="clientes")
    conta = models.ForeignKey("plataforma.Conta", related_name="clientes", on_delete=models.CASCADE)
    contrato = models.ForeignKey("plataforma.Contrato", related_name="clientes")
    situacao = models.CharField(db_column='cliente_situacao', max_length=32, default=CLIENTE_SITUACAO_PENDENTE, null=False)
    desativado = models.BooleanField(db_column='cliente_desativado', default=False)

    class Meta:
        # app_label = "cliente"
        db_table = u"cliente\".\"tb_cliente"
        verbose_name = u"Cliente"
        verbose_name_plural = u"Clientes"
        ordering = ["email"]
        unique_together = (("conta", "email"),)
        get_latest_by = 'id'

    def __unicode__(self):
        return self.email

    def _gerar_senha(self):
        letras = ['qpwoeiruruty1029384756alskdjfhgzmxncbv']
        senha = ''.join([random.choice(letras) for x in range(10)])
        return senha

    def autorizado(self):
        """
        Retorna se o cliente esta ou não autorizado a fazer login
        """
        if self.conta.gerenciar_cliente:
            return self.situacao == self.CLIENTE_SITUACAO_APROVADO
        return True

    def logar(self, codigo, descricao, **kwargs):
        return None
        # return NoSQLLog(codigo=codigo, conta_id=self.conta_id,
        #                 descricao=descricao, **kwargs).save()

    def alterar_grupo(self, grupo):
        self.grupo = grupo
        self.save()

        # msg = u'Alterando grupo do usuário "%s" (id=%s) para "%s" (id=%s).' % (
        #     self.nome, self.id, self.grupo.nome, self.grupo.id)
        # self.logar('LPN08002', msg)

    def chave_alteracao(self):
        data = self.data_modificacao or self.data_criacao
        data = data.strftime('%Y-%m-%d %H:%M:%S')
        salt = '%s.:.%s.:.%s.:.%s' % (self.id, self.email, self.senha, data)
        return hash(salt)

    def enviar_email_aprovado(self,request):
        utils.enviar_email(
            request,
            template_file='cliente/solicitacao_aprovada',
            cliente_id=self.id,
            salva_evidencia=False)

    def _marcar_como_principal(self, endereco):
        endereco.principal = True
        endereco.save()
        self.enderecos.exclude(pk=endereco.id) \
            .update(principal=False)

    @property
    def primeiro_nome(self):
        if self.nome:
            return self.nome.split()[0]

    @property
    def endereco(self):
        if not hasattr(self, '_endereco'):
            try:
                self._endereco = self.enderecos.get(principal=True)
            except (MultipleObjectsReturned, ClienteEndereco.DoesNotExist):
                # Caso tenha mais de um endereço principal ou o endereço
                # principal não existe, escolhe um e marca os outros como
                # principal = False.
                try:
                    endereco_principal = self.enderecos.all()[0]
                except IndexError:
                    self._endereco = None
                else:
                    self._marcar_como_principal(endereco_principal)
                    self._endereco = endereco_principal

        return self._endereco

    @property
    def eh_primeira_compra_na_loja(self):
        return len(self.pedidos.all()[:0]) > 0

    @property
    def eh_confiavel(self):
        return False

    @property
    def rg(self):
        if self.endereco():
            return self.endereco().rg

    @property
    def cpf(self):
        if self.endereco():
            return self.endereco().cpf

    def aniversario(self):
        """Retorna a data de aniversário do cliente"""
        if not self.data_nascimento:
            return None
        hoje = datetime.date.today()
        try:
            aniversario = self.data_nascimento.replace(year=hoje.year)
        except ValueError:
            bisexto = True
            aniversario = self.data_nascimento.replace(day=self.data_nascimento.day - 1)
            aniversario = aniversario.replace(year=hoje.year)
        else:
            bisexto = False
        if aniversario < hoje:
            try:
                aniversario = aniversario.replace(year=hoje.year + 1)
            except ValueError:
                # O aniversário do cliente é no dia 29/02 e o ano
                # adicionado não é bisexto.
                aniversario = aniversario.replace(year=hoje.year + 1,
                                                  day=aniversario.day - 1)
        return aniversario

    def aniversario_hoje(self):
        """Verifica se o aniversário é hoje
           se for retorna True """
        return datetime.date.today() == self.aniversario()

    def save(self, *args, **kwargs):
        """ se não existe a senha, cria e faz o hash e salva """
        if not self.senha:
            self.senha = hashlib.md5(self._gerar_senha()).hexdigest()
        elif len(self.senha) != 32:
            self.senha = hashlib.md5(self.senha.encode('utf-8')).hexdigest()
        if isinstance(self.data_nascimento, basestring):
            data = re.match(
                '(?P<dia>[0-9]{2})/(?P<mes>[0-9]{2})/(?P<ano>[0-9]{4})',
                self.data_nascimento)
            if data:
                self.data_nascimento = '%s-%s-%s' % (
                    data.group('ano'), data.group('dia'), data.group('mes'))
        if not self.grupo_id:
            try:
                self.grupo = ClienteGrupo.objects.get(
                    padrao=True, conta_id=self.conta_id)
            except ClienteGrupo.DoesNotExist:
                self.grupo = ClienteGrupo.grupo_padrao()

        if self.sexo and len(self.sexo) > 1:
            self.sexo = self.sexo[0].lower()

        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id

        super(self.__class__, self).save(*args, **kwargs)

    @property
    def md5_data_criacao(self):
        return hash(self.data_criacao.strftime('%Y-%m-%d %H:%M:%S'))

    @models.permalink
    def get_newsletter_unsubscribe_url(self):
        kwargs = {'cliente_id': self.id, 'chave': self.md5_data_criacao}
        return ('loja_newsletter_unsubscribe', (), kwargs)

    def unsubscribe_newsletter(self):
        from repositories.marketing.models import NewsletterAssinatura

        self.newsletter = False
        self.save()

        NewsletterAssinatura.objects.filter(
            Q(cliente=self) | Q(email=self.email),
            conta=self.conta
        ).delete()

        return True


class ClienteFavorito(models.Model):

    id = custom_models.BigAutoField(db_column="cliente_favorito_id", primary_key=True)
    cliente = models.ForeignKey('cliente.Cliente', db_column="cliente_id")
    codigo = models.CharField(db_column="cliente_favorito_codigo", null=True, blank=True, max_length=32)
    data_criacao = models.DateTimeField(db_column="cliente_favorito_data_criacao", auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column="cliente_favorito_data_modificacao", auto_now=True)

    produtos = models.ManyToManyField('catalogo.Produto', db_column="produto_id", related_name='favoritos', through='cliente.ClienteFavoritoProduto')
    conta = models.ForeignKey('plataforma.Conta', related_name='favoritos')
    contrato = models.ForeignKey("plataforma.Contrato", related_name="favoritos")

    class Meta:
        db_table = u"cliente\".\"tb_cliente_favorito"
        verbose_name = u"Favorito do cliente"
        verbose_name_plural = u"Favoritos dos clientes"
        ordering = ['data_criacao']

    def id_produtos(self):
        return [x.id for x in self.produtos.all()]


    def gerar_codigo(self):
        return hash('%s..%s..%s' % (
            self.cliente_id,
            self.conta_id,
            datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), tipo='sha1')[:10]

    def save(self, *args, **kwargs):
        if not self.codigo:
            self.codigo = self.gerar_codigo()
        if self.conta_id and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id
        super(ClienteFavorito, self).save(*args, **kwargs)


class ClienteFavoritoProduto(models.Model):

    id = custom_models.BigAutoField(db_column="cliente_favorito_produto_id", primary_key=True)
    produto = models.ForeignKey('catalogo.Produto', db_column="produto_id", related_name='produtos_favoritos')
    favorito = models.ForeignKey('cliente.ClienteFavorito', db_column="cliente_favorito_id", related_name='produtos_favoritos')

    conta = models.ForeignKey('plataforma.Conta', related_name='produtos_favoritos')
    contrato = models.ForeignKey("plataforma.Contrato", related_name="produtos_favoritos")

    class Meta:
        db_table = u"cliente\".\"tb_cliente_favorito_produto"
        verbose_name = u"Produto favorito"
        verbose_name_plural = u"Produtos favoritos"

    def save(self, *args, **kwargs):
        if self.conta_id and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id
        super(ClienteFavoritoProduto, self).save(*args, **kwargs)


class ClienteEndereco(models.Model):
    """Endereços dos clientes."""
    ENDERECO_TIPOS = [
        ("PF", u"Pessoa Física"),
        ("PJ", u"Pessoa Jurídica"),
        ("IN", u"Internacional"),
    ]

    id = custom_models.BigAutoField(db_column="cliente_endereco_id", primary_key=True)
    tipo = models.CharField(db_column="cliente_endereco_tipo", max_length=64, choices=ENDERECO_TIPOS, null=True, default=None)
    cpf = models.CharField(db_column="cliente_endereco_cpf", max_length=11, null=True, default=None)
    rg = models.CharField(db_column="cliente_endereco_rg", max_length=20, null=True, default=None)
    cnpj = models.CharField(db_column="cliente_endereco_cnpj", max_length=14, null=True, default=None)
    razao_social = models.CharField(db_column="cliente_endereco_razao_social", max_length=255, null=True, default=None)
    ie = models.CharField(db_column="cliente_endereco_ie", max_length=20, null=True, default=None)
    nome = models.CharField(db_column="cliente_endereco_nome", max_length=255)
    endereco = models.CharField(db_column="cliente_endereco_endereco", max_length=255)
    numero = models.CharField(db_column="cliente_endereco_numero", max_length=10)
    complemento = models.CharField(db_column="cliente_endereco_complemento", max_length=255, null=True)
    referencia = models.CharField(db_column="cliente_endereco_referencia", max_length=255, null=True)
    bairro = models.CharField(db_column="cliente_endereco_bairro", max_length=128)
    cidade = models.CharField(db_column="cliente_endereco_cidade", max_length=128)
    estado = models.CharField(db_column="cliente_endereco_estado", max_length=2)
    cep = models.CharField(db_column="cliente_endereco_cep", max_length=8)
    pais_extenso = models.CharField(db_column="cliente_endereco_pais", max_length=128, null=True)
    principal = models.BooleanField(db_column="cliente_endereco_principal", default=False)

    pais = models.ForeignKey("domain.Pais", related_name="enderecos")
    cliente = models.ForeignKey('cliente.Cliente', related_name="enderecos", on_delete=models.CASCADE)
    conta = models.ForeignKey("plataforma.Conta", related_name="enderecos")
    contrato = models.ForeignKey("plataforma.Contrato", related_name="enderecos")

    class Meta:
        db_table = u"cliente\".\"tb_cliente_endereco"
        verbose_name = u"Endereço do cliente"
        verbose_name_plural = u"Endereços do cliente"
        ordering = ["nome"]
        unique_together = (
            "tipo", "cpf", "rg", "cnpj", "razao_social", "ie", "nome",
            "endereco", "numero", "complemento", "bairro", "cidade",
            "estado", "cep", "pais", "cliente", "conta")
        get_latest_by = "id"

    def __unicode__(self):
        return self.nome

    @property
    def primeiro_nome(self):
        if self.nome:
            return self.nome.split()[0]

    @classmethod
    def criar_endereco_vazio(cls, cliente):
        endereco = cls()
        endereco.tipo = 'PF'
        endereco.cpf = '00000000000'
        endereco.rg = ''
        endereco.cnpj = ''
        endereco.razao_social = ''
        endereco.ie = ''
        endereco.nome = ''
        endereco.endereco = ''
        endereco.numero = ''
        endereco.complemento = ''
        endereco.referencia = ''
        endereco.bairro = ''
        endereco.cidade = ''
        endereco.estado = 'XX'
        endereco.cep = '00000000'
        endereco.pais_id = 'BRA'
        endereco.principal = True
        endereco.cliente_id = cliente.id
        endereco.conta_id = cliente.conta_id

        endereco.save()
        return endereco

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


    def save(self, *args, **kwargs):
        # Caso seja o único endereço, ele sempre será o principal.
        tem_enderecos = self.cliente.enderecos.exclude(pk=self.id).exists()
        if self.cliente_id and not tem_enderecos:
            self.principal = True

        if not self.pais_id:
            self.pais_id = 'BRA'

        # Caso o endereço seja marcado como principal os outros terão que
        # ser atualizados. Esta verificação de self.principal deve ficar
        # abaixo da verificação do primeiro endereço.
        if self.principal:
            # Atualiza os outros endereços para não-principal.
            ClienteEndereco.objects.filter(
                conta=self.conta, cliente=self.cliente
            ).exclude(
                pk=self.id
            ).update(
                principal=False
            )

            if self.tipo and self.tipo == 'PF' and not self.cpf:
                msg = u'Quando o tipo é Pessoa Física, deve ter CPF.'
                raise ValidationError(msg)
            if self.tipo and self.tipo == 'PJ' and (not self.cnpj or not self.razao_social):
                msg = u'Quando o tipo é Pessoa Jurídica, deve ter CNPJ e Razão Social.'
                raise ValidationError(msg)

        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id

        super(ClienteEndereco, self).save(*args, **kwargs)

    @classmethod
    def extrair_numero_endereco(cls, logradouro):
        if ',' in logradouro:
            numero = logradouro.split(',')[-1].strip()
            logradouro = u' '.join(logradouro.split(',')[:-1])
        else:
            numero = logradouro.split()[-1].strip()
            logradouro = u' '.join(logradouro.split()[:-1])

        if not re.search('\d', numero):
            numero = u'S/N'
        return numero[:10]

    @property
    def cnpj_valido(self):

        if self.tipo != 'PJ':
            return True

        c = [int(x) for x in self.cnpj[:12]]
        p = [5,4,3,2,9,8,7,6,5,4,3,2]

        while len(c) < 14:
            t = sum([x*y for (x,y) in zip(c,p)]) % 11
            c.append((0,11-t)[t>1])
            p.insert(0,6)
        return bool(''.join([str(x) for x in c]) == self.cnpj)


    @property
    def cpf_valido(self):

        if self.tipo != 'PF':
            return True
        if len(self.cpf) != 11:
            return False
        c = [int(x) for x in self.cpf[:9]]
        p = [10, 9, 8, 7, 6, 5, 4, 3, 2]


        while len(c) < 11:
            t = sum([x * y for (x, y) in zip(c, p)]) % 11
            c.append((0, 11 - t)[t >= 2])
            p.insert(0, 11)

        return bool(''.join([str(x) for x in c]) == self.cpf)


@receiver(pre_save, sender=ClienteEndereco)
def endereco_pre_save(sender, instance, raw, *args, **kwargs):
    if instance.id and instance.tipo:
        if instance.tipo == 'PF':
            instance.cnpj = instance.razao_social = instance.ie = None
        elif instance.tipo == 'PJ':
            instance.cpf = instance.rg = None

    # Se o endereço for o primeiro a ser criado ou é o único do cliente,
    # sempre será principal.
    if instance.cliente_id:
        total_enderecos = instance.cliente.enderecos.exclude(pk=instance.id).count()
        if (instance.id and total_enderecos == 1) or \
                (not instance.id and not total_enderecos):
            instance.principal = True

