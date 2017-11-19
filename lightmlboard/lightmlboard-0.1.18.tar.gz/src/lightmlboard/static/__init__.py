"""
@file
@brief Helpers around static files.
"""
import os
import shutil


def copy_static(dest):
    """
    Copy static files into *dest/static*.
    """
    dst = os.path.join(dest, "static")
    if not os.path.exists(dst):
        os.mkdir(dst)
    this = os.path.dirname(__file__)
    copied = 0
    for name in os.listdir(this):
        if os.path.splitext(name)[-1] in {'.png', '.ico', '.css', '.js'}:
            shutil.copy(os.path.join(this, name), dst)
            copied += 1
    if copied == 0:
        raise ValueError("No file found in '{0}'.".format(this))
