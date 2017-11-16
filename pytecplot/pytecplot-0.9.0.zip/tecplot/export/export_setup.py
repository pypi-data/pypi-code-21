from builtins import super, int

from ..tecutil import sv
from ..exception import *
from ..constant import *
from .. import session


class ExportSetup(session.Style):
    def __init__(self):
        super().__init__(sv.EXPORTSETUP)

    def reset(self):
        '''
        This should probably be a TecUtil function
        like TecUtilExportReset(StyleBase_e)
        several of these are commented out to maintain
        pre-existing behavior.
        '''
        # self.animation_speed = None
        # self.avi_compression = None
        self.convert_to_256_colors = False
        # self.filename = None
        # self.flash_compression_type = None
        # self.flash_image_type = None
        # self.format = None
        self.gray_scale_depth = 8
        # self.jpeg_encoding = None
        # self.multiple_color_tables = None
        self.quality = 75
        # self.quality_scale = None
        self.region = ExportRegion.CurrentFrame
        # self.render_type = None
        self.supersample = 1
        self.tiff_byte_order = TIFFByteOrder.Intel
        self.width = 512


    @property
    def animation_speed(self):
        return self._get_style(float, sv.ANIMATIONSPEED)

    @animation_speed.setter
    def animation_speed(self, value):
        if value is not None:
            self._set_style(float(value), sv.ANIMATIONSPEED)

    @property
    def avi_compression(self):
        return self._get_style(AVICompression, sv.AVICOMPRESSION)

    @avi_compression.setter
    def avi_compression(self, value):
        if value is not None:
            self._set_style(AVICompression(value), sv.AVICOMPRESSION)

    @property
    def convert_to_256_colors(self):
        return self._get_style(bool, sv.CONVERTTO256COLORS)

    @convert_to_256_colors.setter
    def convert_to_256_colors(self, value):
        if value is not None:
            self._set_style(bool(value), sv.CONVERTTO256COLORS)

    @property
    def filename(self):
        return self._get_style(str, sv.EXPORTFNAME)

    @filename.setter
    def filename(self, value):
        if value is not None:
            self._set_style(str(value), sv.EXPORTFNAME)

    @property
    def flash_compression_type(self):
        return self._get_style(FlashCompressionType, sv.FLASHCOMPRESSIONTYPE)

    @flash_compression_type.setter
    def flash_compression_type(self, value):
        if value is not None:
            self._set_style(FlashCompressionType(value),
                            sv.FLASHCOMPRESSIONTYPE)

    @property
    def flash_image_type(self):
        return self._get_style(FlashImageType, sv.FLASHIMAGETYPE)

    @flash_image_type.setter
    def flash_image_type(self, value):
        if value is not None:
            self._set_style(FlashImageType(value), sv.FLASHIMAGETYPE)

    @property
    def format(self):
        return self._get_style(ExportFormat, sv.EXPORTFORMAT)

    @format.setter
    def format(self, value):
        self._set_style(ExportFormat(value), sv.EXPORTFORMAT)

    @property
    def gray_scale_depth(self):
        return self._get_style(int, sv.GRAYSCALEDEPTH)

    @gray_scale_depth.setter
    def gray_scale_depth(self, value):
        if value is not None:
            value = int(value)
            if __debug__:
                value_choices = (0, 1, 4, 8)
                if value not in value_choices:
                    raise TecplotLogicError(
                        'Gray scale depth must be one of: ' +
                        ', '.join(str(x) for x in value_choices))
            self._set_style(int(value), sv.GRAYSCALEDEPTH)

    @property
    def jpeg_encoding(self):
        return self._get_style(JPEGEncoding, sv.JPEGENCODING)

    @jpeg_encoding.setter
    def jpeg_encoding(self, value):
        if value is not None:
            self._set_style(JPEGEncoding(value), sv.JPEGENCODING)

    @property
    def multiple_color_tables(self):
        return self._get_style(bool, sv.USEMULTIPLECOLORTABLES)

    @multiple_color_tables.setter
    def multiple_color_tables(self, value):
        if value is not None:
            self._set_style(bool(value), sv.USEMULTIPLECOLORTABLES)

    @property
    def quality(self):
        return self._get_style(float, sv.QUALITY)

    @quality.setter
    def quality(self, value):
        if value is not None:
            self._set_style(float(value), sv.QUALITY)

    @property
    def quality_scale(self):
        return self._get_style(int, sv.FFMPEGQSCALE)

    @quality_scale.setter
    def quality_scale(self, value):
        if value is not None:
            self._set_style(int(value), sv.FFMPEGQSCALE)

    @property
    def region(self):
        return self._get_style(ExportRegion, sv.EXPORTREGION)

    @region.setter
    def region(self, value):
        if value is not None:
            self._set_style(ExportRegion(value), sv.EXPORTREGION)

    @property
    def render_type(self):
        return self._get_style(PrintRenderType, sv.PRINTRENDERTYPE)

    @render_type.setter
    def render_type(self, value):
        if value is not None:
            self._set_style(PrintRenderType(value), sv.PRINTRENDERTYPE)

    @property
    def supersample(self):
        if not self._get_style(bool, sv.USESUPERSAMPLEANTIALIASING):
            return 1
        else:
            return self._get_style(int, sv.SUPERSAMPLEFACTOR)

    @supersample.setter
    def supersample(self, value):
        if value is not None:
            if __debug__:
                if not (1 <= value <= 16):
                    msg = 'supersample must be between 1 and 16'
                    raise TecplotLogicError(msg)
            if value < 2:
                self._set_style(False, sv.USESUPERSAMPLEANTIALIASING)
            else:
                self._set_style(True, sv.USESUPERSAMPLEANTIALIASING)
                self._set_style(int(value), sv.SUPERSAMPLEFACTOR)

    @property
    def tiff_byte_order(self):
        return self._get_style(TIFFByteOrder, sv.TIFFBYTEORDER)

    @tiff_byte_order.setter
    def tiff_byte_order(self, value):
        if value is not None:
            self._set_style(TIFFByteOrder(value), sv.TIFFBYTEORDER)

    @property
    def width(self):
        return self._get_style(int, sv.IMAGEWIDTH)

    @width.setter
    def width(self, value):
        if value is not None:
            self._set_style(int(value), sv.IMAGEWIDTH,
                            assignmodifier=AssignOp.Equals)
