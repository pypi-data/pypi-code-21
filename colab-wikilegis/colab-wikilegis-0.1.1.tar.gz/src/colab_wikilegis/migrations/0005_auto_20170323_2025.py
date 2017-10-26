# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('colab_wikilegis', '0004_wikilegisbill_closing_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='WikilegisBillTheme',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('description', models.CharField(unique=True, max_length=50)),
                ('slug', models.SlugField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='wikilegiscomment',
            name='user',
        ),
        migrations.DeleteModel(
            name='WikilegisComment',
        ),
        migrations.RemoveField(
            model_name='wikilegissegment',
            name='author',
        ),
        migrations.RemoveField(
            model_name='wikilegissegment',
            name='bill',
        ),
        migrations.RemoveField(
            model_name='wikilegissegment',
            name='parent',
        ),
        migrations.RemoveField(
            model_name='wikilegissegment',
            name='replaced',
        ),
        migrations.RemoveField(
            model_name='wikilegissegment',
            name='type',
        ),
        migrations.DeleteModel(
            name='WikilegisSegment',
        ),
        migrations.DeleteModel(
            name='WikilegisSegmentType',
        ),
        migrations.RemoveField(
            model_name='wikilegisbill',
            name='theme',
        ),
        migrations.AddField(
            model_name='wikilegisbill',
            name='amendments_count',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='wikilegisbill',
            name='comments_count',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='wikilegisbill',
            name='downvote_count',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='wikilegisbill',
            name='upvote_count',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='wikilegisbill',
            name='votes_count',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
