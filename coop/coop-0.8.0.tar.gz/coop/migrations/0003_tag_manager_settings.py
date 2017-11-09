# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coop', '0002_analyticssettings'),
    ]

    operations = [
        migrations.AddField(
            model_name='analyticssettings',
            name='google_tag_manager',
            field=models.CharField(blank=True, help_text='Your Google Tag Manager container ID, e.g GTM-XXXX', max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='analyticssettings',
            name='google_analytics',
            field=models.CharField(blank=True, help_text='Your Google Analytics property ID, e.g UA-XXXXX-Y', max_length=10, null=True),
        ),
    ]
