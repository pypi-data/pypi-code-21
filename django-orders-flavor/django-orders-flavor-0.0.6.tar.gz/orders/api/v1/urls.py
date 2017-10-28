from rest_framework.routers import SimpleRouter

from . import views


app_name = 'orders.api.v1'
router = SimpleRouter(trailing_slash=False)

router.register(r'orders', views.OrderViewSet, base_name='order')


urlpatterns = router.urls
