import logging
import logging.config

import factory
import pytest
from django.conf import settings
from rest_framework.test import APIClient

from ..models import Order, OrderItem


@pytest.fixture(autouse=True, scope="session")
def configure_logging():
    logging.config.dictConfig(settings.LOGGING)


@pytest.fixture
def api_client():
    """
    Api client fixture.
    """
    return APIClient()


class OrderFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating Order instances.
    """

    class Meta:
        model = Order


@pytest.fixture
def create_order():
    """
    Fixture for OrderFactory
    """
    return OrderFactory


class OrderItemFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating OrderItems instances.
    """

    class Meta:
        model = OrderItem


@pytest.fixture
def create_order_item():
    """
    Fixture for OrderItemFactory.
    """
    return OrderItemFactory
