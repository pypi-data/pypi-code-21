# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PautaAgenda',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('initial_date', models.DateField()),
                ('end_date', models.DateField()),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('votes_count', models.IntegerField(default=0)),
                ('participants_count', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name': 'Pauta Agenda',
                'verbose_name_plural': 'Pauta Agendas',
            },
            bases=(models.Model,),
        ),
    ]
