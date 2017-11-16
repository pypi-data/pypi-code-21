# -*- coding:utf-8 -*- 
from django.apps import AppConfig

class Config(AppConfig):
    name = 'django_szuprefix.survey'
    verbose_name = u'调查问卷'
    # def ready(self):
    #     from . import receivers
