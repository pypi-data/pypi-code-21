"""Sphinx Nameko MW Theme.

A fork of https://github.com/onefinestay/sphinx-nameko-theme for use
at Mediaware (http://www.mediaware.com.au)

"""

import os


def get_html_theme_path():
    """Return path to directory containing package theme."""
    return os.path.abspath(os.path.dirname(__file__))
