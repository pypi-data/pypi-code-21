# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from django_szuprefix.saas.models import Party
from django.contrib.auth.models import User
from django_szuprefix.utils import modelutils


class Paper(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = u"试卷"
        ordering = ('-create_time',)

    party = models.ForeignKey(Party, verbose_name=Party._meta.verbose_name, related_name="exam_papers",
                              on_delete=models.PROTECT)
    user = models.ForeignKey(User, verbose_name=User._meta.verbose_name, related_name="exam_papers",
                             on_delete=models.PROTECT)
    title = models.CharField(u"标题", max_length=255, blank=False)
    content = models.TextField(u"内容", blank=True, null=True)
    content_object = modelutils.JSONField(u"内容对象", blank=True, null=True, help_text="")
    create_time = models.DateTimeField(u"创建时间", auto_now_add=True)
    is_active = models.BooleanField(u"有效", blank=False)

    def __unicode__(self):
        return self.title


    def save(self, **kwargs):
        if not self.title:
            self.title = u"试卷"
        return super(Paper, self).save(**kwargs)