# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('colab_pauta', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PautaGroup',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('theme_slug', models.CharField(max_length=250)),
                ('theme_name', models.CharField(max_length=250)),
                ('agenda', models.ForeignKey(related_name='groups', to='colab_pauta.PautaAgenda')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='pautaagenda',
            name='description',
        ),
    ]
