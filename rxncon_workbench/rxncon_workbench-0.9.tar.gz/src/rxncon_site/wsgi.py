"""
WSGI config for rxncon_site project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

try:
    import rxncon_site.import_tester
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rxncon_site.settings")
except ImportError:
    import src.rxncon_site.import_tester
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.rxncon_site.settings")

application = get_wsgi_application()
