from django import forms
from django.conf import settings as django_settings
from django.contrib.admin.widgets import AdminRadioSelect
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from feincms import settings
from feincms.admin.editor import ItemEditorForm
from feincms.module.medialibrary.models import MediaFile

from feincms.content.medialibrary.models import MediaFileWidget

VIDEO_TYPE = 'video'
IMAGE_TYPE = 'image'

class VideoSectionContent(models.Model):
    """
    Title, video media file and preview image media file fields in one content block.
    """

    feincms_item_editor_includes = {
        'head': [
            'admin/content/mediafile/init.html',
            ],
        }

    title = models.CharField(_('title'), max_length=200, blank=True)

    class Meta:
        abstract = True
        verbose_name = _('video section')
        verbose_name_plural = _('video sections')

    @classmethod
    def initialize_type(cls):
        if 'feincms.module.medialibrary' not in django_settings.INSTALLED_APPS:
            raise ImproperlyConfigured, 'You have to add \'feincms.module.medialibrary\' to your INSTALLED_APPS before creating a %s' % cls.__name__

        cls.add_to_class('video_mediafile', models.ForeignKey(MediaFile, limit_choices_to={'type':VIDEO_TYPE}, verbose_name=_('video'),
            related_name='%s_%s_set' % (cls._meta.app_label, cls._meta.module_name),
            ))
        cls.add_to_class('preview_mediafile', models.ForeignKey(MediaFile, limit_choices_to={'type':IMAGE_TYPE}, verbose_name=_('preview image'),
            blank=True, null=True,
            ))

        class MediaFileContentAdminForm(ItemEditorForm):
           video_mediafile = forms.ModelChoiceField(queryset=MediaFile.objects.all(),#filter(type=VIDEO_TYPE),
                                          widget=MediaFileWidget, required=True)
           preview_mediafile = forms.ModelChoiceField(queryset=MediaFile.objects.all(),#filter(type=VIDEO_TYPE),
                                            widget=MediaFileWidget, required=True)

        cls.feincms_item_editor_form = MediaFileContentAdminForm
        cls.form = MediaFileContentAdminForm

    @classmethod
    def get_queryset(cls, filter_args):
        # Explicitly add nullable FK mediafile to minimize the DB query count
        return cls.objects.select_related('parent', 'video_mediafile', 'preview_mediafile').filter(filter_args)

    def render(self, **kwargs):

        return render_to_string([
            'content/videosection/default.html',
            ], {'content': self})
