# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse

from .models import SiteExceptionLogger

# Create your views here.


@staff_member_required()
def admin_traceback_version(request, traceback_id):
    exception = get_object_or_404(SiteExceptionLogger, pk=traceback_id)
    return HttpResponse(exception.rendered_html_debug, {'obj': exception})

