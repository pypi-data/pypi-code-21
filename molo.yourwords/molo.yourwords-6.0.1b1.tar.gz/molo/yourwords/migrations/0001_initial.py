# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import molo.core.blocks
import wagtail.wagtailcore.fields
import wagtail.wagtailimages.blocks
from django.conf import settings
import django.db.models.deletion
import wagtail.wagtailcore.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_auto_20150925_1554'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('wagtailimages', '0006_add_verbose_names'),
        ('wagtailcore', '0001_squashed_0016_change_page_url_path_to_text_field'),
    ]

    operations = [
        migrations.CreateModel(
            name='TermsAndConditions',
            fields=[
                ('articlepage_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='core.ArticlePage')),
            ],
            options={
                'abstract': False,
            },
            bases=('core.articlepage',),
        ),
        migrations.CreateModel(
            name='ThankYou',
            fields=[
                ('articlepage_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='core.ArticlePage')),
            ],
            options={
                'abstract': False,
            },
            bases=('core.articlepage',),
        ),
        migrations.CreateModel(
            name='YourWordsCompetition',
            fields=[
                ('page_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('description', models.TextField(null=True, blank=True)),
                ('content', wagtail.wagtailcore.fields.StreamField([(b'heading', wagtail.wagtailcore.blocks.CharBlock(classname=b'full title')), (b'paragraph', molo.core.blocks.MarkDownBlock()), (b'image', wagtail.wagtailimages.blocks.ImageChooserBlock()), (b'list', wagtail.wagtailcore.blocks.ListBlock(wagtail.wagtailcore.blocks.CharBlock(label=b'Item'))), (b'numbered_list', wagtail.wagtailcore.blocks.ListBlock(wagtail.wagtailcore.blocks.CharBlock(label=b'Item'))), (b'page', wagtail.wagtailcore.blocks.PageChooserBlock())], null=True, blank=True)),
                ('start_date', models.DateTimeField(null=True, blank=True)),
                ('end_date', models.DateTimeField(null=True, blank=True)),
                ('extra_style_hints', models.TextField(default=b'', help_text='Styling options that can be applied to this section and all its descendants', null=True, blank=True)),
                ('image', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='wagtailimages.Image', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='YourWordsCompetitionEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('story_name', models.CharField(max_length=128)),
                ('story_text', models.TextField()),
                ('terms_or_conditions_approved', models.BooleanField()),
                ('hide_real_name', models.BooleanField()),
                ('competition', models.ForeignKey(to='yourwords.YourWordsCompetition')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
