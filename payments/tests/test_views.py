import base64
import json
from decimal import Decimal
from typing import Any, Callable, Tuple

import pytest
from django.urls import reverse
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED,
                                   HTTP_202_ACCEPTED, HTTP_400_BAD_REQUEST,
                                   HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN,
                                   HTTP_404_NOT_FOUND)
from rest_framework.test import APIClient

from orders.models import OrderItem
from orders.tests.conftest import create_order
from payments.gateways.liqpay import LiqpayPayGateway
from store.models import Product
from users.models import AuthUser
from users.tests.conftest import create_user

from ..models import Payment
from .conftest import api_client


@pytest.mark.django_db
def test_authenticated_user_can_create_payment(
    api_client: APIClient,
    create_user: Callable[..., AuthUser],
    create_filled_products: Tuple[Product, Product],
    create_order_item: Callable[..., OrderItem],
    create_order: Any,
) -> None:
    """
    Ensure that an authorized user can make a payment.
    """

    user = create_user()

    product_1, product_2 = create_filled_products

    order = create_order.create(user=user)

    order_item_1 = create_order_item(order=order, product=product_1, quantity=2)
    order_item_2 = create_order_item(order=order, product=product_2, quantity=1)

    api_client.force_authenticate(user)

    data = {"gateway": "liqpay"}

    response = api_client.post(
        reverse("payment-process", kwargs={"pk": order.id}), data, format="json"
    )

    assert response.status_code == HTTP_201_CREATED

    assert "payment_token" in response.data
    assert "amount" in response.data
    assert "currency" in response.data
    assert "gateway" in response.data
    assert "status" in response.data

    assert Decimal(response.data["amount"]) == order.get_total_price()
    assert response.data["currency"] == "UAH"
    assert response.data["gateway"] == "liqpay"
    assert response.data["status"] == "pending"


# ----------------------------------------------------------------
# Testing payments processing
# ----------------------------------------------------------------
@pytest.mark.django_db
def test_anonymous_can_not_create_payment(
    api_client: APIClient,
    create_user: Callable[..., AuthUser],
    create_filled_products: Tuple[Product, Product],
    create_order_item: Callable[..., OrderItem],
    create_order: Any,
) -> None:
    """
    Ensure that the anonymous user can not make payment
    """

    user = create_user()

    product_1, _ = create_filled_products

    order = create_order.create(user=user)
    order_item_1 = create_order_item(order=order, product=product_1, quantity=2)

    data = {"gateway": "liqpay"}
    response = api_client.post(
        reverse("payment-process", kwargs={"pk": order.id}), data, format="json"
    )

    assert response.status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_only_order_owner_can_make_payment(
    api_client: APIClient,
    create_user: Callable[..., AuthUser],
    create_filled_products: Tuple[Product, Product],
    create_order_item: Callable[..., OrderItem],
    create_order: Any,
) -> None:
    """
    Test that only the order owner can initiate payment.

    Ensure a user who does not own the order receives HTTP 403 Forbidden
    when attempting to make a payment.
    """

    user = create_user()
    owner = create_user(email="owner@example.com")

    product_1, _ = create_filled_products

    order = create_order.create(user=owner)
    order_item_1 = create_order_item(order=order, product=product_1, quantity=2)

    api_client.force_authenticate(user)

    data = {"gateway": "liqpay"}
    response = api_client.post(
        reverse("payment-process", kwargs={"pk": order.id}), data, format="json"
    )

    assert response.status_code == HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_create_payment_for_non_existing_order(
    api_client: APIClient, create_user: Callable[..., AuthUser]
) -> None:
    """
    Test payment creation for a non-existing order.
    Ensure that attempting to make a payment for an order that does not exist returns HTTP 404 Not Found.
    """

    user = create_user()
    api_client.force_authenticate(user)

    data = {"gateway": "liqpay"}
    response = api_client.post(
        reverse("payment-process", kwargs={"pk": 20}), data, format="json"
    )

    assert response.status_code == HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_create_payment_with_non_existing_gateway(
    api_client: APIClient,
    create_user: Callable[..., AuthUser],
    create_filled_products: Tuple[Product, Product],
    create_order_item: Callable[..., OrderItem],
    create_order: Any,
) -> None:
    """
    Test that payment creation fails and api status 400 when using a non-existing gateway.
    """

    user = create_user()

    product_1, _ = create_filled_products

    order = create_order.create(user=user)
    order_item_1 = create_order_item(order=order, product=product_1, quantity=2)

    api_client.force_authenticate(user)

    data = {"gateway": "Non exists gateway"}
    response = api_client.post(
        reverse("payment-process", kwargs={"pk": order.id}), data, format="json"
    )

    assert response.status_code == HTTP_400_BAD_REQUEST


# ----------------------------------------------------------------
# Testing payments callback
# ----------------------------------------------------------------
@pytest.mark.django_db
def test_callback_with_correct_signature(
    api_client: APIClient,
    create_user: Callable[..., AuthUser],
    create_filled_products: Tuple[Product, Product],
    create_order_item: Callable[..., OrderItem],
    create_order: Any,
) -> None:
    """
    Test that an authenticated user can correctly receive and process a payment callback.

    Steps:
    - Authenticate a user and create an order with items.
    - Initiate a payment request and obtain the payment token.
    - Simulate a callback from the payment gateway (e.g. LiqPay).
    - Assert that the response is correct and order status is updated based on payment status.
    """

    user = create_user()

    product_1, product_2 = create_filled_products

    order = create_order.create(user=user)

    order_item_1 = create_order_item(order=order, product=product_1, quantity=2)
    order_item_2 = create_order_item(order=order, product=product_2, quantity=1)

    api_client.force_authenticate(user)
    data_payment = {"gateway": "liqpay"}
    created_payment = api_client.post(
        reverse("payment-process", kwargs={"pk": order.id}), data_payment, format="json"
    )

    gateway = LiqpayPayGateway()

    payment_token = created_payment.data["payment_token"]
    payment_status = gateway.check_payment_status(payment_token)

    data_from_bank = {
        "gateway": payment_status["gateway"],
        "payment_token": payment_status["payment_token"],
        "signature": payment_status["signature"],
        "data": payment_status["data"],
    }

    response = api_client.post(
        reverse("payment-callback"), data=data_from_bank, format="json"
    )

    assert response.status_code == HTTP_202_ACCEPTED
    assert response.data["status"] in ["success", "failure"]

    order.refresh_from_db()

    if response.data["status"] == "success":
        assert order.status == "paid"
    else:
        assert order.status == "failed"


@pytest.mark.django_db
def test_callback_with_invalid_signature(
    api_client: APIClient,
    create_user,
    create_order,
    create_order_item,
    create_filled_products,
) -> None:
    """
    Test that the payment callback endpoint returns 403 Forbidden
    when the provided signature is invalid.
    """
    user = create_user()
    order = create_order.create(user=user)

    product_1, _ = create_filled_products
    create_order_item(order=order, product=product_1, quantity=1)

    api_client.force_authenticate(user=user)

    created_payment = api_client.post(
        reverse("payment-process", kwargs={"pk": order.id}),
        {"gateway": "liqpay"},
        format="json",
    )

    gateway = LiqpayPayGateway()

    payment_token = created_payment.data["payment_token"]
    payment_status = gateway.check_payment_status(payment_token)

    data_from_bank = {
        "gateway": payment_status["gateway"],
        "payment_token": payment_status["payment_token"],
        "signature": "invalid signature",
        "data": payment_status["data"],
    }

    response = api_client.post(
        reverse("payment-callback"), data=data_from_bank, format="json"
    )

    assert response.status_code == HTTP_403_FORBIDDEN
    assert response.data["error"] == "Invalid signature"


@pytest.mark.django_db
def test_callback_with_out_payment_token(
    api_client: APIClient,
    create_user,
    create_order,
    create_order_item,
    create_filled_products,
) -> None:
    """
    Test that the payment callback endpoint returns 400 Forbidden
    when the provided signature is invalid.
    """
    user = create_user()
    order = create_order.create(user=user)

    product_1, _ = create_filled_products
    create_order_item(order=order, product=product_1, quantity=1)

    api_client.force_authenticate(user=user)

    created_payment = api_client.post(
        reverse("payment-process", kwargs={"pk": order.id}),
        {"gateway": "liqpay"},
        format="json",
    )

    payload = {
        "gateway": created_payment.data["gateway"],
        "status": created_payment.data["status"],
    }

    json_payload = json.dumps(payload)
    encoded_data = base64.b64encode(json_payload.encode()).decode()

    gateway = LiqpayPayGateway()
    signature = gateway._generate_signature(encoded_data)

    bad_encoded_data = base64.b64encode(json.dumps(payload).encode()).decode()

    data_from_bank = {
        "gateway": "liqpay",
        "data": bad_encoded_data,
        "signature": signature,
    }

    response = api_client.post(
        reverse("payment-callback"), data=data_from_bank, format="json"
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.data["error"] == "Missing payment token in decoded data"


@pytest.mark.django_db
def test_callback_invalid_gateway(
    api_client: APIClient,
    create_user,
    create_order,
    create_order_item,
    create_filled_products,
) -> None:
    """
    Test that callback returns 400 Bad Request if an unknown gateway is provided.
    """

    # user = create_user()
    # order = create_order.create(user=user)
    #
    # product_1, _ = create_filled_products
    # create_order_item(order=order, product=product_1, quantity=1)
    #
    # api_client.force_authenticate(user=user)
    #
    # created_payment = api_client.post(
    #     reverse("payment-process", kwargs={"pk": order.id}),
    #     {"gateway": "liqpay"},
    #     format="json"
    # )

    payload = {"payment_token": "FAKE-TOKEN", "status": "success"}

    json_payload = json.dumps(payload)
    encoded_data = base64.b64encode(json_payload.encode()).decode()

    signature = "invalidsignature"

    data = {
        "gateway": "unknownpay",  # неизвестный шлюз
        "data": encoded_data,
        "signature": signature,
    }

    response = api_client.post(reverse("payment-callback"), data=data, format="json")

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert "gateway" in response.data
    assert response.data["gateway"][0] == "Gateway not supported"


@pytest.mark.django_db
def test_callback_for_already_processed_payment_returns_info(
    api_client: APIClient,
    create_user: Callable[..., AuthUser],
    create_filled_products: Tuple[Product, Product],
    create_order_item: Callable[..., OrderItem],
    create_order: Any,
) -> None:
    """
    Test that the callback endpoint does not update the status of a payment
    if it has already been processed (i.e. status is not 'pending').
    The endpoint should return the current status and a message indicating
    that the payment was already handled.
    """

    user = create_user()

    product_1, product_2 = create_filled_products

    order = create_order.create(user=user)

    order_item_1 = create_order_item(order=order, product=product_1, quantity=2)
    order_item_2 = create_order_item(order=order, product=product_2, quantity=1)

    api_client.force_authenticate(user)
    data_payment = {"gateway": "liqpay"}
    created_payment = api_client.post(
        reverse("payment-process", kwargs={"pk": order.id}), data_payment, format="json"
    )
    payment = Payment.objects.get(payment_token=created_payment.data["payment_token"])
    payment.status = "Success"
    payment.save()

    gateway = LiqpayPayGateway()

    payment_token = created_payment.data["payment_token"]
    payment_status = gateway.check_payment_status(payment_token)

    data_from_bank = {
        "gateway": payment_status["gateway"],
        "payment_token": payment_status["payment_token"],
        "signature": payment_status["signature"],
        "data": payment_status["data"],
    }

    response = api_client.post(
        reverse("payment-callback"), data=data_from_bank, format="json"
    )
    assert response.status_code == HTTP_200_OK
    assert response.data["status"] == "Success"
    assert response.data["message"] == "already processed"


@pytest.mark.django_db
def test_callback_with_nonexistent_payment_token(api_client: APIClient) -> None:
    """
    Test that the callback endpoint returns 400 Bad Request
    if the payment_token does not exist in the database.
    """

    fake_payment_token = "FAKE-TOKEN-123"

    # Собираем payload, в котором есть фейковый токен
    payload = {"payment_token": fake_payment_token, "status": "success"}

    encoded_data = base64.b64encode(json.dumps(payload).encode()).decode()

    gateway = LiqpayPayGateway()
    signature = gateway._generate_signature(encoded_data)

    callback_data = {"gateway": "liqpay", "data": encoded_data, "signature": signature}

    response = api_client.post(
        reverse("payment-callback"), data=callback_data, format="json"
    )
    assert response.status_code == 400
    assert response.data["detail"] == "Payment not found"
