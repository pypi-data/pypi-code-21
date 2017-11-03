"""URLs for the API interfaces."""
from itertools import chain

from django.conf import settings
from django.conf.urls import include, url
from rest_auth import urls as rest_auth_urls
from rest_auth.registration import urls as rest_auth_registration_urls
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter
from rest_framework.viewsets import ViewSetMixin
from rest_framework_jwt import views as jwt_views
from dj_core.utils import get_app_submodules

from .views import get_schema_view


v1_router = DefaultRouter()

# Add viewsets from apps in the format "routes = [(r'regex', MyViewSet), ...]"
viewsets = [
    module.routes for app_name, module in get_app_submodules('routes')
    if app_name != __package__ and hasattr(module, 'routes')
]
for regex, viewset in chain.from_iterable(viewsets):
    if not issubclass(viewset, ViewSetMixin):
        raise TypeError('Only ViewSets may be added to routers')
    v1_router.register(regex, viewset, base_name=regex)

api_v1 = [
    url(r'', include(v1_router.urls)),
    url(r'^docs/', get_schema_view(title=settings.DJCORE.SITE_NAME)),
    url(r'^drf-docs/', include_docs_urls(title=settings.DJCORE.SITE_NAME)),
    url(r'^auth/', include(rest_auth_urls)),
    url(r'^auth/token/', include([
        url(r'obtain/', jwt_views.obtain_jwt_token),
        url(r'refresh/', jwt_views.refresh_jwt_token),
        url(r'verify/', jwt_views.verify_jwt_token),
    ])),
]

if settings.ACCOUNT_REGISTRATION.lower() == 'enabled':
    api_v1.append(url(r'^auth/registration/', include(rest_auth_registration_urls)))


urlpatterns = [url(r'^backend/api/v1/', include(api_v1))]
