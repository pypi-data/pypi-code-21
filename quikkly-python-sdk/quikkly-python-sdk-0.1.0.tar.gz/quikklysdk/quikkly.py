"""High-level interface to the Quikkly Python SDK.
"""
from __future__ import absolute_import

import base64
import os.path

from quikklysdk import quikklycore
from quikklysdk.quikklycore import QuikklyError


def init(native_libs_dir=None):
    """Calling init is optional.

    The native library will be loaded automatically from environment variable QUIKKLY_NATIVE_DIR
    on first API call.

    Use init() before other API calls if you want to pass the directory from other code.
    """
    quikklycore.init(native_libs_dir=native_libs_dir)


def get_native_version():
    """Returns native library version string."""
    return quikklycore.check_linking()


def generate_svg(type, data,
                 border_color=None, background_color=None,
                 mask_color=None, overlay_color=None, data_colors=None,
                 image_url=None, image_filename=None, image_fit=None,
                 logo_url=None, logo_filename=None, logo_fit=None,
                 join=None):
    """Generates and returns a SVG string with the given template ID and data integer.

    The theme parameters are optional - and some may be ignored for some templates.
    """
    image_url = _prepare_image_url('image', image_url, image_filename)
    logo_url = _prepare_image_url('logo', logo_url, logo_filename)
    return quikklycore.generate_svg(
        type, data,
        border_color=border_color, background_color=background_color, mask_color=mask_color,
        overlay_color=overlay_color, data_colors=data_colors,
        image_url=image_url, image_fit=image_fit,
        logo_url=logo_url, logo_fit=logo_fit,
        join=join)


def _prepare_image_url(name, url, filename):
    if url and filename:
        raise QuikklyError('To generate Quikkly code, please provide %s_url or %s_filename, not both.' % (name, name))
    elif url:
        return url
    elif filename:
        filename = os.path.abspath(filename)
        ext = os.path.splitext(filename)[1][1:].lower()
        if ext in ['png']:
            mime = 'image/png'
        elif ext in ['jpg', 'jpeg']:
            mime = 'image/jpeg'
        else:
            raise QuikklyError('Cannot determine MIME type of file with extension "%s", known extensions are "png", "jpg", and "jpeg".' % ext)
        with open(filename, 'rb') as f:
            imgbytes = f.read()
            return 'data:' + mime + ';base64,' + base64.b64encode(imgbytes).decode('utf-8')
    else:
        return None


def scan_pil_image(image):
    """Scans PIL image, returns list of tag data found."""
    return quikklycore.process_image(image)


def scan_image_file(filename):
    """Scans image file, returns list of tag data found.

    Filename must point to a file that Pillow can open.
    """
    from PIL import Image
    image = Image.open(filename)
    return scan_pil_image(image)
