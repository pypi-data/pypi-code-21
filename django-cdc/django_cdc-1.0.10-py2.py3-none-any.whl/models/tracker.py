from __future__ import unicode_literals

from copy import deepcopy

import django
from django.core.exceptions import FieldError
from django.db.models.fields.files import FileDescriptor
from django.db.models.query_utils import DeferredAttribute


class DescriptorMixin(object):
    tracker_instance = None

    def __get__(self, instance, owner):
        if instance is None:
            return self
        was_deferred = False
        field_name = self._get_field_name()
        if field_name in instance._deferred_fields:
            instance._deferred_fields.remove(field_name)
            was_deferred = True
        value = super(DescriptorMixin, self).__get__(instance, owner)
        if was_deferred:
            self.tracker_instance.saved_data[field_name] = deepcopy(value)
        return value

    def _get_field_name(self):
        return self.field_name


class FieldInstanceTracker(object):
    def __init__(self, instance, fields, field_map):
        self.instance = instance
        self.fields = fields
        self.field_map = field_map
        self.init_deferred_fields()

    def get_field_value(self, field):
        return getattr(self.instance, self.field_map[field])

    def set_saved_fields(self, fields=None):
        if not self.instance.pk:
            self.saved_data = {}
        elif fields is None:
            self.saved_data = self.current()
        else:
            self.saved_data.update(**self.current(fields=fields))

        # preventing mutable fields side effects
        for field, field_value in self.saved_data.items():
            self.saved_data[field] = deepcopy(field_value)

    def current(self, fields=None):
        """Returns dict of current values for all tracked fields"""
        if fields is None:
            if self.instance._deferred_fields:
                fields = [
                    field for field in self.fields
                    if field not in self.instance._deferred_fields
                ]
            else:
                fields = self.fields

        return dict((f, self.get_field_value(f)) for f in fields)

    def has_changed(self, field):
        """Returns ``True`` if field has changed from currently saved value"""
        if field in self.fields:
            return self.previous(field) != self.get_field_value(field)
        else:
            raise FieldError('field "%s" not tracked' % field)

    def previous(self, field):
        """Returns currently saved value of given field"""
        return self.saved_data.get(field)

    def changed(self):
        """Returns dict of fields that changed since save (with old values)"""
        return dict(
            (field, self.previous(field))
            for field in self.fields
            if self.has_changed(field)
        )

    def init_deferred_fields(self):
        self.instance._deferred_fields = set()
        if hasattr(self.instance, '_deferred') and not self.instance._deferred:
            return

        class DeferredAttributeTracker(DescriptorMixin, DeferredAttribute):
            tracker_instance = self

        class FileDescriptorTracker(DescriptorMixin, FileDescriptor):
            tracker_instance = self

            def _get_field_name(self):
                return self.field.name

        if django.VERSION >= (1, 8):
            self.instance._deferred_fields = self.instance.get_deferred_fields()
            for field in self.instance._deferred_fields:
                if django.VERSION >= (1, 10):
                    field_obj = getattr(self.instance.__class__, field)
                else:
                    field_obj = self.instance.__class__.__dict__.get(field)
                if isinstance(field_obj, FileDescriptor):
                    field_tracker = FileDescriptorTracker(field_obj.field)
                    setattr(self.instance.__class__, field, field_tracker)
                else:
                    field_tracker = DeferredAttributeTracker(
                        field_obj.field_name, None)
                    setattr(self.instance.__class__, field, field_tracker)
        else:
            for field in self.fields:
                field_obj = self.instance.__class__.__dict__.get(field)
                if isinstance(field_obj, DeferredAttribute):
                    self.instance._deferred_fields.add(field)

                    # Django 1.4
                    if django.VERSION >= (1, 5):
                        model = None
                    else:
                        model = field_obj.model_ref()

                    field_tracker = DeferredAttributeTracker(
                        field_obj.field_name, model)
                    setattr(self.instance.__class__, field, field_tracker)
