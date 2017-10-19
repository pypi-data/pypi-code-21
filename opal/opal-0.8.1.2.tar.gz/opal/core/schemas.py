"""
Utilities for dealing with OPAL Schemas
"""
import itertools
from opal.core.subrecords import subrecords
from opal import models


def serialize_model(model):
    col = {
        'name'        : model.get_api_name(),
        'display_name': model.get_display_name(),
        'single'      : model._is_singleton,
        'advanced_searchable': model._advanced_searchable,
        'fields'      : model.build_field_schema(),
    }
    if hasattr(model, '_sort'):
        col['sort'] = model._sort
    if hasattr(model, '_read_only'):
        col['readOnly'] = model._read_only
    if hasattr(model, '_angular_service'):
        col['angular_service'] = model._angular_service
    if hasattr(model, 'get_form_url'):
        col["form_url"] = model.get_form_url()
    if hasattr(model, 'get_icon'):
        col["icon"] = model.get_icon()

    return col


def serialize_schema(schema):
    return [serialize_model(column) for column in schema]


def _get_all_fields():
    response = {
        subclass.get_api_name(): serialize_model(subclass)
        for subclass in subrecords()
    }
    response['tagging'] = serialize_model(models.Tagging)
    return response


def list_records():
    return _get_all_fields()


def extract_schema():
    return serialize_schema(itertools.chain([models.Tagging], subrecords()))
