# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AudienciasAgenda',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('date', models.DateTimeField(null=True, blank=True)),
                ('session', models.CharField(max_length=200, null=True, blank=True)),
                ('location', models.CharField(max_length=200, null=True, blank=True)),
                ('situation', models.CharField(max_length=200, null=True, blank=True)),
                ('commission', models.CharField(max_length=200, null=True, blank=True)),
                ('created', models.DateTimeField(editable=False)),
                ('modified', models.DateTimeField(editable=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AudienciasQuestion',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('question', models.TextField()),
                ('answer_time', models.CharField(max_length=200, null=True, blank=True)),
                ('created', models.DateTimeField(editable=False)),
                ('modified', models.DateTimeField(editable=False)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AudienciasVideo',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('videoId', models.CharField(unique=True, max_length=200)),
                ('thumb_default', models.URLField(null=True, blank=True)),
                ('thumb_medium', models.URLField(null=True, blank=True)),
                ('thumb_high', models.URLField(null=True, blank=True)),
                ('title', models.CharField(max_length=200, null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('published_date', models.DateTimeField(auto_now=True)),
                ('closed_date', models.DateTimeField(null=True, blank=True)),
                ('slug', models.SlugField(max_length=200, blank=True)),
                ('created', models.DateTimeField(editable=False)),
                ('modified', models.DateTimeField(editable=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='audienciasquestion',
            name='video',
            field=models.ForeignKey(related_name='questions', to='colab_audiencias.AudienciasVideo'),
            preserve_default=True,
        ),
    ]
