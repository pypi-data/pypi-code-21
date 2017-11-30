from django.conf.urls import url
from django.contrib import admin

from model_api.urls import urlpatterns as model_urlpattern
from model_jobs_api.urls import urlpatterns as model_job_urlpattern
from server_docs_api.urls import urlpatterns as server_docs_urlpattern

urlpatterns = []
urlpatterns += model_urlpattern
urlpatterns += model_job_urlpattern
urlpatterns += server_docs_urlpattern