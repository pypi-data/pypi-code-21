from typing import Iterable, Type

from django.db.models import Model, QuerySet, Prefetch

from .utils.model_meta import get_model_prefetch, get_model_columns
from .utils.selectors import Selector


def get_queryset(model: Type[Model], selector: Selector) -> QuerySet:
    return model._default_manager.get_queryset() \
        .only(*(get_model_columns(model).intersection(selector.keys()))) \
        .prefetch_related(*get_prefetch(model, selector))


def get_prefetch(model: Type[Model], selector: Selector) -> Iterable[Prefetch]:
    return (
        Prefetch(field_name, queryset=get_queryset(field_model, selector[field_name]))
        for field_name, field_model in get_model_prefetch(model).items() if field_name in selector.keys()
    )
