from __future__ import unicode_literals, absolute_import

from decimal import Decimal

from django.test import TestCase

from ..cart import Cart, CartModificationError
from ..models import Product, ProductCategory, ProductEntry


class CartTestCase(TestCase):
    def setUp(self):
        self.category = ProductCategory.objects.create(
            name='Категория', slug='category', description='Описание',
            image='/image.png'
        )
        self.p1 = Product.objects.create(
            name='Продукт', slug='product', price=1000, is_weight=True, width=10, depth=10, height=10,
            weight=1500, short_description='Короткое описание', description='Описание'
        )
        ProductEntry.objects.create(product=self.p1, price=1000, quantity=4.5)
        self.p2 = Product.objects.create(
            name='Продукт2', slug='product2', price=500, width=10, depth=10, height=10,
            weight=1500, short_description='Короткое описание', description='Описание'
        )
        ProductEntry.objects.create(product=self.p2, price=500, quantity=3)
        self.category.products.add(self.p1, self.p2)

    def test_no_basket_data(self):
        session = {}
        basket = Cart(session)
        self.assertTrue(basket.is_empty)
        self.assertEqual(session, {})

    def test_has_basket_data(self):
        session = {Cart.OLD_CART: [(self.p1.id, 1.3), (self.p2.id, 1)]}
        basket = Cart(session)
        self.assertFalse(basket.is_empty)
        self.assertEqual(basket.get_amount(self.p1), 1.3)
        self.assertEqual(basket.get_amount(self.p2), 1)

        self.assertAlmostEqual(basket.price, Decimal('1800'))
        self.assertAlmostEqual(basket.weight, 3450)
        self.assertAlmostEqual(basket.items_num, 2)

        self.assertEqual(session, {Cart.OLD_CART: [(self.p1.id, 1.3), (self.p2.id, 1)]})

        basket.clean()

        self.assertEqual(session, {Cart.OLD_CART: []})

    def test_basket_modification(self):
        session = {}
        basket = Cart(session)
        self.assertFalse(basket)

        basket.add(self.p1, Decimal(1.5))
        self.assertEqual(basket.get_amount(self.p1), 1.5)
        self.assertEqual(session, {Cart.OLD_CART: [(self.p1.id, 1.5)]})
        self.assertTrue(basket)

        with self.assertRaises(CartModificationError):
            basket.add(self.p2, Decimal(1.5))
        self.assertEqual(basket.get_amount(self.p2), 0)
        self.assertEqual(session, {Cart.OLD_CART: [(self.p1.id, 1.5)]})

        basket.add(self.p2, Decimal(1))
        self.assertEqual(basket.get_amount(self.p2), 1)
        self.assertEqual(session, {Cart.OLD_CART: [(self.p1.id, 1.5), (self.p2.id, 1)]})

        basket.set(self.p1, Decimal(1))
        self.assertEqual(basket.get_amount(self.p1), 1)
        self.assertEqual(session, {Cart.OLD_CART: [(self.p1.id, 1), (self.p2.id, 1)]})

        basket.remove(self.p2)
        self.assertEqual(basket.get_amount(self.p2), 0)
        self.assertEqual(session, {Cart.OLD_CART: [(self.p1.id, 1)]})

        with self.assertRaises(CartModificationError):
            basket.set(self.p2, Decimal(5))
        self.assertEqual(basket.get_amount(self.p2), 0)
        self.assertEqual(session, {Cart.OLD_CART: [(self.p1.id, 1)]})

        basket.add(self.p2, Decimal(3))
        self.assertEqual(basket.get_amount(self.p2), 3)
        self.assertEqual(session, {Cart.OLD_CART: [(self.p1.id, 1), (self.p2.id, 3)]})

    def test_basket_iter(self):
        session = {Cart.OLD_CART: [(self.p1.id, 1.3), (self.p2.id, 1)]}
        basket = Cart(session)
        lb = list(basket)
        self.assertEqual(len(lb), 2)

        p, amount, price = lb[0]
        self.assertEqual(p, self.p1)
        self.assertEqual(amount, 1.3)
        self.assertAlmostEqual(price, Decimal('1300'))

        p, amount, price = lb[1]
        self.assertEqual(p, self.p2)
        self.assertEqual(amount, 1)
        self.assertAlmostEqual(price, Decimal('500'))
