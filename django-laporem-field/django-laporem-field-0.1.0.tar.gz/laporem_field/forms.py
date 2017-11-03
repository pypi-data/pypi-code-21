from uuid import UUID

from django.db import models
from django import forms
from django.db.models import QuerySet

from laporem_field.widget import LaporemWidget


class LaporemImageField(models.Field):
    def __init__(self, *args, **kwargs):
        self.laporem_model_file = kwargs.pop("laporem_model_file", None)
        super(LaporemImageField, self).__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection, context):
        objs = self.laporem_model_file.objects.filter(object_id=value).order_by('weight')
        return objs

    def db_type(self, connection):
        return 'char(200)'

    def get_db_prep_save(self, value, connection):
        if isinstance(value, QuerySet) and value.count() > 0:
            value = value.first().object_id
        elif isinstance(value, UUID) or isinstance(value, str):
            pass
        else:
            value = None
        return self.get_db_prep_value(value, connection=connection,
                                      prepared=False)

    def get_internal_type(self):
        return "LaporemImageField"

    def formfield(self, **kwargs):
        defaults = {
            'form_class': self._get_form_class(),
            'laporem_model_file': self.laporem_model_file,
            'base_model': self.model.__name__.lower()
        }
        defaults.update(kwargs)
        return super(LaporemImageField, self).formfield(**defaults)

    @staticmethod
    def _get_form_class():
        return LaporemUploadingFormField


class LaporemUploadingFormField(forms.fields.CharField):
    def __init__(self, laporem_model_file=None, base_model=None, *args, **kwargs):
        kwargs.update({'widget': LaporemWidget(laporem_model_file=laporem_model_file, base_model=base_model), 'label': "Действия"})
        super(LaporemUploadingFormField, self).__init__(*args, **kwargs)



