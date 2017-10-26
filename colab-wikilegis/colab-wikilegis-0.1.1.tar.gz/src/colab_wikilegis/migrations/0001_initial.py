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
            name='WikilegisBill',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('title', models.CharField(max_length=999)),
                ('epigraph', models.CharField(max_length=999, null=True)),
                ('description', models.CharField(max_length=999)),
                ('status', models.CharField(default=b'1', max_length=999, choices=[(b'draft', 'Draft'), (b'published', 'Published'), (b'closed', 'Closed')])),
                ('theme', models.CharField(default=b'documento', max_length=999, choices=[(b'documento', 'Others'), (b'adm-publica', 'Public Administration'), (b'agropecuaria', 'Farming'), (b'assistencia-social', 'Social Assistance'), (b'cidades', 'Cities'), (b'ciencia', 'Science'), (b'comunicacao', 'Communication'), (b'consumidor', 'Consumer'), (b'cultura', 'Culture'), (b'direito-e-justica', 'Law and Justice'), (b'direitos-humanos', 'Human Rights'), (b'economia', 'Economy'), (b'educacao', 'Education'), (b'esportes', 'Sports'), (b'familia', 'Family'), (b'industria', 'Industry'), (b'institucional', 'Institutional'), (b'meio-ambiente', 'Environment'), (b'participacao_e_transparencia', 'Participation and Transparency'), (b'politica', 'Policy'), (b'previdencia', 'Foresight'), (b'relacoes-exteriores', 'Foreign Affairs'), (b'saude', 'Health'), (b'seguranca', 'Security'), (b'trabalho', 'Work'), (b'transporte-e-transito', 'Transportation and Transit'), (b'turismo', 'Tourism')])),
                ('created', models.DateTimeField(editable=False)),
                ('modified', models.DateTimeField(editable=False)),
                ('reporting_member', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='WikilegisComment',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('submit_date', models.DateTimeField()),
                ('content_type', models.CharField(max_length=999)),
                ('object_pk', models.IntegerField()),
                ('comment', models.TextField()),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='WikilegisSegment',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('original', models.BooleanField(default=True)),
                ('number', models.PositiveIntegerField(default=0, null=True, blank=True)),
                ('content', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('bill', models.ForeignKey(related_name='segments', to='colab_wikilegis.WikilegisBill')),
                ('parent', models.ForeignKey(related_name='children', blank=True, to='colab_wikilegis.WikilegisSegment', null=True)),
                ('replaced', models.ForeignKey(related_name='substitutes', blank=True, to='colab_wikilegis.WikilegisSegment', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='WikilegisSegmentType',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=999)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='wikilegissegment',
            name='type',
            field=models.ForeignKey(to='colab_wikilegis.WikilegisSegmentType'),
            preserve_default=True,
        ),
    ]
