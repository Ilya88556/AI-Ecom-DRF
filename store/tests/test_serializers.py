import logging
from typing import Callable

import factory
import pytest

from ..serializers import CarouselSerializer

logger = logging.getLogger("project")


# Testing Carousel serializers
@pytest.mark.django_db
def test_serializer_valid_data(create_carousel: factory.django.DjangoModelFactory):
    """
    Test that the serializer correctly serializes a valid carousel instance.
    """

    carousel = create_carousel.create()

    serializer = CarouselSerializer(instance=carousel)

    serialized_data = serializer.data

    assert serialized_data["id"] == carousel.id
    assert serialized_data["name"] == carousel.name
    assert serialized_data["description"] == carousel.description
    assert serialized_data["image"] == carousel.image.url if carousel.image else None
    assert serialized_data["url"] == carousel.url
    assert serialized_data["ordering"] == carousel.ordering
    assert serialized_data["is_active"] == carousel.is_active


@pytest.mark.django_db
def test_serializer_invalid_url(test_image):
    """
    Test that the serializer raises a validation error for an invalid URL.
    """
    invalid_data = {
        "name": "Invalid Carousel",
        "description": "Test description",
        "image": test_image,
        "url": "invalid_url",  # Incorrect format
        "ordering": 1,
        "is_active": True,
    }

    serializer = CarouselSerializer(data=invalid_data)

    assert not serializer.is_valid()
    assert "url" in serializer.errors
    assert serializer.errors["url"] == ["Enter a valid URL."]


@pytest.mark.django_db
def test_serializer_valid_url(test_image: Callable) -> None:
    """
    Test that the serializer accepts a valid URL.
    """
    valid_data = {
        "name": "Valid Carousel",
        "description": "Test description",
        "image": test_image,
        "url": "https://example.com",
        "ordering": 1,
        "is_active": True,
    }

    serializer = CarouselSerializer(data=valid_data)
    assert serializer.is_valid(), serializer.errors


@pytest.mark.django_db
def test_serializer_strips_html_from_description(
    create_carousel: factory.django.DjangoModelFactory,
) -> None:
    """
    Test that the serializer strips HTML tags from the description before saving.
    """
    carousel = create_carousel.create(description="<h1>Title</h1><p>Some content</p>")

    serializer = CarouselSerializer(instance=carousel)
    serialized_data = serializer.data

    assert "<h1>" not in serialized_data["description"]
    assert "<p>" not in serialized_data["description"]
    assert "Title" in serialized_data["description"]
    assert "Some content" in serialized_data["description"]
