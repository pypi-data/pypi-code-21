import re

from django.core.urlresolvers import reverse
from shuup.core.models import Product
from shuup_testutils.generators.shuup.admin_forms import ShuupProductAdminFormsGen
from shuup_testutils.generators.shuup.models import ShuupModelsGen
from shuup_testutils.cases import AuthAdminTestCase


class ShuupFormGenTest(AuthAdminTestCase):
    @classmethod
    def set_up_class(cls):
        super().set_up_class()
        cls.gen = ShuupModelsGen()

    def test_barcode_update(self):
        product_barcode_new = '123123123'
        product = self.gen.product()
        form_gen = ShuupProductAdminFormsGen(product_pk=product.pk)
        form_gen.set_barcode_field(product_barcode_new)
        form = form_gen.get_form()
        response = self.client.post(
            reverse('shuup_admin:shop_product.edit', kwargs={'pk': product.pk}),
            data=form,
            follow=True,
        )
        product_updated = Product.objects.get(pk=product.pk)
        self.assert_contains(response, product_barcode_new)
        self.assert_equal(product_barcode_new, product_updated.barcode)

    def test_name_update(self):
        product_name_new = 'product_name_new'
        product = self.gen.product()
        form_gen = ShuupProductAdminFormsGen(product_pk=product.pk)
        form_gen.set_name_field(product_name_new)
        form = form_gen.get_form()
        response = self.client.post(
            reverse('shuup_admin:shop_product.edit', kwargs={'pk': product.pk}),
            data=form,
            follow=True,
        )
        product_updated = Product.objects.get(pk=product.pk)
        self.assert_contains(response, product_name_new)
        self.assert_not_contains(response, 'This field is required')
        self.assert_equal(product_name_new, product_updated.name)

    def test_product_new_post(self):
        form_gen = ShuupProductAdminFormsGen()
        form_gen.set_name_field('some product name')
        form_gen.set_price_field(42)
        response = self.client.post(
            path=reverse('shuup_admin:shop_product.new'),
            data=form_gen.get_form(),
            follow=True,
        )
        product_created_url = response.wsgi_request.path
        match = re.match('/sa/products/(?P<id>[0-9]+)/', product_created_url)
        is_product_created = match is not None
        self.assert_true(is_product_created)
