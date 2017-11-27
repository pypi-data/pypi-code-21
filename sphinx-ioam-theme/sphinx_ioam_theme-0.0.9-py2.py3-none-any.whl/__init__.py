from os import path

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

def setup(app):
    app.add_html_theme('sphinx_ioam_theme', path.abspath(path.dirname(__file__)))

