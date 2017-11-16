# -*- coding: utf-8 -*-
from django.conf.urls import url
from .views import api_oauth_login_view, api_oauth_granted_view, api_oauth_logout_view, api_oauth_account_view


urlpatterns = [
    url(r'api-oauth-login/', api_oauth_login_view),
    url(r'api-oauth-logout/', api_oauth_logout_view),
    url(r'api-oauth-granted/', api_oauth_granted_view),
    url(r'api-oauth-account/', api_oauth_account_view),
]
