from rest_framework.routers import SimpleRouter

from .views import CartViewSet

router = SimpleRouter()

router.register(r"cart", CartViewSet, basename="cart")

urlpatterns = router.urls
