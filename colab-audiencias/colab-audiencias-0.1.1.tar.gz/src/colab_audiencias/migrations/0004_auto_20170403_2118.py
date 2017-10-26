# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('colab_audiencias', '0003_audienciasroom_is_visible'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='audienciasroom',
            name='agenda',
        ),
        migrations.DeleteModel(
            name='AudienciasAgenda',
        ),
        migrations.RemoveField(
            model_name='audienciasroom',
            name='video',
        ),
        migrations.DeleteModel(
            name='AudienciasVideo',
        ),
        migrations.AddField(
            model_name='audienciasroom',
            name='legislative_body_alias',
            field=models.CharField(max_length=200, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='audienciasroom',
            name='youtube_id',
            field=models.CharField(max_length=200, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='audienciasroom',
            name='youtube_status',
            field=models.IntegerField(default=0, choices=[(0, b'Sem transmiss\xc3\xa3o'), (1, b'Em andamento'), (2, b'Transmiss\xc3\xa3o encerrada')]),
            preserve_default=True,
        ),
    ]
