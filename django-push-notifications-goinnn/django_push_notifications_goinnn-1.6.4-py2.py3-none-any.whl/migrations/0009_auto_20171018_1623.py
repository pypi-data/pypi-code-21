# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def add_application_id(apps, schema_editor):
    WebPushDevice = apps.get_model('push_notifications', 'WebPushDevice')
    FirefoxDevice = apps.get_model('push_notifications', 'FirefoxDevice')
    APNSDevice = apps.get_model('push_notifications', 'APNSDevice')

    GCMDevice = apps.get_model('push_notifications', 'GCMDevice')
    devices = FirefoxDevice.objects.all()
    devices.delete()
    devices = GCMDevice.objects.filter(name__startswith='browser')
    devices.delete()

    APNSDevice.objects.filter(company='accenture').update(application_id='APNS_ACCENTURE')

    APNSDevice.objects.exclude(company='accenture').filter(name__icontains='@').update(application_id='APNS_PASSENGER')

    APNSDevice.objects.exclude(company='accenture').exclude(name__icontains='@').update(application_id='APNS_TAXI')
    GCMDevice.objects.all().update(application_id='GCM')

    WebPushDevice.objects.all().update(application_id='BROWSER')


class Migration(migrations.Migration):

    dependencies = [
        ('push_notifications', '0008_auto_20171018_1621'),
    ]

    operations = [
        migrations.RunPython(add_application_id, migrations.RunPython.noop),
    ]
