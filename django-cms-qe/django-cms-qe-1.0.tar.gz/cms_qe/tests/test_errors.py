import pytest

from test_utils.cms import create_page


def test_page_found(client):
    create_page('Test page', page_params={'slug': 'test'})
    html = client.get('/en/test/').content
    assert b'<h1>Generic error</h1>' not in html
    assert b'<title>Test page</title>' in html


def test_page_not_found(client):
    html = client.get('/en/non-existing-page/').content
    assert b'<h1>Generic error</h1>' in html
    assert b'error404' in html


def test_page_not_found_custom_by_cms(client):
    create_page('custom page not found', page_params={'slug': 'error404'})
    html = client.get('/en/non-existing-page/').content
    assert b'<h1>Generic error</h1>' not in html
    assert b'<title>custom page not found</title>' in html
