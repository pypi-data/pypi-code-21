from django.conf.urls import url

from acserv.views import KickSessionACView, IndexACView, LogoutACView, PasswordACView, UsernameACView

urlpatterns = [
    url('^$', IndexACView.as_view()),
    url('^auth/username$', UsernameACView.as_view()),
    url('^auth/password$', PasswordACView.as_view()),
    url('^auth/sessions', KickSessionACView.as_view()),
    url('^logout$', LogoutACView.as_view()),
]
