"""rxncon_site URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

from . import views

try:
    import rxncon_site.import_tester

    urlpatterns = [
        url(r'^admin/', admin.site.urls),
        url(r'^files/', include("fileTree.urls", namespace='fileTree')),
        url(r'^quick/', include("quick_format.urls", namespace='quick_format')),
        url(r'^graphs/', include("graphs.urls", namespace='graphs')),
        url(r'^bool/', include("boolean_model.urls", namespace='bool')),
        url(r'^rule_based/', include("rule_based.urls", namespace='rule_based')),
        url(r'^$', views.rxncon_site_index, name='index'),
        url(r'^publications$', views.publications, name='publications'),
        url(r'^funding', views.funding, name='funding'),
        url(r'^support', views.support, name='support'),
        url(r'^getting_started', views.getting_started, name='getting_started'),
        url(r'^how_to_cite', views.how_to_cite, name='how_to_cite'),
    ]

except ImportError:
    import src.rxncon_site.import_tester
    urlpatterns = [
        url(r'^admin/', admin.site.urls),
        url(r'^files/', include("src.fileTree.urls", namespace='fileTree')),
        url(r'^quick/', include("src.quick_format.urls", namespace='quick_format')),
        url(r'^graphs/', include("src.graphs.urls", namespace='graphs')),
        url(r'^bool/', include("src.boolean_model.urls", namespace='bool')),
        url(r'^rule_based/', include("src.rule_based.urls", namespace='rule_based')),
        url(r'^$', views.rxncon_site_index, name='index'),
        url(r'^publications$', views.publications, name='publications'),
        url(r'^funding', views.funding, name='funding'),
        url(r'^support', views.support, name='support'),
        url(r'^getting_started', views.getting_started, name='getting_started'),
        url(r'^how_to_cite', views.how_to_cite, name='how_to_cite'),

    ]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
