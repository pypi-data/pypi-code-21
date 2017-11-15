from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils.translation import ugettext_lazy as _
import feincms
from feincms.module.page.models import Page


if feincms.VERSION >= (1, 9):
    raise ImproperlyConfigured(
        'prepared_date is not compatible with FeinCMS >= 1.9. Use feincms_extensions.prepared_date from https://github.com/incuna/feincms-extensions'
    )


def register(cls, admin_cls):
    cls.add_to_class('_prepared_date', models.TextField('Date of Preparation', default='', blank=True))

    def getter(obj):
        if obj._prepared_date:
            return obj._prepared_date

        # Find the best matching parent page (based on url) that has a _prepared_date
        tokens = obj.get_absolute_url().strip('/').split('/')
        paths = ['/'] + ['/%s/' % '/'.join(tokens[:i]) for i in range(1, len(tokens)+1)]
        try:
            return Page.objects.apply_active_filters(
                Page.objects.exclude(
                    _prepared_date=''
                ).filter(
                    _cached_url__in=paths
                ).extra(
                    select={'_url_length': 'LENGTH(_cached_url)'}
                ).order_by(
                    '-_url_length'
                )
            )[0]._prepared_date
        except IndexError:
            return ''

    def setter(obj, value):
        obj._prepared_date = value

    cls.prepared_date = property(getter, setter)

    admin_cls.add_extension_options(_('Date of Preparation'), {
        'fields': ('_prepared_date',),
        'classes': ('collapse',),
    })
