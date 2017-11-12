# import re
#
# from datetime import date, datetime
#
# from django.db import models
# from django.utils.dateformat import DateFormat
# from django.utils.formats import date_format
# from django.utils.html import strip_tags
# from django.utils.text import Truncator
# from django.utils.translation import ugettext_lazy as _
#
# from wagtail.wagtailcore.models import Page, Orderable, Site

from django_comments_xtd.models import XtdComment


class WappsComment(XtdComment):
    pass
    # site = models.ForeignKey(Site, on_delete=models.CASCADE)
