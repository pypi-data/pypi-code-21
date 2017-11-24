from typing import Dict, List, Tuple

from django.apps import apps
from django.db.models.base import ModelBase
from django.contrib.auth import get_user_model

from .exceptions import TableDoesNotExists


def get_model_by_table(table: str) -> ModelBase:
    """
    Returns Django model by table name.
    """
    if table == 'auth_user':
        return get_user_model()

    for app_models in apps.all_models.values():
        for cls in app_models.values():
            if cls._meta.db_table == table:
                return cls
    raise TableDoesNotExists(table)


def get_models_choices() -> Tuple[Tuple[str, Tuple[Tuple[str, str], ...]], ...]:
    """
    Returns sorted and grouped choices of all models per app.

    Example output:

    .. code-block:: txt

        (
            'app1',
            (
                ('choice1 key', 'choice1 name'),
                ...
            ),
        ), (
            'app2',
            (
                ('choice2 key', 'choice2 name'),
                ...
            ),
        ), (
            ...
        )
    """
    return tuple((
        app,
        tuple(
            (cls._meta.db_table, cls._meta.object_name)
            for model, cls in sorted(app_models.items())
        ),
    ) for app, app_models in sorted(apps.all_models.items()) if app_models)


def get_table_choices(table: str) -> Dict[str, List[Tuple[str, str]]]:
    """
    Returns other choices for table depending on exact table name.

    .. code-block:: txt

        {
            "columns": [
                ["name", "label"],
                ...
            ]
        }
    """
    model = get_model_by_table(table)
    choices = {
        'columns': [(field.name, getattr(field, 'verbose_name', field.name)) for field in model._meta.get_fields()],
    }
    return choices
