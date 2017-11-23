# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('yourwords', '0002_yourwordscompetitionentry_submission_date'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='yourwordscompetition',
            options={'verbose_name': 'YourWords Competition', 'verbose_name_plural': 'YourWords Competitions'},
        ),
        migrations.AlterModelOptions(
            name='yourwordscompetitionentry',
            options={'verbose_name': 'YourWords Competition Entry', 'verbose_name_plural': 'YourWords Competition Entries'},
        ),
        migrations.AddField(
            model_name='yourwordscompetitionentry',
            name='is_read',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='yourwordscompetitionentry',
            name='is_shortlisted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='yourwordscompetitionentry',
            name='is_winner',
            field=models.BooleanField(default=False),
        ),
    ]
