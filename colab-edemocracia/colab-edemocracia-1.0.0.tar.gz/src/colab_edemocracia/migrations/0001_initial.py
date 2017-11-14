# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import image_cropping.fields
import colab_edemocracia.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('gender', models.CharField(max_length=999, null=True, choices=[(b'male', b'Masculino'), (b'female', b'Feminino'), (b'other', b'Outro')])),
                ('uf', models.CharField(max_length=2, null=True, choices=[(b'AC', b'AC'), (b'AL', b'AL'), (b'AP', b'AP'), (b'AM', b'AM'), (b'BA', b'BA'), (b'CE', b'CE'), (b'DF', b'DF'), (b'ES', b'ES'), (b'GO', b'GO'), (b'MA', b'MA'), (b'MS', b'MS'), (b'MT', b'MT'), (b'MG', b'MG'), (b'PA', b'PA'), (b'PB', b'PB'), (b'PR', b'PR'), (b'PE', b'PE'), (b'PI', b'PI'), (b'RJ', b'RJ'), (b'RN', b'RN'), (b'RS', b'RS'), (b'RO', b'RO'), (b'RR', b'RR'), (b'SC', b'SC'), (b'SP', b'SP'), (b'SE', b'SE'), (b'TO', b'TO')])),
                ('birthdate', models.DateField(null=True)),
                ('photo', models.ImageField(null=True, upload_to=b'')),
                ('avatar', image_cropping.fields.ImageCropField(blank=True, null=True, upload_to=b'avatars/', validators=[colab_edemocracia.models.avatar_validation])),
                (b'cropping', image_cropping.fields.ImageRatioField(b'avatar', '70x70', hide_image_field=False, size_warning=False, allow_fullsize=False, free_crop=False, adapt_rotation=False, help_text=None, verbose_name='cropping')),
                ('user', models.OneToOneField(related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
