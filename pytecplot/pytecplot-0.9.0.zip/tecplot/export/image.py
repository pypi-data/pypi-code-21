import logging

from ..tecutil import _tecutil, lock, sv
from ..constant import *
from ..exception import *
from .. import layout, session

from .export_setup import ExportSetup
from .print_setup import PrintSetup

log = logging.getLogger(__name__)


@lock()
def _do_export(region):

    if isinstance(region, layout.Frame):
        ExportSetup().region = ExportRegion.CurrentFrame
        with region.activated():
            success = _tecutil.Export(append=False)
    else:
        ExportSetup().region = region
        success = _tecutil.Export(append=False)
    if not success:
        raise TecplotSystemError()


def save_jpeg(filename,
              width=800,
              region=ExportRegion.CurrentFrame,
              supersample=3,
              encoding=JPEGEncoding.Standard,
              quality=75):
    """Save a `JPEG image
    <https://en.wikipedia.org/wiki/JPEG>`_.

    Parameters:
        filename (`string <str>`): |export_filename_description| (See note
            below conerning absolute and relative paths.)
        width (`integer <int>`): |export_width_description|
        region (`frame <Frame>` or `ExportRegion`, optional): |export_region_description|
        supersample (`integer <int>`, optional): |export_supersample_description|
        quality (`integer <int>` 1-100, optional)
            Select the quality of JPEG image.
            Higher quality settings produce larger files and better
            looking export images. Lower quality settings produce smaller files.
            For best results, use a quality setting of **75** or higher.
            (default: **75**)
        encoding (`JPEGEncoding`, optional)
            Encoding method for the JPEG file which may be one of the following:
                * `JPEGEncoding.Standard`
                    Creates a JPEG which downloads one line at a time,
                    starting at the top line.
                * `JPEGEncoding.Progressive`
                    Creates a JPEG image that can be displayed with
                    a "fade in" effect in a browser.
                    This is sometimes useful when viewing the JPEG in a
                    browser with a slow connection, since it allows
                    an approximation of the JPEG to be drawn immediately,
                    and the browser does not have to wait for the entire
                    image to download.

                (default: `JPEGEncoding.Standard`)

    Raises:
        `TecplotSystemError`: The image could not be saved due to a
            file I/O error or invalid attribute.

    .. note:: **Absolute and relative paths with PyTecplot**

        Unless file paths are absolute, saving and loading files will be
        relative to the current working directory of the parent process. This
        is different when running the PyTecplot script in batch mode and when
        running in connected mode with `tecplot.session.connect()`. In batch
        mode, paths will be relative to Python's current working directory as
        obtained by :func:`os.getcwd()`. When connected to an instance of
        Tecplot 360, paths will be relative to Tecplot 360's' start-up folder
        which is typically the Tecplot 360 installation "bin" folder.

    .. note::
        |export_general_info|

    Create a new `frame <Frame>` and save a JPEG image of the frame
    with quality **50** and supersampling::

        >>> frame = tecplot.active_page().add_frame()
        >>> tecplot.load_layout('mylayout.lay')
        >>> tecplot.export.save_jpeg('image.jpeg', width=600, supersample=3,
        ...                         region=frame, quality=50)
    """
    setup = ExportSetup()
    setup.reset()
    setup.format = ExportFormat.JPEG
    setup.filename = filename
    setup.width = width
    setup.supersample = supersample
    setup.quality = quality
    setup.jpeg_encoding = encoding

    _do_export(region)
    log.info('JPEG image file created: ' + filename)


def save_tiff(filename,
              width=800,
              region=ExportRegion.CurrentFrame,
              supersample=3,
              convert_to_256_colors=False,
              gray_scale_depth=None,
              byte_order=TIFFByteOrder.Intel):
    """Save a `TIFF image
    <https://en.wikipedia.org/wiki/TIFF>`_.

    Parameters:
        filename (`string <str>`): |export_filename_description| (See note
            below conerning absolute and relative paths.)
        width (`integer <int>`): |export_width_description|
        region (`frame <Frame>` or `ExportRegion`, optional): |export_region_description|
        supersample (`integer <int>`, optional): |export_supersample_description|
        convert_to_256_colors (`Boolean <bool>`, optional): |export_convert256_description|
        gray_scale_depth (`integer <int>`, optional)
            Export a gray-scale TIFF.
            The ``gray_scale_depth`` parameter may be
            set to a depth of **1-8**

            ``gray_scale_depth`` specifies the
            number of shades of gray by how many bits of gray scale
            information is used per pixel.
            The larger the number of bits per pixel, the larger the
            resulting file.

            Options are:
                * **0**: On/Off
                    One bit per pixel using an on/off strategy.
                    All background pixels are made white (on),
                    and all foreground pixels, black (off).
                    This setting creates small files and is
                    good for images with lots of background, such as line
                    plots and contour lines.
                * **1**: 1 Bit per Pixel
                    One bit per pixel using gray scale values of
                    pixels to determine black or white.
                    Those pixels that are more than 50 percent gray are
                    black; the rest are white. This setting creates small
                    files that might be useful for a rough draft
                    or a preview image.
                * **4**: 4 Bits per Pixel
                    Four bits per pixel resulting
                    in sixteen levels of gray scale. This setting
                    generates fairly small image files with a
                    fair number of gray levels.
                    This setting works well for most preview image purposes.
                * **8**:  8 Bits per Pixel
                    Eight bits per pixel resulting in 256 levels of gray.
                    This setting is useful for full image
                    representation, but the files generated by this
                    setting can be large.

                (default: `None`)

        byte_order (`TIFFByteOrder`, optional)
            Specify the byte order (Intel or Motorola) of the TIFF image.
            (Default: `TIFFByteOrder.Intel`)

    Raises:
        `TecplotSystemError`: The image could not be saved due to a
            file I/O error or invalid attribute.

    .. note:: **Absolute and relative paths with PyTecplot**

        Unless file paths are absolute, saving and loading files will be
        relative to the current working directory of the parent process. This
        is different when running the PyTecplot script in batch mode and when
        running in connected mode with `tecplot.session.connect()`. In batch
        mode, paths will be relative to Python's current working directory as
        obtained by :func:`os.getcwd()`. When connected to an instance of
        Tecplot 360, paths will be relative to Tecplot 360's' start-up folder
        which is typically the Tecplot 360 installation "bin" folder.

    .. note::
        |export_general_info|

    Save a 4-bit gray scale TIFF image of the entire workspace with supersampling::

        >>> from tecplot.constant import ExportRegion
        >>> tecplot.load_layout('mylayout.lay')
        >>> tecplot.export.save_tiff('image.tiff', width=600, supersample=2,
        >>>                         region=ExportRegion.WorkArea,
        >>>                         gray_scale_depth=4)
    """

    print_setup = PrintSetup()
    print_setup.palette = (
        Palette.Color if gray_scale_depth is None else Palette.Monochrome)

    setup = ExportSetup()
    setup.reset()
    setup.format = ExportFormat.TIFF
    setup.filename = filename
    setup.width = width
    setup.supersample = supersample
    setup.convert_to_256_colors = convert_to_256_colors
    setup.gray_scale_depth = gray_scale_depth
    setup.tiff_byte_order = byte_order

    _do_export(region)
    log.info('TIFF image file created: ' + filename)


def save_png(filename,
             width=800,
             region=ExportRegion.CurrentFrame,
             supersample=3,
             convert_to_256_colors=False):
    """Save a `PNG image
    <https://en.wikipedia.org/wiki/Portable_Network_Graphics>`_.

    Parameters:
        filename (`string <str>`): |export_filename_description| (See note
            below conerning absolute and relative paths.)
        width (`integer <int>`):  |export_width_description|
        region (`frame <Frame>` or `ExportRegion`, optional): |export_region_description|
        supersample (`integer <int>`, optional): |export_supersample_description|
        convert_to_256_colors (`Boolean <bool>`, optional): |export_convert256_description|

    Raises:
        `TecplotSystemError`: The image could not be saved due to a
            file I/O error or invalid attribute.

    .. note:: **Absolute and relative paths with PyTecplot**

        Unless file paths are absolute, saving and loading files will be
        relative to the current working directory of the parent process. This
        is different when running the PyTecplot script in batch mode and when
        running in connected mode with `tecplot.session.connect()`. In batch
        mode, paths will be relative to Python's current working directory as
        obtained by :func:`os.getcwd()`. When connected to an instance of
        Tecplot 360, paths will be relative to Tecplot 360's' start-up folder
        which is typically the Tecplot 360 installation "bin" folder.

    .. note::
        |export_general_info|

    Save a PNG image of the entire workspace with supersampling::

        >>> from tecplot.constant import ExportRegion
        >>> tecplot.load_layout('mylayout.lay')
        >>> tecplot.export.save_png('image.png', width=600, supersample=3,
        ...                         region=ExportRegion.WorkArea)
    """
    setup = ExportSetup()
    setup.reset()
    setup.format = ExportFormat.PNG
    setup.filename = filename
    setup.width = width
    setup.supersample = supersample
    setup.convert_to_256_colors = convert_to_256_colors

    _do_export(region)
    log.info('PNG image file created: ' + filename)


def save_wmf(filename,
             palette=Palette.Color,
             region=ExportRegion.CurrentFrame,
             force_extra_3d_sorting=False):
    """Save a Windows Metafile image

    Parameters:
        filename (`string <str>`): |export_filename_description| (See note
            below conerning absolute and relative paths.)
        palette (`Palette`, optional): Export color image. (default:
            `Palette.Color`) Note: `Palette.PenPlotter` cannot be used.
        region (`frame <Frame>` or `ExportRegion`, optional): |export_region_description|
        force_extra_3d_sorting (`bool`, optional): Force extra sorting for all
            3D frames. (default: `False`)

    Raises:
        `TecplotSystemError`: The image could not be saved due to a
            file I/O error or invalid attribute.

    .. note:: **Absolute and relative paths with PyTecplot**

        Unless file paths are absolute, saving and loading files will be
        relative to the current working directory of the parent process. This
        is different when running the PyTecplot script in batch mode and when
        running in connected mode with `tecplot.session.connect()`. In batch
        mode, paths will be relative to Python's current working directory as
        obtained by :func:`os.getcwd()`. When connected to an instance of
        Tecplot 360, paths will be relative to Tecplot 360's' start-up folder
        which is typically the Tecplot 360 installation "bin" folder.

    .. note::
        WMF (Windows Metafile) is a Microsoft vector graphics format widely
        accepted by Windows applications. Since WMFs are vector graphics, they
        can be easily resized by the importing application without the
        introduction of visual artifacts, but they cannot accurately represent
        plots with translucency or smooth color gradations

    Save a WMF image of the active frame::

        >>> tecplot.load_layout('mylayout.lay')
        >>> tecplot.export.save_wmf('image.wmf')
    """
    print_setup = PrintSetup()
    print_setup.reset()
    print_setup.palette = palette
    print_setup.force_extra_3d_sorting = force_extra_3d_sorting

    export_setup = ExportSetup()
    export_setup.reset()
    export_setup.format = ExportFormat.WindowsMetafile
    export_setup.filename = filename

    _do_export(region)
    log.info('Windows metafile image created: ' + filename)


def save_ps(filename,
            palette=Palette.Color,
            region=ExportRegion.CurrentFrame,
            force_extra_3d_sorting=False,
            extra_precision=0,
            render_type=PrintRenderType.Vector,
            resolution=150):
    """Save a `PostScript image <https://en.wikipedia.org/wiki/PostScript>`_.

    Parameters:
        filename (`string <str>`): |export_filename_description| (See note
            below conerning absolute and relative paths.)
        palette (`Palette`, optional): Export color image. (default: `Palette.Color`)
        region (`frame <Frame>` or `ExportRegion`, optional): |export_region_description|
        force_extra_3d_sorting (`bool`, optional): Force extra sorting for all
            3D frames. (default: `False`)
        extra_precision (`int`, optional): Additional digits for all numbers
            written to postscript file. (default: 0)
        render_type (`PrintRenderType`, optional): Whether to render the
            postscript as a rasterized or vector image. (default:
            `PrintRenderType.Vector`)
        resolution (`integer <int>`): Resolution of the image in dots per inch.
            Larger values create more accurate plots, but result in larger file
            sizes. Note: this value is ignored if `PrintRenderType` is
            `PrintRenderType.Vector` (default: **150**)

    Raises:
        `TecplotSystemError`: The image could not be saved due to a
            file I/O error or invalid attribute.

    .. note:: **Absolute and relative paths with PyTecplot**

        Unless file paths are absolute, saving and loading files will be
        relative to the current working directory of the parent process. This
        is different when running the PyTecplot script in batch mode and when
        running in connected mode with `tecplot.session.connect()`. In batch
        mode, paths will be relative to Python's current working directory as
        obtained by :func:`os.getcwd()`. When connected to an instance of
        Tecplot 360, paths will be relative to Tecplot 360's' start-up folder
        which is typically the Tecplot 360 installation "bin" folder.

    Save a PostScript image of the active frame::

        >>> tecplot.load_layout('mylayout.lay')
        >>> tecplot.export.save_ps('image.ps')
    """
    print_setup = PrintSetup()
    print_setup.reset()
    print_setup.palette = palette
    print_setup.force_extra_3d_sorting = force_extra_3d_sorting
    print_setup.extra_precision = extra_precision
    print_setup.resolution = resolution

    export_setup = ExportSetup()
    export_setup.reset()
    export_setup.format = ExportFormat.PS
    export_setup.filename = filename
    export_setup.render_type = render_type

    _do_export(region)
    log.info('Postscript file created: ' + filename)
