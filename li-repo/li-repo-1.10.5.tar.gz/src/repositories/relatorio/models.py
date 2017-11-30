# -*- coding: utf-8 -*-
import datetime
from django.db import models
from repositories.libs.utils import formatar_decimal_br


class RelatorioPedidoVendaPorDataManager(models.Manager):
    def gera_saida(self, queryset):
        if not queryset:
            return []

        saida = [queryset[0].dados_xls(cabecalho=True)]

        for i in queryset:
            saida.append(i.dados_xls())

        return saida

    def por_data(self, conta_id=None, dias=None, data=None):
        timedelta = data - datetime.timedelta(days=dias)

        queryset = super(RelatorioPedidoVendaPorDataManager, self).get_queryset().filter(
            conta_id=conta_id, data_criacao__gte=timedelta, data_criacao__lte=data)

        return self.gera_saida(queryset)

    def por_dias(self, conta_id=None, dias=None):
        timedelta = datetime.datetime.today() - datetime.timedelta(days=dias)

        queryset = super(RelatorioPedidoVendaPorDataManager, self).get_queryset().filter(
            conta_id=conta_id, data_criacao__gte=timedelta)

        return self.gera_saida(queryset)

    def por_um_dia(self, conta_id=None, dia=None):
        timedelta = datetime.datetime.today() - datetime.timedelta(days=dia)

        queryset = super(RelatorioPedidoVendaPorDataManager, self).get_queryset().filter(
            conta_id=conta_id, data_criacao=timedelta.date())

        return self.gera_saida(queryset)


class RelatorioPedidoVendaPorData(models.Model):

    data_criacao = models.DateTimeField(
        db_column="pedido_venda_data_criacao", primary_key=True)

    objects = RelatorioPedidoVendaPorDataManager()

    qtd_concluidos = models.DecimalField(
        db_column="qtd_concluidos", max_digits=16, decimal_places=3)
    subtotal_concluidos = models.DecimalField(
        db_column="subtotal_concluidos", max_digits=16, decimal_places=3)
    envio_concluidos = models.DecimalField(
        db_column="envio_concluidos", max_digits=16, decimal_places=3)
    desconto_concluidos = models.DecimalField(
        db_column="desconto_concluidos", max_digits=16, decimal_places=3)
    total_concluidos = models.DecimalField(
        db_column="total_concluidos", max_digits=16, decimal_places=3)

    qtd_nao_concluidos = models.DecimalField(
        db_column="qtd_nao_concluidos", max_digits=16, decimal_places=3)
    subtotal_nao_concluidos = models.DecimalField(
        db_column="subtotal_nao_concluidos", max_digits=16, decimal_places=3)
    envio_nao_concluidos = models.DecimalField(
        db_column="envio_nao_concluidos", max_digits=16, decimal_places=3)
    desconto_nao_concluidos = models.DecimalField(
        db_column="desconto_nao_concluidos", max_digits=16, decimal_places=3)
    total_nao_concluidos = models.DecimalField(
        db_column="total_nao_concluidos", max_digits=16, decimal_places=3)

    conta_id = models.BigIntegerField(db_column="conta_id")

    class Meta:
        db_table = u"pedido\".\"vw_relatorio_pedido_venda_simples_por_data"
        managed = False

    def dados_xls(self, cabecalho=False):
        """Retorna os dados na ordem pro xls"""
        if cabecalho:
            return [
                u'Dia', u'Pedidos', u'Pedidos finalizados', u'Subtotal finalizados (R$)',
                u'Envio finalizados (R$)', u'Descontos finalizados (R$)', u'Total finalizados (R$)',
                u'Pedidos não finalizados', u'Subtotal não finalizados (R$)',
                u'Envios não finalizados (R$)', u'Descontos não finalizados (R$)',
                u'Total não finalizados (R$)'
            ]
        total_pedidos = self.qtd_concluidos + self.qtd_nao_concluidos
        return [
            str(self.data_criacao.strftime('%d/%m/%Y')), total_pedidos,
            self.qtd_concluidos, self.subtotal_concluidos,
            self.envio_concluidos, self.desconto_concluidos,
            self.total_concluidos, self.qtd_nao_concluidos,
            self.subtotal_nao_concluidos, self.envio_nao_concluidos,
            self.desconto_nao_concluidos, self.total_nao_concluidos
        ]


class RelatorioPedidoVendaPorProdutoManager(models.Manager):

    def ultimos_meses(self, conta_id=None, dias=None):
        timedelta = datetime.datetime.today() - datetime.timedelta(days=dias)
        timedelta = int(timedelta.strftime('%Y%m'))
        queryset = super(RelatorioPedidoVendaPorProdutoManager, self).get_queryset() \
            .filter(conta_id=conta_id, mes_ano__gte=timedelta)
        if not queryset:
            return []
        saida = [queryset[0].dados_xls(cabecalho=True)]

        for i in queryset:
            saida.append(i.dados_xls())
        return saida


class RelatorioPedidoVendaPorProduto(models.Model):

    conta_id = models.ForeignKey('plataforma.Conta', db_column="conta_id")
    mes_ano = models.IntegerField(db_column="mes_ano")
    produto = models.ForeignKey('catalogo.Produto', db_column="produto_id", on_delete=models.DO_NOTHING)
    nome = models.CharField(db_column="nome", max_length=254)
    quantidade = models.DecimalField(
        db_column="quantidade", max_digits=16, decimal_places=3)
    subtotal = models.DecimalField(
        db_column="subtotal", max_digits=16, decimal_places=3)
    subtotal_unitario = models.DecimalField(
        db_column="subtotal_unitario", max_digits=16, decimal_places=3)

    objects = RelatorioPedidoVendaPorProdutoManager()

    class Meta:
        db_table = u"pedido\".\"vw_relatorio_pedido_venda_simples_por_produto"
        managed = False

    def dados_xls(self, cabecalho=False):
        """Retorna os dados na ordem pro xls"""
        if cabecalho:
            return [
                u'Mês / Ano', u'ID', u'Nome do Produto', u'Quantidade',
                u'Subtotal (R$)', u'Valor médio unitário (R$)'
            ]
        str_mes_ano = str(self.mes_ano)
        mes_ano = '%s/%s' % (str_mes_ano[4:6], str_mes_ano[:4])
        return [
            mes_ano, self.produto_id, self.nome,
            int(self.quantidade), formatar_decimal_br(self.subtotal),
            formatar_decimal_br(self.subtotal_unitario)
        ]
