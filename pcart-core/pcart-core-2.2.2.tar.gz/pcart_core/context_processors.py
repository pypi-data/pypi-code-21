from django.contrib.sites.shortcuts import get_current_site
from .models import ThemeSettings


def pcart_settings(request):
    site = get_current_site(request)
    try:
        theme_settings = ThemeSettings.objects.get(site=site)
        _settings = theme_settings.data.get('current', {})
    except ThemeSettings.DoesNotExist:
        _settings = {}
    context = {
        'site': site,
        'settings': _settings,
    }
    return context
