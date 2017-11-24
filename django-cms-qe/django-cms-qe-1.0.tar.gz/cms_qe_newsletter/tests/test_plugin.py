from test_utils import render_plugin

from ..cms_plugins import NewsletterPlugin


def test_render():
    html = render_plugin(NewsletterPlugin)
    assert '<form' in html
    assert '<input' in html
    assert 'email' in html
    assert 'first' not in html
    assert 'last' not in html
    assert 'submit' in html


def test_render_fullname_show():
    html = render_plugin(NewsletterPlugin, fullname_show=True)
    assert 'email' in html
    assert 'first' in html
    assert 'last' in html
    assert 'submit' in html
