# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0016_auto_20160608_1535'),
    ]

    operations = [
        migrations.CreateModel(
            name='GoogleCalendar',
            fields=[
                ('title', models.CharField(verbose_name='Calendar title', blank=True, max_length=255)),
                ('width', models.CharField(default='100%', help_text='Width of the calendar, including the CSS length units (e.g. "100%", "400px" or "400rem").', verbose_name='Width', max_length=6)),
                ('height', models.CharField(default='400px', help_text='Height of the calendar, including the CSS length units (e.g. "400px" or "400rem").', verbose_name='Height', max_length=6)),
                ('cmsplugin_ptr', models.OneToOneField(related_name='djangocms_googlecalendar_googlecalendar', to='cms.CMSPlugin', parent_link=True, primary_key=True, serialize=False)),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
    ]
