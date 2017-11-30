# -*- coding: utf-8 -*-
import logging
from repositories.integration.base import notifications
from repositories.catalogo.models import (
    Produto,
    Marca,
    Categoria,
    ProdutoEstoque,
    ProdutoImagem,
    ProdutoGradeVariacao)
from repositories.integration.serializers import (
    ProdutoSerializer, MarcaSerializer, CategoriaSerializer,
    ProdutoImagemSerializer, ProdutoVariacaoSerializer,
    PedidoVendaSerializer, ProdutoEstoqueSerializer
)
from repositories.pedido.models import PedidoVenda
from repositories.plataforma.models import Feature
from repositories.integration.models import ModelIntegration


class ProdutoNotifier(notifications.BaseNotificationService):

    model = Produto
    serializer = ProdutoSerializer

    def model_select_is_valid(self, obj, slug):
        result = super(ProdutoNotifier, self).model_select_is_valid(obj, slug)
        if obj.conta.id != self.account_id:
            raise ValueError(
                u"A conta informada ({}) não é "
                u"valida para este Produto ({})".format(
                    obj.conta.id, self.account_id))
        object_active = obj.ativo
        if not object_active:
            logging.warning('OBJETO DESATIVADO')
        feature_enabled = Feature.is_enabled(slug, obj.conta, plan=self.plan)
        if not feature_enabled:
            logging.warning('FEATURE DESATIVADA PARA ESTE OBJETO')
        return result and object_active and feature_enabled


class MarcaNotifier(notifications.BaseNotificationService):

    model = Marca
    serializer = MarcaSerializer

    def model_select_is_valid(self, obj, slug):
        result = super(MarcaNotifier, self).model_select_is_valid(obj, slug)
        if obj.conta.id != self.account_id:
            raise ValueError(
                u"A conta informada ({}) não é "
                u"valida para esta Marca ({})".format(
                    obj.conta.id, self.account_id))
        object_active = obj.ativo
        if not object_active:
            logging.warning('OBJETO DESATIVADO')
        feature_enabled = Feature.is_enabled(slug, obj.conta, plan=self.plan)
        if not feature_enabled:
            logging.warning('FEATURE DESATIVADA PARA ESTE OBJETO')
        return result and object_active and feature_enabled


class CategoriaNotifier(notifications.BaseNotificationService):

    model = Categoria
    serializer = CategoriaSerializer

    def model_select_is_valid(self, obj, slug):
        result = super(
            CategoriaNotifier,
            self).model_select_is_valid(
            obj,
            slug)
        if obj.conta.id != self.account_id:
            raise ValueError(
                u"A conta informada ({}) não é "
                u"valida para esta Categoria ({})".format(
                    obj.conta.id, self.account_id))
        object_active = obj.ativa
        if not object_active:
            logging.warning('OBJETO DESATIVADO')
        feature_enabled = Feature.is_enabled(slug, obj.conta, plan=self.plan)
        if not feature_enabled:
            logging.warning('FEATURE DESATIVADA PARA ESTE OBJETO')
        return result and object_active and feature_enabled


class ProdutoImagemNotifier(notifications.BaseNotificationService):

    model = ProdutoImagem
    serializer = ProdutoImagemSerializer

    def model_select_is_valid(self, obj, slug):
        result = super(
            ProdutoImagemNotifier,
            self).model_select_is_valid(
            obj,
            slug)
        if obj.conta.id != self.account_id:
            raise ValueError(
                u"A conta informada ({}) não é "
                u"valida para esta Imagem ({})".format(
                    obj.conta.id, self.account_id))
        object_active = obj.produto.ativo
        if not object_active:
            logging.warning('OBJETO DESATIVADO')
        feature_enabled = Feature.is_enabled(slug, obj.conta, plan=self.plan)
        if not feature_enabled:
            logging.warning('FEATURE DESATIVADA PARA ESTE OBJETO')
        return result and object_active and feature_enabled


class ProdutoVariacaoNotifier(notifications.BaseNotificationService):

    model = ProdutoGradeVariacao
    serializer = ProdutoVariacaoSerializer

    def model_select_is_valid(self, obj, slug):
        result = super(
            ProdutoVariacaoNotifier,
            self).model_select_is_valid(obj, slug)
        if obj.conta.id != self.account_id:
            raise ValueError(
                u"A conta informada ({}) não é "
                u"valida para esta Variação ({})".format(
                    obj.conta.id, self.account_id))
        object_active = obj.produto_pai.ativo
        if not object_active:
            logging.warning('OBJETO PAI DESATIVADO')
        feature_enabled = Feature.is_enabled(slug, obj.conta, plan=self.plan)
        if not feature_enabled:
            logging.warning('FEATURE DESATIVADA PARA ESTE OBJETO')
        return result and object_active and feature_enabled


class PedidoVendaNotifier(notifications.BaseNotificationService):
    model = PedidoVenda
    serializer = PedidoVendaSerializer

    def model_select_is_valid(self, obj, slug):
        result = super(
            PedidoVendaNotifier,
            self).model_select_is_valid(obj, slug)
        if obj.conta.id != self.account_id:
            raise ValueError(
                u"A conta informada ({}) não é "
                u"valida para este Pedido ({})".format(
                    obj.conta.id, self.account_id))
        feature_enabled = Feature.is_enabled(slug, obj.conta, plan=self.plan)
        if not feature_enabled:
            logging.warning('FEATURE DESATIVADA PARA ESTE OBJETO')
        return result and feature_enabled


class ProdutoEstoqueNotifier(notifications.BaseNotificationService):
    model = ProdutoEstoque
    serializer = ProdutoEstoqueSerializer

    def model_select_is_valid(self, obj, slug):
        logging.warning("ENTROU VALIDACAO PRODUTOESTOQUE")
        result = super(
            ProdutoEstoqueNotifier,
            self).model_select_is_valid(
            obj,
            slug)
        if obj.conta.id != self.account_id:
            raise ValueError(
                u"A conta informada ({}) não é "
                u"valida para este Produto ({})".format(
                    obj.conta.id, self.account_id))
        if obj.produto.pai:
            active = obj.produto.pai.ativo
        else:
            active = obj.produto.ativo

        found_integration = False
        prod_model = None
        try:
            prod_model = ModelIntegration.objects.get(
                account_id=obj.conta.id,
                model_selected='produtogradevariacao'
                if obj.produto.pai else 'produto',
                model_selected_id=obj.id,
                integration__slug=slug
            )
        except ModelIntegration.DoesNotExist:
            logging.warning(
                'NÃO ENCONTROU A REFERENCIA EXTERNA DO PRODUTO NO BANCO')
            found_integration = False
        except Exception as e:
            logging.warning(
                'Ocorreu um erro ao buscar '
                'a referencia externa do estoque: {}'.format(e))
            found_integration = False

        if prod_model and (
                prod_model.external_id or prod_model.external_sku_id):
            found_integration = True
        else:
            logging.warning(
                'NÃO ENCONTROU A REFERENCIA EXTERNA DO PRODUTO NO MODELO')

        feature_enabled = Feature.is_enabled(slug, obj.conta, plan=self.plan)
        if not feature_enabled:
            logging.warning('FEATURE DESATIVADA PARA ESTE OBJETO')

        return result and found_integration and active and feature_enabled
