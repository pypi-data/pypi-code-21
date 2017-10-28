# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('epic', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='part',
            name='last_bom_mod_name',
            field=models.CharField(default=b'', help_text=b'Name of entity which last modified this part.', max_length=31, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='part',
            name='last_bom_mod_type',
            field=models.IntegerField(default=0, choices=[(0, b'user'), (1, b'tool')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='vendor_part',
            name='status',
            field=models.IntegerField(default=1, help_text=b'The life-time status of this vendor part.', verbose_name=b'Life-time Status', choices=[(0, b'preview'), (1, b'active'), (2, b'deprecated'), (3, b'obsolete')]),
            preserve_default=True,
        ),
    ]
