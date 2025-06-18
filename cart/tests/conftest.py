import logging
import logging.config

import factory
import pytest
from django.conf import settings
from rest_framework.test import APIClient

from ..models import Cart, CartItem


@pytest.fixture(autouse=True, scope="session")
def configure_logging():
    logging.config.dictConfig(settings.LOGGING)


@pytest.fixture
def api_client():
    """
    Api client fixture.
    """
    return APIClient()


class CartFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating Cart instances.
    """

    class Meta:
        model = Cart


@pytest.fixture
def create_cart():
    """
    Fixture for CartFactory.
    """
    return CartFactory


class CartItemFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating Cart instances.
    """

    class Meta:
        model = CartItem


@pytest.fixture
def create_cart_item():
    """
    Fixture for CartItemFactory.
    """
    return CartItemFactory
