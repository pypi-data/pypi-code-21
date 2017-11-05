# coding=utf-8
from __future__ import unicode_literals, absolute_import

from django.test import TestCase

from ..views import CartModifyFormView
from ..forms import CartModifyForm
from ..models import ProductCategory, Product, ProductEntry


class BasketModificationViewTestCase(TestCase):
    def setUp(self):
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

    def _get_response(self, remove_fields=None, **data):
        post_data = {'action': CartModifyForm.ACTION_ADD, 'product': self.p1.id,
                     'amount': 1.4, 'response': CartModifyForm.RESPONSE_MINIMAL}
        post_data.update(data)
        if remove_fields is not None:
            for f in remove_fields:
                del post_data[f]

        res = self.client.post('/cart/modify/', post_data,
                               HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.resolver_match.func.__name__,
                         CartModifyFormView.as_view().__name__)
        return res

    def test_invalid_requests(self):
        response = self.client.get('/cart/modify/')
        self.assertEqual(response.status_code, 405)

        response = self.client.post('/cart/modify/')
        self.assertEqual(response.status_code, 400)

    def test_correct_actions(self):
        response = self._get_response()
        data = response.json()
        self.assertEqual(data['success'], True)
        self.assertEqual(data['basket'], {'items_num': 1, 'price': 1400})

        response = self._get_response(product=self.p2.id, amount=2)
        data = response.json()
        self.assertEqual(data['success'], True)
        self.assertEqual(data['basket'], {'items_num': 2, 'price': 2400})

        response = self._get_response(product=self.p1.id, amount=2,
                                      action=CartModifyForm.ACTION_SET)
        data = response.json()
        self.assertEqual(data['success'], True)
        self.assertEqual(data['basket'], {'items_num': 2, 'price': 3000})

        response = self._get_response(remove_fields=['amount'], product=self.p1.id,
                                      action=CartModifyForm.ACTION_REMOVE)
        data = response.json()
        self.assertEqual(data['success'], True)
        self.assertEqual(data['basket'], {'items_num': 1, 'price': 1000})

    def test_errors(self):
        response = self._get_response(remove_fields=['amount'])
        data = response.json()
        self.assertEqual(data['success'], False)

        response = self._get_response(remove_fields=['action'])
        data = response.json()
        self.assertEqual(data['success'], False)
