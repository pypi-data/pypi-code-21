"""
Add a show_title flag to the page
"""

from django.db import models
from django.utils.translation import ugettext_lazy as _

def register(cls, admin_cls):
    cls.add_to_class('show_title', models.BooleanField(_('show title'), default=True,))

    admin_cls.show_on_top += ['show_title']