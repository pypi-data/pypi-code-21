# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from cms.models.pluginmodel import CMSPlugin
from filer.fields.image import FilerImageField
from jsonfield import JSONField

from .settings import get_setting


@python_2_unicode_compatible
class LightGallery(CMSPlugin):
    """
    Main Plugin Model for the gallery.
    """
    class Meta:
        verbose_name = _('light gallery')
        verbose_name_plural = _('light galleries')

    def __str__(self):
        """
        String representation of LightGallery class.
        """
        return "{title}".format(title=self.title)

    THUMBNAIL_FORMATS = (
        ('1by1', '1:1'),
        ('4by3', '4:3'),
        ('16by9', '16:9')
    )

    title = models.CharField(
        verbose_name=_('light gallery title'),
        max_length=255)

    settings = JSONField(
        verbose_name=_('light gallery settings'),
        default=get_setting('LIGHTGALLERY_DEFAULT_OPTIONS'),
        null=True, blank=True,
        help_text=_(
            'Check <a href="http://sachinchoolur.github.io/lightGallery/docs/api.html" '  # noqa
            'target="_blank">'
            'LightGallery Documentation</a> for possible settings '
            '<br>'
            'Use JSON format and check the errors in the editor<br>'
            'You can also use online JSON validators'))

    def copy_relations(self, oldinstance):
        """
        Take an instance and copy the images of that instance to this
        instance.
        """
        for image in oldinstance.images.all():
            image.pk = None
            image.gallery = self
            image.save()


@python_2_unicode_compatible
class LightGalleryImage(models.Model):
    """
    Image model für LightGallery class.
    """
    class Meta:
        verbose_name = _('light gallery image')
        verbose_name_plural = _('light gallery images')

    gallery = models.ForeignKey(
        LightGallery,
        related_name='images')

    image = FilerImageField(
        verbose_name=_('light gallery image'),
        related_name='gallery_images_filer')

    link = models.URLField(
        verbose_name=_('image link'),
        null=True, blank=True)

    link_target = models.BooleanField(
        verbose_name=_('image link target'),
        help_text=_('open link in new window'),
        default=True)

    caption_text = models.TextField(
        _('caption text'),
        null=True,
        blank=True)

    def __str__(self):
        """
        String representation of LightGalleryImage class.
        """
        return "{filename}".format(filename=self.image.original_filename)
