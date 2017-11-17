
from django.conf.urls import url

from flatpages.views import flatpage


urlpatterns = [

    url(r'^(?P<url>.*)$', flatpage, name='flatpage'),

]
