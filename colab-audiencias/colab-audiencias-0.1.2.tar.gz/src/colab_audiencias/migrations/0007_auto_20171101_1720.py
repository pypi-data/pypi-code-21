# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('colab_audiencias', '0006_auto_20170524_1404'),
    ]

    operations = [
        migrations.AddField(
            model_name='audienciasroom',
            name='legislative_body',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='audienciasroom',
            name='legislative_body_initials',
            field=models.CharField(max_length=200, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='audienciasroom',
            name='reunion_status',
            field=models.IntegerField(default=1, choices=[(1, b'N\xc3\xa3o Confirmada'), (2, b'Convocada'), (3, b'Em Andamento'), (4, b'Encerrada'), (5, b'Cancelada'), (6, b'Suspensa'), (7, b'Encerrada (Termo)'), (8, b'Encerrada (Final)'), (9, b'Encerrada(Comunicado)')]),
            preserve_default=True,
        ),
    ]
