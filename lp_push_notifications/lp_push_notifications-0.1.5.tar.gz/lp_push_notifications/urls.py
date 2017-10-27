from django.conf.urls import url
from push_notifications.api.rest_framework import APNSDeviceAuthorizedViewSet, GCMDeviceAuthorizedViewSet
from rest_framework.urlpatterns import format_suffix_patterns
from .views import NotificationReceiptListCreateView

urlpatterns = [
    url(r'^notifications$', NotificationReceiptListCreateView.as_view(), name='notificationreceipts_list'),
    url(r'^device/apns/?$', APNSDeviceAuthorizedViewSet.as_view({'post': 'create'}), name='create_apns_device'),
    url(r'^device/gcm/?$', GCMDeviceAuthorizedViewSet.as_view({'post': 'create'}), name='create_gcm_device'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
