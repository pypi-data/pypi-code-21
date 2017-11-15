from django import forms
from django.conf import settings
from django.contrib.admin.widgets import AdminRadioSelect
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from feincms.admin.editor import ItemEditorForm

# FeinCMS connector
class VideoContent(models.Model):
    video = models.ForeignKey('videos.video',
                              #related_name='%s_%s_set' % (cls._meta.app_label, cls._meta.module_name)
                             )

    class Meta:
        abstract = True


    @classmethod
    def initialize_type(cls, POSITION_CHOICES=None):
        if 'videos' not in settings.INSTALLED_APPS:
            raise ImproperlyConfigured, 'You have to add \'videos\' to your INSTALLED_APPS before creating a %s' % cls.__name__

        if POSITION_CHOICES is None:
            raise ImproperlyConfigured, 'You need to set POSITION_CHOICES when creating a %s' % cls.__name__


        cls.add_to_class('position', models.CharField(_('position'),
            max_length=10, choices=POSITION_CHOICES,
            default=POSITION_CHOICES[0][0]))

        class VideoContentAdminForm(ItemEditorForm):
            position = forms.ChoiceField(choices=POSITION_CHOICES,
                initial=POSITION_CHOICES[0][0], label=_('position'),
                widget=AdminRadioSelect(attrs={'class': 'radiolist'}))

        cls.feincms_item_editor_form = VideoContentAdminForm


    def render(self, **kwargs):
        request = kwargs.get('request')
        return render_to_string([
            'content/videocontent/%s.html' % self.position,
            'content/videocontent/default.html',
            ], { 'content': self, 'request': request })


    @classmethod
    def default_create_content_type(cls, cms_model):
        return cms_model.create_content_type(cls, POSITION_CHOICES=(
            ('block', _('block')),
            ('left', _('left')),
            ('right', _('right')),
            ))

