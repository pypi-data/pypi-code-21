import platform
import unittest

from tecplot.constant import *
from tecplot.exception import *
from tecplot.export.export_setup import ExportSetup

class TestExportSetup(unittest.TestCase):
    def setUp(self):
        self.setup = ExportSetup()

    def test_reset(self):
        self.setup.reset()
        self.assertEqual(self.setup.convert_to_256_colors, False)
        self.assertEqual(self.setup.gray_scale_depth, 8)
        self.assertEqual(self.setup.quality, 75)
        self.assertEqual(self.setup.region, ExportRegion.CurrentFrame)
        self.assertEqual(self.setup.supersample, 1)
        self.assertEqual(self.setup.tiff_byte_order, TIFFByteOrder.Intel)
        self.assertEqual(self.setup.width, 512)

    def test_setting_none(self):
        self.setup.animation_speed = 3
        self.setup.animation_speed = None
        self.assertEqual(self.setup.animation_speed, 3)

        self.setup.avi_compression = AVICompression.LosslessUncompressed
        self.setup.avi_compression = None
        self.assertEqual(self.setup.avi_compression,
            AVICompression.LosslessUncompressed)

        self.setup.convert_to_256_colors = True
        self.setup.convert_to_256_colors = None
        self.assertTrue(self.setup.convert_to_256_colors)

        self.setup.filename = 'testname'
        self.setup.filename = None
        self.assertEqual(self.setup.filename, 'testname')

        self.setup.flash_compression_type = FlashCompressionType.BestSpeed
        self.setup.flash_compression_type = None
        self.assertEqual(self.setup.flash_compression_type,
            FlashCompressionType.BestSpeed)

        self.setup.flash_image_type = FlashImageType.JPEG
        self.setup.flash_image_type = None
        self.assertEqual(self.setup.flash_image_type, FlashImageType.JPEG)

        with self.assertRaises(ValueError):
            self.setup.format = None

        self.setup.gray_scale_depth = 4
        self.setup.gray_scale_depth = None
        self.assertEqual(self.setup.gray_scale_depth, 4)

        self.setup.jpeg_encoding = JPEGEncoding.Progressive
        self.setup.jpeg_encoding = None
        self.assertEqual(self.setup.jpeg_encoding, JPEGEncoding.Progressive)

        self.setup.multiple_color_tables = True
        self.setup.multiple_color_tables = None
        self.assertEqual(self.setup.multiple_color_tables, True)

        self.setup.quality = 50
        self.setup.quality = None
        self.assertAlmostEqual(self.setup.quality, 50)

        self.setup.quality_scale = 5
        self.setup.quality_scale = None
        self.assertEqual(self.setup.quality_scale, 5)

        self.setup.region = ExportRegion.AllFrames
        self.setup.region = None
        self.assertEqual(self.setup.region, ExportRegion.AllFrames)

        self.setup.render_type = PrintRenderType.Image
        self.setup.render_type = None
        self.assertEqual(self.setup.render_type, PrintRenderType.Image)

        self.setup.supersample = 5
        self.setup.supersample = None
        self.assertEqual(self.setup.supersample, 5)

        self.setup.tiff_byte_order = TIFFByteOrder.Motorola
        self.setup.tiff_byte_order = None
        self.assertEqual(self.setup.tiff_byte_order, TIFFByteOrder.Motorola)

        self.setup.width = 5
        self.setup.width = None
        self.assertEqual(self.setup.width, 5)

    def test_animation_speed(self):
        for val in [0.5,1,2,100]:
            self.setup.animation_speed = val
            self.assertEqual(self.setup.animation_speed, val)
        with self.assertRaises(ValueError):
            self.setup.animation_speed = 'badtype'
        with self.assertRaises(TecplotSystemError):
            self.setup.animation_speed = -1
        with self.assertRaises(TecplotSystemError):
            self.setup.animation_speed = 0

    def test_avi_compression(self):
        for val in [AVICompression.LinePreserving,
                    AVICompression.LosslessUncompressed]:
            self.setup.avi_compression = val
            self.assertEqual(self.setup.avi_compression, val)
        with self.assertRaises(ValueError):
            self.setup.avi_compression = 0.5
        with self.assertRaises(ValueError):
            self.setup.avi_compression = 'badvalue'

        # ColorPreserving is only available in Windows, and
        # should throw on other platforms.
        if platform.system() == 'Windows':
            val = AVICompression.ColorPreserving
            self.setup.avi_compression = val
            self.assertEqual(self.setup.avi_compression, val)
        else:
            with self.assertRaises(TecplotSystemError):
                self.setup.avi_compression = AVICompression.ColorPreserving

    def test_convert_to_256_colors(self):
        for val in [True, False, True]:
            self.setup.convert_to_256_colors = val
            self.assertEqual(self.setup.convert_to_256_colors, val)

    def test_filename(self):
        for val in ['aa', '11', 0, 3.14]:
            self.setup.filename = val
            self.assertEqual(self.setup.filename, str(val))

    def test_flash_compression_type(self):
        for val in [FlashCompressionType.BestSpeed,
                    FlashCompressionType.SmallestSize]:
            self.setup.flash_compression_type = val
            self.assertEqual(self.setup.flash_compression_type, val)
        with self.assertRaises(ValueError):
            self.setup.flash_compression_type = 0.5
        with self.assertRaises(ValueError):
            self.setup.flash_compression_type = 'badvalue'

    def test_flash_image_type(self):
        for val in [FlashImageType.Color256,
                    FlashImageType.JPEG,
                    FlashImageType.Lossless]:
            self.setup.flash_image_type = val
            self.assertEqual(self.setup.flash_image_type, val)
        with self.assertRaises(ValueError):
            self.setup.flash_image_type = 0.5
        with self.assertRaises(ValueError):
            self.setup.flash_image_type = 'badvalue'

    def test_format(self):
        for val in [ExportFormat.AVI, ExportFormat.BMP,
                    ExportFormat.EPS]:
            self.setup.format = val
            self.assertEqual(self.setup.format, val)
        with self.assertRaises(ValueError):
            self.setup.format = 0.5
        with self.assertRaises(ValueError):
            self.setup.format = 'badvalue'

    def test_gray_scale_depth(self):
        for val in [0,1,4,8]:
            self.setup.gray_scale_depth = val
            self.assertEqual(self.setup.gray_scale_depth, val)
        with self.assertRaises(ValueError):
            self.setup.gray_scale_depth = 'badtype'
        if __debug__:
            with self.assertRaises(TecplotLogicError):
                self.setup.gray_scale_depth = 2

    def test_jpeg_encoding(self):
        for val in [JPEGEncoding.Progressive, JPEGEncoding.Standard]:
            self.setup.jpeg_encoding = val
            self.assertEqual(self.setup.jpeg_encoding, val)
        with self.assertRaises(ValueError):
            self.setup.jpeg_encoding = 0.5
        with self.assertRaises(ValueError):
            self.setup.jpeg_encoding = 'badvalue'

    def test_multiple_color_tables(self):
        for val in [True, False, True]:
            self.setup.multiple_color_tables = val
            self.assertEqual(self.setup.multiple_color_tables, val)

    def test_quality(self):
        for val in [1,2,100]:
            self.setup.quality = val
            self.assertEqual(self.setup.quality, val)
        with self.assertRaises(ValueError):
            self.setup.quality = 'badtype'
        with self.assertRaises(TecplotSystemError):
            self.setup.quality = -1
        with self.assertRaises(TecplotSystemError):
            self.setup.quality = 0
        with self.assertRaises(TecplotSystemError):
            self.setup.quality = 0.9
        with self.assertRaises(TecplotSystemError):
            self.setup.quality = 101

    def test_quality_scale(self):
        for val in [1,2,3]:
            self.setup.quality_scale = val
            self.assertEqual(self.setup.quality_scale, val)
        with self.assertRaises(ValueError):
            self.setup.quality_scale = 'badtype'
        with self.assertRaises(TecplotSystemError):
            self.setup.quality_scale = 0
        with self.assertRaises(TecplotSystemError):
            self.setup.quality_scale = 100

    def test_region(self):
        for val in [ExportRegion.AllFrames, ExportRegion.CurrentFrame,
                    ExportRegion.WorkArea]:
            self.setup.region = val
            self.assertEqual(self.setup.region, val)
        with self.assertRaises(ValueError):
            self.setup.region = 0.5
        with self.assertRaises(ValueError):
            self.setup.region = 'badvalue'

    def test_render_type(self):
        for val in [PrintRenderType.Image, PrintRenderType.Vector]:
            self.setup.render_type = val
            self.assertEqual(self.setup.render_type, val)
        with self.assertRaises(ValueError):
            self.setup.render_type = 0.5
        with self.assertRaises(ValueError):
            self.setup.render_type = 'badvalue'

    def test_supersample(self):
        for val in [1,2,16]:
            self.setup.supersample = val
            self.assertEqual(self.setup.supersample, val)
        with self.assertRaises((ValueError, TypeError, TecplotLogicError)):
            self.setup.supersample = 'badtype'
        if __debug__:
            with self.assertRaises(TecplotLogicError):
                self.setup.supersample = 0
            with self.assertRaises(TecplotLogicError):
                self.setup.supersample = 17

    def test_tiff_byte_order(self):
        for val in [TIFFByteOrder.Intel, TIFFByteOrder.Motorola]:
            self.setup.tiff_byte_order = val
            self.assertEqual(self.setup.tiff_byte_order, val)
        with self.assertRaises(ValueError):
            self.setup.tiff_byte_order = 0.5
        with self.assertRaises(ValueError):
            self.setup.tiff_byte_order = 'badvalue'

    def test_width(self):
        for val in [500,1000,10000]:
            self.setup.width = val
            self.assertEqual(self.setup.width, val)
        with self.assertRaises(TecplotSystemError):
            self.setup.width = 0
        with self.assertRaises(TecplotSystemError):
            self.setup.width = 100000


if __name__ == '__main__':
    from .. import main
    main()
