from rest_framework.routers import SimpleRouter

from .views import (CarouselViewSet, CategoryViewSet, IndustryViewSet,
                    ProductTypeViewSet, ProductViewSet, ReviewViewSet,
                    VendorViewSet)

router = SimpleRouter()

router.register(r"sliders", CarouselViewSet, basename="sliders")
router.register(r"categories", CategoryViewSet, basename="categories")
router.register(r"industries", IndustryViewSet, basename="industries")
router.register(r"vendors", VendorViewSet, basename="vendors")
router.register(r"product_types", ProductTypeViewSet, basename="product_types")
router.register(r"products", ProductViewSet, basename="products")
router.register(r"reviews", ReviewViewSet, basename="reviews")

urlpatterns = router.urls
