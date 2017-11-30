from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import OrfiumOAuth2Provider

urlpatterns = default_urlpatterns(OrfiumOAuth2Provider)
