import unittest

import tecplot
from tecplot.constant import *
from tecplot.exception import *
from tecplot.export.print_setup import PrintSetup
import platform
from test import skip_windows


_IS_WINDOWS = platform.system() == 'Windows'


class TestPrintSetup(unittest.TestCase):
    def setUp(self):
        self.setup = PrintSetup()

        if platform.system() == 'Windows':
            # In Windows, we need to explicitly set USETECPLOTPRINTDRIVERS
            # to TRUE in order to change other settings. The default
            # is FALSE in non-Windows
            tecplot.macro.execute_command(
                '$!INTERFACE USETECPLOTPRINTDRIVERS=TRUE')

    def tearDown(self):
        if platform.system() == 'Windows':
            # Restore the default in Windows
            tecplot.macro.execute_command(
                '$!INTERFACE USETECPLOTPRINTDRIVERS=FALSE')

    def test_setting_none(self):
        if not _IS_WINDOWS:
            self.setup.driver = PrinterDriver.PS
            self.setup.driver = None
            self.assertEqual(self.setup.driver, PrinterDriver.PS)

        self.setup.extra_precision = 2
        self.setup.extra_precision = None
        self.assertEqual(self.setup.extra_precision, 2)

        self.setup.filename = 'testfile'
        self.setup.filename = None
        self.assertEqual(self.setup.filename, 'testfile')

        self.setup.force_extra_3d_sorting = True
        self.setup.force_extra_3d_sorting = None
        self.assertEqual(self.setup.force_extra_3d_sorting, True)

        if not _IS_WINDOWS:
            self.setup.lg_mopup = 'test'
            self.setup.lg_mopup = None
            self.assertEqual(self.setup.lg_mopup, 'test')

            self.setup.lg_setup = 'test'
            self.setup.lg_setup = None
            self.assertEqual(self.setup.lg_setup, 'test')

        self.setup.num_copies = 2
        self.setup.num_copies = None
        self.assertEqual(self.setup.num_copies, 2)

        self.setup.num_shades = 2
        self.setup.num_shades = None
        self.assertEqual(self.setup.num_shades, 2)

        self.setup.palette = Palette.Color
        self.setup.palette = None
        self.assertEqual(self.setup.palette, Palette.Color)

        if not _IS_WINDOWS:
            self.setup.post_mopup = 'test'
            self.setup.post_mopup = None
            self.assertEqual(self.setup.post_mopup, 'test')

            self.setup.post_setup = 'test'
            self.setup.post_setup = None
            self.assertEqual(self.setup.post_setup, 'test')

        self.setup.print_to_file = True
        self.setup.print_to_file = None
        self.assertEqual(self.setup.print_to_file, True)

        self.setup.render_type = PrintRenderType.Vector
        self.setup.render_type = None
        self.assertEqual(self.setup.render_type, PrintRenderType.Vector)

        self.setup.resolution = 20
        self.setup.resolution = None
        self.assertEqual(self.setup.resolution, 20)

        self.setup.rgb_legend_resolution = 20
        self.setup.rgb_legend_resolution = None
        self.assertEqual(self.setup.rgb_legend_resolution, 20)

        if not _IS_WINDOWS:
            self.setup.spool_cmd_lg = 'test'
            self.setup.spool_cmd_lg = None
            self.assertEqual(self.setup.spool_cmd_lg, 'test')

            self.setup.spool_cmd_ps_color = 'test'
            self.setup.spool_cmd_ps_color = None
            self.assertEqual(self.setup.spool_cmd_ps_color, 'test')

            self.setup.spool_cmd_ps_mono = 'test'
            self.setup.spool_cmd_ps_mono = None
            self.assertEqual(self.setup.spool_cmd_ps_mono, 'test')

        self.setup.use_latin1_fonts = False
        self.setup.use_latin1_fonts = None
        self.assertEqual(self.setup.use_latin1_fonts, False)

    @skip_windows()
    def test_driver(self):
        for val in [PrinterDriver.EPS, PrinterDriver.PS]:
            self.setup.driver = val
            self.assertEqual(self.setup.driver, val)
        with self.assertRaises(ValueError):
            self.setup.driver = 0.5
        with self.assertRaises(ValueError):
            self.setup.driver = 'badvalue'
        with self.assertRaises(TecplotSystemError):
            self.setup.driver = PrinterDriver.WMF

    def test_extra_precision(self):
        for val in [0,1,8]:
            self.setup.extra_precision = val
            self.assertEqual(self.setup.extra_precision, val)
        with self.assertRaises(ValueError):
            self.setup.extra_precision = 'badtype'

    def test_filename(self):
        for val in ['aa', '11', 0, 3.14]:
            self.setup.filename = val
            self.assertEqual(self.setup.filename, str(val))

    def test_force_extra_3d_sorting(self):
        for val in [True, False, True]:
            self.setup.force_extra_3d_sorting = val
            self.assertEqual(self.setup.force_extra_3d_sorting, val)

    @skip_windows()
    def test_lg_mopup(self):
        for val in ['aa', '11', 0, 3.14]:
            self.setup.lg_mopup = val
            self.assertEqual(self.setup.lg_mopup, str(val))

    @skip_windows()
    def test_lg_setup(self):
        for val in ['aa', '11', 0, 3.14]:
            self.setup.lg_setup = val
            self.assertEqual(self.setup.lg_setup, str(val))

    def test_num_copies(self):
        for val in [1,2]:
            self.setup.num_copies = val
            self.assertEqual(self.setup.num_copies, val)
        with self.assertRaises(ValueError):
            self.setup.num_copies = 'badtype'
        with self.assertRaises(TecplotSystemError):
            self.setup.num_copies = 0

    def test_num_shades(self):
        for val in [2,100,10000]:
            self.setup.num_shades = val
            self.assertEqual(self.setup.num_shades, val)
        with self.assertRaises(ValueError):
            self.setup.num_shades = 'badtype'
        with self.assertRaises(TecplotSystemError):
            self.setup.num_shades = 0
        with self.assertRaises(TecplotSystemError):
            self.setup.num_shades = 1

    def test_palette(self):
        for val in [Palette.Color, Palette.Monochrome]:
            self.setup.palette = val
            self.assertEqual(self.setup.palette, val)
        with self.assertRaises(ValueError):
            self.setup.palette = 0.5
        with self.assertRaises(ValueError):
            self.setup.palette = 'badvalue'

    @skip_windows()
    def test_post_mopup(self):
        for val in ['aa', '11', 0, 3.14]:
            self.setup.post_mopup = val
            self.assertEqual(self.setup.post_mopup, str(val))

    @skip_windows()
    def test_post_setup(self):
        for val in ['aa', '11', 0, 3.14]:
            self.setup.post_setup = val
            self.assertEqual(self.setup.post_setup, str(val))

    def test_print_to_file(self):
        for val in [True, False, True]:
            self.setup.print_to_file = val
            self.assertEqual(self.setup.print_to_file, val)

    def test_render_type(self):
        for val in [PrintRenderType.Image, PrintRenderType.Vector]:
            self.setup.render_type = val
            self.assertEqual(self.setup.render_type, val)
        with self.assertRaises(ValueError):
            self.setup.render_type = 0.5
        with self.assertRaises(ValueError):
            self.setup.render_type = 'badvalue'

    def test_resolution(self):
        for val in [1,2,100,10000]:
            self.setup.resolution = val
            self.assertEqual(self.setup.resolution, val)
        with self.assertRaises(ValueError):
            self.setup.resolution = 'badtype'
        with self.assertRaises(TecplotSystemError):
            self.setup.resolution = 0

    def test_rgb_legend_resolution(self):
        for val in [1,2,100]:
            self.setup.rgb_legend_resolution = val
            self.assertEqual(self.setup.rgb_legend_resolution, val)
        with self.assertRaises(ValueError):
            self.setup.rgb_legend_resolution = 'badtype'
        with self.assertRaises(TecplotSystemError):
            self.setup.rgb_legend_resolution = 0

    @skip_windows()
    def test_spool_cmd_lg(self):
        for val in ['aa', '11', 0, 3.14]:
            self.setup.spool_cmd_lg = val
            self.assertEqual(self.setup.spool_cmd_lg, str(val))

    @skip_windows()
    def test_spool_cmd_ps_color(self):
        for val in ['aa', '11', 0, 3.14]:
            self.setup.spool_cmd_ps_color = val
            self.assertEqual(self.setup.spool_cmd_ps_color, str(val))

    @skip_windows()
    def test_spool_cmd_ps_mono(self):
        for val in ['aa', '11', 0, 3.14]:
            self.setup.spool_cmd_ps_mono = val
            self.assertEqual(self.setup.spool_cmd_ps_mono, str(val))

    def test_use_latin1_fonts(self):
        for val in [True, False, True]:
            self.setup.use_latin1_fonts = val
            self.assertEqual(self.setup.use_latin1_fonts, val)


if __name__ == '__main__':
    from .. import main
    main()
