from django.db import models
from wagtail.contrib.settings.models import BaseSetting, register_setting


@register_setting(icon='site')
class AnalyticsSettings(BaseSetting):
    google_analytics = models.CharField(
        max_length=255, blank=True, null=True,
        help_text='Your Google Analytics property ID, e.g UA-XXXXX-Y')
    google_tag_manager = models.CharField(
        max_length=255, blank=True, null=True,
        help_text='Your Google Tag Manager container ID, e.g GTM-XXXX'
    )
