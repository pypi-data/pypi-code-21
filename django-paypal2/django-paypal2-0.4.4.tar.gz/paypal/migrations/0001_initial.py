# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-29 02:59
from __future__ import unicode_literals

from django.db import migrations, models
import django_extensions.db.fields.json


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PaypalTransaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=127)),
                ('items', django_extensions.db.fields.json.JSONField(default=[])),
                ('reference_id', models.CharField(blank=True, max_length=256, null=True)),
                ('note_to_payer', models.CharField(blank=True, max_length=165, null=True)),
                ('custom', models.CharField(blank=True, max_length=127, null=True)),
                ('payment_id', models.CharField(blank=True, max_length=64, null=True)),
                ('invoice_number', models.CharField(blank=True, max_length=127, null=True)),
                ('amount_total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('currency', models.CharField(choices=[('USD', 'USD')], max_length=3)),
                ('amount_details', django_extensions.db.fields.json.JSONField(default={})),
                ('payer_id', models.CharField(blank=True, max_length=16, null=True)),
                ('payer_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('payer_data', django_extensions.db.fields.json.JSONField(default=dict, null=True)),
                ('payee_merchant_id', models.CharField(blank=True, max_length=16, null=True)),
                ('state', models.CharField(choices=[('created', 'created'), ('approved', 'approved'), ('failed', 'failed')], max_length=16)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
