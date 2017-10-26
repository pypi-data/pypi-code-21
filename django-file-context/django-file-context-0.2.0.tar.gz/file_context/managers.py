# coding: utf-8
from django import VERSION
from django.db import models
from django.contrib.contenttypes.models import ContentType
from .models import (
    File,
    FileContext
)


class RelatedFileManager(models.Manager):

    """
    This is a RelatedFileManager.
    this provides an easy api to manage
    attachments on objects.
    The basic thing is:
    1. create a model that has the Files object.
    2. use instance.files.all() or any of the
    methods present in this object to do cool
    stuff with the files.
    """

    def __init__(self, instance, model):
        self.instance = instance
        self.model = model

    def _context_queryset(self):
        if self.instance and not self.instance.pk:
            raise ValueError('you must save your instance %s first to work with RelatedFileManager', self.instance)
        ct = ContentType.objects.get_for_model(self.instance)
        return FileContext.objects.filter(
            content_type=ct,
            object_id=self.instance.pk
        ).prefetch_related('file')

    def get_queryset(self):
        values = self._context_queryset().values_list('file_id', flat=True)
        return File.objects.filter(pk__in=values)

    def attach(self, *files):
        if self.instance and not self.instance.pk:
            raise ValueError('you must save your instance %s first to work with RelatedFileManager', self.instance)
        if not files:
            return
        for file in files:
            file.attach(self.instance)

    def detach(self, *files):
        if self.instance and not self.instance.pk:
            raise ValueError('you must save your instance %s first to work with RelatedFileManager', self.instance)
        if not files:
            return
        for file in files:
            file.detach(self.instance)

    def clear(self):
        self._context_queryset().all().delete()


class Files(object):

    def __get__(self, instance, model):
        return RelatedFileManager(instance, model)
