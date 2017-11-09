
from auth_token.urls import urlpatterns as auth_token_urls
from user.urls import urlpatterns as user_urls
from profile.urls import urlpatterns as profile_urls


urlpatterns = []
urlpatterns += auth_token_urls
urlpatterns += profile_urls
urlpatterns += user_urls