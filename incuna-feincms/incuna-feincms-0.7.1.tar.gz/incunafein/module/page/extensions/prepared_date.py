from django.db import models

def get_prepared_date(cls):
    return cls.prepared_date or cls.parent.prepared_date

def register(cls, admin_cls):
    cls.add_to_class('prepared_date', models.TextField('Date of Preparation', blank=True, null=True))
    cls.add_to_class('get_prepared_date', get_prepared_date)

