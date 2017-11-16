import unittest
import tecplot as tp
from tecplot.version import sdk_version_info
from .recording_util import *

from test import skip_if_connected


@unittest.skipIf(sdk_version_info < (2017, 3, 0, 81450),
                 '2017 R3 is required for macro translate unit tests.')
class TestTranslateExecuteMacro(unittest.TestCase):
    @skip_if_connected
    def setUp(self):
        tp.new_layout()

    def check_result_is_comment(self, command):
        for line in translate(command).split('\n'):
            self.assertTrue(line.startswith('#'))

    def test_execute_invalid_macro_command(self):
        translated = translate(
            '$!INVALID_COMMAND')
        self.assertTrue(translated.startswith('#'))

    def test_execute_valid_macro_command(self):
        # $!PICK CUT will probably never exist in the pytecplot API
        translated = translate(
            '$!PICK CUT')
        self.assertFalse(translated.startswith('#'))
        self.assertIn('tp.macro.execute_command', translated)

    def test_commands_may_start_and_end_with_a_newline(self):
        # i.e., check that the translating engine trims the input
        # string.
        translated = translate(
            '\n$!CREATECIRCULARZONE \n  IMAX = 10\n  JMAX = 25\n  KMAX = 10\n')
        self.assertFalse(translated.startswith('#'))
        self.assertIn('tp.macro.execute_command', translated)

    def test_record_macro_comment(self):
        translated = translate(
            '#Comment')
        self.assertEqual(translated, '#Comment')

    def test_macro_command_strings_should_be_double_quoted(self):
        self.assertIn('"$!SYSTEM \'abc\'"', translate(r"$!SYSTEM 'abc'"))

    def test_invalid_macro_recorded_as_comment(self):
        self.check_result_is_comment('$!abc')

if __name__ == '__main__':
    from .. import main
    main()
