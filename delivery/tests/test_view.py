from typing import Callable

import pytest
from django.urls import reverse
from rest_framework.status import (HTTP_200_OK, HTTP_400_BAD_REQUEST,
                                   HTTP_401_UNAUTHORIZED,
                                   HTTP_405_METHOD_NOT_ALLOWED)
from rest_framework.test import APIClient

from users.models import AuthUser
from users.tests.conftest import create_user

from ..models import Area, CarrierChoices, City, DeliveryAddress


@pytest.mark.parametrize("method", ["post", "put", "patch", "delete"])
@pytest.mark.django_db
def test_cities_unsupported_methods_return_405(api_client, method, create_user):
    """
    Test that unsupported HTTP methods on the cities endpoint return 405.
    """
    user = create_user()
    api_client.force_authenticate(user=user)

    url = reverse("delivery-cities")
    client_method = getattr(api_client, method)
    response = client_method(url, {"q": "anything"})
    assert response.status_code == HTTP_405_METHOD_NOT_ALLOWED


# GET /api/v1/delivery/cities/search/?q=<term>
@pytest.mark.django_db
def test_authenticated_user_can_get_cities(
    api_client: APIClient,
    create_user: Callable[..., AuthUser],
    create_area: Callable[..., Area],
    create_city: Callable[..., City],
    create_address: Callable[..., DeliveryAddress],
) -> None:
    """
    Test that an authenticated user can retrieve a list of active cities
    filtered by the 'q' parameter (case-insensitive substring match),
    where each city must also have at least one active delivery address.
    """
    user = create_user()

    area_1 = create_area(name="Lvivska")
    area_2 = create_area(name="Kyivska")

    city_1 = create_city.create(area=area_1, name="Пірогівка")
    city_2 = create_city.create(area=area_2, name="Груздівка")
    city_3 = create_city.create(area=area_2, name="Грузівка")
    city_4 = create_city.create(area=area_2, name="Грузка")
    city_5 = create_city.create(area=area_2, name="Груздів", is_active=False)

    carrier_pickup = CarrierChoices.PICKUP
    carrier_np = CarrierChoices.NOVA_POSHTA

    addresses_1 = create_address.create(city=city_2, carrier=carrier_pickup)
    addresses_2 = create_address.create(
        city=city_3, carrier=carrier_np, is_active=False
    )

    api_client.force_authenticate(user=user)

    data = {"q": "гру"}

    response = api_client.get(reverse("delivery-cities"), data, format="json")

    assert response.status_code == HTTP_200_OK
    assert len(response.data) == 1


@pytest.mark.django_db
def test_anonymous_user_cannot_search_cities(api_client):
    """
    Ensure that an anonymous (unauthenticated) user
    cannot access the list of delivery addresses.
    """
    response = api_client.get(reverse("delivery-cities"), {"q": "Kiy"}, format="json")
    assert response.status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_search_missing_q_parameter(api_client, create_user):
    """
    Ensure that an authenticated user cannot retrieve a list of active cities without search query Q
    """
    user = create_user()
    api_client.force_authenticate(user=user)
    response = api_client.get(reverse("delivery-cities"), format="json")
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert "q" in response.data
    assert "The 'q' parameter is required." in response.data["q"]


@pytest.mark.django_db
def test_search_q_min_length(api_client, create_user):
    """
    Ensure that an authenticated user cannot retrieve a list of active cities if q less than 3 character
    """
    user = create_user()
    api_client.force_authenticate(user=user)
    response = api_client.get(reverse("delivery-cities"), {"q": "Ki"})
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert "q" in response.data
    assert "Enter at least 3 characters." in response.data["q"]


@pytest.mark.django_db
def test_search_q_doesnt_match_any_city(api_client, create_user):
    """
    Ensure that an authenticated user receives an empty list of active cities
    if the 'q' parameter does not match any cities in the database.
    """
    user = create_user()
    api_client.force_authenticate(user=user)
    response = api_client.get(reverse("delivery-cities"), {"q": "Kie"}, format="json")
    assert response.status_code == HTTP_200_OK
    assert response.data == []


@pytest.mark.django_db
def test_cites_multiply_matches_sorted(
    api_client: APIClient,
    create_user: Callable[..., AuthUser],
    create_area: Callable[..., Area],
    create_city: Callable[..., City],
    create_address: Callable[..., DeliveryAddress],
) -> None:
    """
    Test that GET /delivery/cities/?q=<term> returns multiple matching cities
    sorted by 'name' ascending.
    """
    user: AuthUser = create_user()
    api_client.force_authenticate(user=user)

    area = create_area(name="Area")
    city_1 = create_city.create(area=area, name="City_1", is_active=True)
    city_2 = create_city.create(area=area, name="City_2", is_active=True)

    create_address.create(city=city_1, carrier=CarrierChoices.PICKUP, is_active=True)
    create_address.create(city=city_2, carrier=CarrierChoices.PICKUP, is_active=True)

    response = api_client.get(reverse("delivery-cities"), {"q": "City"}, format="json")
    assert response.status_code == HTTP_200_OK

    names = [c["name"] for c in response.data]
    assert names == [city_1.name, city_2.name]


@pytest.mark.django_db
def test_addresses_filters_carriers_with_no_offices(
    api_client: APIClient,
    create_user: Callable[..., AuthUser],
    create_area: Callable[..., Area],
    create_city: Callable[..., City],
    create_address: Callable[..., DeliveryAddress],
) -> None:
    """
    Test that GET /delivery/addresses/?city_id=<id> excludes carriers
    that have no active offices.
    """
    user: AuthUser = create_user()
    api_client.force_authenticate(user=user)

    area = create_area(name="Area")
    city = create_city.create(area=area, name="City_1", is_active=True)
    create_address.create_batch(
        2, city=city, carrier=CarrierChoices.PICKUP, is_active=True
    )
    create_address.create(
        city=city, carrier=CarrierChoices.NOVA_POSHTA, is_active=False
    )

    response = api_client.get(
        reverse("delivery-addresses"), {"city_id": city.id}, format="json"
    )
    assert response.status_code == HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["carrier"]["value"] == CarrierChoices.PICKUP


@pytest.mark.django_db
def test_addresses_invalid_city_id_negative_or_zero(
    api_client: APIClient,
    create_user: Callable[..., AuthUser],
    create_area: Callable[..., Area],
    create_city: Callable[..., City],
    create_address: Callable[..., DeliveryAddress],
) -> None:
    """
    Test that GET /delivery/addresses/?city_id=<invalid> returns 400
    when city_id is zero or negative.
    """
    user: AuthUser = create_user()
    api_client.force_authenticate(user=user)

    for bad_id in (0, -10):
        response = api_client.get(
            reverse("delivery-addresses"), {"city_id": bad_id}, format="json"
        )
        assert response.status_code == HTTP_400_BAD_REQUEST
        assert "city_id" in response.data
        assert f"City with ID {bad_id} does not exist." in response.data["city_id"][0]


@pytest.mark.django_db
def test_search_case_insensitive_prefix(
    api_client, create_user, create_area, create_city, create_address
):
    """
    Test that search is case-insensitive on the 'q' parameter.
    """
    user = create_user()
    api_client.force_authenticate(user=user)

    area = create_area(name="TestArea")
    city = create_city(name="CityABC", area=area, is_active=True)
    # active address required for inclusion
    create_address(city=city, carrier=CarrierChoices.PICKUP, is_active=True)

    # lowercase query against mixed-case name
    response = api_client.get(reverse("delivery-cities"), {"q": "cityabc"})
    assert response.status_code == HTTP_200_OK
    assert response.data and response.data[0]["name"] == city.name


@pytest.mark.django_db
def test_search_strip_whitespace(
    api_client, create_user, create_area, create_city, create_address
):
    """
    Test that leading and trailing whitespace in 'q' is ignored.
    """
    user = create_user()
    api_client.force_authenticate(user=user)

    area = create_area(name="Area1")
    city = create_city(name="MyCity", area=area, is_active=True)
    create_address(city=city, carrier=CarrierChoices.PICKUP, is_active=True)

    response = api_client.get(reverse("delivery-cities"), {"q": "  MyCity  "})
    assert response.status_code == HTTP_200_OK
    assert [c["name"] for c in response.data] == [city.name]


@pytest.mark.django_db
def test_response_fields_contain_only_id_and_name(
    api_client, create_user, create_area, create_city, create_address
):
    """
    Test that the response returns only 'id' and 'name' fields for each city.
    """
    user = create_user()
    api_client.force_authenticate(user=user)

    area = create_area(name="Area4")
    city = create_city(name="FieldCity", area=area, is_active=True)
    create_address(city=city, carrier=CarrierChoices.PICKUP, is_active=True)

    response = api_client.get(reverse("delivery-cities"), {"q": "FieldCity"})
    assert response.status_code == HTTP_200_OK
    keys = set(response.data[0].keys())
    assert keys == {"area", "id", "name"}


# GET /api/v1/delivery/options/?city_id=<id>
@pytest.mark.django_db
def test_anonymous_user_cannot_get_addresses(api_client: APIClient) -> None:
    """
    Ensure that an anonymous (unauthenticated) user
    cannot access the list of delivery addresses.
    """
    response = api_client.get(reverse("delivery-addresses"), format="json")
    assert response.status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_authenticated_user_can_get_addresses(
    api_client: APIClient,
    create_user: Callable[..., AuthUser],
    create_area: Callable[..., Area],
    create_city: Callable[..., City],
    create_address: Callable[..., DeliveryAddress],
) -> None:
    """
    Ensure that an authenticated user can retrieve a list of active delivery addresses for selected city
    """
    user = create_user()

    area_1 = create_area(name="Lvivska")
    area_2 = create_area(name="Kyivska")

    cities_area_1 = create_city.create(area=area_1)
    cities_area_2 = create_city.create(area=area_2)

    сarrier_pickup = CarrierChoices.PICKUP
    сarrier_np = CarrierChoices.NOVA_POSHTA

    addresses_1 = create_address.create_batch(
        3, city=cities_area_1, carrier=сarrier_pickup
    )
    addresses_2 = create_address.create_batch(3, city=cities_area_1, carrier=сarrier_np)
    addresses_3 = create_address.create_batch(
        3, city=cities_area_2, carrier=сarrier_pickup
    )
    addresses_4 = create_address.create_batch(3, city=cities_area_2, carrier=сarrier_np)

    addresses = DeliveryAddress.objects.all()

    api_client.force_authenticate(user=user)
    response = api_client.get(
        reverse("delivery-addresses"), data={"city_id": cities_area_1.id}, format="json"
    )

    assert response.status_code == HTTP_200_OK
    assert len(response.data) == 2
    assert len(response.data[0]["addresses"]) == 3
    assert len(response.data[1]["addresses"]) == 3
    assert "carrier" in response.data[0]
    assert "addresses" in response.data[0]


@pytest.mark.django_db
def test_authenticated_user_cannot_get_addresses_missing_city(
    api_client: APIClient, create_user
) -> None:
    """
    Ensure that an authenticated user cannot retrieve a list of active delivery addresses with empty city
    """
    user = create_user()

    api_client.force_authenticate(user=user)
    response = api_client.get(reverse("delivery-addresses"), format="json")

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert "city_id" in response.data
    assert "Area ID is required" in response.data["city_id"]


@pytest.mark.django_db
def test_authenticated_user_cannot_get_addresses_incorrect_city_type(
    api_client: APIClient,
    create_user: Callable[..., AuthUser],
    create_area: Callable[..., Area],
    create_city: Callable[..., City],
    create_address: Callable[..., DeliveryAddress],
) -> None:
    """
    Ensure that an authenticated user can retrieve a list of active delivery addresses with bad type city.
    """
    user = create_user()

    api_client.force_authenticate(user=user)
    response = api_client.get(
        reverse("delivery-addresses"), data={"city_id": "foo"}, format="json"
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert "Uncorrected area ID" in response.data["city_id"]


@pytest.mark.django_db
def test_authenticated_user_cannot_get_addresses_nonexistent_city_type(
    api_client: APIClient, create_user: Callable[..., AuthUser]
) -> None:
    """
    Ensure that an authenticated user can retrieve a list of active delivery addresses with nonexistent city.
    """
    user = create_user()

    data = {"city_id": 99}

    api_client.force_authenticate(user=user)
    response = api_client.get(reverse("delivery-addresses"), data=data, format="json")

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert f"City with ID {data["city_id"]} does not exist." in response.data["city_id"]
    expected = f"City with ID {data['city_id']} does not exist."
    assert "city_id" in response.data
    assert expected in response.data["city_id"][0]


@pytest.mark.django_db
def test_authenticated_user_can_get_only_active_addresses(
    api_client: APIClient,
    create_user: Callable[..., AuthUser],
    create_area: Callable[..., Area],
    create_city: Callable[..., City],
    create_address: Callable[..., DeliveryAddress],
) -> None:
    """
    Ensure that an authenticated user can retrieve a list of active delivery addresses for selected city
    """
    user = create_user()

    area_1 = create_area(name="Lvivska")
    area_2 = create_area(name="Kyivska")

    cities_area_1 = create_city.create(area=area_1)
    cities_area_2 = create_city.create(area=area_2)

    carrier_pickup = CarrierChoices.PICKUP
    carrier_np = CarrierChoices.NOVA_POSHTA

    addresses_1 = create_address.create(city=cities_area_1, carrier=carrier_pickup)
    addresses_2 = create_address.create(city=cities_area_1, carrier=carrier_np)
    addresses_3 = create_address.create(
        city=cities_area_1, carrier=carrier_np, is_active=False
    )

    addresses = DeliveryAddress.objects.all()

    api_client.force_authenticate(user=user)
    response = api_client.get(
        reverse("delivery-addresses"), data={"city_id": cities_area_1.id}, format="json"
    )

    assert response.status_code == HTTP_200_OK
    assert len(response.data) == 2


@pytest.mark.django_db
def test_authenticated_user_get_addresses_no_active_addresses(
    api_client: APIClient,
    create_user: Callable[..., AuthUser],
    create_area: Callable[..., Area],
    create_city: Callable[..., City],
    create_address: Callable[..., DeliveryAddress],
) -> None:
    """
    Test that when a city has only inactive addresses, the addresses endpoint
    returns an empty list with HTTP 200.
    """
    user: AuthUser = create_user()
    api_client.force_authenticate(user=user)

    area = create_area(name="Lvivska")
    city = create_city.create(area=area, name="Lviv")

    create_address.create(city=city, carrier=CarrierChoices.PICKUP, is_active=False)
    create_address.create(
        city=city, carrier=CarrierChoices.NOVA_POSHTA, is_active=False
    )

    response = api_client.get(
        reverse("delivery-addresses"), {"city_id": city.id}, format="json"
    )
    assert response.status_code == HTTP_200_OK
    assert response.data == []
