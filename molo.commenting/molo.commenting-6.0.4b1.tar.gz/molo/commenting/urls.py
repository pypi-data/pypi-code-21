from django.conf.urls import url

from molo.commenting import views
from molo.commenting.views import CommentReplyView

urlpatterns = [
    url(r'molo/report/(\d+)/$', views.report, name='molo-comments-report'),
    url(r'^comments/reported/(?P<comment_pk>\d+)/$',
        views.report_response, name='report_response'),

    url(r'molo/reply/(?P<parent_comment_pk>\d+)/$',
        CommentReplyView.as_view(),
        name='molo-comments-reply'),

    url(r'molo/post/$', views.post_molo_comment, name='molo-comments-post'),
    url(
        r'molo/(?P<page_id>\d+)/comments/$',
        views.view_more_article_comments,
        name='more-comments'),
    url(r'molo/replies/$',
        views.reply_list, name='reply_list'),
]
