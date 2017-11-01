from rest_framework import routers

from .viewsets import AccountViewSet

router = routers.DefaultRouter()
router.register(r'account', AccountViewSet)

urlpatterns = router.urls
