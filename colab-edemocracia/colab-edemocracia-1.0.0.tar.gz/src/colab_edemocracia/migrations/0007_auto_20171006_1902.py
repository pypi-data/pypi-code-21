# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('colab_edemocracia', '0006_auto_20170908_2045'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userprofile',
            options={'verbose_name': 'perfil', 'verbose_name_plural': 'perfis'},
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='birthdate',
            field=models.DateField(null=True, verbose_name=b'data de nascimento', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='birthyear',
            field=models.IntegerField(max_length=4, null=True, verbose_name=b'ano de nascimento', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='country',
            field=models.CharField(max_length=200, null=True, verbose_name=b'pa\xc3\xads', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='gender',
            field=models.CharField(blank=True, max_length=999, null=True, verbose_name=b'g\xc3\xaanero', choices=[(b'male', b'Masculino'), (b'female', b'Feminino'), (b'other', b'Outro'), (b'undisclosed', b'Prefiro n\xc3\xa3o informar')]),
            preserve_default=True,
        ),
    ]
