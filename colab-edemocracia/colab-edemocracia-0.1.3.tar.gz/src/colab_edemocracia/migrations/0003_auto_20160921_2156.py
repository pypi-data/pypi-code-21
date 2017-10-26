# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import image_cropping.fields


class Migration(migrations.Migration):

    dependencies = [
        ('colab_edemocracia', '0002_remove_userprofile_photo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='birthdate',
            field=models.DateField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='userprofile',
            name=b'cropping',
            field=image_cropping.fields.ImageRatioField(b'avatar', '140x140', hide_image_field=False, size_warning=False, allow_fullsize=False, free_crop=False, adapt_rotation=False, help_text=None, verbose_name='cropping'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='gender',
            field=models.CharField(blank=True, max_length=999, null=True, choices=[(b'male', b'Masculino'), (b'female', b'Feminino'), (b'other', b'Outro')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='uf',
            field=models.CharField(blank=True, max_length=2, null=True, choices=[(b'AC', b'AC'), (b'AL', b'AL'), (b'AP', b'AP'), (b'AM', b'AM'), (b'BA', b'BA'), (b'CE', b'CE'), (b'DF', b'DF'), (b'ES', b'ES'), (b'GO', b'GO'), (b'MA', b'MA'), (b'MS', b'MS'), (b'MT', b'MT'), (b'MG', b'MG'), (b'PA', b'PA'), (b'PB', b'PB'), (b'PR', b'PR'), (b'PE', b'PE'), (b'PI', b'PI'), (b'RJ', b'RJ'), (b'RN', b'RN'), (b'RS', b'RS'), (b'RO', b'RO'), (b'RR', b'RR'), (b'SC', b'SC'), (b'SP', b'SP'), (b'SE', b'SE'), (b'TO', b'TO')]),
            preserve_default=True,
        ),
    ]
