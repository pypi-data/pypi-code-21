# -*- encoding:utf-8 -*-
from __future__ import unicode_literals
from bgframework import add_ons
from django.conf.urls import include, url
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView


class HomeAddon(add_ons.BaseAddon):
    urlpatterns = [
        url(r'home/$', TemplateView.as_view(template_name="home.html"), name="home"),
    ]
    name = _('Home')
    navs = [
        {"nav_name":_('Home'), "url_name":"home", "nav_id":"nav-book-list", "iconclass":"fa fa-home"},
    ]
    sort_id = 1


add_ons.register(HomeAddon)
