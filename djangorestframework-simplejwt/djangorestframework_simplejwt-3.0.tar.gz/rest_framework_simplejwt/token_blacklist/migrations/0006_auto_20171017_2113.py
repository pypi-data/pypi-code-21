# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-10-17 21:13
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('token_blacklist', '0005_remove_outstandingtoken_jti'),
    ]

    operations = [
        migrations.RenameField(
            model_name='outstandingtoken',
            old_name='jti_hex',
            new_name='jti',
        ),
    ]
