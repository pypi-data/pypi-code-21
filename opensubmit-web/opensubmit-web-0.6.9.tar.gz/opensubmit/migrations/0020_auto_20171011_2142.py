# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2017-10-11 21:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('opensubmit', '0019_auto_20171011_2103'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='description',
            field=models.FileField(blank=True, help_text=b'Uploaded document with the assignment description.', null=True, upload_to=b'assignment_desc', verbose_name=b'As file'),
        ),
        migrations.AlterField(
            model_name='assignment',
            name='download',
            field=models.URLField(blank=True, help_text=b'External link to the assignment description.', null=True, verbose_name=b'As link'),
        ),
        migrations.AlterField(
            model_name='assignment',
            name='gradingScheme',
            field=models.ForeignKey(blank=True, help_text=b'Grading scheme for this assignment. Leave empty to have an ungraded assignment.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assignments', to='opensubmit.GradingScheme', verbose_name=b'grading scheme'),
        ),
        migrations.AlterField(
            model_name='assignment',
            name='hard_deadline',
            field=models.DateTimeField(blank=True, help_text=b'Deadline after which submissions are no longer possible. Can be empty.', null=True),
        ),
        migrations.AlterField(
            model_name='assignment',
            name='has_attachment',
            field=models.BooleanField(default=False, help_text=b'Activate this if the students must upload a (document / ZIP /TGZ) file as solution. Otherwise, they can only provide notes.', verbose_name=b'Student file upload ?'),
        ),
        migrations.AlterField(
            model_name='assignment',
            name='publish_at',
            field=models.DateTimeField(default=django.utils.timezone.now, help_text=b'Shown for students after this point in time. Users with backend rights always see it.'),
        ),
    ]
