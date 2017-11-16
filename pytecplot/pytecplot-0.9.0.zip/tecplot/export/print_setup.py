from builtins import super, int

from ..tecutil import sv
from ..constant import *
from .. import session
import platform
import tecplot as tp
import functools


# Except for a select few commands needed by the exporters,
# $!PrintSetup commands should not be supported in Windows.
# We should never expose $!PrintSetup in the pytecplot api.
_IS_WINDOWS = platform.system() == 'Windows'


class PrintSetup(session.Style):
    def __init__(self):
        super().__init__(sv.PRINTSETUP)

    def reset(self):
        '''
        This should probably be a TecUtil function
        like TecUtilExportReset(StyleBase_e)
        several of these are commented out to maintain
        pre-existing behavior.
        '''
        self.driver = PrinterDriver.PS
        self.filename = 'untitled.ps'

        self.force_extra_3d_sorting = False
        self.lg_mopup = ''
        self.lg_setup = ''
        self.num_copies = 1
        self.num_shades = 80
        self.palette = Palette.Color if platform.system() == 'Windows' else Palette.Monochrome
        self.post_mopup = ''
        self.post_setup = ''
        self.print_to_file = False if platform.system() == 'Windows' else True
        self.render_type = PrintRenderType.Vector
        self.resolution = 150
        self.rgb_legend_resolution = 20
        self.spool_cmd_lg = ''
        self.spool_cmd_ps_color = ''
        self.spool_cmd_ps_mono = ''
        self.use_latin1_fonts = True

    @property
    def driver(self):
        return self._get_style(PrinterDriver, sv.DRIVER)

    @driver.setter
    def driver(self, value):
        if not _IS_WINDOWS:
            if value is not None:
                self._set_style(PrinterDriver(value), sv.DRIVER)

    @property
    def extra_precision(self):
        return self._get_style(int, sv.PRECISION)

    @extra_precision.setter
    def extra_precision(self, value):
        if value is not None:
            self._set_style(int(value), sv.PRECISION)

    @property
    def filename(self):
        return self._get_style(str, sv.PRINTFNAME)

    @filename.setter
    def filename(self, value):
        if value is not None:
            self._set_style(str(value), sv.PRINTFNAME)
    @property
    def force_extra_3d_sorting(self):
        return self._get_style(bool, sv.FORCEEXTRA3DSORTING)

    @force_extra_3d_sorting.setter
    def force_extra_3d_sorting(self, value):
        if value is not None:
            self._set_style(bool(value), sv.FORCEEXTRA3DSORTING)

    @property
    def lg_mopup(self):
        return self._get_style(str, sv.JOBCONTROL, sv.LGMOPUPSTR)

    @lg_mopup.setter
    def lg_mopup(self, value):
        if not _IS_WINDOWS:
            if value is not None:
                self._set_style(str(value), sv.JOBCONTROL, sv.LGMOPUPSTR)

    @property
    def lg_setup(self):
        return self._get_style(str, sv.JOBCONTROL, sv.LGSETUPSTR)

    @lg_setup.setter
    def lg_setup(self, value):
        if not _IS_WINDOWS:
            if value is not None:
                self._set_style(str(value), sv.JOBCONTROL, sv.LGSETUPSTR)

    @property
    def num_copies(self):
        return self._get_style(int, sv.NUMHARDCOPYCOPIES)

    @num_copies.setter
    def num_copies(self, value):
        if value is not None:
            self._set_style(int(value), sv.NUMHARDCOPYCOPIES)

    @property
    def num_shades(self):
        return self._get_style(int, sv.NUMLIGHTSOURCESHADES)

    @num_shades.setter
    def num_shades(self, value):
        if value is not None:
            self._set_style(int(value), sv.NUMLIGHTSOURCESHADES)

    @property
    def palette(self):
        return self._get_style(Palette, sv.PALETTE)

    @palette.setter
    def palette(self, value):
        if value is not None:
            self._set_style(Palette(value), sv.PALETTE)

    @property
    def post_mopup(self):
        return self._get_style(str, sv.JOBCONTROL, sv.POSTMOPUPSTR)

    @post_mopup.setter
    def post_mopup(self, value):
        if not _IS_WINDOWS:
            if value is not None:
                self._set_style(str(value), sv.JOBCONTROL, sv.POSTMOPUPSTR)

    @property
    def post_setup(self):
        return self._get_style(str, sv.JOBCONTROL, sv.POSTSETUPSTR)

    @post_setup.setter
    def post_setup(self, value):
        if not _IS_WINDOWS:
            if value is not None:
                self._set_style(str(value), sv.JOBCONTROL, sv.POSTSETUPSTR)

    @property
    def print_to_file(self):
        return self._get_style(bool, sv.SENDPRINTTOFILE)

    @print_to_file.setter
    def print_to_file(self, value):
        if value is not None:
            self._set_style(bool(value), sv.SENDPRINTTOFILE)

    @property
    def render_type(self):
        return self._get_style(PrintRenderType, sv.PRINTRENDERTYPE)

    @render_type.setter
    def render_type(self, value):
        if value is not None:
            self._set_style(PrintRenderType(value), sv.PRINTRENDERTYPE)

    @property
    def resolution(self):
        return self._get_style(int, sv.IMAGERESOLUTION)

    @resolution.setter
    def resolution(self, value):
        if value is not None:
            self._set_style(int(value), sv.IMAGERESOLUTION)

    @property
    def rgb_legend_resolution(self):
        return self._get_style(int, sv.RGBLEGENDOUTPUTRESOLUTION)

    @rgb_legend_resolution.setter
    def rgb_legend_resolution(self, value):
        if value is not None:
            self._set_style(int(value), sv.RGBLEGENDOUTPUTRESOLUTION)

    @property
    def spool_cmd_lg(self):
        return self._get_style(str, sv.SPOOLER, sv.LGSPOOLCMD)

    @spool_cmd_lg.setter
    def spool_cmd_lg(self, value):
        if not _IS_WINDOWS:
            if value is not None:
                self._set_style(str(value), sv.SPOOLER, sv.LGSPOOLCMD)

    @property
    def spool_cmd_ps_color(self):
        return self._get_style(str, sv.SPOOLER, sv.PSCOLORSPOOLCMD)

    @spool_cmd_ps_color.setter
    def spool_cmd_ps_color(self, value):
        if not _IS_WINDOWS:
            if value is not None:
                self._set_style(str(value), sv.SPOOLER, sv.PSCOLORSPOOLCMD)

    @property
    def spool_cmd_ps_mono(self):
        return self._get_style(str, sv.SPOOLER, sv.PSMONOSPOOLCMD)

    @spool_cmd_ps_mono.setter
    def spool_cmd_ps_mono(self, value):
        if not _IS_WINDOWS:
            if value is not None:
                self._set_style(str(value), sv.SPOOLER, sv.PSMONOSPOOLCMD)

    @property
    def use_latin1_fonts(self):
        return self._get_style(bool, sv.USEISOLATIN1FONTSINPS)

    @use_latin1_fonts.setter
    def use_latin1_fonts(self, value):
        if value is not None:
            self._set_style(bool(value), sv.USEISOLATIN1FONTSINPS)
