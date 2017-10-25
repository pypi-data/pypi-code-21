# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('colab_audiencias', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AudienciasRoom',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('cod_reunion', models.CharField(max_length=200, null=True, blank=True)),
                ('online_users', models.IntegerField(default=0)),
                ('max_online_users', models.IntegerField(default=0)),
                ('created', models.DateTimeField(editable=False)),
                ('modified', models.DateTimeField(editable=False)),
                ('agenda', models.ForeignKey(related_name='room', blank=True, to='colab_audiencias.AudienciasAgenda', null=True)),
                ('video', models.ForeignKey(related_name='room', blank=True, to='colab_audiencias.AudienciasVideo', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='audienciasquestion',
            name='video',
        ),
        migrations.AddField(
            model_name='audienciasagenda',
            name='cod_reunion',
            field=models.CharField(max_length=200, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='audienciasquestion',
            name='room',
            field=models.ForeignKey(related_name='questions', default='', to='colab_audiencias.AudienciasRoom'),
            preserve_default=False,
        ),
    ]
