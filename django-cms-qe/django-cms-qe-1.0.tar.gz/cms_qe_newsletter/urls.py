"""
URL Configuration
https://docs.djangoproject.com/en/1.11/topics/http/urls/
"""

from django.conf.urls import url

from .views import update_lists


urlpatterns = [
    url(r'^cms-qe/newsletter/sync-lists', update_lists, name='sync_mailing_lists'),
]
