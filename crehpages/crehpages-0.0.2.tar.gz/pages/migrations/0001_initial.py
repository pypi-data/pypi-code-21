# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import pages.utils.image
import django.utils.timezone
import imagekit.models.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('seo_title', models.CharField(max_length=100)),
                ('seo_sub_title', models.CharField(max_length=100)),
                ('seo_desc', models.CharField(max_length=100)),
                ('seo_keywords', models.CharField(max_length=100)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('is_active', models.BooleanField(default=False)),
                ('title', models.CharField(max_length=100)),
                ('slug', models.SlugField(max_length=150)),
                ('external_url', models.URLField(max_length=500, verbose_name=b'External URL', blank=True)),
            ],
            options={
                'db_table': 'pages',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Slider',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('title', models.CharField(max_length=200)),
                ('is_active', models.BooleanField(default=False)),
                ('dots', models.BooleanField(default=False)),
                ('speed', models.IntegerField(default=500)),
                ('page', models.ForeignKey(to='pages.Page')),
            ],
            options={
                'db_table': 'sliders',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SliderContent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.TextField()),
                ('config', models.TextField()),
                ('order', models.SmallIntegerField(default=1)),
            ],
            options={
                'db_table': 'slider_contents',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SliderContentType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'slider_content_types',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SliderItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('is_active', models.BooleanField(default=False)),
                ('picture_pc', imagekit.models.fields.ProcessedImageField(upload_to=pages.utils.image.upload_picture_to)),
                ('picture_tablet', imagekit.models.fields.ProcessedImageField(null=True, upload_to=pages.utils.image.upload_picture_to)),
                ('picture_mobile', imagekit.models.fields.ProcessedImageField(null=True, upload_to=pages.utils.image.upload_picture_to)),
                ('active_from', models.DateTimeField()),
                ('active_to', models.DateTimeField()),
                ('order', models.SmallIntegerField(default=1)),
                ('slider', models.ForeignKey(to='pages.Slider')),
            ],
            options={
                'db_table': 'slider_items',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='slideritem',
            unique_together=set([('order', 'slider')]),
        ),
        migrations.AddField(
            model_name='slidercontent',
            name='slider_item',
            field=models.ForeignKey(to='pages.SliderItem'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='slidercontent',
            name='type_content',
            field=models.ForeignKey(to='pages.SliderContentType'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='slidercontent',
            unique_together=set([('order', 'slider_item')]),
        ),
    ]
