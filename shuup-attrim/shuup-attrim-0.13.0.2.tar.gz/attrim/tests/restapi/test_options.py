from typing import List

from parler.utils.context import switch_language
from rest_framework.reverse import reverse
from shuup_testutils.cases import ApiAuthAdminTestCase
from shuup_utils.lang_constants import LANG_CODES, DEFAULT_LANG

from attrim.models import Option, Attribute
from attrim.models.type import Type
from attrim.testutils.generators import ModelsGen
from attrim.trans_str import TransStr


class OptionsRestapiTest(ApiAuthAdminTestCase):
    def set_up(self):
        super().set_up()
        self.gen = ModelsGen()

    def test_get(self):
        cls = self.gen.attrim.cls()
        options = self.gen.attrim.option_list(cls=cls) # type: List[Option]

        response = self.client.get(reverse('option-list'))
        for option in options:
            for lang_code in LANG_CODES:
                with switch_language(option, lang_code):
                    self.assert_contains(response, option.get_value())

    def test_delete(self):
        cls = self.gen.attrim.cls(type=Type.TRANS_STR)
        option = self.gen.attrim.option(cls=cls)

        self.client.delete(
            path=reverse('option-detail', kwargs={'pk': option.pk}),
            format='json',
        )
        with self.assert_raises(Option.DoesNotExist):
            Option.objects.get(pk=option.pk)

    def test_create_trans_str(self):
        cls = self.gen.attrim.cls(type=Type.TRANS_STR, options_amount=0)

        value_expected = 'english value'
        self.client.post(reverse('option-list'), format='json', data=dict(
            cls=cls.pk,
            value=dict(
                en=value_expected,
            ),
        ))
        option = Option.objects.get(cls=cls)
        self.assert_equal(value_expected, actual=option.get_value())

    def test_create_int(self):
        cls = self.gen.attrim.cls(type=Type.INT, options_amount=0)

        value_expected = 42
        self.client.post(reverse('option-list'), format='json', data=dict(
            cls=cls.pk,
            value=value_expected,
        ))
        option = Option.objects.get(cls=cls)
        self.assert_equal(value_expected, actual=option.get_value())

    def test_update_trans_str(self):
        cls = self.gen.attrim.cls(type=Type.TRANS_STR, options_amount=0)
        option = self.gen.attrim.option(cls=cls)

        value_new = 'new value'
        self.client.patch(
            path=reverse('option-detail', kwargs={'pk': option.pk}),
            format='json',
            data=dict(
                cls=cls.pk,
                value={
                    DEFAULT_LANG: value_new,
                },
            ),
        )
        option_updated = Option.objects.get(pk=option.pk)
        self.assert_equal(expected=value_new, actual=option_updated.get_value())

    def test_add_attribute(self):
        cls = self.gen.attrim.cls(type=Type.TRANS_STR, options_amount=0)
        option_value = self.gen.attrim.trans_str()  # type: TransStr
        option = self.gen.attrim.option(cls=cls, value=option_value)

        product = self.gen.product()
        attribute_new = Attribute.objects.create(product=product, cls=cls)
        self.client.patch(
            path=reverse('option-detail', kwargs={'pk': option.pk}),
            format='json',
            data=dict(
                cls=cls.pk,
                value=option_value.as_dict(),
                attributes=[attribute_new.pk],
            ),
        )
        option_updated = Option.objects.get(pk=option.pk)
        self.assert_equal(expected=attribute_new, actual=option_updated.attributes.first())

    def test_update_order(self):
        cls = self.gen.attrim.cls(type=Type.INT, options_amount=0)
        option = self.gen.attrim.option(cls=cls)
        option_order_new = 6
        self.client.patch(
            path=reverse('option-detail', kwargs={'pk': option.pk}),
            format='json',
            data=dict(
                cls=cls.pk,
                value=option.get_value(),
                order=option_order_new,
            ),
        )
        option_updated = Option.objects.get(pk=option.pk)
        self.assert_equal(expected=option_order_new, actual=option_updated.order)

    def test_update_order_with_none(self):
        cls = self.gen.attrim.cls(type=Type.INT, options_amount=0)
        option = self.gen.attrim.option(cls=cls, order=5)
        self.client.patch(
            path=reverse('option-detail', kwargs={'pk': option.pk}),
            format='json',
            data=dict(
                cls=cls.pk,
                value=option.get_value(),
                order=None,
            ),
        )
        option_updated = Option.objects.get(pk=option.pk)
        self.assert_equal(expected=None, actual=option_updated.order)
