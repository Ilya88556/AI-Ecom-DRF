import logging
from typing import Callable

import factory
import pytest
from django.urls import reverse
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED,
                                   HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST,
                                   HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN,
                                   HTTP_404_NOT_FOUND)
from rest_framework.test import APIClient

from users.tests.conftest import create_user

from ..models import (Carousel, Category, Industry, Product, ProductImages,
                      ProductType, Review, ReviewReply, Vendor)

logger = logging.getLogger("project")


# Testing carousel
@pytest.mark.django_db
def test_get_carousel_sliders_anonymous(
        api_client: APIClient, create_carousel: factory.django.DjangoModelFactory
) -> None:
    """
    Test that anonymous users see only active carousels without restricted fields.
    """

    create_carousel.create_batch(3, is_active=True)
    create_carousel.create_batch(2, is_active=False)

    response = api_client.get(reverse("sliders-list"), format="json")

    assert response.status_code == HTTP_200_OK

    assert len(response.data) == 3
    for item in response.data:
        assert "time_created" not in item
        assert "time_updated" not in item
        assert item["is_active"] is True


@pytest.mark.django_db
def test_get_carousel_sliders_non_staff(
        api_client: APIClient,
        create_carousel: factory.django.DjangoModelFactory,
        create_user: Callable,
) -> None:
    """
    Test that non-staff users see only active carousels without time_created and time_updated.
    """
    user = create_user()

    api_client.force_authenticate(user=user)  # force authenticated mechanism

    create_carousel.create_batch(3, is_active=True)
    create_carousel.create_batch(2, is_active=False)

    response = api_client.get(reverse("sliders-list"), format="json")

    assert response.status_code == HTTP_200_OK

    assert len(response.data) == 3
    for item in response.data:
        assert "time_created" not in item
        assert "time_updated" not in item
        assert item["is_active"] is True


@pytest.mark.django_db
def test_get_carousel_sliders_staff(
        api_client: APIClient,
        create_carousel: factory.django.DjangoModelFactory,
        create_user: Callable,
) -> None:
    """
    Test that staff users see all carousels with all fields.
    """

    user = create_user(is_staff=True)

    api_client.force_authenticate(user=user)  # force authenticated mechanism

    create_carousel.create_batch(3, is_active=True)
    create_carousel.create_batch(2, is_active=False)

    response = api_client.get(reverse("sliders-list"), format="json")

    assert response.status_code == HTTP_200_OK

    assert len(response.data) == 5
    for item in response.data:
        assert "time_created" in item
        assert "time_updated" in item


@pytest.mark.django_db
def test_create_carousel_staff(
        api_client: APIClient,
        create_carousel: factory.django.DjangoModelFactory,
        create_user: Callable,
        test_image: Callable,
) -> None:
    """
    Test that staff users can create a carousel.
    """

    user = create_user(is_staff=True)
    api_client.force_authenticate(user=user)

    data: dict[str, str | bool] = {
        "name": "Staff Carousel",
        "description": "Created by staff",
        "image": test_image,
        "url": "https://example.com",
        "ordering": 1,
        "is_active": True,
    }

    response = api_client.post(reverse("sliders-list"), data, format="multipart")

    assert response.status_code == HTTP_201_CREATED
    assert Carousel.objects.filter(name="Staff Carousel").exists()


@pytest.mark.django_db
def test_create_carousel_non_staff(
        api_client: APIClient, create_user: Callable, test_image: Callable
) -> None:
    """
    Test ensure that non-staff users cannot create a carousel.
    """

    user = create_user(is_staff=False)
    api_client.force_authenticate(user=user)

    data: dict[str, str | bool] = {
        "name": "Non staff Carousel",
        "description": "Created by staff",
        "image": test_image,
        "url": "https://example.com",
        "ordering": 1,
        "is_active": True,
    }

    response = api_client.post(reverse("sliders-list"), data, format="multipart")
    assert response.status_code == HTTP_403_FORBIDDEN
    assert not Carousel.objects.filter(name="Staff Carousel").exists()


@pytest.mark.django_db
def test_create_carousel_anonymous(api_client: APIClient, test_image: Callable) -> None:
    """
    Test ensure that anonymous users cannot create a carousel.
    """

    data = {
        "name": "Non staff Carousel",
        "description": "Created by staff",
        "image": test_image,
        "url": "https://example.com",
        "ordering": 1,
        "is_active": True,
    }

    response = api_client.post(reverse("sliders-list"), data, format="multipart")
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert not Carousel.objects.filter(name="Non staff Carousel").exists()


@pytest.mark.django_db
def test_update_carousel_staff(
        api_client: APIClient,
        create_user: Callable,
        create_carousel: factory.django.DjangoModelFactory,
) -> None:
    """
    Test that a staff user can successfully update a carousel instance
    """

    user = create_user(is_staff=True)
    api_client.force_authenticate(user=user)

    carousel = create_carousel.create(is_active=True)
    updated_data = {"name": "Updated_carousel"}

    response = api_client.patch(
        reverse("sliders-detail", args=[carousel.id]), updated_data, format="json"
    )

    assert response.status_code == HTTP_200_OK
    assert Carousel.objects.get(id=carousel.id).name == "Updated_carousel"


@pytest.mark.django_db
def test_update_carousel_non_staff(
        api_client: APIClient,
        create_user: Callable,
        create_carousel: factory.django.DjangoModelFactory,
) -> None:
    """
    Test ensure that non staff users cannot update a carousel.
    """

    user = create_user()
    api_client.force_authenticate(user=user)

    carousel = create_carousel.create(is_active=True)
    initial_name = carousel.name

    updated_data = {"name": "Updated_carousel"}

    response = api_client.patch(
        reverse("sliders-detail", args=[carousel.id]), updated_data, format="json"
    )

    assert response.status_code == HTTP_403_FORBIDDEN

    carousel.refresh_from_db()
    assert carousel.name == initial_name


@pytest.mark.django_db
def test_update_carousel_anonymous(
        api_client: APIClient, create_carousel: factory.django.DjangoModelFactory
) -> None:
    """
    Test ensure that anonymous users cannot update a carousel.
    """

    carousel = create_carousel.create(is_active=True)
    initial_name = carousel.name

    updated_data = {"name": "Updated_carousel"}

    response = api_client.patch(
        reverse("sliders-detail", args=[carousel.id]), updated_data, format="json"
    )

    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert carousel.name == initial_name


@pytest.mark.django_db
def test_delete_carousel_staff(
        api_client: APIClient,
        create_user: Callable,
        create_carousel: factory.django.DjangoModelFactory,
) -> None:
    """
    Test that staff users can delete a carousel.
    """

    user = create_user(is_staff=True)
    api_client.force_authenticate(user=user)

    carousel = create_carousel.create()

    response = api_client.delete(reverse("sliders-detail", args=[carousel.id]))

    assert response.status_code == HTTP_204_NO_CONTENT
    assert not Carousel.objects.filter(id=carousel.id).exists()


@pytest.mark.django_db
def test_delete_carousel_non_staff(
        api_client: APIClient,
        create_user: Callable,
        create_carousel: factory.django.DjangoModelFactory,
) -> None:
    """
    Test ensure that non staff users cannot delete a carousel.
    """

    user = create_user()
    api_client.force_authenticate(user=user)

    carousel = create_carousel.create()

    response = api_client.delete(reverse("sliders-detail", args=[carousel.id]))

    assert response.status_code == HTTP_403_FORBIDDEN
    assert Carousel.objects.filter(id=carousel.id).exists()


@pytest.mark.django_db
def test_delete_carousel_anonymous(
        api_client: APIClient, create_carousel: factory.django.DjangoModelFactory
) -> None:
    """
    Test ensure that anonymous users cannot delete a carousel.
    """

    carousel = create_carousel.create()

    response = api_client.delete(reverse("sliders-detail", args=[carousel.id]))

    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert Carousel.objects.filter(id=carousel.id).exists()


@pytest.mark.django_db
def test_carousel_ordering(
        api_client: APIClient, create_carousel: factory.django.DjangoModelFactory
) -> None:
    """
    Test that carousels objects are returned in the correct ordering.
    """

    create_carousel.create(ordering=3, is_active=True)
    create_carousel.create(ordering=1, is_active=True)
    create_carousel.create(ordering=5, is_active=True)
    create_carousel.create(ordering=2, is_active=True)
    create_carousel.create(ordering=4, is_active=True)

    response = api_client.get(reverse("sliders-list"))

    assert response.status_code == HTTP_200_OK

    returned_order = [item["ordering"] for item in response.data]
    expected_order = sorted(returned_order)

    assert returned_order == expected_order


# Testing categories
@pytest.mark.django_db
def test_get_category_anonymous(
        api_client: APIClient, create_category: factory.django.DjangoModelFactory
) -> None:
    """
    Test that anonymous users see only active categories without restricted fields.
    """

    cat_active_parent = create_category.create(is_active=True, parent=None)
    cat_active_child = create_category.create(is_active=True, parent=cat_active_parent)
    cat_inactive_parent = create_category.create(is_active=False, parent=None)
    cat_inactive_child = create_category.create(
        is_active=False, parent=cat_inactive_parent
    )

    response = api_client.get(reverse("categories-list"), format="json")

    assert response.status_code == HTTP_200_OK

    assert len(response.data) == 1
    assert cat_active_parent.name == response.data[0]["name"]

    assert len(response.data[0]["children"]) == 1
    assert cat_active_child.name == response.data[0]["children"][0]["name"]
    assert "time_created" not in response.data[0]
    assert "time_updated" not in response.data[0]
    assert "time_created" not in response.data[0]["children"][0]
    assert "time_updated" not in response.data[0]["children"][0]


@pytest.mark.django_db
def test_get_category_staff(
        api_client: APIClient,
        create_category: factory.django.DjangoModelFactory,
        create_user: Callable,
) -> None:
    """
    Test that non-staff users see only active categories without time_created and time_updated.
    """
    user = create_user(is_staff=True)

    api_client.force_authenticate(user=user)  # force authenticated mechanism

    cat_active_parent = create_category.create_batch(2, is_active=True, parent=None)
    cat_active_child = create_category.create(
        is_active=True, parent=cat_active_parent[0]
    )
    cat_inactive_parent = create_category.create(is_active=False, parent=None)
    cat_inactive_child = create_category.create(
        is_active=False, parent=cat_inactive_parent
    )

    response = api_client.get(reverse("categories-list"), format="json")

    assert response.status_code == HTTP_200_OK

    assert len(response.data) == 3
    assert cat_active_parent[0].name == response.data[0]["name"]

    assert len(response.data[0]["children"]) == 1
    assert cat_active_child.name == response.data[0]["children"][0]["name"]

    assert "time_created" in response.data[0]
    assert "time_updated" in response.data[0]
    assert "time_created" in response.data[0]["children"][0]
    assert "time_updated" in response.data[0]["children"][0]


@pytest.mark.django_db
def test_create_category_staff(
        api_client: APIClient, create_user: Callable, test_image: Callable
) -> None:
    """
    Test that staff users can create a category.
    """

    user = create_user(is_staff=True)
    api_client.force_authenticate(user=user)

    data_category: dict[str, str | bool] = {
        "name": "Staff Category",
        "description": "Created by staff",
        "image": test_image,
        "ordering": 1,
        "is_active": True,
    }

    response = api_client.post(
        reverse("categories-list"), data_category, format="multipart"
    )

    assert response.status_code == HTTP_201_CREATED
    assert Category.objects.filter(name="Staff Category").exists()


@pytest.mark.django_db
def test_create_unique_category_staff(
        api_client: APIClient, create_user: Callable, test_image: Callable
) -> None:
    """
    Test that staff users can create a unique category.
    """

    user = create_user(is_staff=True)
    api_client.force_authenticate(user=user)

    data_category: dict[str, str | bool] = {
        "name": "Staff Category",
        "description": "Created by staff",
        "image": test_image,
        "ordering": 1,
        "is_active": True,
    }

    response = api_client.post(
        reverse("categories-list"), data_category, format="multipart"
    )

    assert response.status_code == HTTP_201_CREATED
    assert Category.objects.filter(name="Staff Category").exists()

    response = api_client.post(
        reverse("categories-list"), data_category, format="multipart"
    )
    assert response.status_code == HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_create_category_as_non_staff(
        api_client: APIClient, create_user: Callable, test_image: Callable
) -> None:
    user = create_user()
    api_client.force_authenticate(user=user)

    data_category = {"name": "Forbidden Category", "description": "Should fail"}
    response = api_client.post(
        reverse("categories-list"), data_category, format="multipart"
    )

    assert response.status_code == HTTP_403_FORBIDDEN
    assert not Category.objects.filter(name="Forbidden Category").exists()


@pytest.mark.django_db
def test_create_category_as_anonymous(
        api_client: APIClient, test_image: Callable
) -> None:
    data_category = {"name": "Forbidden Category", "description": "Should fail"}
    response = api_client.post(
        reverse("categories-list"), data_category, format="multipart"
    )

    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert not Category.objects.filter(name="Staff Carousel").exists()


@pytest.mark.django_db
def test_update_category_staff(
        api_client: APIClient,
        create_user: Callable,
        create_category: factory.django.DjangoModelFactory,
) -> None:
    """
    Test that a staff user can successfully update a category instance
    """

    user = create_user(is_staff=True)
    api_client.force_authenticate(user=user)

    category = create_category.create(is_active=True)
    updated_data = {"name": "Updated_category"}

    response = api_client.patch(
        reverse("categories-detail", args=[category.id]), updated_data, format="json"
    )

    assert response.status_code == HTTP_200_OK
    assert Category.objects.get(id=category.id).name == "Updated_category"


@pytest.mark.django_db
def test_update_category_non_staff(
        api_client: APIClient,
        create_user: Callable,
        create_category: factory.django.DjangoModelFactory,
) -> None:
    """
    Test ensure that non staff users cannot update a category.
    """

    user = create_user()
    api_client.force_authenticate(user=user)

    category = create_category.create(is_active=True)
    updated_data = {"name": "Updated_category"}

    response = api_client.patch(
        reverse("categories-detail", args=[category.id]), updated_data, format="json"
    )

    assert response.status_code == HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_update_carousel_anonymous(
        api_client: APIClient, create_carousel: factory.django.DjangoModelFactory
) -> None:
    """
    Test ensure that anonymous users cannot update a category.
    """

    category = create_carousel.create(is_active=True)
    updated_data = {"name": "Updated_carousel"}

    response = api_client.patch(
        reverse("sliders-detail", args=[category.id]), updated_data, format="json"
    )

    assert response.status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_delete_carousel_staff(
        api_client: APIClient,
        create_user: Callable,
        create_category: factory.django.DjangoModelFactory,
) -> None:
    """
    Test that staff users can delete a category.
    """

    user = create_user(is_staff=True)
    api_client.force_authenticate(user=user)

    category = create_category.create()

    response = api_client.delete(reverse("categories-detail", args=[category.id]))

    assert response.status_code == HTTP_204_NO_CONTENT
    assert not Category.objects.filter(id=category.id).exists()


@pytest.mark.django_db
def test_delete_carousel_non_staff(
        api_client: APIClient,
        create_user: Callable,
        create_category: factory.django.DjangoModelFactory,
) -> None:
    """
    Test ensure that non staff users cannot delete a category.
    """

    user = create_user()
    api_client.force_authenticate(user=user)

    category = create_category.create()

    response = api_client.delete(reverse("categories-detail", args=[category.id]))

    assert response.status_code == HTTP_403_FORBIDDEN
    assert Category.objects.filter(id=category.id).exists()


@pytest.mark.django_db
def test_delete_carousel_anonymous(
        api_client: APIClient, create_category: factory.django.DjangoModelFactory
) -> None:
    """
    Test ensure that non staff users cannot delete a category.
    """

    category = create_category.create()

    response = api_client.delete(reverse("categories-detail", args=[category.id]))

    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert Category.objects.filter(id=category.id).exists()


@pytest.mark.django_db
def test_category_ordering(
        api_client: APIClient, create_category: factory.django.DjangoModelFactory
) -> None:
    """
    Test that carousels objects are returned in the correct ordering.
    """

    create_category.create(name="Category A", ordering=2)
    create_category.create(name="Category B", ordering=1)

    response = api_client.get(reverse("categories-list"), format="json")

    assert response.status_code == HTTP_200_OK

    returned_order = [item["ordering"] for item in response.data]
    expected_order = sorted(returned_order)

    assert returned_order == expected_order


# Testing industries
@pytest.mark.django_db
def test_get_industry_anonymous(
        api_client: APIClient, create_industry: factory.django.DjangoModelFactory
) -> None:
    """
    Test that anonymous users see only active industries without restricted fields.
    """

    create_industry.create_batch(3, is_active=True)
    create_industry.create_batch(2, is_active=False)

    response = api_client.get(reverse("industries-list"), format="json")

    assert response.status_code == HTTP_200_OK

    assert len(response.data) == 3
    for item in response.data:
        assert "time_created" not in item
        assert "time_updated" not in item
        assert item["is_active"] is True


@pytest.mark.django_db
def test_get_industry_sliders_non_staff(
        api_client: APIClient,
        create_industry: factory.django.DjangoModelFactory,
        create_user: Callable,
) -> None:
    """
    Test that non-staff users see only active industry without time_created and time_updated.
    """
    user = create_user()

    api_client.force_authenticate(user=user)  # force authenticated mechanism

    create_industry.create_batch(3, is_active=True)
    create_industry.create_batch(2, is_active=False)

    response = api_client.get(reverse("industries-list"), format="json")

    assert response.status_code == HTTP_200_OK

    assert len(response.data) == 3
    for item in response.data:
        assert "time_created" not in item
        assert "time_updated" not in item
        assert item["is_active"] is True


@pytest.mark.django_db
def test_get_industries_staff(
        api_client: APIClient,
        create_industry: factory.django.DjangoModelFactory,
        create_user: Callable,
) -> None:
    """
    Test that staff users see all industries with all fields.
    """

    user = create_user(is_staff=True)

    api_client.force_authenticate(user=user)  # force authenticated mechanism

    create_industry.create_batch(3, is_active=True)
    create_industry.create_batch(2, is_active=False)

    response = api_client.get(reverse("industries-list"), format="json")

    assert response.status_code == HTTP_200_OK

    assert len(response.data) == 5
    for item in response.data:
        assert "time_created" in item
        assert "time_updated" in item


@pytest.mark.django_db
def test_create_industries_staff(
        api_client: APIClient,
        create_industry: factory.django.DjangoModelFactory,
        create_user: Callable,
        test_image: Callable,
) -> None:
    """
    Test that staff users can create an industry.
    """

    user = create_user(is_staff=True)
    api_client.force_authenticate(user=user)

    data: dict[str, str | bool] = {
        "name": "Staff Industry",
        "description": "Created by staff",
        "image": test_image,
        "ordering": 1,
        "is_active": True,
    }

    response = api_client.post(reverse("industries-list"), data, format="multipart")

    assert response.status_code == HTTP_201_CREATED
    assert Industry.objects.filter(name="Staff Industry").exists()


@pytest.mark.django_db
def test_create_industry_non_staff(
        api_client: APIClient, create_user: Callable, test_image: Callable
) -> None:
    """
    Test ensure that non-staff users cannot create an industry.
    """

    user = create_user(is_staff=False)
    api_client.force_authenticate(user=user)

    data: dict[str, str | bool] = {
        "name": "Non staff Industry",
        "description": "Created by staff",
        "image": test_image,
        "ordering": 1,
        "is_active": True,
    }

    response = api_client.post(reverse("industries-list"), data, format="multipart")
    assert response.status_code == HTTP_403_FORBIDDEN
    assert not Carousel.objects.filter(name="Non staff Industry").exists()


@pytest.mark.django_db
def test_create_industry_anonymous(api_client: APIClient, test_image: Callable) -> None:
    """
    Test ensure that anonymous users cannot create an industry.
    """

    data = {
        "name": "Non staff Industry",
        "description": "Created by anonymous",
        "image": test_image,
        "ordering": 1,
        "is_active": True,
    }

    response = api_client.post(reverse("industries-list"), data, format="multipart")
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert not Carousel.objects.filter(name="Non staff Industry").exists()


@pytest.mark.django_db
def test_update_industry_staff(
        api_client: APIClient,
        create_user: Callable,
        create_industry: factory.django.DjangoModelFactory,
) -> None:
    """
    Test that a staff user can successfully update an industry instance
    """

    user = create_user(is_staff=True)
    api_client.force_authenticate(user=user)

    industry = create_industry.create(is_active=True)
    updated_data = {"name": "Updated_industry"}

    response = api_client.patch(
        reverse("industries-detail", args=[industry.id]), updated_data, format="json"
    )

    assert response.status_code == HTTP_200_OK
    assert Industry.objects.get(id=industry.id).name == "Updated_industry"


@pytest.mark.django_db
def test_update_industry_non_staff(
        api_client: APIClient,
        create_user: Callable,
        create_industry: factory.django.DjangoModelFactory,
) -> None:
    """
    Test ensure that non staff users cannot update an industry.
    """

    user = create_user()
    api_client.force_authenticate(user=user)

    industry = create_industry.create(is_active=True)
    initial_name = industry.name

    updated_data = {"name": "Updated_industry"}

    response = api_client.patch(
        reverse("industries-detail", args=[industry.id]), updated_data, format="json"
    )

    assert response.status_code == HTTP_403_FORBIDDEN

    industry.refresh_from_db()
    assert industry.name == initial_name


@pytest.mark.django_db
def test_update_industry_anonymous(
        api_client: APIClient, create_industry: factory.django.DjangoModelFactory
) -> None:
    """
    Test ensure that anonymous users cannot update an industry.
    """

    industry = create_industry.create(is_active=True)
    initial_name = industry.name

    updated_data = {"name": "Updated_industry"}

    response = api_client.patch(
        reverse("industries-detail", args=[industry.id]), updated_data, format="json"
    )

    assert response.status_code == HTTP_401_UNAUTHORIZED

    industry.refresh_from_db()
    assert industry.name == initial_name


@pytest.mark.django_db
def test_delete_industry_staff(
        api_client: APIClient,
        create_user: Callable,
        create_industry: factory.django.DjangoModelFactory,
) -> None:
    """
    Test that staff users can delete an industry.
    """

    user = create_user(is_staff=True)
    api_client.force_authenticate(user=user)

    industry = create_industry.create()

    response = api_client.delete(reverse("industries-detail", args=[industry.id]))

    assert response.status_code == HTTP_204_NO_CONTENT
    assert not Industry.objects.filter(id=industry.id).exists()


@pytest.mark.django_db
def test_delete_industry_non_staff(
        api_client: APIClient,
        create_user: Callable,
        create_industry: factory.django.DjangoModelFactory,
) -> None:
    """
    Test ensure that non staff users cannot delete an industry.
    """

    user = create_user()
    api_client.force_authenticate(user=user)

    industry = create_industry.create()

    response = api_client.delete(reverse("industries-detail", args=[industry.id]))

    assert response.status_code == HTTP_403_FORBIDDEN
    assert Industry.objects.filter(id=industry.id).exists()


@pytest.mark.django_db
def test_delete_industry_anonymous(
        api_client: APIClient, create_industry: factory.django.DjangoModelFactory
) -> None:
    """
    Test ensure that anonymous users cannot delete an industry.
    """

    industry = create_industry.create()

    response = api_client.delete(reverse("industries-detail", args=[industry.id]))

    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert Industry.objects.filter(id=industry.id).exists()


@pytest.mark.django_db
def test_industries_ordering(
        api_client: APIClient, create_industry: factory.django.DjangoModelFactory
) -> None:
    """
    Test that industries objects are returned in the correct ordering.
    """

    create_industry.create(ordering=3, is_active=True)
    create_industry.create(ordering=1, is_active=True)
    create_industry.create(ordering=5, is_active=True)
    create_industry.create(ordering=2, is_active=True)
    create_industry.create(ordering=4, is_active=True)

    response = api_client.get(reverse("industries-list"))

    assert response.status_code == HTTP_200_OK

    returned_order = [item["ordering"] for item in response.data]
    expected_order = sorted(returned_order)

    assert returned_order == expected_order


# Testing vendors
@pytest.mark.django_db
def test_get_vendor_anonymous(
        api_client: APIClient, create_vendor: factory.django.DjangoModelFactory
) -> None:
    """
    Test that anonymous users see only active vendor without restricted fields.
    """

    create_vendor.create_batch(3, is_active=True)
    create_vendor.create_batch(2, is_active=False)

    response = api_client.get(reverse("vendors-list"), format="json")

    assert response.status_code == HTTP_200_OK

    assert len(response.data) == 3
    for item in response.data:
        assert "time_created" not in item
        assert "time_updated" not in item
        assert item["is_active"] is True


@pytest.mark.django_db
def test_get_vendor_non_staff(
        api_client: APIClient,
        create_vendor: factory.django.DjangoModelFactory,
        create_user: Callable,
) -> None:
    """
    Test that non-staff users see only active vendor without time_created and time_updated.
    """
    user = create_user()

    api_client.force_authenticate(user=user)  # force authenticated mechanism

    create_vendor.create_batch(3, is_active=True)
    create_vendor.create_batch(2, is_active=False)

    response = api_client.get(reverse("vendors-list"), format="json")

    assert response.status_code == HTTP_200_OK

    assert len(response.data) == 3
    for item in response.data:
        assert "time_created" not in item
        assert "time_updated" not in item
        assert item["is_active"] is True


@pytest.mark.django_db
def test_get_vendor_staff(
        api_client: APIClient,
        create_vendor: factory.django.DjangoModelFactory,
        create_user: Callable,
) -> None:
    """
    Test that staff users see all vendors with all fields.
    """

    user = create_user(is_staff=True)

    api_client.force_authenticate(user=user)  # force authenticated mechanism

    create_vendor.create_batch(3, is_active=True)
    create_vendor.create_batch(2, is_active=False)

    response = api_client.get(reverse("vendors-list"), format="json")

    assert response.status_code == HTTP_200_OK

    assert len(response.data) == 5
    for item in response.data:
        assert "time_created" in item
        assert "time_updated" in item


@pytest.mark.django_db
def test_create_vendor_staff(
        api_client: APIClient,
        create_vendor: factory.django.DjangoModelFactory,
        create_user: Callable,
        test_image: Callable,
) -> None:
    """
    Test that staff users can create a vendor.
    """

    user = create_user(is_staff=True)
    api_client.force_authenticate(user=user)

    data: dict[str, str | bool] = {
        "name": "Staff Vendor",
        "description": "Created by staff",
        "image": test_image,
        "ordering": 1,
        "is_active": True,
    }

    response = api_client.post(reverse("vendors-list"), data, format="multipart")

    assert response.status_code == HTTP_201_CREATED
    assert Vendor.objects.filter(name="Staff Vendor").exists()


@pytest.mark.django_db
def test_create_vendor_non_staff(
        api_client: APIClient, create_user: Callable, test_image: Callable
) -> None:
    """
    Test ensure that non-staff users cannot create a vendor.
    """

    user = create_user(is_staff=False)
    api_client.force_authenticate(user=user)

    data: dict[str, str | bool] = {
        "name": "Non staff Vendor",
        "description": "Created by staff",
        "image": test_image,
        "ordering": 1,
        "is_active": True,
    }

    response = api_client.post(reverse("vendors-list"), data, format="multipart")
    assert response.status_code == HTTP_403_FORBIDDEN
    assert not Vendor.objects.filter(name="Non staff Vendor").exists()


@pytest.mark.django_db
def test_create_vendor_anonymous(api_client: APIClient, test_image: Callable) -> None:
    """
    Test ensure that anonymous users cannot create a vendor.
    """

    data = {
        "name": "Non staff Vendor",
        "description": "Created by anonymous",
        "image": test_image,
        "ordering": 1,
        "is_active": True,
    }

    response = api_client.post(reverse("vendors-list"), data, format="multipart")
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert not Vendor.objects.filter(name="Non staff Vendor").exists()


@pytest.mark.django_db
def test_update_vendor_staff(
        api_client: APIClient,
        create_user: Callable,
        create_vendor: factory.django.DjangoModelFactory,
) -> None:
    """
    Test that a staff user can successfully update a vendor instance
    """

    user = create_user(is_staff=True)
    api_client.force_authenticate(user=user)

    vendor = create_vendor.create(is_active=True)
    updated_data = {"name": "Updated_vendor"}

    response = api_client.patch(
        reverse("vendors-detail", args=[vendor.id]), updated_data, format="json"
    )

    assert response.status_code == HTTP_200_OK
    assert Vendor.objects.get(id=vendor.id).name == "Updated_vendor"


@pytest.mark.django_db
def test_update_vendor_non_staff(
        api_client: APIClient,
        create_user: Callable,
        create_vendor: factory.django.DjangoModelFactory,
) -> None:
    """
    Test ensure that non staff users cannot update an industry.
    """

    user = create_user()
    api_client.force_authenticate(user=user)

    vendor = create_vendor.create(is_active=True)
    initial_name = vendor.name

    updated_data = {"name": "Updated_industry"}

    response = api_client.patch(
        reverse("vendors-detail", args=[vendor.id]), updated_data, format="json"
    )

    assert response.status_code == HTTP_403_FORBIDDEN

    vendor.refresh_from_db()
    assert vendor.name == initial_name


@pytest.mark.django_db
def test_update_vendor_anonymous(
        api_client: APIClient, create_vendor: factory.django.DjangoModelFactory
) -> None:
    """
    Test ensure that anonymous users cannot update a vendor.
    """

    vendor = create_vendor.create(is_active=True)
    initial_name = vendor.name

    updated_data = {"name": "Updated_industry"}

    response = api_client.patch(
        reverse("vendors-detail", args=[vendor.id]), updated_data, format="json"
    )

    assert response.status_code == HTTP_401_UNAUTHORIZED

    vendor.refresh_from_db()
    assert vendor.name == initial_name


@pytest.mark.django_db
def test_delete_vendor_staff(
        api_client: APIClient,
        create_user: Callable,
        create_vendor: factory.django.DjangoModelFactory,
) -> None:
    """
    Test that staff users can delete a vendor.
    """

    user = create_user(is_staff=True)
    api_client.force_authenticate(user=user)

    vendor = create_vendor.create()

    response = api_client.delete(reverse("vendors-detail", args=[vendor.id]))

    assert response.status_code == HTTP_204_NO_CONTENT
    assert not Vendor.objects.filter(id=vendor.id).exists()


@pytest.mark.django_db
def test_delete_vendor_non_staff(
        api_client: APIClient,
        create_user: Callable,
        create_vendor: factory.django.DjangoModelFactory,
) -> None:
    """
    Test ensure that non staff users cannot delete a vendor.
    """

    user = create_user()
    api_client.force_authenticate(user=user)

    vendor = create_vendor.create()

    response = api_client.delete(reverse("vendors-detail", args=[vendor.id]))

    assert response.status_code == HTTP_403_FORBIDDEN
    assert Vendor.objects.filter(id=vendor.id).exists()


@pytest.mark.django_db
def test_delete_vendor_anonymous(
        api_client: APIClient, create_vendor: factory.django.DjangoModelFactory
) -> None:
    """
    Test ensure that anonymous users cannot delete a vendor.
    """

    vendor = create_vendor.create()

    response = api_client.delete(reverse("vendors-detail", args=[vendor.id]))

    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert Vendor.objects.filter(id=vendor.id).exists()


@pytest.mark.django_db
def test_vendors_ordering(
        api_client: APIClient, create_vendor: factory.django.DjangoModelFactory
) -> None:
    """
    Test that vendors objects are returned in the correct ordering.
    """

    create_vendor.create(ordering=3, is_active=True)
    create_vendor.create(ordering=1, is_active=True)
    create_vendor.create(ordering=5, is_active=True)
    create_vendor.create(ordering=2, is_active=True)
    create_vendor.create(ordering=4, is_active=True)

    response = api_client.get(reverse("vendors-list"))

    assert response.status_code == HTTP_200_OK

    returned_order = [item["ordering"] for item in response.data]
    expected_order = sorted(returned_order)

    assert returned_order == expected_order


# Testing product_types
@pytest.mark.django_db
def test_get_product_types_anonymous(
        api_client: APIClient, create_product_type: factory.django.DjangoModelFactory
) -> None:
    """
    Test that anonymous users see only active product_types without restricted fields.
    """

    create_product_type.create_batch(3, is_active=True)
    create_product_type.create_batch(2, is_active=False)

    response = api_client.get(reverse("product_types-list"), format="json")

    assert response.status_code == HTTP_200_OK

    assert len(response.data) == 3
    for item in response.data:
        assert "time_created" not in item
        assert "time_updated" not in item
        assert item["is_active"] is True


@pytest.mark.django_db
def test_get_product_types_non_staff(
        api_client: APIClient,
        create_product_type: factory.django.DjangoModelFactory,
        create_user: Callable,
) -> None:
    """
    Test that non-staff users see only active product types without time_created and time_updated.
    """
    user = create_user()

    api_client.force_authenticate(user=user)  # force authenticated mechanism

    create_product_type.create_batch(3, is_active=True)
    create_product_type.create_batch(2, is_active=False)

    response = api_client.get(reverse("product_types-list"), format="json")

    assert response.status_code == HTTP_200_OK

    assert len(response.data) == 3
    for item in response.data:
        assert "time_created" not in item
        assert "time_updated" not in item
        assert item["is_active"] is True


@pytest.mark.django_db
def test_get_product_types_staff(
        api_client: APIClient,
        create_product_type: factory.django.DjangoModelFactory,
        create_user: Callable,
) -> None:
    """
    Test that staff users see all product_types with all fields.
    """

    user = create_user(is_staff=True)

    api_client.force_authenticate(user=user)  # force authenticated mechanism

    create_product_type.create_batch(3, is_active=True)
    create_product_type.create_batch(2, is_active=False)

    response = api_client.get(reverse("product_types-list"), format="json")

    assert response.status_code == HTTP_200_OK

    assert len(response.data) == 5
    for item in response.data:
        assert "time_created" in item
        assert "time_updated" in item


@pytest.mark.django_db
def test_create_product_types_staff(
        api_client: APIClient,
        create_product_type: factory.django.DjangoModelFactory,
        create_user: Callable,
) -> None:
    """
    Test that staff users can create a ProductType.
    """

    user = create_user(is_staff=True)
    api_client.force_authenticate(user=user)

    data: dict[str, str | bool] = {
        "name": "Staff ProductType",
        "description": "Created by staff",
        "ordering": 1,
        "is_active": True,
    }

    response = api_client.post(reverse("product_types-list"), data, format="multipart")

    assert response.status_code == HTTP_201_CREATED
    assert ProductType.objects.filter(name="Staff ProductType").exists()


@pytest.mark.django_db
def test_create_product_types_non_staff(
        api_client: APIClient, create_user: Callable
) -> None:
    """
    Test ensure that non-staff users cannot create a product types.
    """

    user = create_user(is_staff=False)
    api_client.force_authenticate(user=user)

    data: dict[str, str | bool] = {
        "name": "Non staff Product Type",
        "description": "Created by staff",
        "ordering": 1,
        "is_active": True,
    }

    response = api_client.post(reverse("product_types-list"), data, format="multipart")
    assert response.status_code == HTTP_403_FORBIDDEN
    assert not ProductType.objects.filter(name="Non staff Product Type").exists()


@pytest.mark.django_db
def test_create_product_types_anonymous(api_client: APIClient) -> None:
    """
    Test ensure that anonymous users cannot create a product type.
    """

    data = {
        "name": "Non staff Product Type",
        "description": "Created by anonymous",
        "ordering": 1,
        "is_active": True,
    }

    response = api_client.post(reverse("product_types-list"), data, format="multipart")
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert not ProductType.objects.filter(name="Non staff Product Type").exists()


@pytest.mark.django_db
def test_update_product_types_staff(
        api_client: APIClient,
        create_user: Callable,
        create_product_type: factory.django.DjangoModelFactory,
) -> None:
    """
    Test that a staff user can successfully update a product type instance
    """

    user = create_user(is_staff=True)
    api_client.force_authenticate(user=user)

    product_type = create_product_type.create(is_active=True)
    updated_data = {"name": "Updated_product_type"}

    response = api_client.patch(
        reverse("product_types-detail", args=[product_type.id]),
        updated_data,
        format="json",
    )

    assert response.status_code == HTTP_200_OK
    assert ProductType.objects.get(id=product_type.id).name == "Updated_product_type"


@pytest.mark.django_db
def test_update_product_types_non_staff(
        api_client: APIClient,
        create_user: Callable,
        create_product_type: factory.django.DjangoModelFactory,
) -> None:
    """
    Test ensure that non staff users cannot update a product type.
    """

    user = create_user()
    api_client.force_authenticate(user=user)

    product_type = create_product_type.create(is_active=True)
    initial_name = product_type.name

    updated_data = {"name": "Updated_product_type"}

    response = api_client.patch(
        reverse("product_types-detail", args=[product_type.id]),
        updated_data,
        format="json",
    )

    assert response.status_code == HTTP_403_FORBIDDEN

    product_type.refresh_from_db()
    assert product_type.name == initial_name


@pytest.mark.django_db
def test_update_product_types_anonymous(
        api_client: APIClient, create_product_type: factory.django.DjangoModelFactory
) -> None:
    """
    Test ensure that anonymous users cannot update an industry.
    """

    product_type = create_product_type.create(is_active=True)
    initial_name = product_type.name

    updated_data = {"name": "Updated_product_type"}

    response = api_client.patch(
        reverse("product_types-detail", args=[product_type.id]),
        updated_data,
        format="json",
    )

    assert response.status_code == HTTP_401_UNAUTHORIZED

    product_type.refresh_from_db()
    assert product_type.name == initial_name


@pytest.mark.django_db
def test_delete_product_types_staff(
        api_client: APIClient,
        create_user: Callable,
        create_product_type: factory.django.DjangoModelFactory,
) -> None:
    """
    Test that staff users can delete a vendor.
    """

    user = create_user(is_staff=True)
    api_client.force_authenticate(user=user)

    product_type = create_product_type.create()

    response = api_client.delete(
        reverse("product_types-detail", args=[product_type.id])
    )

    assert response.status_code == HTTP_204_NO_CONTENT
    assert not ProductType.objects.filter(id=product_type.id).exists()


@pytest.mark.django_db
def test_delete_product_types_non_staff(
        api_client: APIClient,
        create_user: Callable,
        create_product_type: factory.django.DjangoModelFactory,
) -> None:
    """
    Test ensure that non staff users cannot delete a vendor.
    """

    user = create_user()
    api_client.force_authenticate(user=user)

    product_type = create_product_type.create()

    response = api_client.delete(
        reverse("product_types-detail", args=[product_type.id])
    )

    assert response.status_code == HTTP_403_FORBIDDEN
    assert ProductType.objects.filter(id=product_type.id).exists()


@pytest.mark.django_db
def test_delete_product_types_anonymous(
        api_client: APIClient, create_product_type: factory.django.DjangoModelFactory
) -> None:
    """
    Test ensure that anonymous users cannot delete a vendor.
    """

    product_type = create_product_type.create()

    response = api_client.delete(
        reverse("product_types-detail", args=[product_type.id])
    )

    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert ProductType.objects.filter(id=product_type.id).exists()


@pytest.mark.django_db
def test_product_types_ordering(
        api_client: APIClient, create_product_type: factory.django.DjangoModelFactory
) -> None:
    """
    Test that vendors objects are returned in the correct ordering.
    """

    create_product_type.create(ordering=3, is_active=True)
    create_product_type.create(ordering=1, is_active=True)
    create_product_type.create(ordering=5, is_active=True)
    create_product_type.create(ordering=2, is_active=True)
    create_product_type.create(ordering=4, is_active=True)

    response = api_client.get(reverse("product_types-list"))

    assert response.status_code == HTTP_200_OK

    returned_order = [item["ordering"] for item in response.data]
    expected_order = sorted(returned_order)

    assert returned_order == expected_order


# Testing Products
@pytest.mark.django_db
def test_get_product_anonymous(
        api_client: APIClient,
        create_product: factory.django.DjangoModelFactory,
        create_category: factory.django.DjangoModelFactory,
        create_industry: factory.django.DjangoModelFactory,
        create_vendor: factory.django.DjangoModelFactory,
        create_product_type: factory.django.DjangoModelFactory,
        create_extra_image: factory.django.DjangoModelFactory,
) -> None:
    """
    Test that anonymous users see only active product without restricted fields.
    """
    category = create_category.create()
    industry = create_industry.create_batch(2)
    vendor = create_vendor.create()
    product_type = create_product_type.create_batch(2)

    product_active = create_product.create_batch(
        3, category=category, vendor=vendor, is_active=True
    )

    product_inactive = create_product.create_batch(
        2, category=category, vendor=vendor, is_active=False
    )

    for product in product_active:
        product.industry.set(industry)
        product.product_type.set(product_type)
        product.save()

        create_extra_image.create_batch(2, product=product)

    for product in product_inactive:
        product.industry.set(industry)
        product.product_type.set(product_type)
        product.save()

        create_extra_image.create_batch(2, product=product)

    response = api_client.get(reverse("products-list"), format="json")
    assert response.status_code == HTTP_200_OK

    assert response.data["count"] == 3
    for item in response.data["results"]:
        assert "time_created" not in item
        assert "time_updated" not in item
        assert "category" not in item
        assert "vendor" not in item
        assert "industry" not in item
        assert "product_type" not in item
        assert item["is_active"] is True


@pytest.mark.django_db
def test_get_product_non_staff(
        api_client: APIClient,
        create_product: factory.django.DjangoModelFactory,
        create_category: factory.django.DjangoModelFactory,
        create_industry: factory.django.DjangoModelFactory,
        create_vendor: factory.django.DjangoModelFactory,
        create_product_type: factory.django.DjangoModelFactory,
        create_extra_image: factory.django.DjangoModelFactory,
        create_user: Callable,
) -> None:
    """
    Test that non_staff users see only active product without restricted fields.
    """

    category = create_category.create()
    industry = create_industry.create_batch(2)
    vendor = create_vendor.create()
    product_type = create_product_type.create_batch(2)

    product_active = create_product.create_batch(
        3, category=category, vendor=vendor, is_active=True
    )

    product_inactive = create_product.create_batch(
        2, category=category, vendor=vendor, is_active=False
    )

    for product in product_active:
        product.industry.set(industry)
        product.product_type.set(product_type)
        product.save()

        create_extra_image.create_batch(2, product=product)

    for product in product_inactive:
        product.industry.set(industry)
        product.product_type.set(product_type)
        product.save()

        create_extra_image.create_batch(2, product=product)

    user = create_user()
    api_client.force_authenticate(user=user)

    response = api_client.get(reverse("products-list"), format="json")
    assert response.status_code == HTTP_200_OK

    assert response.data["count"] == 3
    for item in response.data["results"]:
        assert "time_created" not in item
        assert "time_updated" not in item
        assert "category" not in item
        assert "vendor" not in item
        assert "industry" not in item
        assert "product_type" not in item
        assert item["is_active"] is True


@pytest.mark.django_db
def test_get_product_staff(
        api_client: APIClient,
        create_product: factory.django.DjangoModelFactory,
        create_category: factory.django.DjangoModelFactory,
        create_industry: factory.django.DjangoModelFactory,
        create_vendor: factory.django.DjangoModelFactory,
        create_product_type: factory.django.DjangoModelFactory,
        create_extra_image: factory.django.DjangoModelFactory,
        create_user: Callable,
) -> None:
    """
    Test that staff users see all products with all fields.
    """

    category = create_category.create()
    industry = create_industry.create_batch(2)
    vendor = create_vendor.create()
    product_type = create_product_type.create_batch(2)

    product_active = create_product.create_batch(
        3, category=category, vendor=vendor, is_active=True
    )

    product_inactive = create_product.create_batch(
        2, category=category, vendor=vendor, is_active=False
    )

    for product in product_active:
        product.industry.set(industry)
        product.product_type.set(product_type)
        product.save()

        create_extra_image.create_batch(2, product=product)

    for product in product_inactive:
        product.industry.set(industry)
        product.product_type.set(product_type)
        product.save()

        create_extra_image.create_batch(2, product=product)

    user = create_user(is_staff=True)
    api_client.force_authenticate(user=user)

    response = api_client.get(reverse("products-list"), format="json")
    assert response.status_code == HTTP_200_OK

    assert response.data["count"] == 5
    for item in response.data["results"]:
        assert "time_created" in item
        assert "time_updated" in item
        assert "category" in item
        assert "vendor" in item
        assert "industry" in item
        assert "product_type" in item


@pytest.mark.django_db(reset_sequences=True)
def test_create_product_staff(
        api_client: APIClient,
        create_product: factory.django.DjangoModelFactory,
        create_category: factory.django.DjangoModelFactory,
        create_industry: factory.django.DjangoModelFactory,
        create_vendor: factory.django.DjangoModelFactory,
        create_product_type: factory.django.DjangoModelFactory,
        create_extra_image: factory.django.DjangoModelFactory,
        create_user: Callable,
        test_image: Callable,
) -> None:
    user = create_user(is_staff=True)
    api_client.force_authenticate(user=user)

    category = create_category.create()
    industry = create_industry.create()
    industry2 = create_industry.create()
    vendor = create_vendor.create()
    product_type = create_product_type.create()
    product_type1 = create_product_type.create()

    print(Industry.objects.all())

    data: dict[str: str | bool] = {
        "name": "Staff Test Product",
        "description": "Test product description",
        "price": 0.1,
        "image": test_image,
        "ordering": 1,
        "category": category.id,
        "vendor": vendor.id,
        "industry": [industry.id, industry2.id],
        "product_type": [product_type.id, product_type1.id],
    }

    response = api_client.post(reverse("products-list"), data, format="multipart")

    assert response.status_code == HTTP_201_CREATED

    product = Product.objects.get(name="Staff Test Product")

    create_extra_image.create_batch(3, product=product)

    response = api_client.get(
        reverse("products-detail", args=[product.id]), format="json"
    )

    assert response.status_code == HTTP_200_OK
    assert Product.objects.filter(name="Staff Test Product").exists()


@pytest.mark.django_db
def test_create_invalid_product_staff(
        api_client: APIClient,
        create_product: factory.django.DjangoModelFactory,
        create_category: factory.django.DjangoModelFactory,
        create_industry: factory.django.DjangoModelFactory,
        create_vendor: factory.django.DjangoModelFactory,
        create_product_type: factory.django.DjangoModelFactory,
        create_extra_image: factory.django.DjangoModelFactory,
        create_user: Callable,
        test_image: Callable,
) -> None:
    user = create_user(is_staff=True)
    api_client.force_authenticate(user=user)

    category = create_category.create()
    industry = create_industry.create()
    industry2 = create_industry.create()
    vendor = create_vendor.create()
    product_type = create_product_type.create()
    product_type1 = create_product_type.create()

    data: dict[str: str | bool] = {
        "name": "Staff Test Product",
        "description": "Test product description",
        "price": -1.00,
        "image": test_image,
        "ordering": 1,
        "category": category.id,
        "vendor": vendor.id,
        "industry": [industry.id, industry2.id],
        "product_type": [product_type.id, product_type1.id],
    }

    response = api_client.post(reverse("products-list"), data, format="multipart")

    assert response.status_code == HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_create_product_non_staff(
        api_client: APIClient,
        create_product: factory.django.DjangoModelFactory,
        create_category: factory.django.DjangoModelFactory,
        create_industry: factory.django.DjangoModelFactory,
        create_vendor: factory.django.DjangoModelFactory,
        create_product_type: factory.django.DjangoModelFactory,
        create_extra_image: factory.django.DjangoModelFactory,
        create_user: Callable,
        test_image: Callable,
) -> None:
    """
    Test ensure that non-staff users cannot create a product.
    """

    user = create_user(is_staff=False)
    api_client.force_authenticate(user=user)

    category = create_category.create()
    industry = create_industry.create()
    industry2 = create_industry.create()
    vendor = create_vendor.create()
    product_type = create_product_type.create()
    product_type1 = create_product_type.create()

    data: dict[str: str | bool] = {
        "name": "Staff Test Product",
        "description": "Test product description",
        "price": 0.1,
        "image": test_image,
        "ordering": 1,
        "category": category.id,
        "vendor": vendor.id,
        "industry": [industry.id, industry2.id],
        "product_type": [product_type.id, product_type1.id],
    }

    response = api_client.post(reverse("products-list"), data, format="multipart")
    assert response.status_code == HTTP_403_FORBIDDEN
    assert not Product.objects.filter(name="Staff Test Product").exists()


@pytest.mark.django_db
def test_create_product_anonymous(
        api_client: APIClient,
        create_product: factory.django.DjangoModelFactory,
        create_category: factory.django.DjangoModelFactory,
        create_industry: factory.django.DjangoModelFactory,
        create_vendor: factory.django.DjangoModelFactory,
        create_product_type: factory.django.DjangoModelFactory,
        test_image: Callable,
) -> None:
    """
    Test ensure that anonymous users cannot create a product.
    """

    category = create_category.create()
    industry = create_industry.create()
    industry2 = create_industry.create()
    vendor = create_vendor.create()
    product_type = create_product_type.create()
    product_type1 = create_product_type.create()

    data: dict[str: str | bool] = {
        "name": "Staff Test Product",
        "description": "Test product description",
        "price": 0.1,
        "main_image": test_image,
        "ordering": 1,
        "category": category.id,
        "vendor": vendor.id,
        "industry": [industry.id, industry2.id],
        "product_type": [product_type.id, product_type1.id],
    }

    response = api_client.post(reverse("products-list"), data, format="multipart")
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert not Product.objects.filter(name="Staff Test Product").exists()


@pytest.mark.django_db
def test_update_product_staff(
        api_client: APIClient,
        create_product: factory.django.DjangoModelFactory,
        create_category: factory.django.DjangoModelFactory,
        create_industry: factory.django.DjangoModelFactory,
        create_vendor: factory.django.DjangoModelFactory,
        create_product_type: factory.django.DjangoModelFactory,
        create_extra_image: factory.django.DjangoModelFactory,
        create_user: Callable,
        test_image: Callable,
) -> None:
    """
    Test that a staff user can successfully update a product instance
    """

    user = create_user(is_staff=True)
    api_client.force_authenticate(user=user)

    category = create_category.create()
    industry = create_industry.create_batch(2)
    vendor = create_vendor.create()
    product_type = create_product_type.create_batch(2)

    product = create_product.create(category=category, vendor=vendor, is_active=True)

    product.industry.set(industry)
    product.product_type.set(product_type)
    product.save()

    updated_data = {"name": "Updated_product", "industry": [industry[0].id]}

    response = api_client.patch(
        reverse("products-detail", args=[product.id]), updated_data, format="json"
    )

    product = Product.objects.get(id=product.id)
    assert response.status_code == HTTP_200_OK
    assert product.name == "Updated_product"
    assert product.category.name == category.name
    assert product.vendor.name == vendor.name

    updated_industry_ids = set(product.industry.values_list("id", flat=True))
    assert updated_industry_ids == {industry[0].id}


@pytest.mark.django_db
def test_update_products_non_staff(
        api_client: APIClient,
        create_product: factory.django.DjangoModelFactory,
        create_category: factory.django.DjangoModelFactory,
        create_industry: factory.django.DjangoModelFactory,
        create_vendor: factory.django.DjangoModelFactory,
        create_product_type: factory.django.DjangoModelFactory,
        create_extra_image: factory.django.DjangoModelFactory,
        create_user: Callable,
) -> None:
    """
    Test ensure that non_staff users cannot update a product.
    """

    user = create_user()
    api_client.force_authenticate(user=user)

    category = create_category.create()
    industry = create_industry.create_batch(2)
    vendor = create_vendor.create()
    product_type = create_product_type.create_batch(2)

    product = create_product.create(category=category, vendor=vendor, is_active=True)

    product.industry.set(industry)
    product.product_type.set(product_type)
    product.save()

    updated_data = {"name": "Updated_product"}

    response = api_client.patch(
        reverse("products-detail", args=[product.id]), updated_data, format="json"
    )

    product = Product.objects.get(id=product.id)
    assert response.status_code == HTTP_403_FORBIDDEN
    assert not Product.objects.get(id=product.id).name == "Updated_product"


@pytest.mark.django_db
def test_update_products_anonymous(
        api_client: APIClient,
        create_product: factory.django.DjangoModelFactory,
        create_category: factory.django.DjangoModelFactory,
        create_industry: factory.django.DjangoModelFactory,
        create_vendor: factory.django.DjangoModelFactory,
        create_product_type: factory.django.DjangoModelFactory,
) -> None:
    """
    Test ensure that anonymous users cannot update a product.
    """

    category = create_category.create()
    industry = create_industry.create_batch(2)
    vendor = create_vendor.create()
    product_type = create_product_type.create_batch(2)

    product = create_product.create(category=category, vendor=vendor, is_active=True)

    product.industry.set(industry)
    product.product_type.set(product_type)
    product.save()

    updated_data = {"name": "Updated_product"}

    response = api_client.patch(
        reverse("products-detail", args=[product.id]), updated_data, format="json"
    )

    product = Product.objects.get(id=product.id)
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert not Product.objects.get(id=product.id).name == "Updated_product"


@pytest.mark.django_db
def test_delete_product_staff(
        api_client: APIClient,
        create_product: factory.django.DjangoModelFactory,
        create_category: factory.django.DjangoModelFactory,
        create_industry: factory.django.DjangoModelFactory,
        create_vendor: factory.django.DjangoModelFactory,
        create_product_type: factory.django.DjangoModelFactory,
        create_extra_image: factory.django.DjangoModelFactory,
        create_user: Callable,
) -> None:
    """
    Test that staff users can delete a product.
    """

    user = create_user(is_staff=True)
    api_client.force_authenticate(user=user)

    category = create_category.create()
    industry = create_industry.create_batch(2)
    vendor = create_vendor.create()
    product_type = create_product_type.create_batch(2)

    product = create_product.create(category=category, vendor=vendor, is_active=True)

    product.industry.set(industry)
    product.product_type.set(product_type)
    product.save()

    response = api_client.delete(reverse("products-detail", args=[product.id]))

    assert response.status_code == HTTP_204_NO_CONTENT
    assert not Product.objects.filter(id=product.id).exists()


@pytest.mark.django_db
def test_delete_product_non_staff(
        api_client: APIClient,
        create_product: factory.django.DjangoModelFactory,
        create_category: factory.django.DjangoModelFactory,
        create_industry: factory.django.DjangoModelFactory,
        create_vendor: factory.django.DjangoModelFactory,
        create_product_type: factory.django.DjangoModelFactory,
        create_extra_image: factory.django.DjangoModelFactory,
        create_user: Callable,
) -> None:
    """
    Test that non_staff users cannot delete a product.
    """

    user = create_user()
    api_client.force_authenticate(user=user)

    category = create_category.create()
    industry = create_industry.create_batch(2)
    vendor = create_vendor.create()
    product_type = create_product_type.create_batch(2)

    product = create_product.create(category=category, vendor=vendor, is_active=True)

    product.industry.set(industry)
    product.product_type.set(product_type)
    product.save()

    response = api_client.delete(reverse("products-detail", args=[product.id]))

    assert response.status_code == HTTP_403_FORBIDDEN
    assert Product.objects.filter(id=product.id).exists()


@pytest.mark.django_db
def test_delete_product_non_staff(
        api_client: APIClient,
        create_product: factory.django.DjangoModelFactory,
        create_category: factory.django.DjangoModelFactory,
        create_industry: factory.django.DjangoModelFactory,
        create_vendor: factory.django.DjangoModelFactory,
        create_product_type: factory.django.DjangoModelFactory,
        create_extra_image: factory.django.DjangoModelFactory,
) -> None:
    """
    Test that anonymous users cannot delete a product.
    """

    category = create_category.create()
    industry = create_industry.create_batch(2)
    vendor = create_vendor.create()
    product_type = create_product_type.create_batch(2)

    product = create_product.create(category=category, vendor=vendor, is_active=True)

    product.industry.set(industry)
    product.product_type.set(product_type)
    product.save()

    response = api_client.delete(reverse("products-detail", args=[product.id]))

    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert Product.objects.filter(id=product.id).exists()


@pytest.mark.django_db
def test_get_nonexistent_products(api_client: APIClient):
    """
    Ensure that requesting a non-existent product returns a 404 error.
    """

    response = api_client.get(reverse("products-detail", args=[9999]))
    assert response.status_code == HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_filter_products(
        api_client: APIClient,
        create_product: factory.django.DjangoModelFactory,
        create_category: factory.django.DjangoModelFactory,
        create_industry: factory.django.DjangoModelFactory,
        create_vendor: factory.django.DjangoModelFactory,
        create_product_type: factory.django.DjangoModelFactory,
) -> None:
    """
    Ensure that filtering by category and vendor works correctly.
    """

    category1 = create_category.create()
    category2 = create_category.create()

    vendor1 = create_vendor.create()
    vendor2 = create_vendor.create()

    industry1 = create_industry.create()
    industry2 = create_industry.create()

    product_type1 = create_product_type.create()
    product_type2 = create_product_type.create()

    product1 = create_product.create(
        category=category1, vendor=vendor1, price=50.00, is_active=True
    )
    product2 = create_product.create(
        category=category1, vendor=vendor2, price=150.00, is_active=True
    )
    product3 = create_product.create(
        category=category2, vendor=vendor1, price=300.00, is_active=True
    )
    product4 = create_product.create(
        category=category2, vendor=vendor2, price=500.00, is_active=True
    )

    product1.industry.set([industry1])
    product1.product_type.set([product_type1])

    product2.industry.set([industry2])
    product2.product_type.set([product_type2])

    product3.industry.set([industry1, industry2])
    product3.product_type.set([product_type1, product_type2])

    product4.industry.set([industry2])
    product4.product_type.set([product_type2])

    product1.save()
    product2.save()
    product3.save()
    product4.save()

    # Test filtering by category
    response = api_client.get(
        reverse("products-list"), {"category": category1.id}, format="json"
    )
    assert response.status_code == HTTP_200_OK
    assert response.data["count"] == 2
    for product in response.data["results"]:
        assert product["category_detail"] == category1.name

    # Test filtering by vendor
    response = api_client.get(
        reverse("products-list"), {"vendor": vendor1.id}, format="json"
    )
    assert response.status_code == HTTP_200_OK
    assert response.data["count"] == 2
    for product in response.data["results"]:
        assert product["vendor_detail"] == vendor1.name

    # Test filtering by price range (100 - 400)
    response = api_client.get(
        reverse("products-list"), {"price_min": 100, "price_max": 400}
    )
    assert response.status_code == HTTP_200_OK
    assert response.data["count"] == 2

    # Test filtering by single product type
    response = api_client.get(
        reverse("products-list"), {"product_type": product_type1.id}
    )
    assert response.status_code == HTTP_200_OK
    assert response.data["count"] == 2

    # Test filtering by multiple product types
    response = api_client.get(
        reverse("products-list"), {"product_type": [product_type1.id, product_type2.id]}
    )
    assert response.status_code == HTTP_200_OK
    assert response.data["count"] == 4

    # Test filtering by industry
    response = api_client.get(reverse("products-list"), {"industry": industry1.id})
    assert response.status_code == HTTP_200_OK
    assert response.data["count"] == 2
    for product in response.data["results"]:
        assert industry1.name in product["industry_detail"]

    # Test filtering by multiple industries
    response = api_client.get(
        reverse("products-list"), {"industry": [industry1.id, industry2.id]}
    )
    assert response.status_code == HTTP_200_OK
    assert response.data["count"] == 4

    # Test combination of filters
    response = api_client.get(
        reverse("products-list"),
        {
            "category": category2.id,
            "product_type": product_type2.id,
            "vendor": vendor2.id,
        },
    )
    assert response.status_code == HTTP_200_OK
    assert response.data["count"] == 1

    response = api_client.get(
        reverse("products-list"),
        {
            "category": category2.id,
            "product_type": product_type2.id,
            "vendor": [vendor1.id, vendor2.id],
        },
    )
    assert response.status_code == HTTP_200_OK
    assert response.data["count"] == 2


@pytest.mark.django_db
def test_filter_non_existent_values(
        api_client: APIClient,
        create_product: factory.django.DjangoModelFactory,
        create_category: factory.django.DjangoModelFactory,
        create_industry: factory.django.DjangoModelFactory,
        create_vendor: factory.django.DjangoModelFactory,
        create_product_type: factory.django.DjangoModelFactory,
) -> None:
    """
    Ensure that filtering by non-existent values does not break API and returns an empty list.
    """

    category = create_category.create()
    vendor = create_vendor.create()
    industry = create_industry.create()
    product_type = create_product_type.create()

    product = create_product.create(category=category, vendor=vendor, is_active=True)
    product.industry.set([industry])
    product.product_type.set([product_type])
    product.save()

    nonexistent_category = 9999
    nonexistent_vendor = 8888
    nonexistent_industry = 7777
    nonexistent_product_type = 6666
    nonexistent_price_min = 999999
    nonexistent_price_max = 0.003

    # Test non-existent category
    response = api_client.get(
        reverse("products-list"), {"category": nonexistent_category}
    )
    assert response.status_code == HTTP_200_OK
    assert response.data["results"] == []

    # Test non-existent vendor
    response = api_client.get(reverse("products-list"), {"vendor": nonexistent_vendor})
    assert response.status_code == HTTP_200_OK
    assert response.data["results"] == []

    # Test non-existent industry
    response = api_client.get(
        reverse("products-list"), {"industry": nonexistent_industry}
    )
    assert response.status_code == HTTP_200_OK
    assert response.data["results"] == []

    # Test non-existent product_type
    response = api_client.get(
        reverse("products-list"), {"product_type": nonexistent_product_type}
    )
    assert response.status_code == HTTP_200_OK
    assert response.data["results"] == []

    # Test non-existent prices range
    response = api_client.get(
        reverse("products-list"), {"price_min": nonexistent_price_min}
    )
    assert response.status_code == HTTP_200_OK
    assert response.data["results"] == []

    response = api_client.get(
        reverse("products-list"), {"price_max": nonexistent_price_max}
    )
    assert response.status_code == HTTP_200_OK
    assert response.data["results"] == []

    # Test non-existent category and vendor
    response = api_client.get(
        reverse("products-list"),
        {"category": nonexistent_category, "vendor": nonexistent_vendor},
    )
    assert response.status_code == HTTP_200_OK
    assert response.data["results"] == []

    # Test non-existent category and existent vendor
    response = api_client.get(
        reverse("products-list"),
        {"category": nonexistent_category, "vendor": vendor.id},  # Существующий
    )
    assert response.status_code == HTTP_200_OK
    assert response.data["results"] == []


# Testing Reviews
@pytest.mark.django_db
def test_get_reviews_anonymous(
        api_client: APIClient,
        create_user: Callable,
        create_product: factory.django.DjangoModelFactory,
        create_category: factory.django.DjangoModelFactory,
        create_industry: factory.django.DjangoModelFactory,
        create_vendor: factory.django.DjangoModelFactory,
        create_product_type: factory.django.DjangoModelFactory,
        create_review: factory.django.DjangoModelFactory,
) -> None:
    """
    Test that anonymous users see only moderated reviews.
    """

    owner = create_user()

    category = create_category.create()
    industry = create_industry.create()
    vendor = create_vendor.create()
    product_type = create_product_type.create()

    product = create_product.create(category=category, vendor=vendor, is_active=True)
    product.industry.set(
        [
            industry,
        ]
    )
    product.product_type.set(
        [
            product_type,
        ]
    )

    product2 = create_product.create(category=category, vendor=vendor, is_active=True)
    product2.industry.set(
        [
            industry,
        ]
    )
    product2.product_type.set(
        [
            product_type,
        ]
    )

    product.save()
    product2.save()

    reviews_moderated = create_review.create(
        product=product, user=owner, moderated=True
    )

    reviews_unmoderated = create_review.create(
        product=product2, user=owner, moderated=False
    )

    response = api_client.get(reverse("reviews-list"), format="json")
    assert response.status_code == HTTP_200_OK

    assert response.data["count"] == 1


@pytest.mark.django_db
def test_get_reviews_non_staff(
        api_client: APIClient,
        create_user: Callable,
        create_product: factory.django.DjangoModelFactory,
        create_category: factory.django.DjangoModelFactory,
        create_industry: factory.django.DjangoModelFactory,
        create_vendor: factory.django.DjangoModelFactory,
        create_product_type: factory.django.DjangoModelFactory,
        create_review: factory.django.DjangoModelFactory,
) -> None:
    """
    Test that non-staff users see only moderated reviews.
    The owner can see moderated reviews and their own non-moderated reviews.
    """

    owner = create_user()

    user = create_user(email="user@example.com")
    api_client.force_authenticate(user=user)

    category = create_category.create()
    industry = create_industry.create()
    vendor = create_vendor.create()
    product_type = create_product_type.create()

    product = create_product.create(category=category, vendor=vendor, is_active=True)
    product.industry.set(
        [
            industry,
        ]
    )
    product.product_type.set(
        [
            product_type,
        ]
    )

    product2 = create_product.create(category=category, vendor=vendor, is_active=True)
    product2.industry.set(
        [
            industry,
        ]
    )
    product2.product_type.set(
        [
            product_type,
        ]
    )

    product.save()
    product2.save()

    reviews_moderated = create_review.create(
        product=product, user=owner, moderated=True
    )

    reviews_unmoderated = create_review.create(
        product=product2, user=owner, moderated=False
    )

    response = api_client.get(reverse("reviews-list"), format="json")
    assert response.status_code == HTTP_200_OK
    assert response.data["count"] == 1

    api_client.force_authenticate(user=owner)

    response = api_client.get(reverse("reviews-list"), format="json")
    assert response.status_code == HTTP_200_OK
    assert response.data["count"] == 2


@pytest.mark.django_db
def test_get_reviews_staff(
        api_client: APIClient,
        create_user: Callable,
        create_product: factory.django.DjangoModelFactory,
        create_category: factory.django.DjangoModelFactory,
        create_industry: factory.django.DjangoModelFactory,
        create_vendor: factory.django.DjangoModelFactory,
        create_product_type: factory.django.DjangoModelFactory,
        create_review: factory.django.DjangoModelFactory,
) -> None:
    """
    Test that staff users see only all reviews.
    """

    owner = create_user()

    user = create_user(email="user@example.com", is_staff=True)
    api_client.force_authenticate(user=user)

    category = create_category.create()
    industry = create_industry.create()
    vendor = create_vendor.create()
    product_type = create_product_type.create()

    product = create_product.create(category=category, vendor=vendor, is_active=True)
    product.industry.set(
        [
            industry,
        ]
    )
    product.product_type.set(
        [
            product_type,
        ]
    )

    product2 = create_product.create(category=category, vendor=vendor, is_active=True)
    product2.industry.set(
        [
            industry,
        ]
    )
    product2.product_type.set(
        [
            product_type,
        ]
    )

    product.save()
    product2.save()
    reviews_moderated = create_review.create(
        product=product, user=owner, moderated=True
    )

    reviews_unmoderated = create_review.create(
        product=product2, user=owner, moderated=False
    )

    response = api_client.get(reverse("reviews-list"), format="json")
    assert response.status_code == HTTP_200_OK

    assert response.data["count"] == 2


@pytest.mark.django_db
def test_create_review_anonymous(
        api_client: APIClient,
        create_product: factory.django.DjangoModelFactory,
        create_category: factory.django.DjangoModelFactory,
        create_industry: factory.django.DjangoModelFactory,
        create_vendor: factory.django.DjangoModelFactory,
        create_product_type: factory.django.DjangoModelFactory,
        create_review: factory.django.DjangoModelFactory,
) -> None:
    category = create_category.create()
    industry = create_industry.create()
    vendor = create_vendor.create()
    product_type = create_product_type.create()

    product = create_product.create(category=category, vendor=vendor, is_active=True)

    product.industry.set(
        [
            industry,
        ]
    )
    product.product_type.set(
        [
            product_type,
        ]
    )
    product.save()

    data = {
        "product": product.id,
        "rating": True,
        "comment": "Good product",
        "advantages": "low price",
        "disadvantages": "Low quality",
        "moderated": True,
    }

    response = api_client.post(reverse("reviews-list"), data)
    assert response.status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_create_review_non_staff(
        api_client: APIClient,
        create_user: Callable,
        create_product: factory.django.DjangoModelFactory,
        create_category: factory.django.DjangoModelFactory,
        create_industry: factory.django.DjangoModelFactory,
        create_vendor: factory.django.DjangoModelFactory,
        create_product_type: factory.django.DjangoModelFactory,
        create_review: factory.django.DjangoModelFactory,
) -> None:
    category = create_category.create()
    industry = create_industry.create()
    vendor = create_vendor.create()
    product_type = create_product_type.create()

    product = create_product.create(category=category, vendor=vendor, is_active=True)

    product.industry.set(
        [
            industry,
        ]
    )
    product.product_type.set(
        [
            product_type,
        ]
    )
    product.save()

    user = create_user()
    api_client.force_authenticate(user)

    data = {
        "product": product.id,
        "rating": True,
        "comment": "Good product",
        "advantages": "low price",
        "disadvantages": "Low quality",
        "moderated": True,
    }

    response = api_client.post(reverse("reviews-list"), data)

    assert response.status_code == HTTP_201_CREATED
    assert Review.objects.filter(comment="Good product")
    assert response.data["user"] == user.email


@pytest.mark.django_db
def test_user_cannot_create_duplicate_review(
        api_client: APIClient,
        create_user: Callable,
        create_product: factory.django.DjangoModelFactory,
        create_category: factory.django.DjangoModelFactory,
        create_industry: factory.django.DjangoModelFactory,
        create_vendor: factory.django.DjangoModelFactory,
        create_product_type: factory.django.DjangoModelFactory,
        create_review: factory.django.DjangoModelFactory,
) -> None:
    """
    Ensures that the user can not create duplicate reviews
    """

    category = create_category.create()
    industry = create_industry.create()
    vendor = create_vendor.create()
    product_type = create_product_type.create()

    product = create_product.create(category=category, vendor=vendor, is_active=True)

    product.industry.set(
        [
            industry,
        ]
    )
    product.product_type.set(
        [
            product_type,
        ]
    )
    product.save()

    user = create_user()
    api_client.force_authenticate(user)

    data = {
        "product": product.id,
        "rating": True,
        "comment": "Good product",
        "advantages": "low price",
        "disadvantages": "Low quality",
        "moderated": True,
    }

    response = api_client.post(reverse("reviews-list"), data)
    assert response.status_code == HTTP_201_CREATED

    response2 = api_client.post(reverse("reviews-list"), data)
    assert response2.status_code == HTTP_400_BAD_REQUEST
    assert (
            "You have already left a review for this product."
            in response2.data["non_field_errors"]
    )


@pytest.mark.django_db
def test_update_review_anonymous(
        api_client: APIClient,
        create_user: Callable,
        create_product: factory.django.DjangoModelFactory,
        create_category: factory.django.DjangoModelFactory,
        create_industry: factory.django.DjangoModelFactory,
        create_vendor: factory.django.DjangoModelFactory,
        create_product_type: factory.django.DjangoModelFactory,
        create_review: factory.django.DjangoModelFactory,
) -> None:
    """
    Ensures that the anonymous can not make changes to the review
    """

    category = create_category.create()
    industry = create_industry.create()
    vendor = create_vendor.create()
    product_type = create_product_type.create()

    product = create_product.create(category=category, vendor=vendor, is_active=True)
    product.industry.set(
        [
            industry,
        ]
    )
    product.product_type.set(
        [
            product_type,
        ]
    )

    product.save()

    owner = create_user()

    review_moderated = create_review.create(product=product, user=owner, moderated=True)

    updated_data = {"comment": "Updated_review"}

    response = api_client.patch(
        reverse("reviews-detail", args=[review_moderated.id]),
        updated_data,
        format="json",
    )
    assert response.status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_update_review_non_staff_non_owner(
        api_client: APIClient,
        create_user: Callable,
        create_product: factory.django.DjangoModelFactory,
        create_category: factory.django.DjangoModelFactory,
        create_industry: factory.django.DjangoModelFactory,
        create_vendor: factory.django.DjangoModelFactory,
        create_product_type: factory.django.DjangoModelFactory,
        create_review: factory.django.DjangoModelFactory,
) -> None:
    """
    Test that a non staff and a not owner user can't update a review instance
    """

    category = create_category.create()
    industry = create_industry.create()
    vendor = create_vendor.create()
    product_type = create_product_type.create()

    product = create_product.create(category=category, vendor=vendor, is_active=True)

    product.industry.set(
        [
            industry,
        ]
    )
    product.product_type.set(
        [
            product_type,
        ]
    )
    product.save()

    owner = create_user()
    user = create_user(email="Example2@example.com")
    api_client.force_authenticate(user)

    review_moderated = create_review.create(product=product, user=owner, moderated=True)

    updated_data = {"comment": "Updated_review"}

    response = api_client.patch(
        reverse("reviews-detail", args=[review_moderated.id]),
        updated_data,
        format="json",
    )
    assert response.status_code == HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_update_review_owner(
        api_client: APIClient,
        create_user: Callable,
        create_product: factory.django.DjangoModelFactory,
        create_category: factory.django.DjangoModelFactory,
        create_industry: factory.django.DjangoModelFactory,
        create_vendor: factory.django.DjangoModelFactory,
        create_product_type: factory.django.DjangoModelFactory,
        create_review: factory.django.DjangoModelFactory,
) -> None:
    """
    Test that an owner can successfully update a non_moderated_review instance and
    can't update moderated reviews
    """
    category = create_category.create()
    industry = create_industry.create()
    vendor = create_vendor.create()
    product_type = create_product_type.create()

    product = create_product.create(category=category, vendor=vendor, is_active=True)

    product.industry.set(
        [
            industry,
        ]
    )
    product.product_type.set(
        [
            product_type,
        ]
    )

    product2 = create_product.create(category=category, vendor=vendor, is_active=True)

    product2.industry.set(
        [
            industry,
        ]
    )
    product2.product_type.set(
        [
            product_type,
        ]
    )

    product.save()
    product2.save()

    owner = create_user()
    api_client.force_authenticate(owner)

    review_unmoderated = create_review.create(
        product=product, user=owner, moderated=False
    )

    review_moderated = create_review.create(
        product=product2, user=owner, moderated=True
    )

    updated_data = {"comment": "Updated_review"}

    api_client.force_authenticate(owner)

    # Ensure, that owner can not update the moderated review
    response = api_client.patch(
        reverse("reviews-detail", args=[review_moderated.id]),
        updated_data,
        format="json",
    )
    assert response.status_code == HTTP_403_FORBIDDEN
    review_moderated.refresh_from_db()
    assert review_moderated.comment != "Updated_review"

    # Ensure, that owner can update the unmoderated review
    response = api_client.patch(
        reverse("reviews-detail", args=[review_unmoderated.id]),
        updated_data,
        format="json",
    )

    assert response.status_code == HTTP_200_OK
    review_unmoderated.refresh_from_db()
    assert review_unmoderated.comment == "Updated_review"


@pytest.mark.django_db
def test_update_review_staff(
        api_client: APIClient,
        create_user: Callable,
        create_product: factory.django.DjangoModelFactory,
        create_category: factory.django.DjangoModelFactory,
        create_industry: factory.django.DjangoModelFactory,
        create_vendor: factory.django.DjangoModelFactory,
        create_product_type: factory.django.DjangoModelFactory,
        create_review: factory.django.DjangoModelFactory,
) -> None:
    """
    Test that a staff can successfully update any review instance
    """
    category = create_category.create()
    industry = create_industry.create()
    vendor = create_vendor.create()
    product_type = create_product_type.create()

    product = create_product.create(category=category, vendor=vendor, is_active=True)

    product.industry.set(
        [
            industry,
        ]
    )
    product.product_type.set(
        [
            product_type,
        ]
    )

    product2 = create_product.create(category=category, vendor=vendor, is_active=True)

    product2.industry.set(
        [
            industry,
        ]
    )
    product2.product_type.set(
        [
            product_type,
        ]
    )

    product.save()
    product2.save()

    owner = create_user()
    user = create_user(email="new_staff", is_staff=True)

    api_client.force_authenticate(user)

    review_unmoderated = create_review.create(
        product=product, user=owner, moderated=False
    )

    review_moderated = create_review.create(
        product=product2, user=owner, moderated=True
    )

    updated_data = {"comment": "Updated_review"}

    # Ensure, that the staff can update unmoderated reviews
    response = api_client.patch(
        reverse("reviews-detail", args=[review_unmoderated.id]),
        updated_data,
        format="json",
    )

    assert response.status_code == HTTP_200_OK
    review_unmoderated.refresh_from_db()
    assert review_unmoderated.comment == "Updated_review"

    # Ensure, that staff can update moderated review
    response = api_client.patch(
        reverse("reviews-detail", args=[review_moderated.id]),
        updated_data,
        format="json",
    )

    assert response.status_code == HTTP_200_OK
    review_moderated.refresh_from_db()
    assert review_unmoderated.comment == "Updated_review"


@pytest.mark.django_db
def test_delete_review_anonymous(
        api_client: APIClient,
        create_user: Callable,
        create_product: factory.django.DjangoModelFactory,
        create_category: factory.django.DjangoModelFactory,
        create_industry: factory.django.DjangoModelFactory,
        create_vendor: factory.django.DjangoModelFactory,
        create_product_type: factory.django.DjangoModelFactory,
        create_review: factory.django.DjangoModelFactory,
) -> None:
    category = create_category.create()
    industry = create_industry.create()
    vendor = create_vendor.create()
    product_type = create_product_type.create()

    product = create_product.create(category=category, vendor=vendor, is_active=True)

    product.industry.set(
        [
            industry,
        ]
    )
    product.product_type.set(
        [
            product_type,
        ]
    )
    product.save()

    owner = create_user()

    review_moderated = create_review.create(product=product, user=owner, moderated=True)

    response = api_client.delete(
        reverse("reviews-detail", args=[review_moderated.id]), format="json"
    )
    assert response.status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_delete_review_non_staff_non_owner(
        api_client: APIClient,
        create_user: Callable,
        create_product: factory.django.DjangoModelFactory,
        create_category: factory.django.DjangoModelFactory,
        create_industry: factory.django.DjangoModelFactory,
        create_vendor: factory.django.DjangoModelFactory,
        create_product_type: factory.django.DjangoModelFactory,
        create_review: factory.django.DjangoModelFactory,
) -> None:
    """
    Test that a non staff can not delete a review instance
    """

    category = create_category.create()
    industry = create_industry.create()
    vendor = create_vendor.create()
    product_type = create_product_type.create()

    product = create_product.create(category=category, vendor=vendor, is_active=True)

    product.industry.set(
        [
            industry,
        ]
    )
    product.product_type.set(
        [
            product_type,
        ]
    )
    product.save()

    owner = create_user()
    user = create_user(email="Example2@example.com")
    api_client.force_authenticate(user)

    review_moderated = create_review.create(product=product, user=owner, moderated=True)

    response = api_client.delete(
        reverse("reviews-detail", args=[review_moderated.id]), format="json"
    )
    assert response.status_code == HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_delete_review_owner(
        api_client: APIClient,
        create_user: Callable,
        create_product: factory.django.DjangoModelFactory,
        create_category: factory.django.DjangoModelFactory,
        create_industry: factory.django.DjangoModelFactory,
        create_vendor: factory.django.DjangoModelFactory,
        create_product_type: factory.django.DjangoModelFactory,
        create_review: factory.django.DjangoModelFactory,
) -> None:
    """
    Test that an owner can not delete a review
    """
    category = create_category.create()
    industry = create_industry.create()
    vendor = create_vendor.create()
    product_type = create_product_type.create()

    product = create_product.create(category=category, vendor=vendor, is_active=True)

    product.industry.set(
        [
            industry,
        ]
    )
    product.product_type.set(
        [
            product_type,
        ]
    )

    product2 = create_product.create(category=category, vendor=vendor, is_active=True)

    product2.industry.set(
        [
            industry,
        ]
    )
    product2.product_type.set(
        [
            product_type,
        ]
    )

    product.save()
    product2.save()

    owner = create_user()
    api_client.force_authenticate(owner)

    review_unmoderated = create_review.create(
        product=product, user=owner, moderated=False
    )

    review_moderated = create_review.create(
        product=product2, user=owner, moderated=True
    )

    api_client.force_authenticate(owner)

    # Ensure, that owner can not delete the moderated review
    response = api_client.delete(
        reverse("reviews-detail", args=[review_moderated.id]), format="json"
    )
    assert response.status_code == HTTP_403_FORBIDDEN

    # Ensure, that owner can not delete the unmoderated review
    response = api_client.delete(
        reverse("reviews-detail", args=[review_unmoderated.id]), format="json"
    )

    assert response.status_code == HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_delete_review_staff(
        api_client: APIClient,
        create_user: Callable,
        create_product: factory.django.DjangoModelFactory,
        create_category: factory.django.DjangoModelFactory,
        create_industry: factory.django.DjangoModelFactory,
        create_vendor: factory.django.DjangoModelFactory,
        create_product_type: factory.django.DjangoModelFactory,
        create_review: factory.django.DjangoModelFactory,
) -> None:
    """
    Test that a staff can successfully delete any review instance
    """
    category = create_category.create()
    industry = create_industry.create()
    vendor = create_vendor.create()
    product_type = create_product_type.create()

    product = create_product.create(category=category, vendor=vendor, is_active=True)

    product.industry.set(
        [
            industry,
        ]
    )
    product.product_type.set(
        [
            product_type,
        ]
    )

    product2 = create_product.create(category=category, vendor=vendor, is_active=True)

    product2.industry.set(
        [
            industry,
        ]
    )
    product2.product_type.set(
        [
            product_type,
        ]
    )

    product.save()
    product2.save()

    owner = create_user()
    user = create_user(email="new_staff", is_staff=True)

    api_client.force_authenticate(user)

    review_unmoderated = create_review.create(
        product=product, user=owner, moderated=False
    )

    review_moderated = create_review.create(
        product=product2, user=owner, moderated=True
    )

    # Ensure, that the staff can delete unmoderated reviews
    response = api_client.delete(
        reverse("reviews-detail", args=[review_unmoderated.id]), format="json"
    )

    assert response.status_code == HTTP_204_NO_CONTENT

    # Ensure, that staff can delete moderated review
    response = api_client.delete(
        reverse("reviews-detail", args=[review_moderated.id]), format="json"
    )

    assert response.status_code == HTTP_204_NO_CONTENT
