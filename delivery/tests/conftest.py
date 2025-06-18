from random import randint

import factory
import pytest
from django.conf import settings
from rest_framework.test import APIClient

from ..models import Area, City, DeliveryAddress


@pytest.fixture
def api_client():
    """
    Api client fixture.
    """
    return APIClient()


class AreaFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating Area instances.
    """

    name = factory.Sequence(lambda n: f"Area {n}")

    class Meta:
        model = Area


@pytest.fixture
def create_area():
    """
    Fixture for AreaFactory
    """
    return AreaFactory


class CityFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating Area instances.
    """

    name = factory.Sequence(lambda n: f"City {n}")

    class Meta:
        model = City


@pytest.fixture
def create_city():
    """
    Fixture for CityFactory
    """
    return CityFactory


class AddressesFactory(factory.django.DjangoModelFactory):
    address_line = factory.Sequence(lambda n: f"Address {n}")
    office_number = factory.Sequence(lambda n: n)
    phone = factory.LazyFunction(lambda: f"+380{randint(100000000, 999999999)}")

    class Meta:
        model = DeliveryAddress


@pytest.fixture
def create_address():
    """
    Fixture for AddressFactory
    """
    return AddressesFactory
