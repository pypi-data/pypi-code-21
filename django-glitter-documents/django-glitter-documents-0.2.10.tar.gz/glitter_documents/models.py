# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible

from PIL import Image
from taggit.managers import TaggableManager

from glitter.assets.fields import AssetForeignKey
from glitter.mixins import GlitterMixin
from glitter.models import BaseBlock


@python_2_unicode_compatible
class Format(models.Model):
    title = models.CharField(max_length=100, db_index=True)

    class Meta:
        ordering = ('title', )

    def __str__(self):
        return self.title


@python_2_unicode_compatible
class Category(models.Model):
    title = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=100, unique=True)
    parent_category = models.ForeignKey('self', null=True, blank=True)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ('title', )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('glitter-documents:category-list', args=(self.slug, ))


@python_2_unicode_compatible
class Document(GlitterMixin):
    title = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=100, unique=True)
    category = models.ForeignKey(Category)
    document = models.FileField(max_length=200, upload_to='documents/document/%Y/%m')
    image = AssetForeignKey(
        'glitter_assets.Image',
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        help_text='Preview document image',
    )
    valid_image = models.BooleanField(default=False, editable=False)
    author = models.CharField(blank=True, max_length=32)
    file_size = models.PositiveIntegerField(default=0, editable=False)
    document_format = models.ForeignKey(Format)
    summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    publish_at = models.DateTimeField(default=timezone.now, db_index=True)

    tags = TaggableManager(blank=True)

    class Meta(GlitterMixin.Meta):
        get_latest_by = 'publish_at'
        ordering = ('-publish_at', )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('glitter-documents:detail', args=(self.slug, ))

    def save(self, *args, **kwargs):
        # Avoid doing file size requests constantly
        self.file_size = self.document.size

        # See if it's a valid image, so we can show a thumbnail for it
        try:
            Image.open(self.document).verify()
            self.valid_image = True
        except Exception:
            self.valid_image = False

        super(Document, self).save(*args, **kwargs)

    def get_file_extension(self):
        return os.path.splitext(self.document.name)[1]

    def get_file_name(self):
        return os.path.basename(self.document.name)


class LatestDocumentsBlock(BaseBlock):
    category = models.ForeignKey(Category, null=True, blank=True)

    class Meta:
        verbose_name = 'latest documents'
