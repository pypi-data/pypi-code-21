# coding=utf-8
from __future__ import unicode_literals, absolute_import

from decimal import Decimal

from copy import copy
from django.test import TestCase

from ..forms import CartModifyForm
from ..cart import Cart
from ..models import ProductCategory, Product, ProductEntry


class CartModifyFormTestCase(TestCase):
    def setUp(self):
        self.session = {}
        # noinspection PyTypeChecker
        self.basket = Cart(self.session)
        self.category = ProductCategory.objects.create(
            name='Категория', slug='category', description='Описание',
            image='/image.png'
        )
        self.p1 = Product.objects.create(
            name='Продукт', slug='product', price=1000, is_weight=True,
            width=10, depth=10, height=10,
            weight=1500, short_description='Короткое описание', description='Описание'
        )
        ProductEntry.objects.create(product=self.p1, price=1000, quantity=4.5)
        self.p2 = Product.objects.create(
            name='Продукт2', slug='product2', price=500,
            width=10, depth=10, height=10,
            weight=1500, short_description='Короткое описание', description='Описание'
        )
        ProductEntry.objects.create(product=self.p2, price=500, quantity=3)
        self.category.products.add(self.p1, self.p2)

    def test_add_action(self):
        form = CartModifyForm({'action': CartModifyForm.ACTION_ADD, 'product': self.p1.id,
                                 'amount': 1.4, 'response': CartModifyForm.RESPONSE_FULL})
        self.assertTrue(form.is_valid())
        form.perform_action(self.basket)

        self.assertEqual(self.basket.get_amount(self.p1), Decimal('1.4'))
        self.assertEqual(self.session, {Cart.OLD_CART: [(self.p1.id, 1.4)]})

    def test_set_action(self):
        self.basket.add(self.p1, Decimal(1))
        form = CartModifyForm({'action': CartModifyForm.ACTION_SET, 'product': self.p1.id,
                                 'amount': 1.4, 'response': CartModifyForm.RESPONSE_FULL})

        self.assertTrue(form.is_valid())
        form.perform_action(self.basket)

        self.assertEqual(self.basket.get_amount(self.p1), Decimal('1.4'))
        self.assertEqual(self.session, {Cart.OLD_CART: [(self.p1.id, 1.4)]})

    def test_remove_action(self):
        self.basket.add(self.p1, Decimal(1))
        form = CartModifyForm({'action': CartModifyForm.ACTION_REMOVE, 'product': self.p1.id,
                                 'response': CartModifyForm.RESPONSE_FULL})

        self.assertTrue(form.is_valid())
        form.perform_action(self.basket)

        self.assertEqual(self.basket.get_amount(self.p1), 0)
        self.assertTrue(self.basket.is_empty)
        self.assertEqual(self.session, {Cart.OLD_CART: []})

    def test_amount_errors(self):
        form = CartModifyForm({'action': CartModifyForm.ACTION_SET, 'product': self.p1.id,
                                 'response': CartModifyForm.RESPONSE_FULL})

        self.assertFalse(form.is_valid())

        form = CartModifyForm({'action': CartModifyForm.ACTION_ADD, 'product': self.p1.id,
                                 'response': CartModifyForm.RESPONSE_FULL})

        self.assertFalse(form.is_valid())

    def test_form_errors(self):
        data = {'action': CartModifyForm.ACTION_ADD, 'product': self.p1.id,
                'amount': 1.4, 'response': CartModifyForm.RESPONSE_FULL}
        for key in data.keys():
            form_data = copy(data)
            del form_data[key]
            form = CartModifyForm(form_data)
            self.assertFalse(form.is_valid())
