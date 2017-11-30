from parler.utils.context import switch_language
from shuup_testutils.cases import SnakeTestCase
from shuup_utils.lang_constants import LANG_CODES

from attrim.models import Option
from attrim.models.type import Type
from attrim.testutils.generators import ModelsGen
from attrim.trans_str import TransStr


class AttributesTest(SnakeTestCase):
    def set_up(self):
        self.gen = ModelsGen()

    def test_options_set(self):
        cls = self.gen.attrim.cls(options_amount=0)
        options = self.gen.attrim.option_list(cls=cls, amount=5)
        product = self.gen.product()
        
        attr = product.attrim_attrs.create(cls=cls)
        attr_option_expected = options[0]
        attr.options.set([attr_option_expected])
        
        attr_option = attr.options.first()
        self.assert_equal(attr_option_expected, actual=attr_option)

    def test_options_order(self):
        cls = self.gen.attrim.cls(options_amount=0)
        options = self.gen.attrim.option_list(cls=cls, amount=5)
        product = self.gen.product()
        
        attr_options_expected = [options[0], options[1]]
        attr = product.attrim_attrs.create(cls=cls)
        attr.options.set(attr_options_expected)
        attr_options = list(attr.options.all())
        self.assert_equal(attr_options_expected, actual=attr_options)

    def test_options_trans_str(self):
        cls = self.gen.attrim.cls(options_amount=0, type=Type.TRANS_STR)
        option_value = self.gen.attrim.trans_str() # type: TransStr
        option = Option.objects.create(cls=cls, value=option_value)
        product = self.gen.product()
        attr = product.attrim_attrs.create(cls=cls)
        attr.options.set([option])
        
        for lang_code in LANG_CODES:
            attr_option = attr.options.first()
            with switch_language(attr_option, lang_code):
                self.assert_equal(
                    expected=option_value[lang_code],
                    actual=attr_option.get_value(),
                )
