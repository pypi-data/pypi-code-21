from django.conf.urls import url

from jcms.helpers import functions
from .views import optionsViews, articlesViews, usersViews, loginViews, groupsViews

app_name = 'jcms'

crud_models = [
    articlesViews.ArticleViews,
    optionsViews.OptionViews,
    usersViews.UserViews,
    groupsViews.GroupViews
]

urlpatterns = [
    # login views
    url(r'^$', loginViews.LoginView.as_view(), name="login"),
    url(r'^logout/$', loginViews.logout_user, name="logoutUser"),
]

urlpatterns += functions.add_crud(crud_models)
urlpatterns += functions.add_menu_urls()
