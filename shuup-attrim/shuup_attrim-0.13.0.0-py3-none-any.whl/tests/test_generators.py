from parler.utils.context import switch_language
from shuup_testutils.cases import SnakeTestCase
from shuup_utils.lang_constants import LANG_CODES

from attrim.testutils.generators import ModelsGen
from attrim.models.type import Type


class GeneratorTest(SnakeTestCase):
    def set_up(self):
        self.gen = ModelsGen()

    def test_cls_int_options(self):
        cls = self.gen.attrim.cls(type=Type.INT, options_amount=5)
        for option in cls.options.all():
            self.assert_true(isinstance(option.get_value(), int))

    def test_cls_str_options(self):
        cls = self.gen.attrim.cls(type=Type.STR, options_amount=5)
        for option in cls.options.all():
            self.assert_true(len(option.get_value()) > 0)
            self.assert_true(isinstance(option.get_value(), str))

    def test_cls_trans_str_options(self):
        cls = self.gen.attrim.cls(type=Type.TRANS_STR, options_amount=5)
        for option in cls.options.all():
            for lang_code in LANG_CODES:
                with switch_language(option, lang_code):
                    self.assert_true(len(option.get_value()) > 0)

    def test_cls_int_options_amount(self):
        self._test_options_amount(Type.INT)

    def test_cls_str_options_amount(self):
        self._test_options_amount(Type.STR)

    def test_cls_trans_str_options_amount(self):
        self._test_options_amount(Type.TRANS_STR)

    # noinspection PyShadowingBuiltins
    def _test_options_amount(self, type: Type):
        amount_expected = 5
        cls = self.gen.attrim.cls(type=type, options_amount=amount_expected)
        amount_actual = len(cls.options.all())
        self.assert_equal(amount_expected, amount_actual)
