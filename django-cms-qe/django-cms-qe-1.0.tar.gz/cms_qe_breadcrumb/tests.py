from test_utils import render_plugin
from .cms_plugins import BreadcrumbPlugin


def test_render():
    assert '<ol>' in render_plugin(BreadcrumbPlugin)
