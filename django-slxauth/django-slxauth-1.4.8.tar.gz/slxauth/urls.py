from django.conf.urls import url

from slxauth.views import LoginView, CallbackView, LogoutView

""" Include in urlpatterns like this:
url(r'^accounts/', include('slxauth.urls', namespace='slxauth'))
"""


urlpatterns = [
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^callback/$', CallbackView.as_view(), name='callback'),
]