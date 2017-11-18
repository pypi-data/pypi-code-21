"""discourse_django_sso_test_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
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
from discourse_django_sso.views import InMemoryNonceService
from django.conf.urls import url
from django.contrib import admin
from discourse_django_sso import views
from discourse_django_sso.utils import ConsumerType
from discourse_django_sso_test_project import settings


class FixedInMemoryNonceService(InMemoryNonceService):
    def generate_nonce(self) -> str:
        val = "e15917e0320992596f638ebff7678202"
        self.generated_nonces.add(val)
        return val

nonce_service = FixedInMemoryNonceService()

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(
        r'^sso/',
        views.SSOProviderView.as_view(
            sso_redirect=settings.DISCOURSE_SSO_REDIRECT,
            sso_secret=settings.DISCOURSE_SSO_KEY,
            consumer_type=ConsumerType.DISCOURSE
        ),
        name="sso"
    ),
    url(
        r'^client/',
        views.SSOClientView.as_view(
            sso_secret=settings.DISCOURSE_SSO_KEY,
            sso_url=settings.DISCOURSE_SSO_URL,
            nonce_service=nonce_service),
        name="client"
    ),
    url(
        r'^createSession/',
        views.SSOCreateSessionView.as_view(
            sso_secret=settings.DISCOURSE_SSO_KEY,
            nonce_service=nonce_service),
        name="createSession"
    )

]
