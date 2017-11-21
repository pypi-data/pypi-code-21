from os import path

import versioneer

__version__ = versioneer.get_version()

def setup(app):
    app.add_html_theme('sphinx_ioam_theme', path.abspath(path.dirname(__file__)))
