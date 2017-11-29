from django.db import models
from django.contrib.sites.models import Site
from django.contrib.postgres.fields import JSONField, ArrayField
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
# from parler.models import TranslatableModel, TranslatedFields
import uuid
import json


# class ThemeSettings(TranslatableModel):
class ThemeSettings(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    site = models.OneToOneField(Site, verbose_name=_('Site'), on_delete=models.PROTECT, related_name='settings')

    data = JSONField(_('Data'), default=dict, blank=True)

    # translations = TranslatedFields(
    #     data=JSONField(_('Data'), default=dict, blank=True),
    # )

    added = models.DateTimeField(_('Added'), auto_now_add=True)
    changed = models.DateTimeField(_('Changed'), auto_now=True)

    class Meta:
        verbose_name = _('Theme settings')
        verbose_name_plural = _('Theme settings')

    def __str__(self):
        return str(self.site)

    def get_upload_path(self, filename=None):
        from .utils import get_settings_upload_path
        return get_settings_upload_path(self.site_id, filename)

    def get_settings_fields(self):
        from django.core.files.storage import default_storage
        storage = default_storage
        result = json.loads(render_to_string('pcart/settings_schema.json'))

        _current = self.data.get('current', {})

        for group in result:
            for o in group.get('settings', []):
                if 'id' in o:
                    if o.get('type') in ['radio', 'select', 'text', 'collection', 'blog', 'link_list', 'color', 'textarea']:
                        o['value'] = _current.get(o['id'], o.get('default', ''))
                    elif o.get('type') in ['image']:
                        value = _current.get(o['id'], o.get('default', ''))
                        if value:
                            value = self.get_upload_path(value)
                            o['url'] = storage.url(value)
                        o['value'] = value
                    elif o.get('type') in ['checkbox']:
                        o['value'] = _current.get(o['id'], o.get('default', False))
        return result


class RootFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    site = models.ForeignKey(Site, verbose_name=_('Site'), on_delete=models.PROTECT, related_name='root_files')

    file_name = models.CharField(_('File name'), max_length=255)
    content = models.TextField(_('Content'), default='', blank=True)
    content_type = models.CharField(_('Content type'), default='text/plain', max_length=70)
    base64_decode = models.BooleanField(
        _('Base64 decode'), default=False,
        help_text=_('Use this option if you use binary data encoded with Base64 instead a plain text.')
    )

    cache_timeout = models.PositiveIntegerField(_('Cache timeout (seconds)'), default=3600)

    published = models.BooleanField(_('Published'), default=True)

    added = models.DateTimeField(_('Added'), auto_now_add=True)
    changed = models.DateTimeField(_('Changed'), auto_now=True)

    class Meta:
        verbose_name = _('Root file')
        verbose_name_plural = _('Root files')
        unique_together = ['site', 'file_name']

    def __str__(self):
        return str(self.file_name)

    def save(self, *args, **kwargs):
        self.clear_cache()
        super(RootFile, self).save(*args, **kwargs)

    def cache_key(self):
        return 'rootfile-%s-%s' % (self.site_id, self.file_name)

    def clear_cache(self):
        from django.core.cache import cache
        cache.delete(self.cache_key())

    def view(self, request):
        from django.http import HttpResponse
        from django.core.cache import cache
        response = cache.get(self.cache_key())
        if response is None:
            content = self.content
            if self.base64_decode:
                import base64
                content = base64.b64decode(content)
            response = HttpResponse(content, content_type=self.content_type)
            cache.set(self.cache_key(), response, self.cache_timeout)
        return response
