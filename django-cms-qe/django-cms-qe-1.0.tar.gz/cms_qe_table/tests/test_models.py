from django.core.paginator import Page
from pytest_data import use_data


def test_get_header(cms_qe_table_model):
    assert cms_qe_table_model.get_header() == ['username', 'password']


@use_data(cms_qe_table_model_data={'paging_show': False})
def test_get_items_without_paging(cms_qe_table_model):
    assert cms_qe_table_model.get_items() == []


@use_data(cms_qe_table_model_data={'paging_show': True})
def test_get_items_with_paging(cms_qe_table_model):
    items = cms_qe_table_model.get_items()
    assert isinstance(items, Page)
    assert list(items) == []


@use_data(cms_qe_table_model_data={'columns': ['does_not_exist']})
def test_columns_exist(cms_qe_table_model):
    assert not cms_qe_table_model.columns_exist
