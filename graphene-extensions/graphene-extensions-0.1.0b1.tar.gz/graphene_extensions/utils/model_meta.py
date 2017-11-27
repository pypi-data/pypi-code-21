from typing import Type, Set, Dict

from django.db.models import Model, Field
from django.db.models.fields.reverse_related import ForeignObjectRel


def get_field_name(field: Field) -> str:
    if isinstance(field, ForeignObjectRel):
        return field.related_name or field.name + ('_set' if field.multiple else '')
    return field.name


def get_related_fields(model: Type[Model]) -> Set[Field]:
    return {field for field in model._meta.get_fields() if field.related_model}


def get_fields(model: Type[Model]) -> Dict[str, Field]:
    fields = {get_field_name(field): field for field in model._meta.get_fields()}
    return {**fields, 'pk': fields[model._meta.pk.name]}


def is_selectable(field: Field) -> bool:
    return field.many_to_one or field.one_to_one and not field.auto_created


def is_prefetchable(field: Field) -> bool:
    return field.many_to_many or field.one_to_one or field.one_to_many or is_selectable(field)


def get_model_select(model: Type[Model]) -> Dict[str, Type[Model]]:
    return {get_field_name(field): field.related_model
            for field in get_related_fields(model) if is_selectable(field)}


def get_model_prefetch(model: Type[Model]) -> Dict[str, Type[Model]]:
    return {get_field_name(field): field.related_model
            for field in get_related_fields(model) if is_prefetchable(field)}


def get_model_columns(model: Type[Model]) -> Set[str]:
    return {field.attname for field in model._meta._forward_fields_map.values() if not field.many_to_many}
