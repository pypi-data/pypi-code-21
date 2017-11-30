# -*- coding: utf-8 -*-
from django.db import models
from jsonfield import JSONField
from repositories import custom_models


FORMAS_DE_PAGAMENTO = [
    ('BOLETO', 'Boleto'),
    ('CARTAO DE CREDITOC', 'Cartão de Crédito')
]

FORMA_PAGAMENTO_CHOICES = [
    ('BOLETO', u'Boleto'),
    ('CARTAO DE CREDITO', u'Cartão de crédito'),
    ('WHITELABEL', u'Whitelabel'),
]

FATURA_SITUACAO_CHOICES = [
    ('PAGA', u'Paga'),
    ('AGUARDANDO PAGAMENTO', u'Aguardando pagamento'),
    ('CANCELADA', u'Cancelada'),
    ('ESTORNADA', u'Estornada'),
    ('CHARGEBACK', u'Chargeback'),
    ('ISENTA', u'Isenta'),
    ('WHITELABEL', u'Whitelabel'),
    ('PROCESSANDO', u'Processando')

]

TIPO_PESSOA_CHOICES = [
    ('PF', u'Pessoa Física'),
    ('PJ', u'Pessoa Jurídica'),
]

PLANO_ACAO_CHOICES = [
    ('MANTEVE', u'Manteve'),
    ('UPGRADE', u'Upgrade'),
    ('DOWNGRADE', u'Downgrade'),
    ('PRIMEIRO', u'rimeiro'),
]


class DadosCobranca(models.Model):
    id = custom_models.BigAutoField(db_column="dados_cobranca_id", primary_key=True)
    forma_pagamento = models.TextField(db_column="dados_cobranca_forma_pagamento", choices=FORMA_PAGAMENTO_CHOICES)
    tipo_pessoa = models.TextField(db_column="dados_cobranca_tipo_pessoa", choices=TIPO_PESSOA_CHOICES)
    email_nfe = models.TextField(db_column="dados_cobranca_email_nfe")
    nome_responsavel = models.TextField(db_column="dados_cobranca_nome_responsavel")
    cpf = models.TextField(db_column="dados_cobranca_cpf", null=True)
    razao_social = models.TextField(db_column="dados_cobranca_razao_social", null=True)
    cnpj = models.TextField(db_column="dados_cobranca_cnpj", null=True)
    telefone_principal = models.TextField(db_column="dados_cobranca_telefone_principal", null=True)
    telefone_alternativo = models.TextField(db_column="dados_cobranca_telefone_alternativo")
    endereco_logradouro = models.TextField(db_column="dados_cobranca_endereco_logradouro")
    endereco_numero = models.TextField(db_column="dados_cobranca_endereco_numero")
    endereco_complemento = models.TextField(db_column="dados_cobranca_endereco_complemento")
    endereco_bairro = models.TextField(db_column="dados_cobranca_endereco_bairro")
    endereco_cidade_ibge = models.TextField(db_column="dados_cobranca_endereco_cidade_ibge")
    endereco_estado = models.TextField(db_column="dados_cobranca_endereco_estado")
    endereco_cep = models.TextField(db_column="dados_cobranca_endereco_cep")

    data_criacao = models.DateTimeField(db_column='dados_cobranca_data_criacao', auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column='dados_cobranca_data_modificacao', auto_now=True)

    conta = models.OneToOneField("plataforma.Conta", db_column="conta_id")

    class Meta:
        db_table = u"faturamento\".\"tb_dados_cobranca"


class DadosCobrancaCartao(models.Model):
    """Guarda os dados do cartão de crédito da conta.

    Os dados são guardados criptografados e só o executor da tarefas de
    pagamento tem permissão para decriptografar os dados.
    """
    id = custom_models.BigAutoField(db_column="dados_cobranca_cartao_id", primary_key=True)
    nome_portador = models.TextField(db_column="dados_cobranca_cartao_nome_portador",)
    numero = models.TextField(db_column="dados_cobranca_cartao_numero", max_length=64, null=False)
    cvv = models.TextField(db_column="dados_cobranca_cartao_cvv", max_length=64, null=False)
    expiracao_mes = models.TextField(db_column="dados_cobranca_cartao_expiracao_mes", max_length=255, null=False)
    expiracao_ano = models.TextField(db_column="dados_cobranca_cartao_expiracao_ano", max_length=255, null=False)
    ultimos_numeros = models.TextField(db_column="dados_cobranca_cartao_ultimos_numeros", max_length=255, null=False)
    salt = models.TextField(db_column="dados_cobranca_cartao_salt", max_length=23, null=False)

    data_criacao = models.DateTimeField(db_column="dados_cobranca_cartao_data_criacao", auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column="dados_cobranca_cartao_data_modificacao", auto_now=True)

    conta = models.OneToOneField("plataforma.Conta", db_column="conta_id")
    dados_cobranca = models.ForeignKey(DadosCobranca, db_column="dados_cobranca_id")

    class Meta:
        db_table = u"faturamento\".\"tb_dados_cobranca_cartao"


class Fatura(models.Model):
    id = custom_models.BigAutoField(db_column="fatura_id", primary_key=True)
    situacao = models.TextField(db_column="fatura_situacao", choices=FATURA_SITUACAO_CHOICES)
    valor_cheio = models.DecimalField(db_column="fatura_valor_cheio", decimal_places=2, max_digits=12)
    valor_impostos = models.DecimalField(db_column="fatura_valor_impostos", decimal_places=2, max_digits=12)
    valor_impostos_json = JSONField(db_column='fatura_valor_impostos_json', null=True, default=None)
    valor_cobrado = models.DecimalField(db_column="fatura_valor_cobrado", decimal_places=2, max_digits=12)
    valor_pago = models.DecimalField(db_column="fatura_valor_pago", decimal_places=2, max_digits=12, default=0)
    dados_forma_pagamento = models.TextField(db_column="fatura_dados_forma_pagamento", choices=FORMA_PAGAMENTO_CHOICES)
    dados_tipo_pessoa = models.TextField(db_column="fatura_dados_tipo_pessoa", choices=TIPO_PESSOA_CHOICES)
    dados_email_nfe = models.TextField(db_column="fatura_dados_email_nfe")
    dados_nome_responsavel = models.TextField(db_column="fatura_dados_nome_responsavel")
    dados_cpf = models.TextField(db_column="fatura_dados_cpf", default=None)
    dados_razao_social = models.TextField(db_column="fatura_dados_razao_social", default=None)
    dados_cnpj = models.TextField(db_column="fatura_dados_cnpj", default=None)
    dados_telefone_principal = models.TextField(db_column="fatura_dados_telefone_principal", default=None)
    dados_telefone_alternativo = models.TextField(db_column="fatura_dados_telefone_alternativo", default=None)
    dados_endereco_logradouro = models.TextField(db_column="fatura_dados_endereco_logradouro")
    dados_endereco_numero = models.TextField(db_column="fatura_dados_endereco_numero")
    dados_endereco_complemento = models.TextField(db_column="fatura_dados_endereco_complemento", default=None)
    dados_endereco_bairro = models.TextField(db_column="fatura_dados_endereco_bairro")
    dados_endereco_cidade_ibge = models.TextField(db_column="fatura_dados_endereco_cidade_ibge")
    dados_endereco_estado = models.TextField(db_column="fatura_dados_endereco_estado")
    dados_endereco_cep = models.TextField(db_column="fatura_dados_endereco_cep")
    data_vencimento = models.DateField(db_column="fatura_data_vencimento")
    data_tolerancia = models.DateField(db_column="fatura_data_tolerancia")
    data_pagamento = models.DateField(db_column="fatura_data_pagamento", default=None, db_index=True)
    boleto_codigo_de_barras = models.TextField(db_column="fatura_boleto_codigo_de_barras", default=None)
    boleto_url = models.TextField(db_column="fatura_boleto_url", default=None)
    cartao_de_credito_cv = models.TextField(db_column="fatura_cartao_de_credito_cv", default=None)
    cartao_de_credito_numero = models.TextField(db_column="fatura_cartao_de_credito_numero", default=None)
    cartao_de_credito_msgret = models.TextField(db_column="fatura_cartao_de_credito_msgret", default=None)
    cartao_de_credito_codret = models.TextField(db_column="fatura_cartao_de_credito_codret", default=None)
    cartao_de_credito_data_autorizacao = models.DateField(db_column="fatura_cartao_de_credito_data_autorizacao", default=None)
    controle_lancamento_numero = models.TextField(db_column="fatura_controle_lancamento_numero", default=None, db_index=True)
    controle_lancamento_quitado = models.BooleanField(db_column="fatura_controle_lancamento_quitado", default=False)
    controle_nota_fiscal = models.IntegerField(db_column="fatura_controle_nota_fiscal", default=None)
    json = JSONField(db_column='fatura_json', null=True, default=None)
    observacao = models.TextField(db_column="fatura_observacao")
    data_criacao = models.DateTimeField(db_column="fatura_data_criacao", auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column="fatura_data_modificacao", auto_now=True)

    conta = models.ForeignKey("plataforma.Conta", db_column="conta_id")
    contrato = models.ForeignKey("plataforma.Contrato", db_column="contrato_id")
    processando = models.BooleanField(db_column='processando_cobranca', default=False)

    class Meta:
        db_table = u"faturamento\".\"tb_fatura"


class FaturaItem(models.Model):
    id = custom_models.BigAutoField(db_column="fatura_item_id", primary_key=True)
    valor_cheio = models.DecimalField(db_column="fatura_item_valor_cheio", decimal_places=2, max_digits=12)
    valor_cobrado = models.DecimalField(db_column="fatura_item_valor_cobrado", decimal_places=2, max_digits=12)
    referencia_tabela = models.TextField(db_column="fatura_item_referencia_tabela", null=True, default=None)
    referencia_campo = models.TextField(db_column="fatura_item_referencia_campo", null=True, default=None)
    referencia_id = models.IntegerField(db_column="fatura_item_referencia_id", null=True, default=None)
    referencia_situacao_principal = models.TextField(db_column="fatura_item_referencia_situacao_principal", null=True, default=None)
    referencia_situacao_complementar = models.TextField(db_column="fatura_item_referencia_situacao_complementar", null=True, default=None)
    json = JSONField(db_column='fatura_item_json', null=True, default=None)

    conta = models.ForeignKey("plataforma.Conta", db_column="conta_id")
    fatura = models.ForeignKey(Fatura, db_column="fatura_id", related_name='itens')

    class Meta:
        db_table = u"faturamento\".\"tb_fatura_item"


class Colecao(models.Model):
    id = custom_models.BigAutoField(db_column="colecao_id", primary_key=True)
    nome = models.TextField(db_column="colecao_nome")
    data_criacao = models.DateTimeField(db_column="colecao_data_criacao", auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column="colecao_data_modificacao", auto_now=True)

    class Meta:
        db_table = u"faturamento\".\"tb_colecao"


class Plano(models.Model):
    id = custom_models.BigAutoField(db_column="plano_id", primary_key=True)
    nome = models.TextField(db_column="plano_nome")
    valor = models.DecimalField(db_column="plano_valor", decimal_places=2, max_digits=12)
    indice = models.IntegerField(db_column="plano_indice", default=0)
    controle_trafego = models.BigIntegerField(db_column="plano_controle_trafego", default=0)
    controle_visitas = models.BigIntegerField(db_column="plano_controle_visitas", default=0)
    controle_produtos = models.IntegerField(db_column="plano_controle_produtos", default=0)
    comissao = models.DecimalField(db_column="plano_comissao", decimal_places=2, max_digits=12, default=0)
    data_criacao = models.DateTimeField(db_column="plano_data_criacao", auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column="plano_data_modificacao", auto_now=True)

    colecao = models.ForeignKey(Colecao, db_column="colecao_id")

    class Meta:
        db_table = u"faturamento\".\"tb_plano"


class PlanoAssinatura(models.Model):
    id = custom_models.BigAutoField(db_column="plano_assinatura_id", primary_key=True)
    acao = models.TextField(db_column="plano_assinatura_acao", choices=PLANO_ACAO_CHOICES, default='MANTEVE')
    ciclo_inicio = models.DateField(db_column="plano_assinatura_ciclo_inicio")
    ciclo_fim = models.DateField(db_column="plano_assinatura_ciclo_fim")
    controle_trafego = models.BigIntegerField(db_column="plano_assinatura_controle_trafego", default=0)
    controle_visitas = models.BigIntegerField(db_column="plano_assinatura_controle_visitas", default=0)
    controle_produtos = models.IntegerField(db_column="plano_assinatura_controle_produtos", default=0)
    data_criacao = models.DateTimeField(db_column="plano_assinatura_data_criacao", auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column="plano_assinatura_data_modificacao", auto_now=True)

    conta = models.ForeignKey("plataforma.Conta", db_column="conta_id")
    plano = models.ForeignKey(Plano, db_column="plano_id")
    fatura = models.ForeignKey(Fatura, db_column="fatura_id")

    class Meta:
        db_table = u"faturamento\".\"tb_plano_assinatura"
        index_together = (('ciclo_inicio', 'ciclo_fim'),)


class Tema(models.Model):
    id = custom_models.BigAutoField(db_column="tema_id", primary_key=True)
    ativo = models.NullBooleanField(db_column="tema_ativo")
    nome = models.TextField(db_column="tema_nome")
    poweredby = models.TextField(db_column="tema_poweredby")
    chamada = models.TextField(db_column="tema_chamada")
    valor = models.DecimalField(db_column="tema_valor", decimal_places=2, max_digits=12)

    headtags = models.TextField(db_column="tema_headtags")
    footags = models.TextField(db_column="tema_footags")

    layout_parametros = JSONField(db_column='tema_layout_parametros', null=True, default=None)

    url_thumbnail = models.TextField(db_column="tema_url_thumbnail")
    url_screenshots = models.TextField(db_column="tema_url_screenshots")
    url_download = models.TextField(db_column="tema_url_download")
    url_lojamodelo = models.TextField(db_column="tema_url_lojamodelo")

    data_criacao = models.DateTimeField(db_column="tema_data_criacao", auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column="tema_data_modificacao", auto_now=True)

    colecao = models.ForeignKey(Colecao, db_column="colecao_id")

    class Meta:
        db_table = u"faturamento\".\"tb_tema"


class Banner(models.Model):
    id = custom_models.BigAutoField(db_column="banner_id", primary_key=True)
    ativo = models.NullBooleanField(db_column="banner_ativo")
    nome = models.TextField(db_column="banner_nome")
    poweredby = models.TextField(db_column="banner_poweredby")
    chamada = models.TextField(db_column="banner_chamada")
    valor = models.DecimalField(db_column="banner_valor", decimal_places=2, max_digits=12)

    url_thumbnail = models.TextField(db_column="banner_url_thumbnail")
    url_screenshots = models.TextField(db_column="banner_url_screenshots")
    url_download = models.TextField(db_column="banner_url_download")
    url_lojamodelo = models.TextField(db_column="banner_url_lojamodelo")

    data_criacao = models.DateTimeField(db_column="banner_data_criacao", default=0)
    data_modificacao = models.DateTimeField(db_column="banner_data_modificacao", auto_now=True)

    colecao = models.ForeignKey(Colecao, db_column="colecao_id")

    class Meta:
        db_table = u"faturamento\".\"tb_banner"


class Consumo(models.Model):
    id = custom_models.BigAutoField(db_column="consumo_id", primary_key=True)
    data = models.DateField(db_column="consumo_data", null=False, default=None)
    data_modificacao = models.DateTimeField(db_column="consumo_data_modificacao", auto_now=True)

    trafego = models.BigIntegerField(db_column="consumo_trafego", default=0)
    visitas = models.BigIntegerField(db_column="consumo_visitas", default=0)

    conta = models.ForeignKey("plataforma.Conta", db_column="conta_id")

    class Meta:
        db_table = u"faturamento\".\"tb_consumo"
