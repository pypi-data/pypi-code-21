#!/usr/bin/env python
# -*- coding:utf-8 -*-

''' Model file for testing purposes
© StoneworkSolutions 2017-01-11
'''

from django.db import models


class TstModel(models.Model):
    textfield = models.CharField(max_length=255, verbose_name='Text field')
    active = models.BooleanField(default=True, verbose_name='Active')


def getFilterActive():
    ''' Returns active filter '''
    return [{"text": 'true', "id": 'true'}, {"text": 'false', "id": 'false'}]
