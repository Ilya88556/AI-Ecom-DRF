from decimal import Decimal
from typing import Any

from django.core.validators import URLValidator
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import (ModelSerializer,
                                        PrimaryKeyRelatedField,
                                        StringRelatedField)

from .models import (Carousel, Category, Industry, Product, ProductImages,
                     ProductType, Review, ReviewReply, Vendor)


class CarouselSerializer(ModelSerializer):
    """
    Serializer for the Carousel model.
    Responsible for data serialization, validation, filtration.
    """

    class Meta:
        model = Carousel
        fields: list[str] = [
            "id",
            "name",
            "description",
            "image",
            "url",
            "ordering",
            "is_active",
            "time_created",
            "time_updated",
        ]

    read_only_fields = ("time_created", "time_updated")

    def __init__(self, *args, **kwargs):
        """
        Initializes the serializer and hides time-related fields for non-staff users.
        """
        super().__init__(*args, **kwargs)
        request = self.context.get("request")

        if request and not request.user.is_staff:
            for field_name in ["time_created", "time_updated"]:
                self.fields.pop(field_name, None)

    def validate_url(self, value: str) -> str:
        """
        Validates that the URL is valid and starts with http:// or https://.
        """
        validator = URLValidator()
        validator(value)

        return value


class CategorySerializer(ModelSerializer):
    """
    Serializer for the Category model.
    Responsible for data serialization, validation, filtration.
    """

    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields: list[str] = [
            "id",
            "name",
            "description",
            "image",
            "parent",
            "ordering",
            "is_active",
            "time_created",
            "time_updated",
            "children",
        ]

    read_only_fields = ("time_created", "time_updated")

    def get_children(self, obj: Category) -> list[dict[str, Any]]:
        """
        Returns prefetched children categories if available.
        """
        if hasattr(obj, "prefetched_children"):
            return CategorySerializer(
                obj.prefetched_children, many=True, context=self.context
            ).data
        return []

    def __init__(self, *args, **kwargs):
        """
        Initializes the serializer and hides time-related fields for non-staff users.
        """
        super().__init__(*args, **kwargs)
        request = self.context.get("request")

        if request and not request.user.is_staff:
            for field_name in ["time_created", "time_updated"]:
                self.fields.pop(field_name, None)


class IndustrySerializer(ModelSerializer):
    """
    Serializer for the Industry model.
    Responsible for data serialization, validation, filtration.
    """

    class Meta:
        model = Industry
        fields: list[str] = [
            "id",
            "name",
            "description",
            "image",
            "ordering",
            "is_active",
            "time_created",
            "time_updated",
        ]

    read_only_fields = ("time_created", "time_updated")

    def __init__(self, *args, **kwargs):
        """
        Initializes the serializer and hides time-related fields for non-staff users.
        """
        super().__init__(*args, **kwargs)
        request = self.context.get("request")

        if request and not request.user.is_staff:
            for field_name in ["time_created", "time_updated"]:
                self.fields.pop(field_name, None)


class VendorSerializer(ModelSerializer):
    """
    Serializer for the Vendor model.
    Responsible for data serialization, validation, filtration.
    """

    class Meta:
        model = Vendor
        fields: list[str] = [
            "id",
            "name",
            "description",
            "image",
            "ordering",
            "is_active",
            "time_created",
            "time_updated",
        ]

    read_only_fields = ("time_created", "time_updated")

    def __init__(self, *args, **kwargs):
        """
        Initializes the serializer and hides time-related fields for non-staff users.
        """
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and not request.user.is_staff:
            for field_name in ["time_created", "time_updated"]:
                self.fields.pop(field_name, None)


class ProductTypeSerializer(ModelSerializer):
    """
    Serializer for the ProductType model.
    Responsible for data serialization, validation, filtration.
    """

    class Meta:
        model = ProductType
        fields: list[str] = [
            "id",
            "name",
            "description",
            "ordering",
            "is_active",
            "time_created",
            "time_updated",
        ]

    read_only_fields = ("time_created", "time_updated")

    def __init__(self, *args, **kwargs):
        """
        Initializes the serializer and sets fields for staff/non-staff differentiation.
        """
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and not request.user.is_staff:
            for field_name in ["time_created", "time_updated"]:
                self.fields.pop(field_name, None)


class ProductImagesSerializer(serializers.ModelSerializer):
    """
    Serializer for the ProductImages model.
    Responsible for data serialization, validation, filtration.
    """

    class Meta:
        model = ProductImages
        fields = ("id", "photo", "alt", "ordering", "time_created", "time_updated")
        read_only_fields = ("time_created", "time_updated")


class ProductSerializer(ModelSerializer):
    """
    Serializer for the Product model.
    Responsible for data serialization, validation, filtration.
    """

    price = serializers.DecimalField(max_digits=9, decimal_places=2)

    category_detail = serializers.SlugRelatedField(
        source="category", slug_field="name", read_only=True
    )
    vendor_detail = serializers.SlugRelatedField(
        source="vendor", slug_field="name", read_only=True
    )

    industry = serializers.PrimaryKeyRelatedField(
        queryset=Industry.objects.all(), many=True, required=False
    )
    industry_detail = serializers.SerializerMethodField()

    product_type = serializers.PrimaryKeyRelatedField(
        queryset=ProductType.objects.all(), many=True, required=False
    )
    product_type_detail = serializers.SerializerMethodField()

    images = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "description",
            "generated_description",
            "price",
            "image",
            "ordering",
            "is_active",
            "popular_products",
            "category",
            "vendor",
            "industry",
            "product_type",
            "category_detail",
            "vendor_detail",
            "industry_detail",
            "product_type_detail",
            "images",
            "time_created",
            "time_updated",
        )

        read_only_fields = ("time_created", "time_updated")

    def __init__(self, *args, **kwargs):
        """
        Initializes the serializer and sets fields for staff/non-staff differentiation.
        """
        super().__init__(*args, **kwargs)

        request = self.context.get("request")

        if request and request.user.is_staff:
            self.fields["category"] = serializers.PrimaryKeyRelatedField(
                queryset=Category.objects.all()
            )
            self.fields["vendor"] = serializers.PrimaryKeyRelatedField(
                queryset=Vendor.objects.all()
            )
            self.fields["industry"] = serializers.PrimaryKeyRelatedField(
                queryset=Industry.objects.all(), many=True
            )
            self.fields["product_type"] = serializers.PrimaryKeyRelatedField(
                queryset=ProductType.objects.all(), many=True
            )

    def validate_price(self, value: Decimal) -> Decimal:
        if value <= 0:
            raise ValidationError("Price must be greater than zero.")
        return value

    def get_fields(self) -> dict[str, serializers.Field]:
        """
        Dynamically modifies serializer fields depending on user permissions.
        """
        fields = super().get_fields()

        request = self.context.get("request")

        if request and not request.user.is_staff:
            restricted_fields: list[str] = [
                "time_created",
                "time_updated",
                "category",
                "vendor",
                "industry",
                "product_type",
            ]

            for field in restricted_fields:
                fields.pop(field, None)

        return fields

    def get_images(self, obj: Product) -> list[dict[str, Any]]:

        images = getattr(obj, "prefetched_images", None)

        if images is not None:
            return ProductImagesSerializer(images, many=True).data

        return []

    def get_industry_detail(self, obj: Product) -> list[str]:
        """
        Returns names of industries associated with the product.
        """
        industries = getattr(obj, "_prefetched_objects_cache", {}).get(
            "industry", obj.industry.all()
        )
        return [industry.name for industry in industries]

    def get_product_type_detail(self, obj: Product) -> list[str]:
        """
        Returns names of product types associated with the product.
        """
        product_types = getattr(obj, "_prefetched_objects_cache", {}).get(
            "product_type", obj.product_type.all()
        )
        return [ptype.name for ptype in product_types]


class ReviewReplySerializer(ModelSerializer):
    """
    Serializer for the ReviewReply model.
    Responsible for data serialization, validation, filtration.
    """

    user = PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ReviewReply
        fields = ["id", "user", "comment", "time_created", "time_updated"]


class ReviewSerializer(ModelSerializer):
    """
    Serializer for the Review model.
    Responsible for data serialization, validation, filtration.
    """

    user = serializers.CharField(source="user.email", read_only=True)
    replies = ReviewReplySerializer(many=True, read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "user",
            "product",
            "rating",
            "advantages",
            "comment",
            "time_created",
            "time_updated",
            "replies",
        ]

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Validates that a user cannot leave more than one review per product.
        """
        user = self.context["request"].user
        product = data.get("product")

        if Review.objects.filter(user=user, product=product).exists():
            raise serializers.ValidationError(
                "You have already left a review for this product."
            )

        return data
