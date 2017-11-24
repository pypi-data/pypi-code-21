from django.conf.urls import url
from django.contrib.auth import views as django_views

from cms_qe_auth.forms import PasswordResetFormWithEmailExistenceCheck
from . import views

urlpatterns = [
    url(
        r'^login/$',
        django_views.login,
        {'template_name': 'cms_qe/auth/login.html'},
        name='login',
    ),
    url(
        r'^logout/$',
        django_views.logout,
        {'template_name': 'cms_qe/auth/logged_out.html'},
        name='logout',
    ),
    url(
        r'^password_change/$',
        django_views.password_change,
        {'template_name': 'cms_qe/auth/password_change_form.html'},
        name='password_change',
    ),
    url(
        r'^password_change/done/$',
        django_views.password_change_done,
        {'template_name': 'cms_qe/auth/password_change_done.html'},
        name='password_change_done',
    ),
    url(
        r'^password_reset/$',
        django_views.password_reset,
        {
            'template_name': 'cms_qe/auth/password_reset_form.html',
            'email_template_name': 'cms_qe/auth/password_reset_email.txt',
            'html_email_template_name': 'cms_qe/auth/password_reset_email.html',
            'password_reset_form': PasswordResetFormWithEmailExistenceCheck,
        },
        name='password_reset',
    ),
    url(
        r'^password_reset/done/$',
        django_views.password_reset_done,
        {'template_name': 'cms_qe/auth/password_reset_done.html'},
        name='password_reset_done',
    ),
    url(
        r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        django_views.password_reset_confirm,
        {'template_name': 'cms_qe/auth/password_reset_confirm.html'},
        name='password_reset_confirm',
    ),
    url(
        r'^reset/done/$',
        django_views.password_reset_complete,
        {'template_name': 'cms_qe/auth/password_reset_complete.html'},
        name='password_reset_complete',
    ),
    url(
        r'^register/$',
        views.register,
        {'template_name': 'cms_qe/auth/register.html'},
        name='register'
    ),
    url(
        r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate,
        {
            'template_name_complete': 'cms_qe/auth/email_confirmation_complete.html',
            'template_name_fail': 'cms_qe/auth/email_confirmation_fail.html',
        },
        name='activate'
    ),
]
