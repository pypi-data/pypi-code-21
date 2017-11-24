from django.contrib.auth import get_user_model
import pytest

from ..exceptions import TableDoesNotExists
from ..utils import get_model_by_table, get_models_choices, get_table_choices


def test_get_model_by_table():
    User = get_user_model()
    model = get_model_by_table('auth_user')
    assert model is User


def test_get_model_by_table_not_found():
    with pytest.raises(TableDoesNotExists):
        get_model_by_table('table_does_not_exist')


def test_get_all_models():
    choices = get_models_choices()
    choices_admin_group = [item[1] for item in choices if item[0] == 'admin'][0]
    assert choices_admin_group == (
        ('django_admin_log', 'LogEntry'),
    )


def test_get_table_choices():
    choices = get_table_choices('auth_user')
    assert 'columns' in choices
    assert ('username', 'username') in choices['columns']
