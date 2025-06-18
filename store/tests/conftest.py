from decimal import Decimal
from io import BytesIO

import factory
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from rest_framework.test import APIClient

from ..models import (Carousel, Category, Industry, Product, ProductImages,
                      ProductType, Review, ReviewReply, Vendor)


@pytest.fixture
def api_client():
    """Api client fixture"""
    return APIClient()


@pytest.fixture
def test_image():
    """Create a test image"""
    file = BytesIO()
    image = Image.new("RGB", (100, 100), "blue")
    image.save(file, "jpeg")
    file.name = "test_image.jpg"
    file.seek(0)
    return SimpleUploadedFile("test_image.jpg", file.read(), content_type="image/jpeg")


# Factories for creating objects
# Carousel factory
class CarouselFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating Carousel instances.
    """

    class Meta:
        model = Carousel

    name: str = factory.Sequence(lambda n: f"Test Carousel {n}")
    description: str = factory.LazyAttribute(
        lambda obj: f"Test description for {obj.name}"
    )
    image: str = factory.LazyAttribute(lambda obj: f"image_for_{obj.name}.jpeg")
    url: str = factory.LazyAttribute(
        lambda obj: f"https://{obj.name.replace(' ', '_').lower()}.com"
    )
    ordering: int = factory.Sequence(lambda n: n)


@pytest.fixture
def create_carousel():
    """Fixture for CarouselFactory"""
    return CarouselFactory


# Category factory
class CategoryFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating Category instances.
    """

    class Meta:
        model = Category

    name: str = factory.Sequence(lambda n: f"Test Category {n}")
    description: str = factory.LazyAttribute(
        lambda obj: f"Test description for {obj.name}"
    )
    image: str = factory.LazyAttribute(lambda obj: f"image_for_{obj.name}.jpeg")
    ordering: int = factory.Sequence(lambda n: n)


@pytest.fixture
def create_category():
    """
    Fixture for CategoryFactory
    """
    return CategoryFactory


# Industry factory
class IndustryFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating Industry instances.
    """

    class Meta:
        model = Industry

    name: str = factory.Sequence(lambda n: f"Test Industry {n}")
    description: str = factory.LazyAttribute(
        lambda obj: f"Test description for {obj.name}"
    )
    image: str = factory.LazyAttribute(lambda obj: f"image_for_{obj.name}.jpeg")
    ordering: int = factory.Sequence(lambda n: n)


@pytest.fixture
def create_industry():
    """Fixture for IndustryFactory"""
    return IndustryFactory


# Vendor Factory
class VendorFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating Vendor instances.
    """

    class Meta:
        model = Vendor

    name: str = factory.Sequence(lambda n: f"Test Vendor {n}")
    description: str = factory.LazyAttribute(
        lambda obj: f"Test description for {obj.name}"
    )
    image: str = factory.LazyAttribute(lambda obj: f"image_for_{obj.name}.jpeg")
    ordering: int = factory.Sequence(lambda n: n)


@pytest.fixture
def create_vendor():
    """Fixture for VendorFactory"""
    return VendorFactory


# ProductType Factory
class ProductTypeFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating ProductType instances.
    """

    class Meta:
        model = ProductType

    name: str = factory.Sequence(lambda n: f"Test ProductType {n}")
    description: str = factory.LazyAttribute(
        lambda obj: f"Test description for {obj.name}"
    )
    ordering: int = factory.Sequence(lambda n: n)


@pytest.fixture
def create_product_type():
    """Fixture for ProductTypeFactory"""
    return ProductTypeFactory


# Product Factory
class ProductFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating Product instances.
    """

    class Meta:
        model = Product

    name = factory.Sequence(lambda n: f"Test ProductType {n}")
    description = factory.LazyAttribute(lambda obj: f"Test description for {obj.name}")
    price = Decimal("0.10")
    image = factory.LazyAttribute(lambda obj: f"image_for_{obj.name}.jpeg")
    ordering = factory.Sequence(lambda n: n)


@pytest.fixture
def create_product():
    """Fixture for ProductFactory"""
    return ProductFactory


# Extra_images_Factory
class ExtraImagesFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating Extra images instances.
    """

    class Meta:
        model = ProductImages

    photo = factory.LazyAttribute(lambda obj: f"image_for_{obj.product.name}.jpeg")
    alt = factory.Sequence(lambda n: f"Test ExtraImage {n}")
    ordering = factory.Sequence(lambda n: n)
    product = factory.SubFactory(ProductFactory)


@pytest.fixture
def create_extra_image():
    """Fixture for ExtraImagesFactory"""
    return ExtraImagesFactory


# Reviews_factory
class ReviewFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating reviews instances.
    """

    class Meta:
        model = Review

    advantages = factory.Faker("sentence", nb_words=6)
    disadvantages = factory.Faker("sentence", nb_words=6)
    comment = factory.Faker("paragraph")


@pytest.fixture
def create_review():
    """Fixture for ReviewFactory"""
    return ReviewFactory


# ReviewReply
class ReviewReply(factory.django.DjangoModelFactory):
    """
    Factory for creating replies instances.
    """

    class Meta:
        model = ReviewReply

    comment = factory.Faker("paragraph")


@pytest.fixture
def create_review_reply():
    """Fixture for ReplyFactory"""
    return ReviewReply


class DummyImage:
    """
    Simple stub with a .url attribute.
    """

    def __init__(self, url: str) -> None:
        self.url = url


class DummyObj:
    """
    Simple model stub with optional image and description.
    """

    def __init__(self, image=None, description: str | None = None) -> None:
        self.image = image
        self.description = description


@pytest.fixture
def dummy_image() -> DummyImage:
    """
    Returns a DummyImage with a default URL.
    """
    return DummyImage(url="http://example.com/default.png")


@pytest.fixture
def dummy_obj_with_image(dummy_image) -> DummyObj:
    """
    Returns a DummyObj that has a valid image.
    """
    return DummyObj(image=dummy_image, description=None)


@pytest.fixture
def dummy_obj_no_image() -> DummyObj:
    """
    Returns a DummyObj without image and without description.
    """
    return DummyObj(image=None, description=None)


@pytest.fixture(params=[None, object()])
def dummy_obj_invalid_image(request) -> DummyObj:
    """
    Parameterized: DummyObj.image is None or an object without .url.
    """
    return DummyObj(image=request.param, description=None)
