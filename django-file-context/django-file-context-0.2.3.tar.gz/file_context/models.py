# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from taggit.managers import TaggableManager
from common.models import (
    DateCreatedMixIn,
    DateUpdatedMixIn,
    CreatedByMixIn,
)
from .utils import load_module_member


def custom_upload_to(instance, filename):

    """
    Custom Upload To function. It will look
    for FILE_CONTEXT_UPLOAD_TO dotted path and
    use that, otherwise it will just return the file
    name.
    """

    dotted_path = settings.FILE_CONTEXT_UPLOAD_TO if hasattr(settings, 'FILE_CONTEXT_UPLOAD_TO') else None
    if not dotted_path:
        return filename

    fn = load_module_member(dotted_path)
    return fn(instance, filename)


@python_2_unicode_compatible
class File(CreatedByMixIn,
           DateCreatedMixIn,
           DateUpdatedMixIn):

    """
    Models a document
    """

    name = models.CharField(
        max_length=256,
        verbose_name=_('Name')
    )

    description = models.TextField(
        verbose_name=_('Description'),
        null=True,
    )

    document = models.FileField(
        upload_to=custom_upload_to,
        null=True,
    )

    tags = TaggableManager()

    def __str__(self):
        return self.name

    def attach(self, model):
        """
        attaches a model to this file.
        if the model is already attached, it will do
        nothing.
        you can attach anything to the model
        """
        if not model:
            raise ValueError('model is mandatory')

        content_type = ContentType.objects.get_for_model(model)
        try:
            attachment = FileContext.objects.get(
                content_type=content_type,
                object_id=model.pk
            )
        except FileContext.DoesNotExist:
            attachment = FileContext.objects.create(
                content_object=model,
                file=self
            )
        return attachment

    def detach(self, model):
        """
        Detaches a model from this file.
        if this attachment does not exist,
        it will do nothing
        """
        if not model:
            raise ValueError('model is mandatory')

        content_type = ContentType.objects.get_for_model(model)
        try:
            attachment = FileContext.objects.get(
                content_type=content_type,
                object_id=model.pk
            )
            attachment.delete()
        except FileContext.DoesNotExist:
            pass

    class Meta:

        verbose_name = _('Document')
        verbose_name_plural = _('Documents')
        ordering = ('-date_created', )


@python_2_unicode_compatible
class FileContext(DateCreatedMixIn,
                  DateUpdatedMixIn):

    file = models.ForeignKey(
        File,
        verbose_name=_('File'),
        related_name='context'
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)

    object_id = models.PositiveIntegerField()

    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return _('Context: {0}').format(self.content_object)

    class Meta:
        verbose_name = _('File Context')
        verbose_name_plural = _('File Contexts')
