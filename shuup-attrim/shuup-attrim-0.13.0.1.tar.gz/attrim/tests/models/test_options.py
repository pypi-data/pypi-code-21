from shuup_testutils.cases import SnakeTestCase
from shuup_utils.lang_constants import DEFAULT_LANG

from attrim.models import Option
from attrim.models.type import Type
from attrim.testutils.generators import ModelsGen
from attrim.trans_str import TransStr


class OptionsTest(SnakeTestCase):
    def set_up(self):
        self.gen = ModelsGen()

    def test_option_get_type_str(self):
        cls = self.gen.attrim.cls(options_amount=0, type=Type.STR)
        option_value = 'value str'
        option_source = self.gen.attrim.option(cls=cls, value=option_value)
        option = Option.objects.get(cls=cls, value=option_value)
        self.assert_equal(option_source, option)

    def test_option_get_type_trans_str_in_default_lang(self):
        cls = self.gen.attrim.cls(options_amount=0, type=Type.TRANS_STR)
        option_value = 'value in default lang'
        option_value_trans_str = TransStr(**{DEFAULT_LANG: option_value})
        option_source = self.gen.attrim.option(cls=cls, value=option_value_trans_str)
        option = Option.objects.get(cls=cls, value=option_value)
        self.assert_equal(option_source, option)

    def test_option_get_type_trans_str(self):
        cls = self.gen.attrim.cls(options_amount=0, type=Type.TRANS_STR)
        option_value = 'value in some lang'
        option_value_trans_str = TransStr(fi=option_value)
        option_source = self.gen.attrim.option(cls=cls, value=option_value_trans_str)
        option = Option.objects.get(cls=cls, value=option_value_trans_str)
        self.assert_equal(option_source, option)

    def test_option_get_type_str_on_cls(self):
        cls = self.gen.attrim.cls(options_amount=0, type=Type.STR)
        option_value = 'value str'
        option_source = self.gen.attrim.option(cls=cls, value=option_value)
        option = cls.options.get(value=option_value)
        self.assert_equal(option_source, option)

    def test_option_get_invalid_with_exception(self):
        cls = self.gen.attrim.cls(options_amount=0, type=Type.STR)
        option_value = 'value str'
        self.gen.attrim.option(cls=cls, value=option_value)
        with self.assert_raises(ValueError):
            Option.objects.get(value=option_value)
