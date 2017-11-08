# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models

from django_szuprefix.utils.modelutils import JSONField


class Setting(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = u"配置"
        unique_together = ("content_type", "object_id", "name")

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    name = models.CharField(u"名称", max_length=64, null=False, blank=False)
    json_data = JSONField(u"内容", blank=True, null=True)

    def __unicode__(self):
        return u"%s.%s" % (self.content_object, self.name)


class Attachment(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = u"附件"

    content_type = models.ForeignKey(ContentType, null=True, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    file = models.FileField(u"文件", upload_to=u"attachments/%Y/%m/%d/")
    name = models.CharField(u"文件名", null=True, blank=True, max_length=128)
    owner = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True,
                              related_name="common_config_attachments")
    create_time = models.DateTimeField(u"创建时间", auto_now_add=True)

    def __unicode__(self):
        return u"%s.attachments.%s" % (self.content_object, self.file)


class Image(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = u"图片"

    content_type = models.ForeignKey(ContentType, null=True, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    file = models.ImageField(u"文件", upload_to=u"images/%Y/%m/%d/")
    owner = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True, related_name="common_config_images")
    create_time = models.DateTimeField(u"创建时间", auto_now_add=True)

    def __unicode__(self):
        return u"%s.images.%s" % (self.content_object, self.file)


class Trash(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = u"垃圾"
        unique_together = ("content_type", "object_id")

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    json_data = JSONField(u"内容", blank=True, null=True)
    create_time = models.DateTimeField(u"删除时间", auto_now_add=True)

    def __unicode__(self):
        return u"%s.%s" % (self.content_type, self.object_id)


class ExcelTask(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = u"Eexcel导出任务"

    content_type = models.ForeignKey(ContentType, null=True, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    name = models.CharField(u"名称", max_length=128, null=False, blank=False)
    params = JSONField(u"参数")
    status = models.PositiveSmallIntegerField(u"状态", choices=((0, u"等待执行"), (1, u"开始执行"), (2, u"执行中"), (4, u"执行完毕")),
                                              default=0)
    owner = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True, related_name="common_config_tasks")
    create_time = models.DateTimeField(u"创建时间", auto_now_add=True)
    attachments = GenericRelation("common_config.Attachment")

    def __unicode__(self):
        return u"%s.tasks.%s" % (self.content_object, self.name)
