from django.conf.urls import url, include
from . import settings
from . import views



urlpatterns = [
	url(r'^signup/$', views.signup, name = 'signup'),
	url(r'^login/$', views.login, name = 'login'),
	url(r'^logout/$', views.logout, name = 'logout'),
	url(r'^signup-and-get-token/$', views.signup_and_get_token, name = 'signup_and_get_token'),
	url(r'^login-and-get-token/$', views.login_and_get_token, name = 'login_and_get_token'),
]

if settings.INCLUDE_PATCHED_URLS:
	urlpatterns += [
		url(r'^signup-and-get-token/patched/$', views.signup_and_get_token_patched, name = 'signup_and_get_token_patched'),
		url(r'^login-and-get-token/patched/$', views.login_and_get_token_patched, name = 'login_and_get_token_patched'),
	]

urlpatterns += [
	url(r'^send-password-reset-link/$', views.send_password_reset_link, name = 'send_password_reset_link'),
	url(r'^set-password-reset/$', views.set_password_reset, name = 'set_password_reset'),
	url(r'^set-password-reset-and-get-token/$', views.set_password_reset_and_get_token, name = 'set_password_reset_and_get_token'),
	url(r'^update-user-information/$', views.update_user_information, name = 'update_user_information'),
]


if settings.ENABLE_SOCIAL_LOGIN:
	urlpatterns += [
		url(r'^', include('social.apps.django_app.urls', namespace = 'social')),
	]


if settings.FACEBOOK_LOGIN:
	urlpatterns += [
		url(r'^facebook/login-and-get-token/$', views.facebook_login_and_get_token, name = 'facebook_login_and_get_token'),
	]
	if settings.INCLUDE_PATCHED_URLS:
		urlpatterns += [
			url(r'^facebook/login-and-get-token/patched/$', views.facebook_login_and_get_token_patched, name = 'facebook_login_and_get_token_patched'),
		]

if settings.GOOGLE_PLUS_LOGIN:
	urlpatterns += [
		url(r'^google-plus/login-and-get-token/$', views.google_plus_login_and_get_token, name = 'google_plus_login_and_get_token'),
	]
	if settings.INCLUDE_PATCHED_URLS:
		urlpatterns += [
			url(r'^google-plus/login-and-get-token/patched/$', views.google_plus_login_and_get_token_patched, name = 'google_plus_login_and_get_token_patched'),
		]