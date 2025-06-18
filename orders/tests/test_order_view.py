import logging

import pytest
from django.urls import reverse
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED,
                                   HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED,
                                   HTTP_404_NOT_FOUND)
from rest_framework.test import APIClient

from cart.models import Cart
from cart.tests.conftest import create_cart, create_cart_item
from delivery.models import CarrierChoices, Delivery
from delivery.tests.conftest import create_address, create_area, create_city
from store.tests.conftest import (create_category, create_industry,
                                  create_product, create_product_type,
                                  create_vendor)
from users.tests.conftest import create_user

logger = logging.getLogger("project")


# Testing GET Methods
@pytest.mark.django_db
def test_anonymous_user_cannot_access_cart(api_client: APIClient) -> None:
    """
    Ensure that an unauthenticated user cannot get the order list.
    The API should return 401 Unauthorized.
    """

    response = api_client.get(reverse("orders-list"), format="json")
    assert response.status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_authenticate_owner_can_get_orders_list(
    api_client,
    create_user,
    create_product,
    create_product_type,
    create_vendor,
    create_industry,
    create_category,
    create_order,
    create_order_item,
) -> None:
    """
    Ensure that the user can get the orders list
    """

    user = create_user()

    # Create necessary related objects
    category = create_category.create()
    industry = create_industry.create()
    vendor = create_vendor.create()
    product_type = create_product_type.create()

    # Create two active products
    product_1 = create_product.create(
        category=category, vendor=vendor, is_active=True, price=10
    )
    product_2 = create_product.create(
        category=category, vendor=vendor, is_active=True, price=20
    )

    # Associate products with industry and product type
    product_1.industry.set([industry])
    product_1.product_type.set([product_type])
    product_1.save()

    product_2.industry.set([industry])
    product_2.product_type.set([product_type])
    product_2.save()

    order_1 = create_order.create(user=user, status="pending")
    order_2 = create_order.create(user=user, status="shipped")

    order_item_1 = create_order_item.create(
        order=order_1, product=product_1, quantity=2
    )
    order_item_2 = create_order_item.create(
        order=order_1, product=product_2, quantity=3
    )

    order_item_1 = create_order_item.create(
        order=order_2, product=product_1, quantity=2
    )
    order_item_2 = create_order_item.create(
        order=order_2, product=product_2, quantity=3
    )
    api_client.force_authenticate(user=user)
    response = api_client.get(reverse("orders-list"), format="json")

    assert response.status_code == HTTP_200_OK
    assert len(response.data) == 2

    statuses: set[str] = {order["status"] for order in response.data}
    assert statuses == {"pending", "shipped"}

    required_fields: set[str] = {"id", "user", "status", "total_price", "items"}
    for order in response.data:
        assert required_fields.issubset(order.keys())

    for order in response.data:
        assert len(order["items"]) > 0
        for item in order["items"]:
            assert "product_name" in item
            assert "quantity" in item
            assert "total_price" in item


@pytest.mark.django_db
def test_authenticate_user_cannot_access_another_users_orders(
    api_client,
    create_user,
    create_product,
    create_product_type,
    create_vendor,
    create_industry,
    create_category,
    create_order,
    create_order_item,
) -> None:
    """
    Ensure that the user receives only their own orders list.
    """

    user = create_user()
    user_1 = create_user(email="user_1@example.com")

    # Create necessary related objects
    category = create_category.create()
    industry = create_industry.create()
    vendor = create_vendor.create()
    product_type = create_product_type.create()

    # Create active product
    product_1 = create_product.create(
        category=category, vendor=vendor, is_active=True, price=10
    )

    # Associate products with industry and product type
    product_1.industry.set([industry])
    product_1.product_type.set([product_type])
    product_1.save()

    order_1 = create_order.create(user=user, status="pending")
    order_2 = create_order.create(user=user_1, status="shipping")

    order_item_1 = create_order_item.create(
        order=order_1, product=product_1, quantity=2
    )

    order_item_1 = create_order_item.create(
        order=order_2, product=product_1, quantity=2
    )

    api_client.force_authenticate(user=user_1)

    response = api_client.get(reverse("orders-list"), format="json")
    assert response.status_code == HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["id"] == order_2.id


@pytest.mark.django_db
def test_user_can_get_own_order_detail(
    api_client,
    create_user,
    create_order,
    create_order_item,
    create_category,
    create_product,
    create_industry,
    create_product_type,
    create_vendor,
):
    """
    Test that an authenticated user can retrieve the details of their own order.
    """

    user = create_user()

    category = create_category.create()
    industry = create_industry.create()
    vendor = create_vendor.create()
    product_type = create_product_type.create()

    product = create_product.create(
        category=category, vendor=vendor, is_active=True, price=10
    )

    product.industry.set([industry])
    product.product_type.set([product_type])
    product.save()

    order = create_order.create(user=user)
    create_order_item.create(order=order, product=product, quantity=10)

    api_client.force_authenticate(user)

    response = api_client.get(reverse("orders-detail", kwargs={"pk": order.id}))
    assert response.status_code == HTTP_200_OK
    assert response.data["id"] == order.id
    assert response.data["user"] == user.email


@pytest.mark.django_db
def test_user_cannot_get_other_users_order_detail(
    api_client, create_user, create_order
):
    """
    Test that a user cannot retrieve the details of another user's order.
    """

    owner = create_user()
    user = create_user(email="user_1@example.com")

    order = create_order.create(user=owner, status="pending")

    api_client.force_authenticate(user)

    response = api_client.get(reverse("orders-detail", kwargs={"pk": order.id}))
    assert response.status_code == HTTP_404_NOT_FOUND


# Testing POST Methods
@pytest.mark.django_db
def test_authenticate_user_can_create_orders(
    api_client: APIClient,
    create_user,
    create_product,
    create_product_type,
    create_vendor,
    create_industry,
    create_category,
    create_cart,
    create_cart_item,
    create_order,
    create_area,
    create_city,
    create_address,
) -> None:
    """
    Ensure that an authenticated user can create order and delivery.
    The API should return the order lists.
    """
    # logger.info(f"Starting logging")
    user = create_user()

    # Create necessary related objects
    category = create_category.create()
    industry = create_industry.create()
    vendor = create_vendor.create()
    product_type = create_product_type.create()

    # Create two active products
    product_1 = create_product.create(
        category=category, vendor=vendor, is_active=True, price=10
    )
    product_2 = create_product.create(
        category=category, vendor=vendor, is_active=True, price=20
    )

    # Associate products with industry and product type
    product_1.industry.set([industry])
    product_1.product_type.set([product_type])
    product_1.save()

    product_2.industry.set([industry])
    product_2.product_type.set([product_type])
    product_2.save()

    # Create cart
    cart_active = Cart.objects.create(user=user, status="active")

    # Create cart items
    cart_item_1 = create_cart_item.create(
        cart=cart_active, product=product_1, quantity=2
    )
    cart_item_2 = create_cart_item.create(
        cart=cart_active, product=product_2, quantity=2
    )

    # Create delivery address
    area = create_area(name="Lvivska")
    city = create_city(name="Lviv", area=area)
    carrier = CarrierChoices.PICKUP
    address = create_address(city=city, carrier=carrier)

    data = {"delivery_address_id": address.id}

    api_client.force_authenticate(user=user)
    response = api_client.post(reverse("orders-list"), data, format="json")

    assert response.status_code == HTTP_201_CREATED
    assert response.data["user"] == user.email
    assert response.data["status"] == "pending"

    cart_items = cart_active.items.select_related("product").order_by("product__name")
    response_items = sorted(response.data["items"], key=lambda x: x["product_name"])
    for cart_item, response_item in zip(cart_items, response_items):
        assert cart_item.product.name == response_item["product_name"]
        assert cart_item.quantity == response_item["quantity"]
        assert float(cart_item.product.price) == float(response_item["product_price"])

    assert cart_active.get_total_price() == response.data["total_price"]

    cart_active.refresh_from_db()
    assert cart_active.status == "ordered"

    order_id = response.data["id"]
    deliveries = Delivery.objects.filter(order_id=order_id)

    assert deliveries.count() == 1
    delivery = deliveries.first()
    assert delivery.delivery_address_id == address.id


@pytest.mark.django_db
def test_anonymous_cannot_create_orders(api_client: APIClient):
    """
    Ensure that an anonymous user cannot create an order.
    The API should return 401 Unauthorized.
    """

    response = api_client.post(reverse("orders-list"))
    assert response.status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_authenticated_user_cannot_create_order_without_cart(
    api_client: APIClient, create_user, create_area, create_city, create_address
):
    """
    Ensure that an authenticated user cannot create an order without an active cart.
    """

    user = create_user()

    area = create_area()
    city = create_city(area=area)
    address = create_address(city=city, carrier=CarrierChoices.PICKUP)

    api_client.force_authenticate(user=user)
    response = api_client.post(
        reverse("orders-list"), {"delivery_address_id": address.id}, format="json"
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert "Cart is empty or doesn't exist" in response.data["error"]


@pytest.mark.django_db
def test_authenticated_user_cannot_create_order_with_empty_cart(
    api_client, create_user, create_cart, create_area, create_city, create_address
):
    """
    Ensure that an authenticated user cannot create an order with an empty cart.
    """

    user = create_user()
    cart = create_cart.create(user=user, status="active")

    area = create_area()
    city = create_city(area=area)
    address = create_address(city=city, carrier=CarrierChoices.PICKUP)

    api_client.force_authenticate(user=user)
    response = api_client.post(
        reverse("orders-list"), {"delivery_address_id": address.id}, format="json"
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert "Cart is empty or doesn't exist" in response.data["error"]


# Testing PATCH Methods
@pytest.mark.django_db
def test_authenticated_user_can_cancel_pending_and_paid_order(
    api_client, create_user, create_order, create_order_item
) -> None:
    """
    Test that an authenticated user can cancel orders with 'pending' or 'paid' status.
    """

    user = create_user()

    order_pending = create_order.create(user=user)
    order_paid = create_order.create(user=user, status="paid")

    api_client.force_authenticate(user)

    data = {"status": "canceled"}

    response = api_client.patch(
        reverse("orders-detail", kwargs={"pk": order_pending.id}),
        data=data,
        format="json",
    )
    assert response.status_code == HTTP_200_OK
    assert response.data["status"] == "canceled"

    response = api_client.patch(
        reverse("orders-detail", kwargs={"pk": order_paid.id}), data=data, format="json"
    )
    assert response.status_code == HTTP_200_OK
    assert response.data["status"] == "canceled"


@pytest.mark.parametrize("status", ["shipped", "delivered", "canceled", "returned"])
@pytest.mark.django_db
def test_user_cannot_cancel_order_in_invalid_status(
    api_client, create_user, create_order, status
):
    """
    Ensure that a user cannot cancel an order if its status is invalid for cancellation.
    Invalid status is "shipped", "delivered", "canceled", "returned".
    """

    user = create_user()
    order = create_order.create(user=user, status=status)
    api_client.force_authenticate(user)

    response = api_client.patch(
        reverse("orders-detail", kwargs={"pk": order.id}),
        data={"status": "canceled"},
        format="json",
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert "Cannot cancel" in response.data["error"]


@pytest.mark.django_db
def test_user_cannot_cancel_other_users_order(api_client, create_user, create_order):
    """Ensure that a user cannot cancel an order that belong to another user"""

    owner = create_user()
    user = create_user(email="user_1@example.com")

    order = create_order.create(user=owner, status="pending")
    api_client.force_authenticate(user=user)

    response = api_client.patch(
        reverse("orders-detail", kwargs={"pk": order.id}),
        data={"status": "canceled"},
        format="json",
    )

    assert response.status_code == HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_anonymous_user_cannot_cancel_order(api_client, create_order, create_user):
    """
    Ensure that an anonymous user cannot cancel an order
    """

    user = create_user()
    order = create_order.create(user=user, status="pending")

    response = api_client.patch(
        reverse("orders-detail", kwargs={"pk": order.id}),
        data={"status": "canceled"},
        format="json",
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_user_cannot_update_order_with_invalid_status(
    api_client, create_user, create_order
):
    """
    Ensure that the user cannot update order with invalid status
    """

    user = create_user()
    order = create_order.create(user=user, status="pending")

    api_client.force_authenticate(user=user)

    response = api_client.patch(
        reverse("orders-detail", kwargs={"pk": order.id}),
        data={"status": "invalid_status"},
        format="json",
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert "is not a valid choice" in str(response.data)


@pytest.mark.django_db
def test_user_cannot_patch_order_with_empty_data(api_client, create_user, create_order):
    """
    Ensure that the user cannot update order with empty data
    """

    user = create_user()
    order = create_order(user=user)

    api_client.force_authenticate(user)

    response = api_client.patch(
        reverse("orders-detail", kwargs={"pk": order.id}), data={}, format="json"
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
