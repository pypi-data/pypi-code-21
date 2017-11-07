# -*- coding:utf-8 -*-
from django.test import TestCase

from fe_core.models import Entity


class TestEntidade(TestCase):
    def test_create_entidade_com_nome(self):
        nome = 'nome-entidade'
        entidade = Entity.objects.create_entity(nome)
        self.assertIsNotNone(entidade)
        self.assertEquals(nome, entidade.name)

    def test_create_entidade_sem_nome(self):
        entidade = Entity.objects.create_entity()
        self.assertIsNotNone(entidade)
        self.assertEquals(36, len(entidade.name))

    # def test_adiciona_produto_na_entidade(self):
    #     produto = ProductFactory()
    #     self.assertEquals(0, produto.entities.all().count())
    #     entidade = Entity.objects.create_entity()
    #     entidade.product_set.add(produto)
    #     self.assertEquals(1, produto.entities.all().count())
    #
    # def test_adiciona_mesmo_produto_na_entidade(self):
    #     produto = ProductFactory()
    #     self.assertEquals(0, produto.entities.all().count())
    #     entidade = Entity.objects.create_entity()
    #     entidade.product_set.add(produto)
    #     entidade.product_set.add(produto)
    #     self.assertEquals(1, produto.entities.all().count())
