# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-08 15:44
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orchestra', '0029_allow_time_entries_without_assignment'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskTimer',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField(null=True)),
                ('stop_time', models.DateTimeField(null=True)),
                ('assignment', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE,
                                                    related_name='timer', to='orchestra.TaskAssignment')),
                ('worker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                             related_name='timers', to='orchestra.Worker')),
            ],
        ),
        migrations.AddField(
            model_name='timeentry',
            name='timer_start_time',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='timeentry',
            name='timer_stop_time',
            field=models.DateTimeField(null=True),
        ),
    ]
