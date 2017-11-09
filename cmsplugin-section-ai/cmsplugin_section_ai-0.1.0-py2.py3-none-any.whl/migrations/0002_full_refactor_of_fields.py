# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import enumfields.fields
import cmsplugin_section_ai.enums


class Migration(migrations.Migration):

    dependencies = [
        ('cmsplugin_section_ai', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='section',
            name='full_width',
        ),
        migrations.RemoveField(
            model_name='section',
            name='no_bottom_margin',
        ),
        migrations.RemoveField(
            model_name='section',
            name='no_top_margin',
        ),
        migrations.RemoveField(
            model_name='section',
            name='type',
        ),
        migrations.AddField(
            model_name='link',
            name='size',
            field=enumfields.fields.EnumField(default='btn-md', enum=cmsplugin_section_ai.enums.ButtonSize, max_length=50, verbose_name='button size'),
        ),
        migrations.AddField(
            model_name='section',
            name='button_position',
            field=enumfields.fields.EnumField(default='text-left', enum=cmsplugin_section_ai.enums.Justify, max_length=50, verbose_name='section button alignment'),
        ),
        migrations.AddField(
            model_name='section',
            name='column_vertical_alignment',
            field=enumfields.fields.EnumField(default='align-items-start', enum=cmsplugin_section_ai.enums.VerticalAlign, max_length=75, verbose_name='vertical alignment for columns'),
        ),
        migrations.AddField(
            model_name='section',
            name='container_width',
            field=enumfields.fields.EnumField(default='container', enum=cmsplugin_section_ai.enums.ContainerSize, max_length=50, verbose_name='container width'),
        ),
        migrations.AddField(
            model_name='section',
            name='section_padding_bottom',
            field=enumfields.fields.EnumField(default='large-padding', enum=cmsplugin_section_ai.enums.SectionPadding, max_length=50, verbose_name='bottom padding for this section'),
        ),
        migrations.AddField(
            model_name='section',
            name='section_padding_top',
            field=enumfields.fields.EnumField(default='large-padding', enum=cmsplugin_section_ai.enums.SectionPadding, max_length=50, verbose_name='top padding for this section'),
        ),
        migrations.AddField(
            model_name='section',
            name='section_type',
            field=enumfields.fields.EnumField(default='one-column-section', enum=cmsplugin_section_ai.enums.SectionType, max_length=50, verbose_name='section type'),
        ),
        migrations.AddField(
            model_name='section',
            name='title_position',
            field=enumfields.fields.EnumField(default='text-left', enum=cmsplugin_section_ai.enums.Justify, max_length=50, verbose_name='title alignment'),
        ),
        migrations.AlterField(
            model_name='link',
            name='style',
            field=enumfields.fields.EnumField(default='btn-primary', enum=cmsplugin_section_ai.enums.ButtonStyle, max_length=50, verbose_name='button style'),
        ),
        migrations.AlterField(
            model_name='section',
            name='extra_margin',
            field=models.BooleanField(default=False, verbose_name='add extra vertical margin for inner columns'),
        ),
        migrations.AlterField(
            model_name='section',
            name='text_center',
            field=models.BooleanField(default=False, verbose_name='align column content text to center'),
        ),
    ]
