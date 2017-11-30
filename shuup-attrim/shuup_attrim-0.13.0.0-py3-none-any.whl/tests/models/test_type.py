from shuup_testutils.cases import SnakeTestCase
from shuup_utils.lang_constants import LANG_CODES

from attrim.trans_str import TransStr


class TypeTest(SnakeTestCase):
    def test_trans_str_type_with_invalid_lang_code(self):
        lang_code_invalid = 'ri'
        self.assert_true(lang_code_invalid not in LANG_CODES)
        with self.assert_raises(ValueError):
            TransStr(**{lang_code_invalid: 'value'})

    def test_trans_str_type_with_valid_lang_code(self):
        lang_code_valid = LANG_CODES[0]
        TransStr(**{lang_code_valid: 'value'})
