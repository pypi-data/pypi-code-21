# -*- coding: utf-8 -*-

import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _


class Page(models.Model):
    name = models.SlugField(_(u"name"), unique=True, editable=False)
    title = models.CharField(_(u"title"), max_length=100, unique=True)
    content = models.TextField(_(u"content"))

    class Meta:
        verbose_name = _(u"page")
        verbose_name_plural = _(u"pages")

    def __str__(self):
        return self.title
