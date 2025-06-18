from typing import Optional

from django.contrib import admin, messages
from django.db.models.query import QuerySet
from django_object_actions import DjangoObjectActions

from mptt.admin import DraggableMPTTAdmin

from .mixins import PreviewDescriptionMixin
from .models import (Carousel, Category, Industry, Product, ProductImages,
                     ProductType, Review, ReviewReply, Vendor)
from .utils import render_image_preview, short_description, generate_product_description


@admin.register(Carousel)
class CarouselAdmin(PreviewDescriptionMixin, admin.ModelAdmin):
    """
    Admin configuration for the Carousel model.
    Displays key fields, image preview, and supports inline editing in the admin list view.
    """

    list_display = [
        "image_admin_preview",
        "name",
        "short_admin_description",
        "url",
        "ordering",
        "is_active",
        "time_created",
        "time_updated",
    ]
    list_display_links: tuple[str] = ("name",)
    list_editable: tuple[str] = ("ordering", "is_active")
    list_filter: tuple[str] = ("is_active", "ordering")
    search_fields: tuple[str] = ("name", "description")
    ordering: list[str] = ["ordering", "-time_created"]


@admin.register(Category)
class CategoryAdmin(PreviewDescriptionMixin, DraggableMPTTAdmin):
    """
    Admin interface configuration for Category model with draggable tree structure.

    Displays image preview, hierarchy actions, title, short description, ordering,
    status, and timestamps. Enables inline editing, filtering, and search.
    """

    list_display = [
        "image_admin_preview",
        "tree_actions",
        "indented_title",
        "short_admin_description",
        "ordering",
        "is_active",
        "time_created",
        "time_updated",
    ]
    list_editable: tuple[str] = ("ordering", "is_active")
    list_filter: tuple[str] = ("is_active", "ordering")
    search_fields: tuple[str] = ("name", "description")


@admin.register(Industry)
class IndustryAdmin(PreviewDescriptionMixin, admin.ModelAdmin):
    """
    Admin configuration for the Industry model.
    Displays key fields, image preview, and supports inline editing in the admin list view.
    """

    list_display = [
        "image_admin_preview",
        "name",
        "short_admin_description",
        "ordering",
        "is_active",
        "time_created",
        "time_updated",
    ]
    list_display_links: tuple[str] = ("name",)
    list_editable: tuple[str] = ("ordering", "is_active")
    list_filter: tuple[str] = ("is_active", "ordering")
    search_fields: tuple[str] = ("name", "description")
    ordering: list[str] = ["ordering", "-time_created"]


@admin.register(Vendor)
class VendorAdmin(PreviewDescriptionMixin, admin.ModelAdmin):
    """
    Admin configuration for the Vendor model.
    Displays key fields, image preview, and supports inline editing in the admin list view.
    """

    list_display = [
        "image_admin_preview",
        "name",
        "short_admin_description",
        "ordering",
        "is_active",
        "time_created",
        "time_updated",
    ]
    list_display_links: tuple[str] = ("name",)
    list_editable: tuple[str] = ("ordering", "is_active")
    list_filter: tuple[str] = ("is_active", "ordering")
    search_fields: tuple[str] = ("name", "description")
    ordering: list[str] = ["ordering", "-time_created"]


@admin.register(ProductType)
class ProductTypeAdmin(PreviewDescriptionMixin, admin.ModelAdmin):
    """
    Admin configuration for the ProductType model.
    Displays key fields, image preview, and supports inline editing in the admin list view.
    """

    list_display = [
        "name",
        "short_admin_description",
        "ordering",
        "is_active",
        "time_created",
        "time_updated",
    ]
    list_display_links: tuple[str] = ("name",)
    list_editable: tuple[str] = ("ordering", "is_active")
    list_filter: tuple[str] = ("is_active", "ordering")
    search_fields: tuple[str] = ("name", "description")
    ordering: list[str] = ["ordering", "-time_created"]

    @admin.display(description="Description (short)")
    def short_admin_description(self, obj: ProductType) -> str:
        """
        Returns a shortened version of the description field for the admin list view.
        """
        return short_description(obj)


class ProductImagesInline(admin.TabularInline):
    """
    Inline admin configuration for displaying product images.
    Allows adding multiple images to a product directly from the product edit page.
    """

    model = ProductImages
    extra = 1
    fields = (
        "image_admin_preview",
        "photo",
    )
    readonly_fields = ("image_admin_preview",)
    show_change_link = False

    def image_admin_preview(self, obj: ProductImages) -> Optional[str]:
        """
        Renders a safe HTML image tag for previewing the user's uploaded image
        inside the Django admin interface.
        """
        return render_image_preview(obj)


@admin.register(Product)
class ProductAdmin(PreviewDescriptionMixin, DjangoObjectActions, admin.ModelAdmin):
    """
    Admin configuration for the Product model.
    Displays key fields, image preview, and supports inline editing in the admin list view.
    """

    list_display = [
        "image_admin_preview",
        "name",
        "price",
        "short_admin_description",
        "generated_description",
        "ordering",
        "is_active",
        "get_category",
        "get_vendor",
        "get_industry",
        "get_product_type",
        "time_created",
        "time_updated",
    ]

    list_display_links: tuple[str] = ("name",)
    list_editable: tuple[str] = ("price", "ordering", "is_active")
    list_filter: tuple[str] = (
        "price",
        "ordering",
        "is_active",
        "popular_products",
        "category",
        "vendor",
        "industry",
        "product_type",
    )
    search_fields: tuple[str] = ("name", "description")
    ordering: list[str] = ["ordering", "-time_created"]

    inlines = (ProductImagesInline,)

    change_actions = ("generate_ai_description",)

    def get_queryset(self, request) -> QuerySet:
        """
        Request data for related models
        """
        return (
            super()
            .get_queryset(request)
            .select_related("category", "vendor")
            .prefetch_related("industry", "product_type")
        )

    @admin.display(description="Category", ordering="category__name")
    def get_category(self, obj: Product) -> str:
        """
        Return name of Category
        """
        return obj.category.name if obj.category else "---"

    @admin.display(description="Vendor", ordering="vendor__name")
    def get_vendor(self, obj: Product) -> str:
        """
        Return name of Vendor
        """
        return obj.vendor.name if obj.vendor else "---"

    @admin.display(description="Product Type", ordering="product_type__name")
    def get_product_type(self, obj: Product) -> str:
        """
        Return names of ProductTypes
        """
        return (
            ",".join(obj.product_type.values_list("name", flat=True))
            if obj.product_type.exists()
            else "---"
        )

    @admin.display(description="Industry", ordering="industry__name")
    def get_industry(self, obj: Product) -> str:
        """
        Return names of industries
        """
        return (
            ",".join(obj.industry.values_list("name", flat=True))
            if obj.industry.exists()
            else "---"
        )

    def generate_ai_description(self, request, obj):
        generated_text = generate_product_description(
            obj.name,
            obj.description,
            obj.price,
            self.get_category(obj),
            self.get_vendor(obj),
            self.get_industry(obj),
            self.get_product_type(obj),
        )

        obj.generated_description = generated_text
        obj.save()

        self.message_user(request, "AI description generated. Please review and edit if necessary.",
                          level=messages.SUCCESS)


class ReviewReplyInline(admin.TabularInline):
    """
    Inline admin configuration for displaying review replies.
    Allows adding multiple replies to a product directly from the review edit page.
    """

    model = ReviewReply
    extra = 0
    fields = ("user", "comment", "moderated", "time_created", "time_updated")
    show_change_link = False
    readonly_fields = ("time_created", "time_updated")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Product model.
    Displays key fields, image preview, and supports inline editing in the admin list view.
    """

    list_display = [
        "comment",
        "product",
        "user",
        "advantages",
        "disadvantages",
        "moderated",
        "time_created",
        "time_updated",
    ]

    list_display_links: tuple[str] = ("comment",)
    list_editable: tuple[str] = ("moderated",)
    list_filter: tuple[str] = ("product",)
    ordering: list[str] = ["product", "-time_created"]

    inlines = (ReviewReplyInline,)
