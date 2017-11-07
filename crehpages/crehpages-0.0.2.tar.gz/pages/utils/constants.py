from django.conf import settings

PAGE_CONFIG = {
    'products': [],
    'custom_page_admin': False,
    'autoslug': True,
    'landing': [
        {
            'type': (1, 'General'),
            'template': ''
        }
    ]
}

SLIDER_SIZE_PC = (1000, 500)
SLIDER_SIZE_TABLET = (1000, 500)
SLIDER_SIZE_MOBILE = (1000, 500)
SLIDER_SIZE_SHARE = (1000, 500)

SLIDER_FORMAT = 'JPEG'

SLIDER_OPTIONS = {
    'quality': 90,
    'optimize': True,
    'progressive': True
}

SITE_URL = 'https://www.example.com'

PAGE_SITE_URL = getattr(settings, 'SITE_URL', SITE_URL)

PAGE_SLIDER_PC_SIZES = getattr(settings, 'SLIDER_SIZE_PC', SLIDER_SIZE_PC)
PAGE_SLIDER_TABLET_SIZES = getattr(settings, 'SLIDER_SIZE_TABLET', SLIDER_SIZE_TABLET)
PAGE_SLIDER_MOBILE_SIZES = getattr(settings, 'SLIDER_SIZE_MOBILE', SLIDER_SIZE_MOBILE)
PAGE_SLIDER_SHARE_SIZES = getattr(settings, 'SLIDER_SIZE_SHARE', SLIDER_SIZE_SHARE)

PAGE_SLIDER_FORMAT = getattr(settings, 'SLIDER_FORMAT', SLIDER_FORMAT)

PAGE_SLIDER_OPTIONS = getattr(settings, 'SLIDER_OPTIONS', SLIDER_OPTIONS)

SLIDER_TYPE_CONTENT = [
    'TEXT',
    'BUTTON',
]


PAGE_CONFIG = getattr(settings, 'PAGE_CONFIG', PAGE_CONFIG)

PAGE_TYPES = [config.get('type') for config in PAGE_CONFIG.get('landing')]

PAGE_PRODUCTS = PAGE_CONFIG.get('products')

PAGE_CUSTOM_ADMIN = PAGE_CONFIG.get('custom_page_admin')

PAGE_AUTOSLUG = PAGE_CONFIG.get('autoslug')