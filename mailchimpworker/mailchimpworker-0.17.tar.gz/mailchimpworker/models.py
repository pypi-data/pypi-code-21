from __future__ import absolute_import, unicode_literals
from django.db import models


class Subscriber(models.Model):
    email = models.EmailField('Почта')
    name = models.CharField('Имя', max_length=100, blank=True, null=True)
    status = models.BooleanField('Отправлено в Mailchimp', default=False)

    def __str__(self):
        return '{}, {}'.format(self.email, self.name)
