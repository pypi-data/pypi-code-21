from parler.utils.context import switch_language
from shuup_testutils.cases import SnakeTestCase
from shuup_utils.lang_constants import LANG_CODES

from attrim.testutils.generators import ModelsGen
from attrim.trans_str import TransStr
from attrim.models.type import Type


class ClsTransStrTest(SnakeTestCase):
    def test_cls_name(self):
        gen = ModelsGen()
        cls_name = gen.attrim.name() # type: TransStr
        cls = gen.attrim.cls(name=cls_name, type=Type.TRANS_STR)
        for lang_code in LANG_CODES:
            with switch_language(cls, lang_code):
                cls_name_expected = cls_name[lang_code]
                self.assert_equal(cls_name_expected, actual=cls.name)
