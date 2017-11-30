# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from django.db import models
from jsonfield import JSONField

from repositories import custom_models


class MercadolivreConfiguracao(models.Model):
    id = custom_models.BigAutoField(
        db_column='mercadolivre_configuracao_id', primary_key=True)
    access_token = models.TextField(
        db_column='mercadolivre_configuracao_access_token', null=False)
    apelido = models.TextField(
        db_column='mercadolivre_configuracao_apelido', null=True)
    refresh_token = models.TextField(
        db_column='mercadolivre_configuracao_refresh_token', null=False)
    access_token_invalido = models.BooleanField(
        db_column='mercadolivre_configuracao_access_token_invalido', default=False)
    user_id = models.BigIntegerField(
        db_column='mercadolivre_configuracao_user_id', null=False)
    token_expires = models.DateTimeField(
        db_column='mercadolivre_configuracao_token_expires')
    prazo_remocao = models.DateTimeField(
        db_column='mercadolivre_configuracao_prazo_remocao', null=True)
    prazo_cadastro = models.DateTimeField(
        db_column='mercadolivre_configuracao_prazo_cadastro')
    relistar_automaticamente = models.BooleanField(
        db_column='mercadolivre_configuracao_relistar_automaticamente', default=False)
    data_criacao = models.DateTimeField(
        db_column='mercadolivre_configuracao_data_criacao', auto_now_add=True)
    data_modificacao = models.DateTimeField(
        db_column='mercadolivre_configuracao_data_modificacao', auto_now=True)

    contrato = models.ForeignKey('plataforma.Contrato', db_column="contrato_id")
    conta = models.ForeignKey("plataforma.Conta", db_column="conta_id")

    class Meta:
        db_table = u"marketplace\".\"tb_mercadolivre_configuracao"

    def save(self, *args, **kwargs):
        if not self.contrato_id and self.conta:
            self.contrato_id = self.conta.contrato_id
        if isinstance(self.token_expires, int):
            self.token_expires = datetime.now() + timedelta(seconds=self.token_expires)
        super(MercadolivreConfiguracao, self).save(*args, **kwargs)


class MercadolivreAnuncio(models.Model):
    id = custom_models.BigAutoField(db_column='mercadolivre_anuncio_id', primary_key=True)
    item_id = models.TextField(db_column='mercadolivre_anuncio_item_id')
    produto_id = models.BigIntegerField(db_column='produto_id')
    produto_id_pai = models.BigIntegerField(db_column='produto_id_pai')
    categoria_id = models.TextField(db_column='mercadolivre_anuncio_categoria_id')
    tipo = models.CharField(db_column='mercadolivre_anuncio_tipo', max_length=64)
    status = models.CharField(db_column='mercadolivre_anuncio_status', max_length=32)
    prazo_alteracao = models.DateTimeField(db_column='mercadolivre_anuncio_prazo_alteracao', null=True, auto_now_add=True)
    data_vencimento = models.DateTimeField(db_column='mercadolivre_anuncio_data_vencimento', null=True)
    data_criacao = models.DateTimeField(
        db_column='mercadolivre_anuncio_data_criacao', auto_now_add=True)
    data_modificacao = models.DateTimeField(
        db_column='mercadolivre_anuncio_data_modificacao', auto_now=True)

    # Dados do produto
    title = models.TextField(db_column='mercadolivre_anuncio_title')
    price = models.DecimalField(db_column='mercadolivre_anuncio_price', max_digits=16, decimal_places=3)
    quantity = models.IntegerField(db_column='mercadolivre_anuncio_quantity')
    variations = JSONField(db_column='mercadolivre_anuncio_variations', null=True, default=None)

    contrato = models.ForeignKey('plataforma.Contrato', db_column="contrato_id")
    conta = models.ForeignKey("plataforma.Conta", db_column="conta_id")

    class Meta:
        db_table = u"marketplace\".\"tb_mercadolivre_anuncio"

    def save(self, *args, **kwargs):
        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id
        super(MercadolivreAnuncio, self).save(*args, **kwargs)
