from rest_framework.routers import SimpleRouter

from .views import OrderViewSet

router = SimpleRouter()

router.register("orders", OrderViewSet, basename="orders")
urlpatterns = router.urls
