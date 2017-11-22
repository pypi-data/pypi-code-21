# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_auto_20150925_1554'),
        ('yourwords', '0003_auto_20151119_1352'),
    ]

    operations = [
        migrations.AddField(
            model_name='yourwordscompetitionentry',
            name='article_page',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='core.ArticlePage', help_text='Page to which the entry was converted to', null=True),
        ),
    ]
