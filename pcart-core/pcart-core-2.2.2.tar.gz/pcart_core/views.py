import sys
import django
import platform
import getpass
import os
import psutil
import pip
# from django.utils.translation import ugettext_lazy as _
from django.core.cache import cache
from django.urls import reverse
from django.contrib import admin
from django.shortcuts import redirect, render
from .apps import PCartCoreConfig


@admin.site.admin_view
def pcart_system_info_view(request):
    PID = os.getpid()
    context = {
        'opts': {
            'app_label': PCartCoreConfig.name,
            'app_config': {
                'verbose_name': PCartCoreConfig.verbose_name,
            },
        },
        'python_version': sys.version,
        'django_version': django.get_version(),
        'os_version': platform.platform(),
        'virtualenv_dir': getattr(sys, 'prefix', 'sys.prefix is not defined.'),
        'system_user': getpass.getuser(),
        'memory_stats': psutil.virtual_memory(),
        'pid': PID,
        'current_process': psutil.Process(PID),
        'libraries': sorted(pip.get_installed_distributions(local_only=True), key=lambda x: x.key),
    }
    return render(request, 'admin/pcart_core/system_info.html', context)


@admin.site.admin_view
def pcart_clear_cache_view(request):
    cache.clear()
    return redirect(reverse('pcart_core:pcart-admin-system-info'))
