from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from .views import SubscriptionCreateView, SubscriptionRetrieveView, PlanListView, SubscriptionCancelView

urlpatterns = {
    url(r'^stripe/subscription$', SubscriptionCreateView.as_view(), name='lp_stripe_subscriptioncreate'),
    url(r'^stripe/plans', PlanListView.as_view(), name='lp_stripe_planlist'),
    url(r'^account/subscription', SubscriptionRetrieveView.as_view(), name='lp_stripe_subscriptionretrieve'),
    url(r'^stripe/subscription/(?P<pk>[0-9]+)/cancel$', SubscriptionCancelView.as_view(), name='lp_stripe_subscriptioncancel'),
}

urlpatterns = format_suffix_patterns(urlpatterns)
