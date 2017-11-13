# coding: utf-8
from django.db import models
from django_rossvyaz.managers import PhoneCodeManager


class PhoneCode(models.Model):

    PHONE_TYPE_DEF = 'def'

    PHONE_TYPE_CHOICES = [
        (PHONE_TYPE_DEF, PHONE_TYPE_DEF),
    ]

    first_code = models.CharField(verbose_name='АВС/DEF', max_length=16)
    from_code = models.CharField(verbose_name='От', max_length=16)
    to_code = models.CharField(verbose_name='До', max_length=16)
    block_size = models.PositiveIntegerField(verbose_name='Емкость')
    operator = models.CharField(verbose_name='Оператор', max_length=255)
    region = models.CharField(verbose_name='Регион', max_length=255)
    phone_type = models.CharField(
        verbose_name='Тип кода',
        max_length=16,
        choices=PHONE_TYPE_CHOICES,
    )

    objects = PhoneCodeManager()

    class Meta:
        index_together = [
            ('first_code', 'from_code', 'to_code'),
        ]
