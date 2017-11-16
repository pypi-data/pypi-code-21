# -*- coding:utf-8 -*-
import uuid
import json

from django.contrib.auth.models import User
from django.db import models
from django.core.urlresolvers import reverse

from django_szuprefix.saas.models import Party
from django_szuprefix.utils import httputils, modelutils


class Survey(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = u"问卷"
        ordering = ("-is_active", "title")

    party = models.ForeignKey(Party, verbose_name=Party._meta.verbose_name, related_name="surveys")
    slug = models.UUIDField(u"slug", primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, verbose_name=User._meta.verbose_name, related_name="surveys")
    title = models.CharField(u"标题", max_length=255)
    content = modelutils.JSONField(u"内容")
    is_active = models.BooleanField(u'是否在用', default=True, help_text=u'不在用的会被下线不再显示')
    target_users = models.ManyToManyField(User, verbose_name=u'目标人群', null=True, blank=True,
                                        help_text=u"目标人群里的用户才能填写问卷")
    target_user_count = models.PositiveIntegerField(u'目标参与人数', default=0, blank=True)
    actual_user_count = models.PositiveIntegerField(u'实际参与人数', default=0, blank=True)
    begin_time = models.DateTimeField(u"开始时间", help_text=u"开始时间一到问卷会被自动上线")
    end_time = models.DateTimeField(u"结束时间", help_text=u"结束时间一到问卷会被自动下线")

    def __unicode__(self):
        return self.title

    @property
    def content_json(self):
        from . import helper
        return helper.split_survey(self.content)

    def get_absolute_url(self):
        return reverse("survey:survey-show", kwargs={"slug": str(self.slug)})

    def get_answer_url(self):
        return httputils.reverse_absolute_url("survey:survey-show", kwargs={"slug": str(self.slug)})

    get_answer_url.short_description = u"答卷地址"

    def get_stat_url(self):
        return httputils.reverse_absolute_url("survey:survey-stat", kwargs={"slug": str(self.slug)})

    get_stat_url.short_description = u"统计地址"

    def stat_detail(self, extattr_filter=None):
        from . import helper
        return helper.stat_detail(self, extattr_filter)

    def get_target_user_ids(self):
        return list(self.target_users.values_list("id", flat=True))

    def get_actual_user_ids(self):
        return list(self.answers.values_list("user_id", flat=True))

    def get_not_answer_user_ids(self):
        return set(self.get_target_user_ids()).difference(set(self.get_actual_user_ids()))

    def save(self, **kwargs):
        # if self.target_user_count == None:
        self.target_user_count = len(self.get_target_user_ids())
        return super(Survey, self).save(**kwargs)


class Answer(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = u"答案"
        unique_together = ("survey", "user")

    party = models.ForeignKey(Party, verbose_name=Party._meta.verbose_name, related_name="survey_answers")
    survey = models.ForeignKey(Survey, related_name="answers")
    user = models.ForeignKey(User, verbose_name=User._meta.verbose_name, related_name="survey_answers",blank=True)
    content = models.TextField(u"内容")
    create_time = models.DateTimeField(u"创建时间", auto_now_add=True, null=True, blank=True)

    @property
    def content_json(self):
        return json.loads(self.content)

    def user_name(self):
        return self.user and self.user.get_full_name()

    user_name.short_description = u'用户姓名'

    def show_content(self):
        return "\n".join(["%s : %s" % (d.get("name"), d.get("value")) for d in self.content_json])

    show_content.short_description = u'答卷展示'

