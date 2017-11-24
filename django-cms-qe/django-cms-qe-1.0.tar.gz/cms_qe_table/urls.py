"""
URL Configuration
https://docs.djangoproject.com/en/1.11/topics/http/urls/
"""

from django.conf.urls import url

from .views import get_table_choices


urlpatterns = [
    url(r'^cms-qe/table/data', get_table_choices, name='get_table_choices'),
]
