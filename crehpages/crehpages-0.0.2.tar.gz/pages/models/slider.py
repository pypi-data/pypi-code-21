# -*- coding: utf-8 -*-
from django.db import models
from imagekit.models import ProcessedImageField

from pages.utils.database import AuditableMixin, ActivatedMixin
from pages.utils.image import get_slider_sizes, upload_picture_to
from pages.managers import SliderManager
from pages.utils import constants


class Slider(AuditableMixin):

    page = models.ForeignKey('Page')

    title = models.CharField(
        max_length=200,
    )

    is_active = models.BooleanField(
        default=False
    )

    dots = models.BooleanField(
        default=False
    )

    speed = models.IntegerField(
        default=500
    )

    objects = SliderManager()

    def __str__(self):
        return "({}) {}".format(self.page.title, self.title)

    class Meta:
        db_table = 'sliders'


class SliderItem(AuditableMixin, ActivatedMixin):

    slider = models.ForeignKey('Slider')

    picture_pc = ProcessedImageField(
        upload_to=upload_picture_to,
        processors=get_slider_sizes(constants.PAGE_SLIDER_PC_SIZES),
        format=constants.PAGE_SLIDER_FORMAT,
        options=constants.PAGE_SLIDER_OPTIONS,
    )

    picture_tablet = ProcessedImageField(
        upload_to=upload_picture_to,
        processors=get_slider_sizes(constants.PAGE_SLIDER_TABLET_SIZES),
        format=constants.PAGE_SLIDER_FORMAT,
        options=constants.PAGE_SLIDER_OPTIONS,
        null=True
    )

    picture_mobile = ProcessedImageField(
        upload_to=upload_picture_to,
        processors=get_slider_sizes(constants.PAGE_SLIDER_MOBILE_SIZES),
        format=constants.PAGE_SLIDER_FORMAT,
        options=constants.PAGE_SLIDER_OPTIONS,
        null=True
    )

    active_from = models.DateTimeField()

    active_to = models.DateTimeField()

    order = models.SmallIntegerField(
        default=1
    )

    @property
    def absolute_url_picture_pc(self):
        url = '%s/%s' %(constants.SITE_URL, self.picture_pc)
        return url

    @property
    def absolute_url_picture_tablet(self):
        url = '%s/%s' % (constants.SITE_URL, self.picture_tablet)
        return url

    @property
    def absolute_url_picture_mobile(self):
        url = '%s/%s' % (constants.SITE_URL, self.picture_mobile)
        return url

    def __str__(self):
        return "({}) {}".format(self.slider.title, self.picture_pc)

    class Meta:
        unique_together = ('order', 'slider',)
        db_table = 'slider_items'


class SliderContentType(models.Model):

    name = models.CharField(
        max_length=100,
    )

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'slider_content_types'


class SliderContent(models.Model):

    slider_item = models.ForeignKey('SliderItem')

    type_content = models.ForeignKey('SliderContentType')

    content = models.TextField()

    config = models.TextField()

    order = models.SmallIntegerField(
        default=1
    )

    def __str__(self):
        return "({}) {}".format(self.order, self.type_content.name)

    class Meta:
        unique_together = ('order', 'slider_item',)
        db_table = 'slider_contents'

