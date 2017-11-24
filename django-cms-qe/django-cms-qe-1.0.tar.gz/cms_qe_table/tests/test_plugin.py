from test_utils import render_plugin
from ..cms_plugins import TablePlugin


def test_render():
    html = render_plugin(TablePlugin, table='auth_user')
    assert '<table>' in html


def test_render_not_existing_table():
    html = render_plugin(TablePlugin, table='table_does_not_exist')
    assert 'Table table_does_not_exist does not exist!' in html


def test_render_table_with_not_existing_column():
    html = render_plugin(TablePlugin, table='auth_user', columns=['column_does_not_exist'])
    assert 'Some column does not exist!' in html
