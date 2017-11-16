from django.conf.urls import url
import views
from .decorators import weixin_login_required

app_name = "wechat_mp"
urlpatterns = [
    url(r'^ports/', views.ports),
    # url(r'^notice/$',views.notice,name="notice"),
    url(r'^test_pay/$',weixin_login_required(views.TestPayView.as_view()),name="test_pay"),
]
