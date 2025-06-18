from decimal import Decimal
from typing import Callable

import factory.django
import pytest
from django.urls import reverse
from rest_framework.status import (HTTP_200_OK, HTTP_400_BAD_REQUEST,
                                   HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND)
from rest_framework.test import APIClient

from store.tests.conftest import (create_category, create_industry,
                                  create_product, create_product_type,
                                  create_vendor)
from users.tests.conftest import create_user

from ..models import CartItem


# GET
@pytest.mark.django_db
def test_anonymous_user_cannot_access_cart(api_client: APIClient) -> None:
    """
    Ensure that an unauthenticated user cannot retrieve the cart.
    The API should return 401 Unauthorized.
    """
    response = api_client.get(reverse("cart-get-user-cart"), format="json")

    assert response.status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_authenticated_user_without_cart_receives_404(
    api_client: APIClient, create_user: Callable
) -> None:
    """
    Ensure that an authenticated user who does not have a cart
    receives a 404 Not Found response.
    """
    user = create_user(email="w@w.com.ua")

    api_client.force_authenticate(user)
    response = api_client.get(reverse("cart-get-user-cart"), format="json")

    assert response.status_code == HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_authenticated_user_can_retrieve_cart(
    api_client: APIClient,
    create_user: Callable,
    create_cart: factory.django.DjangoModelFactory,
) -> None:
    """
    Ensure that an authenticated user with an existing cart
    can successfully retrieve their cart.
    """
    user = create_user()
    cart = create_cart.create(user=user)

    api_client.force_authenticate(user)
    response = api_client.get(reverse("cart-get-user-cart"), format="json")

    assert response.status_code == HTTP_200_OK


# POST
@pytest.mark.django_db
def test_anonymous_user_cannot_add_product_to_cart(api_client: APIClient) -> None:
    """
    Ensure that an unauthenticated user cannot add a product to the cart.
    The API should return 401 Unauthorized.
    """
    data = {"product": 12}

    response = api_client.post(reverse("cart-add-item"), data=data, format="json")

    assert response.status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_authenticated_user_can_add_products_to_cart(
    api_client: APIClient,
    create_user: Callable,
    create_category: Callable,
    create_industry: Callable,
    create_product_type: Callable,
    create_vendor: Callable,
    create_product: Callable,
    create_cart: factory.django.DjangoModelFactory,
) -> None:
    """
    Ensure that an authenticated user can successfully add products to the cart.
    The test verifies that:
    - A single product is added correctly.
    - A second product with a specified quantity is added correctly.
    - The cart contains the expected number of items.
    """
    user = create_user()

    # Create necessary related objects
    category = create_category.create()
    industry = create_industry.create()
    vendor = create_vendor.create()
    product_type = create_product_type.create()

    # Create two active products
    product_1 = create_product.create(category=category, vendor=vendor, is_active=True)
    product_2 = create_product.create(category=category, vendor=vendor, is_active=True)

    # Associate products with industry and product type
    product_1.industry.set([industry])
    product_1.product_type.set([product_type])
    product_1.save()

    product_2.industry.set([industry])
    product_2.product_type.set([product_type])
    product_2.save()

    # Authenticate user
    api_client.force_authenticate(user=user)

    # First product addition
    data_1 = {"product_id": product_1.id}
    response = api_client.post(reverse("cart-add-item"), data=data_1, format="json")

    assert response.status_code == HTTP_200_OK
    assert len(response.data["items"]) == 1
    assert response.data["items"][0]["product_name"] == product_1.name
    assert response.data["items"][0]["quantity"] == 1

    # Second product addition with specified quantity
    data_2 = {"product_id": product_2.id, "quantity": 10}
    response = api_client.post(reverse("cart-add-item"), data=data_2, format="json")

    assert response.status_code == HTTP_200_OK
    assert len(response.data["items"]) == 2
    assert response.data["items"][0]["product_name"] == product_1.name
    assert response.data["items"][0]["quantity"] == 1
    assert response.data["items"][1]["product_name"] == product_2.name
    assert response.data["items"][1]["quantity"] == 10


@pytest.mark.django_db
def test_authenticated_user_can_increment_product_quantity_in_cart(
    api_client: APIClient,
    create_user: Callable,
    create_category: Callable,
    create_industry: Callable,
    create_product_type: Callable,
    create_vendor: Callable,
    create_product: Callable,
    create_cart: factory.django.DjangoModelFactory,
) -> None:
    """
    Ensure that when an authenticated user adds the same product to the cart again,
    the quantity of that product increases instead of creating a duplicate entry.
    - Initially, the product is added with quantity = 1.
    - When added again, the quantity should increase to 2.
    - The total price should reflect the updated quantity.
    """
    user = create_user()

    # Create necessary related objects
    category = create_category.create()
    industry = create_industry.create()
    vendor = create_vendor.create()
    product_type = create_product_type.create()

    # Create an active product
    product = create_product.create(category=category, vendor=vendor, is_active=True)

    # Associate product with industry and product type
    product.industry.set([industry])
    product.product_type.set([product_type])
    product.save()

    # Authenticate user
    api_client.force_authenticate(user=user)

    data = {"product_id": product.id}

    # First addition to cart
    response = api_client.post(reverse("cart-add-item"), data=data, format="json")

    assert response.status_code == HTTP_200_OK
    assert len(response.data["items"]) == 1
    assert response.data["items"][0]["product_name"] == product.name
    assert response.data["items"][0]["quantity"] == 1
    assert Decimal(response.data["items"][0]["total_price"]) == product.price
    assert Decimal(response.data["total_price"]) == product.price

    # Adding the same product again
    response = api_client.post(reverse("cart-add-item"), data=data, format="json")

    assert response.status_code == HTTP_200_OK
    assert (
        len(response.data["items"]) == 1
    )  # Product should not be duplicated, only quantity increases
    assert response.data["items"][0]["product_name"] == product.name
    assert response.data["items"][0]["quantity"] == 2
    assert Decimal(response.data["items"][0]["total_price"]) == product.price * 2
    assert Decimal(response.data["total_price"]) == product.price * 2


@pytest.mark.django_db
def test_authenticated_user_cannot_add_inactive_product_to_cart(
    api_client: APIClient,
    create_user: Callable,
    create_category: Callable,
    create_industry: Callable,
    create_product_type: Callable,
    create_vendor: Callable,
    create_product: Callable,
) -> None:
    """
    Ensure that an authenticated user cannot add an inactive (is_active=False) product to the cart.
    The API should return 400 Bad Request.
    """
    user = create_user()

    # Create necessary related objects
    category = create_category.create()
    industry = create_industry.create()
    vendor = create_vendor.create()
    product_type = create_product_type.create()

    # Create an inactive product
    inactive_product = create_product.create(
        category=category, vendor=vendor, is_active=False
    )

    # Associate product with industry and product type
    inactive_product.industry.set([industry])
    inactive_product.product_type.set([product_type])
    inactive_product.save()

    # Authenticate user
    api_client.force_authenticate(user=user)

    data = {"product_id": inactive_product.id}

    # Attempt to add an inactive product to the cart
    response = api_client.post(reverse("cart-add-item"), data=data, format="json")
    assert response.status_code == HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_authenticated_user_cannot_add_nonexistent_product_to_cart(
    api_client: APIClient, create_user: Callable
) -> None:
    """
    Ensure that an authenticated user cannot add a nonexistent product to the cart.
    The API should return 404 NOT FOUND.
    """
    user = create_user()

    # Authenticate user
    api_client.force_authenticate(user=user)

    # Attempt to add a product with a non-existent ID
    data = {"product_id": 12}

    response = api_client.post(reverse("cart-add-item"), data=data, format="json")

    assert response.status_code == HTTP_404_NOT_FOUND


# PATCH
@pytest.mark.django_db
def test_anonymous_user_cannot_update_cart_item_quantity(api_client: APIClient) -> None:
    """
    Ensure that an unauthenticated user cannot update the quantity of a cart item.
    The API should return 401 Unauthorized.
    """
    data = {"product_id": 12, "quantity": 12}

    response = api_client.patch(reverse("cart-update-item"), data=data, format="json")

    assert response.status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_authenticated_user_can_update_cart_item_quantity(
    api_client: APIClient,
    create_user: Callable,
    create_category: Callable,
    create_industry: Callable,
    create_product_type: Callable,
    create_vendor: Callable,
    create_product: Callable,
    create_cart: factory.django.DjangoModelFactory,
) -> None:
    """
    Ensure that an authenticated user can update the quantity of an existing product in the cart.
    - Initially, the product is added with the default quantity of 1.
    - The quantity is updated to 5 using a PATCH request.
    - The updated quantity should reflect correctly in the response.
    """
    user = create_user()

    # Create necessary related objects
    category = create_category.create()
    industry = create_industry.create()
    vendor = create_vendor.create()
    product_type = create_product_type.create()

    # Create an active product
    product = create_product.create(category=category, vendor=vendor, is_active=True)

    # Associate product with industry and product type
    product.industry.set([industry])
    product.product_type.set([product_type])
    product.save()

    # Authenticate user
    api_client.force_authenticate(user=user)

    # Create an active cart
    cart = create_cart.create(user=user, status="active")

    # Data for adding and updating the product in the cart
    add_data = {"product_id": product.id}
    update_data = {"product_id": product.id, "quantity": 5}

    # Add product to cart
    response = api_client.post(reverse("cart-add-item"), data=add_data, format="json")

    assert response.status_code == HTTP_200_OK

    # Update the product quantity in the cart
    response = api_client.patch(
        reverse("cart-update-item"), data=update_data, format="json"
    )

    assert response.status_code == HTTP_200_OK
    assert response.data["items"][0]["product_name"] == product.name
    assert response.data["items"][0]["quantity"] == 5


@pytest.mark.django_db
def test_authenticated_user_cannot_update_inactive_product_in_cart(
    api_client: APIClient,
    create_user: Callable,
    create_category: Callable,
    create_industry: Callable,
    create_product_type: Callable,
    create_vendor: Callable,
    create_product: Callable,
    create_cart: factory.django.DjangoModelFactory,
) -> None:
    """
    Ensure that an authenticated user cannot update the quantity of a product in the cart if it is inactive.
    - The inactive product is initially added to the cart.
    - A PATCH request is sent to update the product.
    - The API should return 400 Bad Request.
    """
    user = create_user()

    # Create necessary related objects
    category = create_category.create()
    industry = create_industry.create()
    vendor = create_vendor.create()
    product_type = create_product_type.create()

    # Create an inactive product
    inactive_product = create_product.create(
        category=category, vendor=vendor, is_active=False
    )

    # Associate product with industry and product type
    inactive_product.industry.set([industry])
    inactive_product.product_type.set([product_type])
    inactive_product.save()

    # Create an active cart and add inactive product
    cart = create_cart.create(user=user, status="active")
    CartItem.objects.create(cart=cart, product=inactive_product, quantity=1)

    # Authenticate user
    api_client.force_authenticate(user=user)

    # Attempt to update quantity of an inactive product
    data = {"product_id": inactive_product.id}

    response = api_client.patch(reverse("cart-update-item"), data=data, format="json")

    assert response.status_code == HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_authenticated_user_cannot_update_nonexistent_product_quantity(
    api_client: APIClient, create_user: Callable
) -> None:
    """
    Ensure that an authenticated user cannot update the quantity of a product that does not exist.
    - A PATCH request is sent with a non-existent product ID.
    - The API should return 404 Not Found.
    """
    user = create_user()

    # Authenticate user
    api_client.force_authenticate(user=user)

    # Attempt to update quantity for a non-existent product (ID = 15)
    data = {"product_id": 15, "quantity": 16}

    response = api_client.patch(reverse("cart-update-item"), data=data, format="json")
    assert response.status_code == HTTP_404_NOT_FOUND


# DELETE
@pytest.mark.django_db
def test_anonymous_user_cannot_delete_product_from_cart(api_client: APIClient) -> None:
    """
    Ensure that an unauthenticated user cannot remove a product from the cart.
    The API should return 401 Unauthorized.
    """
    data = {"product_id": 12, "quantity": 12}

    response = api_client.delete(reverse("cart-remove-item"), data=data, format="json")

    assert response.status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_authenticated_user_can_delete_product_from_cart(
    api_client: APIClient,
    create_user: Callable,
    create_category: Callable,
    create_industry: Callable,
    create_product_type: Callable,
    create_vendor: Callable,
    create_product: Callable,
    create_cart: factory.django.DjangoModelFactory,
) -> None:
    """
    Ensure that an authenticated user can successfully remove a product from the cart.
    - A product is added to the cart.
    - A DELETE request is sent to remove the product.
    - The product should be removed, and the response should reflect an empty cart.
    """
    user = create_user()

    # Create necessary related objects
    category = create_category.create()
    industry = create_industry.create()
    vendor = create_vendor.create()
    product_type = create_product_type.create()

    # Create an active product
    product = create_product.create(category=category, vendor=vendor, is_active=True)

    # Associate product with industry and product type
    product.industry.set([industry])
    product.product_type.set([product_type])
    product.save()

    # Authenticate user
    api_client.force_authenticate(user=user)

    # Create an active cart and add product
    cart = create_cart.create(user=user, status="active")
    CartItem.objects.create(cart=cart, product=product, quantity=1)

    # Attempt to remove the product from the cart
    data = {"product_id": product.id}

    response = api_client.delete(reverse("cart-remove-item"), data=data, format="json")
    assert response.status_code == HTTP_200_OK

    # Refresh cart and verify product removal
    cart.refresh_from_db()
    assert CartItem.objects.filter(cart=cart, product=product).count() == 0
    assert len(response.data["items"]) == 0


@pytest.mark.django_db
def test_authenticated_user_cannot_delete_nonexistent_product_from_cart(
    api_client: APIClient,
    create_user: Callable,
    create_cart: factory.django.DjangoModelFactory,
) -> None:
    """
    Ensure that an authenticated user cannot delete a product from the cart if the product does not exist.
    - A DELETE request is sent with a non-existent product ID.
    - The API should return 404 Not Found.
    """
    user = create_user()

    # Authenticate user
    api_client.force_authenticate(user=user)

    # Create an active cart for the user
    cart = create_cart.create(user=user, status="active")

    # Attempt to remove a non-existent product from the cart
    data = {"product_id": 1}  # Assuming product ID 1 does not exist

    response = api_client.delete(reverse("cart-remove-item"), data=data, format="json")
    assert response.status_code == HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_anonymous_user_cannot_delete_product_from_cart(
    api_client: APIClient,
    create_user: Callable,
    create_category: Callable,
    create_industry: Callable,
    create_product_type: Callable,
    create_vendor: Callable,
    create_product: Callable,
    create_cart: factory.django.DjangoModelFactory,
) -> None:
    """
    Ensure that an unauthenticated user cannot delete a product from the cart.
    - A product is added to the cart.
    - An unauthenticated DELETE request is sent to remove the product.
    - The API should return 401 Unauthorized.
    """
    user = create_user()

    # Create an active cart for the user
    cart = create_cart.create(user=user, status="active")

    # Create necessary related objects
    category = create_category.create()
    industry = create_industry.create()
    vendor = create_vendor.create()
    product_type = create_product_type.create()

    # Create an active product
    product = create_product.create(category=category, vendor=vendor, is_active=True)

    # Associate product with industry and product type
    product.industry.set([industry])
    product.product_type.set([product_type])
    product.save()

    # Add product to the cart
    CartItem.objects.create(cart=cart, product=product, quantity=1)

    # Attempt to remove the product from the cart as an anonymous user
    data = {"product_id": product.id}

    response = api_client.delete(reverse("cart-remove-item"), data=data, format="json")

    assert response.status_code == HTTP_401_UNAUTHORIZED
