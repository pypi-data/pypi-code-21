# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nodeconductor_digitalocean', '0002_remove_digitaloceanservice_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='droplet',
            old_name='external_ips',
            new_name='ip_address',
        ),
        migrations.RemoveField(
            model_name='droplet',
            name='internal_ips',
        ),
    ]
