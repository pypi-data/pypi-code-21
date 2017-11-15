
from django.conf.urls import url

from trans import views


app_name = 'trans'


urlpatterns = [

    url(r'^translate/$', views.translate, name='translate'),

]
