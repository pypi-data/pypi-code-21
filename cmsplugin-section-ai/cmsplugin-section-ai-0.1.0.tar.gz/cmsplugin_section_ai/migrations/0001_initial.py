# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import filer.fields.file
import enumfields.fields
import django.db.models.deletion

from .. import enums


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0016_auto_20160608_1535'),
        ('filer', '0006_auto_20160623_1627'),
    ]

    operations = [
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.CharField(verbose_name='button text', max_length=75)),
                ('url', models.CharField(verbose_name='url', max_length=250, blank=True)),
                ('style', enumfields.fields.EnumField(verbose_name='Button style', enum=enums.ButtonStyle, max_length=50, default='btn-primary')),
                ('anchor', models.CharField(verbose_name='bind to anchor', help_text='Set the anchor identifier of an element. Leave out the # prefix.', blank=True, max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(to='cms.CMSPlugin', primary_key=True, related_name='cmsplugin_section_ai_section', serialize=False, parent_link=True, auto_created=True)),
                ('type', enumfields.fields.EnumIntegerField(verbose_name='section type', enum=enums.SectionType, default=1)),
                ('title', models.CharField(verbose_name='title', help_text='Visible title for this section', blank=True, max_length=75)),
                ('background_color', enumfields.fields.EnumField(verbose_name='background color', enum=enums.BackgroundColor, max_length=50, default='bg-color-transparent')),
                ('full_width', models.BooleanField(verbose_name='make the content 100% wide', default=False)),
                ('no_top_margin', models.BooleanField(verbose_name='remove top margin from this section', default=False)),
                ('no_bottom_margin', models.BooleanField(verbose_name='remove bottom margin from this section', default=False)),
                ('extra_margin', models.BooleanField(verbose_name='add extra vertical margin for content', default=False)),
                ('text_center', models.BooleanField(verbose_name='align content text to center', default=False)),
                ('anchor', models.CharField(verbose_name='anchor identifier', help_text='Set anchor identifier for this section to be used with anchor links.', blank=True, max_length=50)),
                ('background_image', filer.fields.file.FilerFileField(verbose_name='background image', blank=True, to='filer.File', help_text='This overrides any given background color', null=True, on_delete=django.db.models.deletion.SET_NULL)),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='SectionButton',
            fields=[
                ('link_ptr', models.OneToOneField(to='cmsplugin_section_ai.Link', primary_key=True, parent_link=True, serialize=False, auto_created=True)),
                ('section', models.ForeignKey(verbose_name='section', to='cmsplugin_section_ai.Section', related_name='section_buttons')),
            ],
            bases=('cmsplugin_section_ai.link',),
        ),
        migrations.AddField(
            model_name='link',
            name='page_link',
            field=models.ForeignKey(verbose_name='link to a page', blank=True, to='cms.Page', related_name='section', help_text='Page link overrides any given URL.', null=True, on_delete=django.db.models.deletion.SET_NULL),
        ),
    ]
