# -*- coding: utf-8 -*-

# https://docs.djangoproject.com/en/dev/ref/contrib/sitemaps/
from django.contrib.sitemaps import Sitemap

from navsy.models import Page
from navsy.urls import reverse
from navsy.utils import i18n_utils


class ModelSitemap(Sitemap):

    """
    class MyModelSitemap(Sitemap):

        changefreq = 'weekly'
        priority = 0.5

        def items(self):
            return MyModeltion.objects.filter(published=True)
    """

    def __init__(self, language):
        self.language = language

    def location(self, obj):
        return i18n_utils.call_function_for_language(
            obj.get_absolute_url, self.language)


class PageSitemap(Sitemap):

    def items(self):
        pages_qs = Page.objects.filter(sitemap_item=True, published=True)
        pages_list = list(pages_qs)
        return pages_list

    def get_priority(self, item):
        return item.sitemap_priority or Page.SITEMAP_DEFAULT_PRIORITY

    def get_changefreq(self, item):
        return item.sitemap_changefreq or Page.SITEMAP_DEFAULT_CHANGEFREQ

    def location(self, item):
        return item.get_absolute_url()

    priority = get_priority
    changefreq = get_changefreq


class RouteSitemap(Sitemap):

    """
    data = {
        'home':{ # view_name
            'args':[]
            'kwargs':{},
            'priority':0.5, # 0.0 - 1.0
            'changefreq':'weekly' # daily, weekly, monthly, yearly
        },
    }
    """

    data = {}

    def __init__(self, data):
        self.data = data

    def items(self):
        return self.data.keys()

    def get_priority(self, view_name):
        return self.data[view_name].get('priority', 0.5)

    def get_changefreq(self, view_name):
        return self.data[view_name].get('changefreq', 'weekly')

    def location(self, view_name):
        view_data = self.data.get(view_name, {})
        kwargs = view_data.get('kwargs', {})
        args = view_data.get('args', [])
        url = reverse(view_name, *args, **kwargs)
        return url

    priority = get_priority
    changefreq = get_changefreq

