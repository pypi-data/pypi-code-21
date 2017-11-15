from django.db import models

def register(cls, admin_cls):
    cls.add_to_class('prepared_date', models.TextField('Date of Preparation', blank=True, null=True))

