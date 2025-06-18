from typing import Type

from django.conf import settings
from django.db import models
from django.utils.html import strip_tags
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
from mptt.models import MPTTModel, TreeForeignKey


class Carousel(models.Model):
    """
    Represents a carousel sliders used for displaying images with optional descriptions and links.
    """

    def carousel_image_upload_path(instance: "Carousel", filename: str) -> str:
        """
        Generate the upload path for the carousel image
        """
        return f"img/carousels/{instance.name}/{filename}"

    name = models.CharField(max_length=255, verbose_name="Slider", unique=True)
    description = CKEditor5Field(blank=True, verbose_name="Slider description")
    image = models.ImageField("Carousel image", upload_to=carousel_image_upload_path)
    url = models.URLField(
        max_length=255, verbose_name="Slider URL", blank=True, null=True
    )
    ordering = models.PositiveSmallIntegerField(
        default=0, blank=True, verbose_name="Slider ordering"
    )
    is_active = models.BooleanField(default=False, verbose_name="Active", db_index=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        """
        Returns a string representation of the Carousel instance.
        """
        return self.name

    def save(self, *args, **kwargs) -> None:
        """
        Strips all HTML tags from the description field before saving the instance.
        """
        if self.description:
            self.description = strip_tags(self.description)
        super().save(*args, **kwargs)

    class Meta:
        """
        Meta options for the Carousel model.
        """

        verbose_name = "Slider"
        verbose_name_plural = "Sliders"
        ordering = ["ordering", "-time_created"]


class Category(MPTTModel):
    """
    Represents a hierarchical category structure using MPTT.
    """

    def category_image_upload_path(instance: "Category", filename: str) -> str:
        """
        Generate the upload path for the category image
        """

        return f"img/categories/{instance.name}/{filename}"

    name = models.CharField(
        max_length=100, db_index=True, unique=True, verbose_name="Category name"
    )
    description = CKEditor5Field(blank=True, verbose_name="Category description")
    image = models.ImageField("Category image", upload_to=category_image_upload_path)
    ordering = models.PositiveSmallIntegerField(
        default=0, verbose_name="Ordering", help_text="Ordering in category list"
    )
    is_active = models.BooleanField(default=True, verbose_name="Active", db_index=True)

    parent = TreeForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )

    time_created = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs) -> None:
        """
        Strips all HTML tags from the description field before saving the instance.
        """
        if self.description:
            self.description = strip_tags(self.description)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name: str = "Category"
        verbose_name_plural: str = "Categories"

    class MPTTMeta:
        order_insertion_by: list[str] = ["ordering", "-time_created"]


class Industry(models.Model):
    """
    Represents an industries used for displaying additional information about industries and filtering products.
    """

    def industry_image_upload_path(instance: Type["Industry"], filename: str) -> str:
        """
        Generate the upload path for the industry image
        """

        return f"img/industries/{instance.name}/{filename}"

    name = models.CharField(max_length=100, db_index=True, verbose_name="Industry name")
    description = CKEditor5Field(blank=True, verbose_name="Industry description")
    image = models.ImageField(
        upload_to=industry_image_upload_path, blank=True, verbose_name="Industry image"
    )
    ordering = models.PositiveSmallIntegerField(
        default=0, verbose_name="Industry ordering"
    )
    is_active = models.BooleanField(default=True, verbose_name="Active", db_index=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Industry"
        verbose_name_plural = "Industries"
        ordering = ["ordering"]

    def save(self, *args, **kwargs) -> None:
        """
        Strips all HTML tags from the description field before saving the instance.
        """
        if self.description:
            self.description = strip_tags(self.description)
        super().save(*args, **kwargs)


class Vendor(models.Model):

    def vendor_image_upload_path(instance: Type["Vendor"], filename: str) -> str:
        """
        Generate the upload path for the vendor image
        """
        return f"img/vendors/{instance.name}/{filename}"

    name = models.CharField(max_length=100, db_index=True, verbose_name="Vendor name")
    description = models.TextField(blank=True, verbose_name="Vendor description")
    image = models.ImageField(
        upload_to=vendor_image_upload_path, verbose_name="Vendor Image"
    )
    ordering = models.PositiveSmallIntegerField(
        default=0, verbose_name="Vendor ordering"
    )
    is_active = models.BooleanField(default=True, verbose_name="Active", db_index=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Vendor"
        verbose_name_plural = "Vendors"
        ordering = ["ordering"]

    def save(self, *args, **kwargs) -> None:
        """
        Strips all HTML tags from the description field before saving the instance.
        """
        if self.description:
            self.description = strip_tags(self.description)
        super().save(*args, **kwargs)


class ProductType(models.Model):
    name = models.CharField(max_length=255, verbose_name="Product type")
    description = CKEditor5Field(blank=True, verbose_name="Product type description")
    ordering = models.PositiveSmallIntegerField(
        default=0, verbose_name="Product type ordering"
    )
    is_active = models.BooleanField(default=True, verbose_name="Active", db_index=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Product type"
        verbose_name_plural = "Product types"
        ordering = ["ordering", "-time_created"]

    def save(self, *args, **kwargs) -> None:
        """
        Strips all HTML tags from the description field before saving the instance.
        """
        if self.description:
            self.description = strip_tags(self.description)
        super().save(*args, **kwargs)


class Product(models.Model):

    def product_image_upload_path(instance: "Product", filename: str) -> str:
        """
        Generate the upload path for the products main image
        """
        return f"img/products/{instance.name}/{filename}"

    name = models.CharField(max_length=100, verbose_name="Product", db_index=True)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    description = CKEditor5Field(
        config_name="default",
        verbose_name="Product description"
    )
    generated_description = CKEditor5Field(
        config_name="default",
        verbose_name="AI generated product description", blank=True)
    image = models.ImageField(
        upload_to=product_image_upload_path, verbose_name="Product Image"
    )
    ordering = models.PositiveSmallIntegerField(
        default=0, blank=True, help_text="Use for ordering", db_index=True
    )
    time_created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    time_updated = models.DateTimeField(auto_now=True, blank=True, null=True)
    is_active = models.BooleanField(default=False, db_index=True)
    popular_products = models.BooleanField(default=False, verbose_name="Popularity")

    category = models.ForeignKey(
        Category,
        verbose_name="Category",
        on_delete=models.PROTECT,
    )
    vendor = models.ForeignKey(Vendor,
                               verbose_name="Vendor",
                               on_delete=models.PROTECT)
    industry = models.ManyToManyField(Industry, related_name="Industries")
    product_type = models.ManyToManyField(ProductType, related_name="product_types")

    def __str__(self):
        return self.name

    class Meta:
        indexes = [
            models.Index(
                fields=["is_active", "ordering"], name="idx_product_active_ordering"
            ),
            models.Index(fields=["name"], name="idx_product_name"),
        ]

        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = [
            "ordering",
        ]

    def save(self, *args, **kwargs) -> None:
        """
        Strips all HTML tags from the description field before saving the instance.
        """
        if self.description:
            self.description = strip_tags(self.description)
        super().save(*args, **kwargs)


class ProductImages(models.Model):
    def product_extra_image_upload_path(
        instance: "ProductImages", filename: str
    ) -> str:
        """
        Generate the upload path for the product extra image
        """
        product_name = (
            slugify(instance.product.name) if instance.product else "undefined"
        )
        return f"img/products/{product_name}/{filename}"

    photo = models.ImageField(
        upload_to=product_extra_image_upload_path, verbose_name="Product image"
    )
    alt = models.CharField(max_length=125, verbose_name="name", blank=True)
    ordering = models.PositiveSmallIntegerField(
        default=0, blank=True, help_text="Use for ordering"
    )
    product = models.ForeignKey(
        Product, verbose_name="Product", on_delete=models.CASCADE
    )
    time_created = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.alt

    class Meta:
        verbose_name = "Extended Product Image"
        verbose_name_plural = "Extended Product Images"
        ordering = ["product", "ordering"]


class Review(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    rating = models.BooleanField(null=True, blank=True)
    advantages = models.CharField(max_length=255)
    disadvantages = models.CharField(max_length=255)
    comment = CKEditor5Field(config_name="default", verbose_name="Review")
    moderated = models.BooleanField(default=False)
    time_created = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email

    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        ordering = [
            "-time_created",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"], name="unique_user_review"
            )
        ]

    def save(self, *args, **kwargs) -> None:
        if self.comment:
            self.comment = strip_tags(self.comment)
        super().save(*args, **kwargs)


class ReviewReply(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="replies")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    comment = CKEditor5Field(config_name="default", verbose_name="Review")
    time_created = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(auto_now=True)
    moderated = models.BooleanField(default=False)

    def __str__(self):
        return self.user.email

    class Meta:
        verbose_name = "Reply"
        verbose_name_plural = "Replies"
        ordering = [
            "-time_created",
        ]

    def save(self, *args, **kwargs):
        if self.comment:
            self.comment = strip_tags(self.comment)
        super().save(*args, **kwargs)
