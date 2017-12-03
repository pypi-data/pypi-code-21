from django.conf.urls import url
from django.views.generic import TemplateView


# noinspection PyUnresolvedReferences
catalog_view = TemplateView.as_view(template_name='catalog.jinja')

urlpatterns = [
    url(r'^catalog/?', catalog_view),
]
