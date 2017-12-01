from django.core.urlresolvers import reverse
from shuup.testing.factories import get_default_shop
from shuup_testutils.cases import ApiAuthAdminTestCase
from shuup_testutils.generators import ShuupProductAdminFormsGen

from attrim.testutils.generators import ModelsGen


class ProductTest(ApiAuthAdminTestCase):
    @classmethod
    def set_up_class(cls):
        super().set_up_class()

    def set_up(self):
        super().set_up()
        self.gen = ModelsGen()

    def test_get(self):
        self.gen.attrim.cls()
        product = self.gen.product()
        shop = get_default_shop()
        product_edit_url = reverse(
            viewname='shuup_admin:shop_product.edit',
            kwargs={'pk': product.get_shop_instance(shop).pk},
        )
        self.client.get(product_edit_url)

    def test_post_attr(self):
        cls = self.gen.attrim.cls(options_amount=0)
        option = self.gen.attrim.option(cls=cls)
        option_field_name = 'form-0-options'
        product = self.gen.product()
        shop_product_pk = product.get_shop_instance(get_default_shop()).pk
        form_gen = ShuupProductAdminFormsGen(product_pk=shop_product_pk)
        form_gen.set_field(field_name=option_field_name, field_value=option.pk)
        self.client.post(
            path=reverse('shuup_admin:shop_product.edit', kwargs={'pk': shop_product_pk}),
            data=form_gen.get_form(),
        )
        product.attrim_attrs.get(option=option)
