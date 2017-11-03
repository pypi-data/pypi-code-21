
import re

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site


PLACEHOLDER_REGEX = re.compile(r'\{\{\s\s*(\S*)\s*\s\}\}')
PLACEHOLDER_TEMPLATE = '{{ %s }}'


class PageMeta(models.Model):

    META_ROBOTS_CHOICES = (
        ('index, follow', _('Index, Follow')),
        ('noindex, nofollow', _('No Index, No Follow')),
        ('index, nofollow', _('Index, No Follow')),
        ('noindex, follow', _('No Index, Follow')),
    )

    site = models.ForeignKey(
        Site, verbose_name=_('Site'), default=settings.SITE_ID)

    url = models.CharField(
        _('URL'), max_length=255, blank=False, db_index=True)

    title = models.CharField(_('Title'), max_length=68, blank=False)

    keywords = models.CharField(_('Keywords'), max_length=100, blank=True)

    description = models.CharField(
        _('Description'), max_length=155, blank=True)

    breadcrumb = models.CharField(_('Breadcrumb'), max_length=100, blank=True)

    header = models.CharField(_('Header'), max_length=100, blank=True)

    robots = models.CharField(
        _('Robots'), max_length=30, blank=True, default='index, follow',
        choices=META_ROBOTS_CHOICES)

    compile_fields = [
        'title', 'keywords', 'description', 'breadcrumb', 'header']

    @staticmethod
    def _get_context_value(context, path):

        value = None

        for key in path.split('.'):
            if value is None:
                value = context.get(key)
            else:
                if isinstance(value, dict):
                    value = value.get(key)
                else:
                    value = getattr(value, key)

        if callable(value):
            value = value()

        return value

    def _render_tag(self, text, context):

        for path in re.findall(PLACEHOLDER_REGEX, text):

            try:
                value = self._get_context_value(context, path)
            except Exception as e:
                value = ''

            try:
                text = text.replace(PLACEHOLDER_TEMPLATE % path, value)
            except TypeError:
                pass

        return text

    def compile(self, context):
        for field in self.compile_fields:
            value = self._render_tag(getattr(self, field), context)
            setattr(self, 'printable_%s' % field, value)

    def __unicode__(self):
        return '%s - %s' % (self.url, self.title)

    class Meta:
        unique_together = ['site', 'url']
        verbose_name = _('Page meta')
        verbose_name_plural = _('Pages meta')
