"""Low-level python bindings for the quikkly native library with ctypes.

In most cases it is advisable to use the higher-level quikkly.py wrapper instead.
"""
from __future__ import absolute_import

from ctypes import cdll, Structure, Array, POINTER, byref, c_char_p, c_void_p, c_float, c_ubyte, c_uint8, c_int32, c_uint64, string_at, c_double
import os
import os.path
import logging
import sys


log = logging.getLogger(__name__)


EXPECTED_LIB_VERSION = '2.2.5'
QC_IMAGE_FORMAT_GREY_UINT8 = 0
QC_IMAGE_FORMAT_BGRA_UINT32 = 1
QC_IMAGE_FORMAT_RGBA_UINT32 = 2

QC_IMAGE_FIT_DEFAULT = 0  # Template default
QC_IMAGE_FIT_STRETCH = 1
QC_IMAGE_FIT_MEET = 2
QC_IMAGE_FIT_SLICE = 3

QC_JOIN_DEFAULT        = -1  # Template default
QC_JOIN_NONE           = 0
QC_JOIN_HORIZONTAL     = 1
QC_JOIN_VERTICAL       = 2
QC_JOIN_DIAGONAL_RIGHT = 4
QC_JOIN_DIAGONAL_LEFT  = 8
QC_JOIN_MAX            = 16


class QuikklyError(Exception):
    pass


class QuikklyImportError(ImportError):
    pass


def get_native_libs_dir(override_dir=None):
    native_dir = override_dir or os.environ.get('QUIKKLY_NATIVE_DIR', None)
    if not native_dir:
        raise QuikklyError('Must set QUIKKLY_NATIVE_DIR environment variable, or call quikklycore.init() with the directory before first API call.')
    native_dir = os.path.abspath(native_dir)
    if not os.path.exists(native_dir):
        raise QuikklyError('Quikkly native library path %s does not exist.' % native_dir)
    if not os.path.isdir(native_dir):
        raise QuikklyError('Quikkly native library path %s is not a directory.' % native_dir)
    return native_dir


class PythonStructure(Structure):
    def to_python(self):
        p = {}
        for k, _ in self._fields_:
            if not k.startswith('_'):
                v = getattr(self, k)
                if isinstance(v, Array):
                    v = [v[i] for i in range(len(v))]
                elif isinstance(v, bytes):
                    v = v.decode('utf-8')
                p[k] = v
        return p


class QCTag(PythonStructure):
    _pack_ = 1
    _fields_ = [
        ('data', c_uint64),
        ('type', c_char_p),
        ('corners', c_float * 8),
        ('area', c_float),
        ('_pad', c_float),
    ]

    def to_python(self):
        p = super(QCTag, self).to_python()
        p['data'] = int(p['data'])
        if all(c == 0 for c in p['corners']):
            p['corners'] = None
        else:
            p['corners'] = [(p['corners'][2 * i], p['corners'][2 * i + 1]) for i in range(4)]
        return p


class QCScanResult(PythonStructure):
    _pack_ = 1
    _fields_ = [
        ('tags', POINTER(QCTag)),
        ('num_tags', c_int32),
        ('_pad', c_int32),
    ]

    def to_python(self):
        p = super(QCScanResult, self).to_python()
        p['tags'] = [self.tags[i].to_python() for i in range(self.num_tags)]
        return p


class QCSkin(PythonStructure):
    _pack_ = 1
    _fields_ = [
        ('border_color', c_char_p),
        ('background_color', c_char_p),
        ('mask_color', c_char_p),
        ('overlay_color', c_char_p),
        ('image_url', c_char_p),
        ('logo_url', c_char_p),
        ('data_colors', POINTER(c_char_p)),
        ('num_data_colors', c_int32),
        ('image_fit', c_int32),
        ('logo_fit', c_int32),
        ('join', c_int32),
        ('_pad', c_int32),
    ]


class Binary(object):
    def __init__(self, basename, funcs):
        self.basename = basename
        self.funcs = funcs

    def get_fname(self):
        if sys.platform.startswith('darwin'):
            return 'lib%s.dylib' % self.basename
        elif sys.platform.startswith('linux'):
            return 'lib%s.so' % self.basename
        else:
            raise QuikklyError('Unknown platform %s, cannot predict library filename.' % sys.platform)

    def get_binary_path(self, libs_dir):
        return os.path.abspath(os.path.join(libs_dir, self.get_fname()))

    def load(self, libs_dir):
        binary_path = self.get_binary_path(libs_dir)
        if not os.path.exists(binary_path):
            raise QuikklyError('Binary library not found at %s, please set QUIKKLY_NATIVE_DIR environment variable or provide an argument to quikklycore.init().' % binary_path)
        lib = cdll.LoadLibrary(binary_path)
        funcs = {}
        for func_name, (restype, argtypes) in sorted(self.funcs.items()):
            dotted_name = '%s.%s' % (self.basename, func_name)
            func = getattr(lib, func_name)
            func.restype = restype
            func.argtypes = argtypes
            funcs[dotted_name] = func
        log.info('Loaded Quikkly native library from %s', binary_path)
        return funcs


BINARIES = [
    Binary('quikklycore', {
        'qc_check_linking': (c_char_p, []),

        'qc_alloc_build_pipeline': (c_void_p, [c_char_p]),
        'qc_release_pipeline': (None, [c_void_p]),

        'qc_process_frame': (c_int32, [c_void_p, POINTER(c_uint8), c_int32, c_int32, c_int32, c_int32]),
        'qc_num_debug_images': (c_int32, [c_void_p, c_char_p]),
        'qc_access_debug_image': (POINTER(c_uint8), [c_void_p, c_char_p, c_int32, POINTER(c_int32), POINTER(c_int32), POINTER(c_int32)]),
        'qc_access_debug_seconds': (c_double, [c_void_p, c_char_p]),

        'qc_alloc_extract_result': (POINTER(QCScanResult), [c_void_p]),
        'qc_release_result': (None, [POINTER(QCScanResult)]),

        'qc_max_data_value': (c_uint64, [c_void_p, c_char_p]),
        'qc_init_default_skin': (None, [POINTER(QCSkin)]),
        'qc_alloc_generate_svg': (c_void_p, [c_void_p, c_char_p, c_uint64, POINTER(QCSkin)]),
        'qc_release_svg': (None, [c_void_p]),
    }),
]

FUNCS = None
PIPELINE = None


def init(native_libs_dir=None):
    global FUNCS
    global PIPELINE
    if FUNCS is not None and PIPELINE is not None:
        return

    native_dir = get_native_libs_dir(native_libs_dir)

    FUNCS = {}
    for binary in BINARIES:
        FUNCS.update(binary.load(native_dir))
    if 'quikklycore.qc_check_linking' not in FUNCS:
        raise QuikklyError('Binary function quikklycore.qc_check_linking not loaded.')
    loaded_version = FUNCS['quikklycore.qc_check_linking']()
    if EXPECTED_LIB_VERSION.encode('utf-8') != loaded_version:
        raise QuikklyError('Quikklycore binary version mismatch: loaded %s, but Python SDK is for %s.' % (loaded_version, EXPECTED_LIB_VERSION))
    log.info('Quikkly native library version is %s', loaded_version)

    blueprint_path = os.path.join(native_dir, 'default_blueprint.json')
    if not os.path.exists(blueprint_path):
        raise QuikklyError('Quikkly template file %s not found.' % blueprint_path)

    with open(blueprint_path, 'rb') as f:
        blueprint = f.read()

    PIPELINE = FUNCS['quikklycore.qc_alloc_build_pipeline'](blueprint)
    if not PIPELINE:
        raise QuikklyError('Loading Quikkly template file %s failed.' % blueprint_path)


def release():
    global FUNCS
    global PIPELINE
    if FUNCS is None or PIPELINE is None:
        raise QuikklyError('Quikklycore is not initialized, cannot release.')
    FUNCS['quikklycore.qc_release_pipeline'](PIPELINE)
    PIPELINE = None
    FUNCS = None
    log.info('Quikkly native data released.')


def check_linking():
    init()
    return FUNCS['quikklycore.qc_check_linking']()


def generate_svg(type, data,
                 border_color=None, background_color=None,
                 mask_color=None, overlay_color=None, data_colors=None,
                 image_url=None, image_fit=None,
                 logo_url=None, logo_fit=None,
                 join=QC_JOIN_DEFAULT):
    """Returns a SVG string with the generated code."""
    init()

    if data < 0:
        raise QuikklyError('Invalid data value %d - cannot be negative.' % data)
    max_data = FUNCS['quikklycore.qc_max_data_value'](PIPELINE, type.encode('utf-8'))
    if data > max_data:
        raise QuikklyError('Invalid data value %d - maximum that fits into template is %d.' % (data, max_data))

    skin = QCSkin()
    FUNCS['quikklycore.qc_init_default_skin'](byref(skin))
    if border_color:
        skin.border_color = border_color.encode('utf-8')
    if background_color:
        skin.background_color = background_color.encode('utf-8')
    if mask_color:
        skin.mask_color = mask_color.encode('utf-8')
    if overlay_color:
        skin.overlay_color = overlay_color.encode('utf-8')
    if data_colors:
        encoded_colors = [c.encode('utf-8') for c in data_colors]
        arr = (c_char_p * len(encoded_colors))()
        arr[:] = encoded_colors
        skin.data_colors = arr
        skin.num_data_colors = len(encoded_colors)
    if image_url:
        skin.image_url = image_url.encode('utf-8')
    if logo_url:
        skin.logo_url = logo_url.encode('utf-8')
    skin.image_fit = image_fit or QC_IMAGE_FIT_DEFAULT
    skin.logo_fit = logo_fit or QC_IMAGE_FIT_DEFAULT
    skin.join = join if join is not None else QC_JOIN_DEFAULT

    svgptr = FUNCS['quikklycore.qc_alloc_generate_svg'](PIPELINE, type.encode('utf-8'), data, byref(skin))
    if svgptr:
        svg = string_at(svgptr).decode('utf-8')
        FUNCS['quikklycore.qc_release_svg'](svgptr)
        return svg
    else:
        return None


def check_numpy_pillow():
    try:
        import numpy
    except ImportError:
        raise QuikklyImportError('Failed to import numpy, which is required for scanning images. SVG generation is still available.')
    try:
        from PIL import Image
    except ImportError:
        raise QuikklyImportError('Failed to import numpy, which is required for scanning images. SVG generation is still available.')


def process_image(image):
    """Image must be a PIL image.

    Returns a Python dictionary with results data.
    """
    init()

    frame, format, width, height, bytes_per_row = _prepare_frame(image)

    # Note: cannot merge frame_pointer into prepare_frame(), because the numpy array must remain in scope while the pointer is used.
    frame_pointer = frame.ctypes.data_as(POINTER(c_ubyte))
    res = FUNCS['quikklycore.qc_process_frame'](
        PIPELINE,
        frame_pointer,
        format,
        width,
        height,
        bytes_per_row
    )
    if res != 0:
        raise QuikklyError('Quikkly scanner returned error code %s', res)

    results = _extract_results()
    if results and results['tags']:
        return results['tags']
    else:
        return []


def _prepare_frame(image):
    """Image must be a PIL image.

    Returns:
        a numpy uint8 rgba array suitable for quikklycore input.
        format
        width
        height
        bytes_per_row
    """
    from PIL import Image
    import numpy

    if not Image.isImageType(image):
        raise QuikklyError('prepare_frame() requires a PIL image.')

    w, h = image.size
    # TODO: this could use some optimisation
    image = image.convert(mode='RGBA')
    frame = numpy.array(image, dtype=numpy.uint8)

    assert frame.shape == (h, w, 4)
    assert frame.dtype == numpy.uint8

    return frame, QC_IMAGE_FORMAT_RGBA_UINT32, w, h, w * 4


def _extract_results():
    """Extracts result of the last process_frame() from the pipeline.

    Returns a Python dictionary with the results. Releases C library result before returning.
    """
    results = FUNCS['quikklycore.qc_alloc_extract_result'](PIPELINE)
    results_python = results.contents.to_python()
    FUNCS['quikklycore.qc_release_result'](results)
    return results_python
