from django.utils.translation import ugettext_lazy as _
from django.conf import settings


_PCART_COLLECTION_ORDERINGS = {
    'cheap': {
        'label': _('From cheaper to more expensive'),
        'without_filters': ['-status__weight', 'min_variant_price', 'id'],
        'with_filters': ['-status__weight', 'filtered_min_variant_price', 'id'],
    },
    'expensive': {
        'label': _('From more expensive to cheaper'),
        'without_filters': ['-status__weight', '-max_variant_price', 'id'],
        'with_filters': ['-status__weight', '-filtered_max_variant_price', 'id'],
    },
}

PCART_COLLECTION_ORDERINGS = getattr(settings, 'PCART_COLLECTION_ORDERINGS', _PCART_COLLECTION_ORDERINGS)

PCART_COLLECTION_DEFAULT_ORDERING = getattr(settings, 'PCART_COLLECTION_DEFAULT_ORDERING', 'cheap')

PCART_ENABLE_PRODUCT_VARIANTS = getattr(settings, 'PCART_ENABLE_PRODUCT_VARIANTS', True)

_PCART_PRICE_AGGREGATION_TEMPLATES = {
    'hli': {
        'label': _('Hotline XML'),
        'template': 'catalog/export/hli.xml',
    },
}

PCART_PRICE_AGGREGATION_TEMPLATES = \
    getattr(settings, 'PCART_PRICE_AGGREGATION_TEMPLATES', _PCART_PRICE_AGGREGATION_TEMPLATES)


PCART_COLLECTION_TRIGGER_MODULES = (('', _('No module')),) + \
    getattr(settings, 'PCART_COLLECTION_TRIGGER_MODULES', tuple())
