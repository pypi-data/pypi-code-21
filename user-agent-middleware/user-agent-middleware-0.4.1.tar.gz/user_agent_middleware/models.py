# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from django.contrib.sessions.models import Session
from django.db import models
from django.db.models import Count
from django.conf import settings
from django.utils.translation import ugettext as _


# Create your models here.

AUTH_USER_MODEL = settings.AUTH_USER_MODEL


class Visitor(models.Model):
    """
    It will store information about user when logged in using django admin
    """
    name = models.ForeignKey(AUTH_USER_MODEL, verbose_name=_('User'), null=True)
    user_uid = models.CharField(max_length=225, null=True, blank=True)
    city = models.CharField(_('City'), max_length=255, null=True)
    state = models.CharField(_('State'), max_length=50, null=True)
    country = models.CharField(_('Country'), max_length=50, null=True)
    visit_datetime = models.DateTimeField(_('Login Date Time'), auto_now=True)
    browser = models.CharField(_('Browser'), max_length=30, null=True)
    browser_version = models.CharField(_('Browser Version'), max_length=20, null=True)
    ipaddress = models.CharField(_('IP Address'), max_length=20, null=True)
    os_info = models.CharField(_('OS Information'), max_length=30, null=True)
    os_info_version = models.CharField(_('OS Version'), max_length=20, null=True)
    device_type = models.CharField(_('Device Type'), max_length=20,
                                   null=True)
    device_name = models.CharField(_('Device Name'), max_length=20, null=True)
    device_name_brand = models.CharField(_('Device Brand Name'), max_length=20, null=True)
    device_name_model = models.CharField(_('Device Model Name'), max_length=20, null=True)
    unique_computer_processor = models.CharField(_('Computer Processor'), max_length=255, null=True)
    session = models.ForeignKey(Session, verbose_name=_('Session'), null=True, blank=True, on_delete=models.SET_NULL)
    latitude = models.DecimalField(_('Latitude'), max_digits=9, decimal_places=6, null=True)
    longitude = models.DecimalField(_('Longitude'), max_digits=9, decimal_places=6, null=True)

    class Meta:
        ordering = ['visit_datetime']
        verbose_name = _("visitor")
        verbose_name_plural = _("visitors")

    def __str__(self):
        return self.os_info

    @staticmethod
    def get_visitors(field_name):
        """
        It will provide distinct field value's according to any given field and
         also provide count of repeat value of field.
        :param field_name:
        :return:
        """
        return Visitor.objects.values(field_name).annotate(count=Count('id')).order_by(field_name)
