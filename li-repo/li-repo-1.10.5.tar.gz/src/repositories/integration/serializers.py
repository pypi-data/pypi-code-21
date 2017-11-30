# -*- coding: utf-8 -*-
"""
Utiliza o conversor Modelo -> JSON genérico
para exportar os modelos.

Crie uma classe para cada modelo que deseja converter.
-   Em 'model' informe o modelo que será convertido
-   Em 'foreign_fields' informe os campos relacionais que
    devem ser convertidos. O 'related_name' pode ser usado para
    trazer tabelas relacionadas indiretamente.
-   Em 'ignore_fields' informe os campos que deverão ser ignorados. O campo
    será ignorado na instancia enviada e nas subsinstâncias vindas dos campos
    relacionais.
-   Sobrescreva a definicao "additional_info"
    para adicionar dados ao dicionário
    Lembre-se que é preciso iterar todas as integrações
    ativas da conta para obter os dados
PEP8: OK
"""
from repositories.integration.base import serializers
from repositories.catalogo.models import (
    Produto, Marca, Categoria, ProdutoCategoria, ProdutoGradeVariacao,
    ProdutoImagem, ProdutoGradeVariacaoImagem, ProdutoPreco,
    ProdutoEstoque)
from repositories.integration.models import (
    ModelIntegration, AccountIntegration)
from repositories.pedido.models import PedidoVenda, PedidoVendaFormaEnvio
from django.conf import settings


def get_produto_price(product):
    try:
        prod_price = ProdutoPreco.objects.get(
            conta_id=product.conta.id,
            produto=product,
            sob_consulta=False
        )
    except:
        prod_price = None
    if prod_price:
        if prod_price.custo:
            return str(prod_price.custo)
        price = prod_price.promocional \
            if prod_price.promocional else prod_price.cheio
        return str(price) if price else ''
    else:
        return ''

def get_product_sale_price(product):
    try:
        prod_price = ProdutoPreco.objects.get(
            conta_id=product.conta.id,
            produto=product,
            sob_consulta=False
        )
    except:
        prod_price = None
    if prod_price:
        price = prod_price.promocional \
            if prod_price.promocional else prod_price.cheio
        return str(price) if price else ''
    else:
        return ''

def get_produto_price_markup(product):
    try:
        prod_price = ProdutoPreco.objects.get(
            conta_id=product.conta.id,
            produto=product,
            sob_consulta=False
        )
    except:
        prod_price = None
    if prod_price:
        cost_price = prod_price.custo
        final_price = prod_price.promocional \
            if prod_price.promocional else prod_price.cheio
        if not cost_price or not final_price:
            return "1.00"
        else:
            return str(final_price / cost_price)
    else:
        return "1.00"


def get_produto_estoque(product):

    available_qty = product.quantidade_disponivel()
    if not available_qty or available_qty < 0:
        available_qty = 0

    return str(available_qty)


def get_sku_variations(prod_sku):
    return {
        str(prod.grade): str(prod.variacao)
        for prod in ProdutoGradeVariacao.objects.filter(
            conta_id=prod_sku.conta.id,
            produto=prod_sku.produto
        )
    }


class ProdutoSerializer(serializers.ModelSerializer):
    model = Produto
    foreign_fields = [
        'imagens',
        'grades',
        'categorias',
        'pai',
        'marca',
        'conta',
        'produto_imagens',
        'produto_grades',
        'estoque'
    ]

    ignore_fields = [
        'certificado_ssl',
        'loja_layout',
        'parametros',
    ]

    def additional_info(self):

        def get_marca(product, integration):
            # Marca
            try:
                marca_external_id = ModelIntegration.objects.get(
                    account_id=product.conta.id,
                    model_selected=product.marca._meta.model_name,
                    model_selected_id=product.marca.id,
                    integration=integration
                ).external_id
            except:
                marca_external_id = None

            return str(marca_external_id) if marca_external_id else ''

        def get_categoria(product, integration):
            # Pega Categoria e Marca
            categoria_id = None
            categoria_external_id = None
            try:
                categoria_id = ProdutoCategoria.objects.get(
                    produto=product,
                    conta_id=product.conta.id,
                    principal=True
                ).categoria.id
                categoria_external_id = ModelIntegration.objects.get(
                    account_id=product.conta.id,
                    model_selected=Categoria._meta.model_name,
                    model_selected_id=categoria_id,
                    integration=integration
                ).external_id
            except:
                categoria_external_id = None

            return str(categoria_external_id) if categoria_external_id else ''

            if product.grade and product.variacao:
                return {str(product.grade.nome): str(product.variacao.nome)}
            else:
                return str({})

        if self.instance:
            brand_dictionary = {
                acc_int.integration.slug: get_marca(
                    self.instance, acc_int.integration)
                for acc_int in AccountIntegration.objects.filter(
                    account_id=self.instance.conta.id,
                    active=True,
                )
            }
            category_dictionary = {
                acc_int.integration.slug: get_categoria(
                    self.instance, acc_int.integration)
                for acc_int in AccountIntegration.objects.filter(
                    account_id=self.instance.conta.id,
                    active=True,
                )
            }

            try:
                categoria_internal_id = str(ProdutoCategoria.objects.get(
                    produto=self.instance,
                    conta_id=self.instance.conta.id,
                    principal=True
                ).categoria.id)
            except:
                categoria_internal_id = ''

            marca_internal_id = str(
                self.instance.marca.id) if self.instance.marca else ''

            # SKUs
            sku_dictionary_list = []
            # SKU do próprio produto
            if self.instance.tipo == "normal":
                produto_estoque = ProdutoEstoque.objects.get(
                    produto=self.instance,
                    conta=self.instance.conta
                )
                data = {}
                data['partnerId'] = self.instance.sku
                data['title'] = self.instance.nome
                if get_produto_price(self.instance):
                    data['price'] = float(get_produto_price(self.instance))
                if get_produto_price_markup(self.instance):
                    data['markup'] = float(
                        get_produto_price_markup(
                            self.instance))

                if produto_estoque.gerenciado:
                    if get_produto_estoque(self.instance):
                        data['amount'] = float(
                            get_produto_estoque(
                                self.instance))
                else:
                    data['amount'] = 9999
                if self.instance.gtin:
                    data['ean'] = self.instance.gtin
                sku_dictionary_list.append(data)
            # SKU das variações
            for prod_sku in ProdutoGradeVariacao.objects.filter(
                conta_id=self.instance.conta.id,
                produto_pai=self.instance
            ):
                data = {}
                data['partnerId'] = prod_sku.produto.sku
                data['title'] = prod_sku.produto_pai.nome
                if get_produto_price(prod_sku.produto):
                    data['price'] = float(get_produto_price(prod_sku.produto))
                if get_product_sale_price(prod_sku.produto):
                    data['sale_price'] = float(get_product_sale_price(prod_sku.produto))
                if get_produto_price_markup(self.instance):
                    data['markup'] = float(
                        get_produto_price_markup(
                            self.instance))
                produto_estoque = ProdutoEstoque.objects.get(
                    produto=prod_sku.produto,
                    conta=prod_sku.conta
                )
                if produto_estoque.gerenciado:
                    if get_produto_estoque(prod_sku.produto):
                        data['amount'] = float(
                            get_produto_estoque(
                                prod_sku.produto))
                else:
                    data['amount'] = 9999
                if prod_sku.produto.gtin:
                    data['ean'] = prod_sku.produto.gtin

                # Adiciona Dimensões físicas
                if prod_sku.produto.altura:
                    data['altura'] = prod_sku.produto.altura
                if prod_sku.produto.largura:
                    data['largura'] = prod_sku.produto.largura
                if prod_sku.produto.peso:
                    data['peso'] = float(prod_sku.produto.peso)
                if prod_sku.produto.profundidade:
                    data['profundidade'] = prod_sku.produto.profundidade

                if get_sku_variations(prod_sku):
                    data['variations'] = get_sku_variations(prod_sku)
                exists = None
                exists = [
                    sku_list
                    for sku_list in sku_dictionary_list
                    if sku_list.get('partnerId') == prod_sku.produto.sku
                ]
                if not exists:
                    sku_dictionary_list.append(data)

            # Adicionar se o produto está com Preco s/ consulta
            try:
                prod_price = ProdutoPreco.objects.get(
                    conta_id=self.instance.conta.id,
                    produto=self.instance
                )
            except:
                prod_price = None

            price_consult = prod_price.sob_consulta if prod_price else False

            self.dictionary['api_reference'] = {
                "brand_internal_id": marca_internal_id,
                "category_internal_id": categoria_internal_id,
                "brand_external_id": brand_dictionary,
                "category_external_id": category_dictionary,
                "skus": sku_dictionary_list,
                "price_consult": price_consult
            }


class ProdutoVariacaoSerializer(serializers.ModelSerializer):
    model = ProdutoGradeVariacao

    foreign_fields = [
        'produto',
        'produto_pai',
        'grade',
        'variacao',
        'conta'
    ]

    def additional_info(self):
        if self.instance:
            self.dictionary['api_reference'] = {
                "price": get_produto_price(self.instance.produto),
                "amount": get_produto_estoque(self.instance.produto),
                "variations": get_sku_variations(self.instance)
            }


class ProdutoImagemSerializer(serializers.ModelSerializer):
    model = ProdutoImagem

    foreign_fields = [
        'produto',
        'imagem',
        'conta'
    ]

    def additional_info(self):

        def get_image_variation(product_image):
            try:
                prod_var_image = ProdutoGradeVariacaoImagem.objects.get(
                    produto=product_image.produto,
                    imagem=product_image.imagem,
                    conta=product_image.conta
                )
            except:
                prod_var_image = None
            if prod_var_image:
                return prod_var_image.variacao.nome
            else:
                return None

        def get_image_external_ids(product, image):
            imagelist = []
            for acc_int in AccountIntegration.objects.filter(
                account_id=product.conta.id,
                active=True
            ):
                external_id = ''
                try:
                    model_int = ModelIntegration.objects.get(
                        model_selected=image._meta.model_name,
                        model_selected_id=image.id,
                        account_id=product.conta.id,
                        integration=acc_int.integration
                    )
                    if model_int.external_id:
                        external_id = str(model_int.external_id)
                except:
                    external_id = ''

                imagelist.append(
                    {acc_int.integration.slug: external_id})

            return imagelist

        if self.instance:
            # Pega Imagens
            self.dictionary['api_reference'] = {
                "url": self.instance.imagem.caminho,
                "variation": get_image_variation(
                    self.instance) if get_image_variation(
                    self.instance) else '',
                "id": get_image_external_ids(
                    self.instance.produto,
                    self.instance.imagem)
            }


class MarcaSerializer(serializers.ModelSerializer):
    model = Marca


class CategoriaSerializer(serializers.ModelSerializer):
    model = Categoria

    def additional_info(self):

        def get_external_id(category, integration):
            try:
                record = ModelIntegration.objects.get(
                    account_id=category.conta.id,
                    model_selected=category._meta.model_name,
                    model_selected_id=category.id,
                    integration=integration,
                )
                return str(record.external_id) if record.external_id else ''
            except:
                return ''

        if self.instance:
            self.dictionary['api_reference'] = {
                acc_int.integration.slug: {
                    str(categoria.level): get_external_id(
                        categoria, acc_int.integration)
                    for categoria in Categoria.objects.filter(
                        tree_id=self.instance.tree_id,
                        conta_id=self.instance.conta.id
                    ).order_by('level')
                }
                for acc_int in AccountIntegration.objects.filter(
                    account_id=self.instance.conta.id,
                    active=True,
                )
            }


class PedidoVendaSerializer(serializers.ModelSerializer):
    model = PedidoVenda

    foreign_fields = [
        'situacao'
    ]

    def additional_info(self):

        def get_external_id(order, integration):
            try:
                record = ModelIntegration.objects.get(
                    account_id=order.conta.id,
                    model_selected=order._meta.model_name,
                    model_selected_id=order.id,
                    integration=integration,
                )
                return str(record.external_id) if record.external_id else ''
            except:
                return ''

        if self.instance:
            shipping_info = PedidoVendaFormaEnvio.objects.filter(
                conta=self.instance.conta,
                pedido=self.instance
            ).last()
            self.dictionary['api_reference'] = {
                "tracking_code": shipping_info.objeto or "",
                "status": self.instance.situacao.id
            }
            self.dictionary['external_id'] = {
                acc_int.integration.slug: get_external_id(
                    self.instance, acc_int.integration)

                for acc_int in AccountIntegration.objects.filter(
                    account_id=self.instance.conta.id,
                    active=True
                )
            }


class ProdutoEstoqueSerializer(serializers.ModelSerializer):
    model = ProdutoEstoque

    foreign_fields = [
        'conta'
    ]

    def additional_info(self):

        if self.instance.produto.pai:
            product_id = self.instance.produto.pai.id
        else:
            product_id = self.instance.produto.id

        if self.instance:
            produto = Produto.objects.get(id=self.instance.produto.id)
            self.dictionary['api_reference'] = {
                'disponivel': get_produto_estoque(produto),
                'model': 'produtogradevariacao'
                if self.instance.produto.pai else 'produto',
                'product_id': product_id,
                'price': get_produto_price(produto)
            }
