from django.conf.urls import url
from django.contrib.auth.views import (
    password_change,
    password_change_done,
    password_reset,
    password_reset_done,
    password_reset_confirm,
    password_reset_complete,
    LoginView,
    LogoutView,
)

from .views import AccountView

app_name = 'account'

urlpatterns = [
    url(r'^$', AccountView.as_view(), name='view'),
    url(r'^(?P<pk>\d+)/$', AccountView.as_view(), name='view-one'),
    url(r'^profile/$', AccountView.as_view(), name='profile'),

    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='logout', kwargs={'next_page': '/'}),
    url(r'^password/change/$', password_change, name='password-change',
        kwargs={'post_change_redirect': 'account:password-change-done'}),
    url(r'^password/change/done/$', password_change_done, name='password-change-done'),
    url(r'^password/reset/$', password_reset, name='password-reset',
        kwargs={'post_reset_redirect': 'account:password-reset-done'}),
    url(r'^password/reset/done/$', password_reset_done, name='password-reset-done'),
    url(r'^password/reset/confirm/$', password_reset_confirm, name='password-reset-confirm',
        kwargs={'post_reset_redirect': 'account:password-reset-complete'}),
    url(r'^password/reset/complete/$', password_reset_complete, name='password-reset-complete'),
]
