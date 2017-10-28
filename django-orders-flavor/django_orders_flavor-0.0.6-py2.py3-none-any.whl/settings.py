from django.conf import settings


FLAVOR_REVERSE_EXTRA_KWARGS = getattr(
    settings,
    'FLAVOR_REVERSE_EXTRA_KWARGS',
    {})


ORDERS_UPLOAD_THUMBNAILS_TO = getattr(
    settings,
    'ORDERS_UPLOAD_THUMBNAILS_TO',
    'orders/items/%Y/%m/')


ORDERS_ITEMS_SERIALIZERS = getattr(
    settings,
    'ORDERS_ITEMS_SERIALIZERS',
    [])


ORDERS_ITEMS_CHILD_MODELS = getattr(
    settings,
    'ORDERS_ITEMS_CHILD_MODELS',
    [])

ORDERS_DEFAULT_CURRENCY_CODE = getattr(
    settings,
    'ORDERS_DEFAULT_CURRENCY_CODE',
    'USD')
