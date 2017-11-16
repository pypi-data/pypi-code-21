# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from treebeard.al_tree import AL_Node

from django_szuprefix.utils import modelutils
from . import choices
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string


class Party(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = u"团体"

    name = models.CharField(u"名称", max_length=128)
    slug = models.CharField(u"编号", max_length=16, blank=True)
    status = models.PositiveSmallIntegerField(u"状态", choices=choices.CHOICES_PARTY_STATUS,
                                              default=choices.PARTY_STATUS_TEST)
    is_active = models.BooleanField(u"有效", default=True)
    worker_count = models.PositiveIntegerField(u"用户规模", blank=True, default=0)
    create_time = models.DateTimeField(u"创建时间", auto_now_add=True)
    modify_time = models.DateTimeField(u"修改时间", auto_now=True)
    settings = GenericRelation("common.Setting")

    def __unicode__(self):
        return self.name

    def save(self, **kwargs):
        self.name = self.name.replace(" ", "")
        if not self.slug:
            self.slug = "og%s" % get_random_string(14, allowed_chars='abcdefghijklmnopqrstuvwxyz0123456789')
        return super(Party, self).save(**kwargs)


class Department(AL_Node):
    class Meta:
        verbose_name_plural = verbose_name = u"部门"
        unique_together = ("party", "parent", "name")

    party = models.ForeignKey(Party, verbose_name=Party._meta.verbose_name,
                              related_name="departments")
    parent = models.ForeignKey("Department", verbose_name=u"上级", null=True, related_name="sub_departments")
    name = models.CharField(u"名字", max_length=64)
    order_num = models.PositiveSmallIntegerField(u"序号", default=0, blank=True)
    is_active = models.BooleanField(u"是否在用", default=True)
    create_time = models.DateTimeField(u"创建时间", auto_now_add=True)
    modify_time = models.DateTimeField(u"修改时间", auto_now=True)
    node_order_by = ("order_num",)

    def __unicode__(self):
        return self.name

    def get_sub_department_ids(self, include_self=True):
        ids = [i.id for i in self.get_descendants() if i.is_active]
        if include_self:
            ids.append(self.id)
        return ids

    def get_workers(self, is_active=None):
        subs = self.get_sub_department_ids()
        qset = self.organization.workers.filter(departments__id__in=subs)
        if is_active is not None:
            qset = qset.filter(is_active)
        return qset

    def path(self):
        return "/".join([a.name for a in self.get_ancestors()] + [self.name])

    path.short_description = u"路径"

    def active_workers_count(self):
        return self.get_workers(is_active=True).count()

    active_workers_count.short_description = u"人数"


class Worker(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = u"成员"
        unique_together = ('party', 'number')

    party = models.ForeignKey(Party, verbose_name=Party._meta.verbose_name, related_name="workers")
    user = models.OneToOneField(User, verbose_name=User._meta.verbose_name, null=True, related_name="as_saas_worker")
    number = models.CharField(u"编号", max_length=64, db_index=True)
    name = models.CharField(u"名字", max_length=64, db_index=True)
    departments = models.ManyToManyField(Department, verbose_name=Department._meta.verbose_name, blank=True,
                                         related_name="workers")
    position = models.CharField(u"职位", max_length=64, null=True, blank=True)
    # status = models.SmallIntegerField(u"状态", choices=choices.CHOICE_WORKER_STATUS,
    #                                   default=choices.WORKER_STATUS_WORKING)
    is_active = models.BooleanField(u"有效", default=True)
    entrance_date = models.DateField(u'加入日期', null=True, blank=True)
    quit_date = models.DateField(u'退出日期', null=True, blank=True)
    profile = modelutils.KeyValueJsonField(u"档案", null=True, blank=True)
    settings = GenericRelation("common.Setting")
    create_time = models.DateTimeField(u"创建时间", auto_now_add=True)
    modify_time = models.DateTimeField(u"修改时间", auto_now=True)

    def __unicode__(self):
        return self.name

    def _auto_create_user(self):
        if not self.user:
            import unidecode
            uid = unidecode.unidecode(self.name).replace(" ", "").lower()
            sid = 1
            org = self.party.slug
            number = uid
            while User.objects.filter(username="%s@%s" % (number, org)).exists():
                sid += 1
                number = "%s%s" % (uid, sid)
            self.user = User.objects.create_user(username="%s@%s" % (number, org), first_name=self.name)
            self.user.save()

    def _auto_deactivated(self):
        # is_active = self.status != choices.WORKER_STATUS_QUIT
        if self.is_active != self.user.is_active:
            self.user.is_active = self.is_active
            self.user.save()

    def save(self, **kwargs):
        self.name = self.name.replace(" ", "")
        self._auto_create_user()
        self._auto_deactivated()
        if not self.number:
            self.number = self.user.username.split("@")[0]
        return super(Worker, self).save(**kwargs)
