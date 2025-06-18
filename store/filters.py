import django_filters
from django_filters.rest_framework import DjangoFilterBackend

from .models import Category, Industry, Product, ProductType, Vendor


class SafeDjangoFilterBackend(DjangoFilterBackend):
    """
    A safe version of DjangoFilterBackend.

    If the filter parameters are invalid, returns an empty queryset instead of raising an exception.
    Prevents filter errors from exposing sensitive data or breaking the API response.
    """

    def filter_queryset(self, request, queryset, view):
        filterset = self.get_filterset(request, queryset, view)
        if not filterset.is_valid():
            return queryset.none()
        return filterset.qs


class ProductFilter(django_filters.FilterSet):
    """
    FilterSet for filtering products based on various criteria.

    Filters:
        - category (ModelChoiceFilter): Filters products by category.
        - vendor (ModelMultipleChoiceFilter): Filters products by vendor.
        - price_min (NumberFilter): Filters products with a price greater than or equal to the specified value.
        - price_max (NumberFilter): Filters products with a price less than or equal to the specified value.
        - product_type (ModelMultipleChoiceFilter): Filters products by multiple product types.
        - industry (ModelMultipleChoiceFilter): Filters products by multiple industries.

    Usage:
        - Supports filtering by individual or multiple values.
        - Allows filtering by price range.
        - Works with `DjangoFilterBackend` in DRF views.

    Example API Queries:
        - `?category=1` → Filters by category ID 1.
        - `?vendor=2` → Filters by vendor ID 2.
        - `?price_min=100&price_max=500` → Filters products priced between 100 and 500.
        - `?product_type=3&product_type=4` → Filters by product types 3 and 4.
        - `?industry=1&industry=2` → Filters by industries 1 and 2.
    """

    category = django_filters.ModelChoiceFilter(
        field_name="category",
        queryset=Category.objects.filter(is_active=True),
        required=False,
    )

    vendor = django_filters.ModelMultipleChoiceFilter(
        field_name="vendor",
        queryset=Vendor.objects.filter(is_active=True),
        required=False,
    )

    price_min = django_filters.NumberFilter(
        field_name="price", lookup_expr="gte", required=False
    )
    price_max = django_filters.NumberFilter(
        field_name="price", lookup_expr="lte", required=False
    )

    product_type = django_filters.ModelMultipleChoiceFilter(
        field_name="product_type",
        queryset=ProductType.objects.filter(is_active=True),
        conjoined=False,
        required=False,
    )

    industry = django_filters.ModelMultipleChoiceFilter(
        field_name="industry",
        queryset=Industry.objects.filter(is_active=True),
        conjoined=False,
        required=False,
    )

    class Meta:
        model = Product
        fields = [
            "vendor",
            "category",
            "product_type",
            "industry",
            "price_min",
            "price_max",
        ]
