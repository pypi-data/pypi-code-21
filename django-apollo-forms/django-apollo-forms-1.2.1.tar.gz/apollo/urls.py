from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from graphene_django.views import GraphQLView
from .settings import apollo_settings
from .schema import api_schema
from .views import FormManager, DownloadFormSubmissions


form_builder_view = FormManager.as_view()
if apollo_settings.BUILDER_REQUIRES_IS_STAFF:
    form_builder_view = staff_member_required(form_builder_view)

download_submissions_view = DownloadFormSubmissions.as_view()
if apollo_settings.DOWNLOAD_REQUIRES_IS_STAFF:
    download_submissions_view = staff_member_required(download_submissions_view)

urlpatterns = [
    url(r'builder/', form_builder_view),
    url(r'download/', download_submissions_view),
    url(r'%s' % apollo_settings.GRAPHQL_PATH.lstrip('/'), GraphQLView.as_view(graphiql=True, schema=api_schema)),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()