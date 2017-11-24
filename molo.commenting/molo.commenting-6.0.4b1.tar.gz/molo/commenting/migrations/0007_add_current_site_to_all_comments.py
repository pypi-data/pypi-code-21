# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def add_site_to_comments(apps, schema_editor):
    MoloComment = apps.get_model("commenting", "MoloComment")
    Site = apps.get_model("wagtailcore", "Site")
    site = Site.objects.all().first()
    if site:
        for comment in MoloComment.objects.all():
            comment.molocomment.wagtail_site = site
            comment.molocomment.save()


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '__latest__'),
        ('commenting', '0006_add_wagtail_site_to_comment'),
    ]

    operations = [
        migrations.RunPython(add_site_to_comments),
    ]
