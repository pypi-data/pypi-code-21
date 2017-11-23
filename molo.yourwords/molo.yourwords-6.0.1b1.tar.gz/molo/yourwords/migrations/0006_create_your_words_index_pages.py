# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def create_competition_index(apps, schema_editor):
    from molo.core.models import Main
    from molo.yourwords.models import YourWordsCompetitionIndexPage
    main = Main.objects.all().first()

    if main:
        competition_index = YourWordsCompetitionIndexPage(title='Your words competitions', slug='Your-words-competitions')
        main.add_child(instance=competition_index)
        competition_index.save_revision().publish()


class Migration(migrations.Migration):

    dependencies = [
        ('yourwords', '0005_your_words_competition_indexPage'),
    ]

    operations = [
        migrations.RunPython(create_competition_index),
    ]
