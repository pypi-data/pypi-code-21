
from django.conf.urls import url

from poll import views


urlpatterns = [

    url(r'^latest/$', views.get_latest_poll, name='latest'),

    url(r'^vote/$', views.VoteView.as_view(), name='vote')

]
