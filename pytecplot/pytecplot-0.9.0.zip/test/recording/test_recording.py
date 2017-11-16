import os
import unittest
import tecplot as tp
from tempfile import NamedTemporaryFile
from tecplot import tecutil, macro
from tecplot.version import sdk_version_info
import re

from test import skip_if_connected

@unittest.skipIf(sdk_version_info < (2017, 3, 0, 82552),
                 '2017 R3 is required for macro translate unit tests.')
class TestRecording(unittest.TestCase):
    def setUp(self):
        tp.new_layout()

    def check_mcr_file_header(self, file_header):
        first_line = file_header.split('\n')[0]
        self.assertIsNotNone(re.match(r'^#!MC\s\d\d\d\d\s*', first_line))

    def record_file(self, suffix, commands_to_run=None):
        file = NamedTemporaryFile(suffix=suffix, delete=False)
        file.close()  # Just need the name
        self.assertFalse(tecutil._tecutil_connector.tecutil_handle.tecUtilMacroIsRecordingActive())
        result = tecutil._tecutil_connector.macro_record_start(file.name)
        self.assertTrue(result)
        self.assertTrue(tecutil._tecutil_connector.tecutil_handle.tecUtilMacroIsRecordingActive())

        if commands_to_run is not None:
            for cmd in commands_to_run:
                macro.execute_command(cmd)

        tecutil._tecutil_connector.macro_record_end()
        self.assertFalse(tecutil._tecutil_connector.tecutil_handle.tecUtilMacroIsRecordingActive())
        self.assertTrue(os.path.exists(file.name))
        try:
            with open(file.name, 'r') as f:
                file_contents = f.read()
        finally:
            try:
                os.remove(file.name)
            except OSError as e:
                self.fail(msg='Could not delete temporary file:'.format(e))
        return file_contents

    @skip_if_connected
    def test_play_macro(self):
        tecplot_macro_file = NamedTemporaryFile(suffix='.mcr', delete=False)
        tecplot_macro_file.close()

        # No need to actually record any macro commands since we're
        # going to be checking for the filename.
        tecutil._tecutil_connector.macro_record_start(tecplot_macro_file.name)
        tecutil._tecutil_connector.macro_record_end()

        pytecplot_macro_file = NamedTemporaryFile(suffix='.py', delete=False)
        pytecplot_macro_file.close()

        tecutil._tecutil_connector.macro_record_start(pytecplot_macro_file.name)
        # The closest way to simulate the user selecting
        # Macro/Play Macro is to record an macro.execute_file() command,
        # which will end up in Action_RunFile(), which will record
        # macro.execute_file()
        tp.macro.execute_file(tecplot_macro_file.name)
        tecutil._tecutil_connector.macro_record_end()

        try:
            with open(pytecplot_macro_file.name, 'r') as f:
                file_contents = f.read()
                final_name = tecplot_macro_file.name.replace('\\', '\\\\')
                self.assertIn("macro.execute_file('{}')".format(final_name),
                              file_contents)
        finally:
            try:
                os.remove(tecplot_macro_file.name)
                os.remove(pytecplot_macro_file.name)
            except OSError as e:
                self.fail(msg='Could not delete temporary file:'.format(e))

    @skip_if_connected
    def test_that_a_real_pytecplot_file_is_recorded(self):
        file_contents = self.record_file('.py')
        self.assertIn('import tecplot', file_contents)

    @skip_if_connected
    def test_that_mcr_recording_without_raw_data_is_not_broken(self):
        file_contents = self.record_file('.mcr', [
            '''
            $!CREATERECTANGULARZONE
  IMAX = 10
  JMAX = 10
  KMAX = 10
  X1 = 0
  Y1 = 0
  Z1 = 0
  X2 = 1
  Y2 = 1
  Z2 = 1
  XVAR = 1
  YVAR = 2
  ZVAR = 3'''
        ])
        self.check_mcr_file_header(file_contents)
        self.assertIn('$!CREATERECTANGULARZONE', file_contents.upper())

    @skip_if_connected
    def test_that_mcr_recording_with_raw_data_is_not_broken(self):
        expected_contents ='''
$!ATTACHGEOM
  ANCHORPOS
    {
    X = 0.2787855444785277
    Y = 0.8375070552147239
    }
  RAWDATA
1
6
0 0
0.0122711658478 -0.561405837536
0.26843175292 -0.475507676601
0.427956908941 -0.0828303694725
0.233152151108 -0.0306779146194
0.665710747242 -0.549134671688'''
        file_contents = self.record_file('.mcr', [expected_contents])
        self.check_mcr_file_header(file_contents)
        self.assertIn(expected_contents, re.sub(r'\s*\n', r'\n', file_contents.upper()))


if __name__ == '__main__':
    from .. import main
    main()
