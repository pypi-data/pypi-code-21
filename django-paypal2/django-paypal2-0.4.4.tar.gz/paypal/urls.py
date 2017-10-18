from django.conf.urls import url
from django.views.generic import TemplateView

from paypal.views import PaypalRedirectView, PaypalReturnView

urlpatterns = [
    url('^redirect/(?P<uid>.*?)/$', PaypalRedirectView.as_view(), name='paypal_redirect'),
    url('^return/$', PaypalReturnView.as_view(), name='paypal_return'),
    url('^cancel/$', TemplateView.as_view(template_name='paypal/cancel.html'), name='paypal_cancel'),
]
