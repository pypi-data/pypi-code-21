"""
Add a allow_comments flag to the page
"""

from django.db import models
from django.utils.translation import ugettext_lazy as _

def register(cls, admin_cls):
    cls.add_to_class('allow_comments', models.BooleanField(_('allow comments'), default=False,))

    admin_cls.list_filter += ['allow_comments',]



