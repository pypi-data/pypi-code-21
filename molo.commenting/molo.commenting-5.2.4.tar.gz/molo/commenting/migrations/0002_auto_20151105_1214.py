# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commenting', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='molocomment',
            options={'ordering': ['-submit_date', 'tree_id', 'lft']},
        ),
    ]
