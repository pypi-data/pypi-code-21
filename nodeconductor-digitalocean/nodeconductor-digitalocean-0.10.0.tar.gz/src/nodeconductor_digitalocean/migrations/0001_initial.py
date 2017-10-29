# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import nodeconductor.logging.loggers
import model_utils.fields
import nodeconductor.core.fields
import nodeconductor.structure.models
import nodeconductor.core.models
import django.db.models.deletion
import django.utils.timezone
import taggit.managers
import django_fsm
import nodeconductor.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        ('structure', '0037_remove_customer_billing_backend_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='DigitalOceanService',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='name', validators=[nodeconductor.core.validators.validate_name])),
                ('uuid', nodeconductor.core.fields.UUIDField()),
                ('available_for_all', models.BooleanField(default=False, help_text='Service will be automatically added to all customers projects if it is available for all')),
                ('customer', models.ForeignKey(verbose_name='organization', to='structure.Customer')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'DigitalOcean provider',
                'verbose_name_plural': 'DigitalOcean providers',
            },
            bases=(nodeconductor.core.models.DescendantMixin, nodeconductor.logging.loggers.LoggableMixin, models.Model),
        ),
        migrations.CreateModel(
            name='DigitalOceanServiceProjectLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('project', models.ForeignKey(to='structure.Project')),
                ('service', models.ForeignKey(to='nodeconductor_digitalocean.DigitalOceanService')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'DigitalOcean provider project link',
                'verbose_name_plural': 'DigitalOcean provider project links',
            },
            bases=(nodeconductor.core.models.DescendantMixin, nodeconductor.logging.loggers.LoggableMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Droplet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('description', models.CharField(max_length=500, verbose_name='description', blank=True)),
                ('name', models.CharField(max_length=150, verbose_name='name', validators=[nodeconductor.core.validators.validate_name])),
                ('uuid', nodeconductor.core.fields.UUIDField()),
                ('error_message', models.TextField(blank=True)),
                ('latitude', models.FloatField(null=True, blank=True)),
                ('longitude', models.FloatField(null=True, blank=True)),
                ('runtime_state', models.CharField(max_length=150, verbose_name='runtime state', blank=True)),
                ('state', django_fsm.FSMIntegerField(default=5, choices=[(5, 'Creation Scheduled'), (6, 'Creating'), (1, 'Update Scheduled'), (2, 'Updating'), (7, 'Deletion Scheduled'), (8, 'Deleting'), (3, 'OK'), (4, 'Erred')])),
                ('cores', models.PositiveSmallIntegerField(default=0, help_text='Number of cores in a VM')),
                ('ram', models.PositiveIntegerField(default=0, help_text='Memory size in MiB')),
                ('disk', models.PositiveIntegerField(default=0, help_text='Disk size in MiB')),
                ('min_ram', models.PositiveIntegerField(default=0, help_text='Minimum memory size in MiB')),
                ('min_disk', models.PositiveIntegerField(default=0, help_text='Minimum disk size in MiB')),
                ('external_ips', models.GenericIPAddressField(null=True, protocol='IPv4', blank=True)),
                ('internal_ips', models.GenericIPAddressField(null=True, protocol='IPv4', blank=True)),
                ('image_name', models.CharField(max_length=150, blank=True)),
                ('key_name', models.CharField(max_length=50, blank=True)),
                ('key_fingerprint', models.CharField(max_length=47, blank=True)),
                ('user_data', models.TextField(help_text='Additional data that will be added to instance on provisioning', blank=True)),
                ('backend_id', models.CharField(max_length=255, blank=True)),
                ('start_time', models.DateTimeField(null=True, blank=True)),
                ('transfer', models.PositiveIntegerField(default=0, help_text='Amount of transfer bandwidth in MiB')),
                ('service_project_link', models.ForeignKey(related_name='droplets', on_delete=django.db.models.deletion.PROTECT, to='nodeconductor_digitalocean.DigitalOceanServiceProjectLink')),
                ('tags', taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', blank=True, help_text='A comma-separated list of tags.', verbose_name='Tags')),
            ],
            options={
                'abstract': False,
            },
            bases=(nodeconductor.core.models.DescendantMixin, nodeconductor.logging.loggers.LoggableMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='name', validators=[nodeconductor.core.validators.validate_name])),
                ('uuid', nodeconductor.core.fields.UUIDField()),
                ('backend_id', models.CharField(unique=True, max_length=255)),
                ('distribution', models.CharField(max_length=100)),
                ('type', models.CharField(max_length=100)),
                ('is_official', models.BooleanField(default=False, help_text='Is image provided by DigitalOcean')),
                ('min_disk_size', models.PositiveIntegerField(help_text='Minimum disk required for a size to use this image', null=True)),
                ('created_at', models.DateTimeField(null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='name', validators=[nodeconductor.core.validators.validate_name])),
                ('uuid', nodeconductor.core.fields.UUIDField()),
                ('backend_id', models.CharField(unique=True, max_length=255)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Size',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='name', validators=[nodeconductor.core.validators.validate_name])),
                ('uuid', nodeconductor.core.fields.UUIDField()),
                ('backend_id', models.CharField(unique=True, max_length=255)),
                ('cores', models.PositiveSmallIntegerField(help_text='Number of cores in a VM')),
                ('ram', models.PositiveIntegerField(help_text='Memory size in MiB')),
                ('disk', models.PositiveIntegerField(help_text='Disk size in MiB')),
                ('transfer', models.PositiveIntegerField(help_text='Amount of transfer bandwidth in MiB')),
                ('price', models.DecimalField(default=0, verbose_name='Hourly price rate', max_digits=11, decimal_places=5)),
                ('regions', models.ManyToManyField(to='nodeconductor_digitalocean.Region')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='image',
            name='regions',
            field=models.ManyToManyField(to='nodeconductor_digitalocean.Region'),
        ),
        migrations.AddField(
            model_name='digitaloceanservice',
            name='projects',
            field=models.ManyToManyField(related_name='digitalocean_services', through='nodeconductor_digitalocean.DigitalOceanServiceProjectLink', to='structure.Project'),
        ),
        migrations.AddField(
            model_name='digitaloceanservice',
            name='settings',
            field=models.ForeignKey(to='structure.ServiceSettings'),
        ),
        migrations.AlterUniqueTogether(
            name='digitaloceanserviceprojectlink',
            unique_together=set([('service', 'project')]),
        ),
        migrations.AlterUniqueTogether(
            name='digitaloceanservice',
            unique_together=set([('customer', 'settings')]),
        ),
    ]
