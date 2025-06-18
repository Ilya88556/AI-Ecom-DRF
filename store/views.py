from django.db import IntegrityError
from django.db.models import Prefetch, Q
from django.db.models.query import QuerySet
from rest_framework import mixins, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.serializers import BaseSerializer

from store.filters import ProductFilter, SafeDjangoFilterBackend
from store.mixins import IsActiveQuerysetMixin
from store.permissions import IsStaffOrReadOnly, ReviewPermission

from .models import (Carousel, Category, Industry, Product, ProductImages,
                     ProductType, Review, ReviewReply, Vendor)
from .serializers import (CarouselSerializer, CategorySerializer,
                          IndustrySerializer, ProductSerializer,
                          ProductTypeSerializer, ReviewSerializer,
                          VendorSerializer)


class CarouselViewSet(
    IsActiveQuerysetMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    A viewset for viewing, creating, updating, and deleting Carousel instances.
    """

    queryset = Carousel.objects.all()
    serializer_class = CarouselSerializer
    permission_classes = [IsStaffOrReadOnly]


class CategoryViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    A viewset for viewing, creating, updating, and deleting Category instances.
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ["ordering"]
    permission_classes = [IsStaffOrReadOnly]

    def get_queryset(self) -> QuerySet:
        """
        Filter queryset based on user role:
        - Non-staff users see only active objects.
        - Staff users see all objects.
        """
        user = self.request.user

        base_queryset = self.queryset.filter(parent__isnull=True)
        if not (user.is_authenticated and user.is_staff):
            base_queryset = base_queryset.filter(is_active=True)

        # Загружаем всех потомков всех уровней одним Prefetch
        return base_queryset.prefetch_related(
            Prefetch(
                "children",
                queryset=Category.objects.all(),
                to_attr="prefetched_children",
            )
        )


class IndustryViewSet(
    IsActiveQuerysetMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    A viewset for viewing, creating, updating, and deleting Industry instances.
    """

    queryset = Industry.objects.all()
    serializer_class = IndustrySerializer
    permission_classes = [IsStaffOrReadOnly]


class VendorViewSet(
    IsActiveQuerysetMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    A viewset for viewing, creating, updating, and deleting Vendor instances.
    """

    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    permission_classes = [IsStaffOrReadOnly]


class ProductTypeViewSet(
    IsActiveQuerysetMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    A viewset for viewing, creating, updating, and deleting ProductType instances.
    """

    queryset = ProductType.objects.all()
    serializer_class = ProductTypeSerializer
    permission_classes = [IsStaffOrReadOnly]


class ProductPagination(PageNumberPagination):
    """
    Custom pagination class for product listings.
    Sets the number of items per page to 12.
    """

    page_size = 12


class ProductViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    ViewSet for managing products.

    Supports CRUD operations, filtering, searching by name and description,
    and ordering by price or custom ordering field. Applies pagination and
    permission control for staff-only modifications.

    The queryset includes related category, vendor, industry, product type,
    and prefetched product images for performance optimization.

    Returns only active products for unauthenticated or non-staff users.
    """

    serializer_class = ProductSerializer
    filter_backends = [SafeDjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ["name", "description"]
    ordering_fields = ["price", "ordering"]
    permission_classes = [IsStaffOrReadOnly]
    pagination_class = ProductPagination

    def get_queryset(self) -> QuerySet:
        """
        Returns the queryset of products with related data optimized using
        select_related and prefetch_related. Filters out inactive products
        for non-staff or unauthenticated users.
        """
        user = self.request.user

        queryset = (
            Product.objects.all()
            .select_related("category", "vendor")
            .prefetch_related(
                Prefetch("industry", queryset=Industry.objects.only("id", "name")),
                Prefetch(
                    "product_type", queryset=ProductType.objects.only("id", "name")
                ),
                Prefetch(
                    "productimages_set",
                    queryset=ProductImages.objects.all(),
                    to_attr="prefetched_images",
                ),
            )
        )

        if not (user.is_authenticated and user.is_staff):
            return queryset.filter(is_active=True)

        return queryset

    def perform_create(self, serializer: BaseSerializer) -> None:
        """
        Saves a new Product instance and assigns related category, vendor,
        industries, and product types based on request data.
        """
        industry_data = self.request.data.get("industry", [])
        product_type = self.request.data.get("product_type", [])
        category = self.request.data.get("category")
        vendor = self.request.data.get("vendor")
        product = serializer.save(category_id=category, vendor_id=vendor)
        if industry_data is not None:
            product.industry.set(industry_data)
        if product_type is not None:
            product.product_type.set(product_type)

    def perform_update(self, serializer: BaseSerializer) -> None:
        """
        Handles the update of a Product instance with related fields.

        - Updates `category` and `vendor` if present in the request.
        - Updates many-to-many relationships (`industry`, `product_type`) only if the new data differs
          from the current state to avoid unnecessary writes.
        """
        update_kwargs = {}

        if "category" in self.request.data:
            update_kwargs["category_id"] = self.request.data["category"]

        if "vendor" in self.request.data:
            update_kwargs["vendor_id"] = self.request.data["vendor"]

        product = serializer.save(**update_kwargs)

        industry_data = self.request.data.get("industry", [])
        product_type_data = self.request.data.get("product_type", [])

        if industry_data is not None:
            current_industry_ids = set(product.industry.values_list("id", flat=True))
            new_industry_isd = set(map(int, industry_data))

            if current_industry_ids != new_industry_isd:
                product.industry.set(industry_data)

        if product_type_data is not None:
            if product_type_data is not None:
                current_product_type_ids = set(
                    product.product_type.values_list("id", flat=True)
                )
                new_product_type_ids = set(map(int, product_type_data))
                if current_product_type_ids != new_product_type_ids:
                    product.product_type.set(new_product_type_ids)


class ReviewPagination(PageNumberPagination):
    """
    Custom pagination class for product reviews.
    Sets the number of reviews per page to 20.
    """

    page_size = 20


class ReviewViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    ViewSet for managing product reviews.

    Supports creating, retrieving, listing, updating, and deleting reviews.
    Applies custom permissions and pagination.

    - Filters reviews by product ID if provided via query parameters.
    - Non-staff users see only moderated reviews, or their own unmoderated ones.
    - Staff sees all reviews.
    - Ensures one review per user per product during creation, raising a validation error otherwise.
    """

    serializer_class = ReviewSerializer
    permission_classes = [ReviewPermission]
    pagination_class = ReviewPagination

    def get_queryset(self) -> QuerySet:
        """
        Returns a queryset of reviews with optimized related data loading.

        - Filters by product ID if provided via query parameters.
        - Prefetches replies and loads user relationships efficiently.
        - Non-staff authenticated users see moderated reviews and their own unmoderated ones.
        - Anonymous users see only moderated reviews.
        - Staff users see all reviews.
        """
        user = self.request.user
        qs = (
            Review.objects.all()
            .select_related("user")
            .prefetch_related(
                Prefetch("replies", queryset=ReviewReply.objects.select_related("user"))
            )
            .only(
                "id",
                "user",
                "product",
                "rating",
                "advantages",
                "disadvantages",
                "comment",
                "time_created",
            )
        )

        product_id = self.request.query_params.get("product")
        if product_id:
            qs = qs.filter(product_id=product_id)

        if not (user.is_authenticated and user.is_staff):
            if user.is_authenticated:
                qs = qs.filter(Q(moderated=True) | Q(user=user))
            else:
                qs = qs.filter(moderated=True)
        return qs

    def perform_create(self, serializer: BaseSerializer) -> None:
        """
        Handles creation of a review, associating it with the authenticated user.
        Raises:
            ValidationError: If the user has already submitted a review for the same product.
        """
        try:
            serializer.save(user=self.request.user)
        except IntegrityError:
            raise ValidationError(
                {"error": "You have already left a review for this product."}
            )
