#!/usr/bin/env python

from __future__ import print_function, unicode_literals, absolute_import, division

import os
from setuptools import setup, find_packages

__version__ = "1.1.0"

DESCRIPTION = "Collection of helpers and useful things for Python: library-specific pieces"

LONG_DESCRIPTION = """
"""

try:
    LONG_DESCRIPTION = (
        LONG_DESCRIPTION +
        open(os.path.join(os.path.dirname(__file__), "README.rst"), "rb").read().decode("utf-8"))
except Exception as _exc:
    print("Pkg-description error:", _exc)


SETUP_KWARGS = dict(
    name="pyauxm",
    version=__version__,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    # classifiers=[],
    # keywords="...,...",
    author="HoverHell",
    author_email="hoverhell@gmail.com",
    url="https://github.com/HoverHell/pyauxm",
    download_url="https://github.com/HoverHell/pyauxm/tarball/%s" % (__version__,),
    packages=find_packages(),
    install_requires=["six"],
    extras_require={
        # All things that are known to be used in some part of this
        # library or another.
        "known": [
            "django",  # in the psql helper
            "Twisted",  # bunch of twisted stuff here
            "Cython",  # at least one pyx module
            "pandas",  # here and there
            "Pygments",  # json / yaml coloring
            "pylzma",  # helpers for it
            "simplejson",  # optional, for speed
            "pp",
            "line_profiler",
            "pyzmq",
        ],
    },
)


if __name__ == "__main__":
    setup(**SETUP_KWARGS)
