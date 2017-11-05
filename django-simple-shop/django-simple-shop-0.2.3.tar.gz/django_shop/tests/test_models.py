from __future__ import unicode_literals, absolute_import

import json
from collections import namedtuple
from decimal import Decimal
from unittest import mock

from django.test import TestCase

from ..models import ProductCategory, Product, ProductEntry, ProductImage, \
    DeliveryAddress, DeliveryType, Order, ProductOrder, PaymentType, \
    ProductCategoryCustomField, ProductCustomFieldValue
from ..utils import delivery


class ProductTestCase(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name='Продукт', slug='product', price=1000,
            width=10, depth=10, height=10,
            weight=1500, short_description='Короткое описание',
            description='Описание'
        )

    def test_empty_product(self):
        self.assertEqual(self.product.in_stock, 0)
        self.assertEqual(self.product.primary_image, None)
        self.assertEqual(self.product.volume, Decimal('0.000001'))

    def test_has_stock_entries(self):
        ProductEntry.objects.create(product=self.product, price=1000,
                                    quantity=4.5)
        ProductEntry.objects.create(product=self.product, price=1000,
                                    quantity=2)
        self.assertEqual(self.product.in_stock, Decimal('6.5'))

    def test_has_stock_and_order_entries(self):
        ProductEntry.objects.create(product=self.product, price=1000,
                                    quantity=4.5)
        ProductEntry.objects.create(product=self.product, price=1000,
                                    quantity=2)
        dt = DeliveryType.objects.create(name='Доставка',
                                         pricing_method=delivery.METHOD_FREE)
        da = DeliveryAddress.objects.create(name='Имя', email='test@test.com',
                                            phone='+79991234567')
        order = Order.objects.create(sid='12345', delivery_type=dt,
                                     delivery_address=da, delivery_price=0)
        ProductOrder.objects.create(product=self.product, order=order,
                                    quantity=5.1, price=5000)
        self.assertEqual(self.product.in_stock, Decimal('1.4'))

    def test_has_stock_and_more_order_entries(self):
        ProductEntry.objects.create(product=self.product, price=1000,
                                    quantity=4.5)
        ProductEntry.objects.create(product=self.product, price=1000,
                                    quantity=2)
        dt = DeliveryType.objects.create(name='Доставка',
                                         pricing_method=delivery.METHOD_FREE)
        da = DeliveryAddress.objects.create(name='Имя', email='test@test.com',
                                            phone='+79991234567')
        order = Order.objects.create(sid='12345', delivery_type=dt,
                                     delivery_address=da, delivery_price=0)
        ProductOrder.objects.create(product=self.product, order=order,
                                    quantity=6.7, price=5000)
        self.assertEqual(self.product.in_stock, 0)

    def test_has_images(self):
        ProductImage.objects.create(product=self.product, image='/image1.png',
                                    priority=1)
        ProductImage.objects.create(product=self.product, image='/image2.png',
                                    priority=2)
        ProductImage.objects.create(product=self.product, image='/image18.png',
                                    priority=18)
        self.assertEqual(self.product.primary_image, '/image18.png')

    def test_get_available(self):
        p1 = Product.objects.create(
            name='Продукт', slug='product1', price=1000,
            width=10, depth=10, height=10, is_unlimited=True,
            weight=1500, short_description='Короткое описание',
            description='Описание'
        )
        p2 = Product.objects.create(
            name='Продукт', slug='product2', price=1000,
            width=10, depth=10, height=10,
            weight=1500, short_description='Короткое описание',
            description='Описание'
        )
        ProductEntry.objects.create(product=p2, price=1000,
                                    quantity=2)
        products = Product.objects.get_available()
        self.assertEqual(len(products), 2)
        self.assertIn(p1, products)
        self.assertIn(p2, products)

    def _create_field(self, key, value):
        category = ProductCategory.objects.create(
            name='Категория', slug=key, description='Описание'
        )
        category.products.add(self.product)
        field = ProductCategoryCustomField.objects.create(
            category=category, name='поле', key=key,
            type=ProductCategoryCustomField.TYPE_INTEGER,
        )
        ProductCustomFieldValue.objects.create(
            product=self.product, field=field,
            value=value
        )
        return field

    def test_one_filter_empty_product(self):
        field = self._create_field('field', '1234')
        self.assertFalse(Product.objects.get_by_value({field: 1234}))

    def test_one_filter_nonempty_product(self):
        field = self._create_field('field', '1234')
        ProductEntry.objects.create(product=self.product, price=1000,
                                    quantity=2)
        products = Product.objects.get_by_value({field: 1234})

        self.assertEqual(len(products), 1)
        self.assertIn(self.product, products)
        self.assertFalse(Product.objects.get_by_value({field: '124'}))

    def test_two_filters_nonempty_product(self):
        field = self._create_field('field', '1234')
        field2 = self._create_field('field2', '123')
        ProductEntry.objects.create(product=self.product, price=1000,
                                    quantity=2)
        products = Product.objects.get_by_value({field: 1234, field2: 123})

        self.assertEqual(len(products), 1)
        self.assertIn(self.product, products)
        self.assertFalse(Product.objects.get_by_value(
            {field: 1234, field2: 1}))
        self.assertFalse(Product.objects.get_by_value(
            {field: 1, field2: 123}))


class ProductCategoryTestCase(TestCase):
    def setUp(self):
        self.category = ProductCategory.objects.create(
            name='Категория', slug='category', description='Описание',
            image='/image.png'
        )

    @staticmethod
    def _create_product(**kwargs):
        product_dict = dict(
            name='Продукт', slug='product', price=1000,
            weight=1500, short_description='Короткое описание',
            width=10, depth=10, height=10,
            description='Описание'
        )
        product_dict.update(kwargs)
        return Product.objects.create(**product_dict)

    def test_empty(self):
        self.assertFalse(self.category.products_ordered())
        self.assertFalse(self.category.has_products)
        self.assertFalse(self.category.have_to_display)
        self.assertEqual(self.category.active_products_num, 0)

    def test_has_products_no_amount(self):
        p = self._create_product()
        self.category.products.add(p)
        self.assertFalse(self.category.products_ordered())
        self.assertTrue(self.category.has_products)
        self.assertFalse(self.category.have_to_display)
        self.assertEqual(self.category.active_products_num, 0)

    def test_product_with_amount(self):
        p1 = self._create_product(slug='product1')
        ProductEntry.objects.create(product=p1, price=1000, quantity=4.5)
        p2 = self._create_product(slug='product2')
        ProductEntry.objects.create(product=p2, price=1000, quantity=3.4)
        p3 = self._create_product(slug='product3', always_visible=True)
        self.category.products.add(p2, p3, p1)

        po = self.category.products_ordered()
        self.assertEqual(len(po), 3)
        for p in [p1, p2, p3]:
            self.assertIn(p, po)
        self.assertTrue(self.category.has_products)
        self.assertTrue(self.category.have_to_display)
        self.assertEqual(self.category.active_products_num, 3)


class PaymentTypeTestCase(TestCase):
    def test_type_online(self):
        pt = PaymentType.objects.create(name='Кеш',
                                        payment_type=PaymentType.TYPE_OFFLINE)
        self.assertIsNone(pt.create_payment(mock.MagicMock()))

    @mock.patch('django_shop.utils.payment._payment_manager')
    def test_type_offline(self, m_manager):
        m_manager.create_object.return_value = '123'
        pt = PaymentType.objects.create(name='Кеш',
                                        payment_type=PaymentType.TYPE_ONLINE)
        payment = pt.create_payment('someorder')
        self.assertEqual(payment, '123')
        m_manager.create_object.assert_called_once_with('', 'someorder')


class DeliveryTypeTestCase(TestCase):
    def setUp(self):
        self.af = {'name': 'Имя', 'email': 'test@test.com',
                   'phone': '+79991234567'}

    @staticmethod
    def _get_dt(method):
        return DeliveryType.objects.create(
            name='Доставка', pricing_method=method, price=10
        )

    def test_method_free(self):
        dt = self._get_dt(delivery.METHOD_FREE)
        self.assertIsNone(dt.actual_pricing())
        self.assertEqual(dt.price_display(), 'Бесплатно')
        self.assertEqual(
            dt.get_price_and_address('', self.af, Decimal(1234), 1500,
                                     (30, 30, 40)),
            (Decimal(0), self.af)
        )

    def test_method_constant(self):
        dt = self._get_dt(delivery.METHOD_CONSTANT)
        self.assertEqual(dt.actual_pricing(), '10 руб.')
        self.assertEqual(dt.price_display(), '10 &#8381;')
        self.assertEqual(
            dt.get_price_and_address('', self.af, Decimal(1234), 1500,
                                     (30, 30, 40)),
            (Decimal(10), self.af)
        )

    def test_method_percent(self):
        dt = self._get_dt(delivery.METHOD_PERCENT)
        self.assertEqual(dt.actual_pricing(), '10%')
        self.assertEqual(dt.price_display(), '10% от стоимости товара')
        self.assertEqual(
            dt.get_price_and_address('', self.af, Decimal(1234), 1500,
                                     (30, 30, 40)),
            (Decimal('124'), self.af)
        )

    @mock.patch('django_shop.utils.delivery.create_delivery_obj')
    def test_method_api(self, m_del):
        t = namedtuple('t', ['price', 'address'])
        m_del.return_value = t(Decimal('12367'),
                               {'id': 12345, 'address': 'Адрес'})

        dt = self._get_dt(delivery.METHOD_API)
        self.assertEqual(dt.actual_pricing(), 'Цена расчетная')
        self.assertEqual(dt.price_display(), 'Цена расчетная')
        self.assertEqual(
            dt.get_price_and_address(
                json.dumps({'id': 12345, 'address': 'Адрес'}),
                self.af, Decimal(1234), 1500, (30, 30, 40)),
            (Decimal('12367'), {'id': 12345, 'address': 'Адрес'})
        )
        m_del.assert_called_once_with(
            '', {'options': {'address': 'Адрес', 'type_price': 10, 'hook': '',
                             'id': 12345},
                 'address': {'phone': '+79991234567', 'name': 'Имя',
                             'email': 'test@test.com'},
                 'order_price': Decimal('1234'), 'weight': 1500,
                 'measures': (30, 30, 40)}
        )


class ProductOrderTestCase(TestCase):
    def setUp(self):
        self.category = ProductCategory.objects.create(
            name='Категория', slug='category', description='Описание',
            image='/image.png'
        )
        self.product = Product.objects.create(
            name='Продукт', slug='product', price=1000,
            weight=1500, short_description='Короткое описание',
            description='Описание',
            width=10, depth=10, height=10,
        )
        self.category.products.add(self.product)
        dt = DeliveryType.objects.create(name='Доставка',
                                         pricing_method=delivery.METHOD_FREE)
        da = DeliveryAddress.objects.create(name='Имя', email='test@test.com',
                                            phone='+79991234567')
        self.order = Order.objects.create(sid='12345', delivery_type=dt,
                                          delivery_address=da,
                                          delivery_price=0)

    def test_reduce_stock_amount(self):
        po = ProductOrder.objects.create(product=self.product,
                                         order=self.order, quantity=1,
                                         price=1000)
        pe = ProductEntry.objects.create(product=self.product, price=1000,
                                         quantity=4.5)
        po.reduce_stock_amount()
        self.assertEqual(po.stock_reduced, True)

        pe = ProductEntry.objects.get(pk=pe.id)
        self.assertEqual(pe.quantity, 3.5)
        with self.assertRaises(RuntimeError):
            po.reduce_stock_amount()

        pe = ProductEntry.objects.get(pk=pe.id)
        self.assertEqual(pe.quantity, 3.5)

    def test_reduce_stock_amount_from_two_entries(self):
        po = ProductOrder.objects.create(product=self.product,
                                         order=self.order, quantity=3,
                                         price=1000)
        pe1 = ProductEntry.objects.create(product=self.product, price=1000,
                                          quantity=1.5)
        pe2 = ProductEntry.objects.create(product=self.product, price=1000,
                                          quantity=2.5)
        po.reduce_stock_amount()
        self.assertEqual(po.stock_reduced, True)

        pe1 = ProductEntry.objects.get(pk=pe1.id)
        self.assertEqual(pe1.quantity, 0)
        pe2 = ProductEntry.objects.get(pk=pe2.id)
        self.assertEqual(pe2.quantity, 1)

    def test_not_enough(self):
        po = ProductOrder.objects.create(product=self.product,
                                         order=self.order, quantity=3,
                                         price=1000)
        pe = ProductEntry.objects.create(product=self.product, price=1000,
                                         quantity=1.5)

        with self.assertRaises(RuntimeError):
            po.reduce_stock_amount()

        self.assertFalse(po.stock_reduced)
        pe = ProductEntry.objects.get(pk=pe.id)
        self.assertEqual(pe.quantity, 1.5)


class OrderTestCase(TestCase):
    def setUp(self):
        self.category = ProductCategory.objects.create(
            name='Категория', slug='category', description='Описание',
            image='/image.png'
        )
        self.product = Product.objects.create(
            name='Продукт', slug='product', price=1000,
            weight=1500, short_description='Короткое описание',
            width=10, depth=10, height=10,
            description='Описание'
        )
        self.category.products.add(self.product)
        self.pe1 = ProductEntry.objects.create(product=self.product,
                                               price=1000, quantity=1.5)
        self.pe2 = ProductEntry.objects.create(product=self.product,
                                               price=1000, quantity=2.5)

        self.dt = DeliveryType.objects.create(
            name='Доставка', pricing_method=delivery.METHOD_CONSTANT,
            price=126)
        da = DeliveryAddress.objects.create(name='Имя', email='test@test.com',
                                            phone='+79991234567')
        self.order = Order.objects.create(sid='12345', delivery_type=self.dt,
                                          delivery_address=da,
                                          delivery_price=126)

        self.po = ProductOrder.objects.create(product=self.product,
                                              order=self.order, quantity=3,
                                              price=1000)

    def test_order(self):
        self.assertEqual(
            self.order.receiver,
            'Имя: Имя\nEmail: test@test.com\nТелефон: +79991234567')
        self.assertEqual(self.order.products_string, ' - Продукт (3 шт);')
        self.assertEqual(self.order.price, 1000)
        self.assertEqual(self.order.full_price, 1126)
        self.assertFalse(self.order.payment_finished, False)
        self.assertFalse(self.order.payment_done, False)
        self.assertEqual(
            [x[0] for x in self.order.get_state_choices()],
            [Order.STATE_CREATED, Order.STATE_CONFIRMED, Order.STATE_DECLINED]
        )

        self.order.reduce_stock_amount()

        pe1 = ProductEntry.objects.get(pk=self.pe1.id)
        self.assertEqual(pe1.quantity, 0)
        pe2 = ProductEntry.objects.get(pk=self.pe2.id)
        self.assertEqual(pe2.quantity, 1)

        po = ProductOrder.objects.get(pk=self.po.id)
        self.assertEqual(po.stock_reduced, True)

        self.order.send_emails()

        # TODO: add_mail testing

    def test_by_order_id(self):
        self.assertEqual(Order.get_by_order_id(str(self.order.uuid)),
                         self.order)

    @mock.patch('django_shop.utils.payment._payment_manager')
    def test_from_form(self, m_pay):
        m_payment = mock.MagicMock()
        m_payment.is_completed = False
        m_payment.is_payed = False
        m_pay.get_object.return_value = m_payment
        m_pay.create_object.return_value = m_payment

        receiver_form = dict(name='Имя', email='test@test.com',
                             phone='+79991234567')
        address_form = {}
        session_key = '12345'
        pm = PaymentType.objects.create(name='Кеш',
                                        payment_type=PaymentType.TYPE_ONLINE)
        order_form = {'delivery_type': self.dt, 'payment_type': pm,
                      'delivery_options': ''}
        products_form = [{'product': self.product, 'amount': Decimal(3)}]
        order = Order.from_forms(products_form, order_form, receiver_form,
                                 address_form, session_key)

        self.assertIsNotNone(order.id)
        self.assertIsNotNone(order.payment)
        self.assertEqual(order.delivery_type, self.dt)
        self.assertEqual(order.price, Decimal(3000))
        self.assertEqual(order.full_price, Decimal(3126))
        self.assertEqual(order.delivery_price, Decimal(126))
        self.assertEqual(order.payment_method, pm)
        self.assertEqual(order.delivery_address.name, 'Имя')
        self.assertEqual(order.delivery_address.email, 'test@test.com')
        self.assertEqual(order.delivery_address.phone, '+79991234567')
        self.assertEqual(order.state, Order.STATE_NC_CREATED)
        self.assertEqual(order.payment_finished, False)
        self.assertEqual(order.payment_done, False)

        p_order = order.products.get()
        self.assertEqual(p_order.product, self.product)
        self.assertEqual(p_order.quantity, Decimal(3))

        m_payment.order_id = order.uuid
        self.assertEqual(Order.get_by_order_id(order.payment.order_id), order)

        m_payment.is_completed = True
        m_payment.is_payed = True

        order = Order.objects.get(pk=order.id)
        order.process_payment()
        self.assertEqual(order.payment_finished, True)
        self.assertEqual(order.payment_done, True)
        self.assertEqual(order.state, Order.STATE_NC_PAID)

        pe1 = ProductEntry.objects.get(pk=self.pe1.id)
        self.assertEqual(pe1.quantity, 0)
        pe2 = ProductEntry.objects.get(pk=self.pe2.id)
        self.assertEqual(pe2.quantity, 1)

        po = ProductOrder.objects.get(pk=p_order.id)
        self.assertEqual(po.stock_reduced, True)

        # TODO: add_mail testing
