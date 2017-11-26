from django.conf.urls import url
from . import views


urlpatterns = [



    url(r'^admin/(?P<pk>[0-9a-f-]+)/$', views.admin_view, name='admin_view'),


    url(r'^admin/add_ques/(?P<pk>[0-9a-f-]+)/$', views.add_question, name='add_question'),


    url(r'^admin/edit_ques/(?P<pk>[0-9a-f-]+)/(?P<ques_id>\d+)/$',views.edit_question,name='edit_question'),

    url(r'^user/view/(?P<view_id>[0-9a-f-]+)/$',views.user_view, name = 'user_view'),

    url(r'^view/response/(?P<pk>[0-9a-f-]+)/$', views.view_filled_form, name='view_filled_form'),

]
