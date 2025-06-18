from unittest.mock import MagicMock

import pytest

from delivery.services import (build_city_options,
                               get_available_carrier_offices,
                               get_available_carriers_for_city)

from ..models import Area, CarrierChoices, City, DeliveryAddress


# get_available_carriers_for_city(city: City)
@pytest.mark.django_db
def test_get_available_carriers_for_city(
    create_city, create_area, create_address
) -> None:
    """
    Test that get_available_carriers_for_city correctly returns a list of unique
    carrier types with active delivery addresses in a given city.
    """
    area: Area = create_area.create()
    city: City = create_city.create(area=area)

    DeliveryAddress.objects.create(
        city=city,
        is_active=True,
        carrier=CarrierChoices.NOVA_POSHTA,
        address_line="Street 1. str",
        office_number=13,
    )

    DeliveryAddress.objects.create(
        city=city,
        is_active=True,
        carrier=CarrierChoices.PICKUP,
        address_line="Street 2. str",
        office_number=13,
    )

    carriers: list[str] = get_available_carriers_for_city(city)

    assert set(carriers) == {CarrierChoices.NOVA_POSHTA, CarrierChoices.PICKUP}


@pytest.mark.django_db
def test_get_available_carriers_no_address(create_city, create_area) -> None:
    """
    Test that get_available_carriers_for_city returns an empty list
    when no delivery addresses exist for the given city.
    """
    area: Area = create_area.create()
    city: City = create_city.create(area=area)

    carriers: list[str] = get_available_carriers_for_city(city)

    assert carriers == []


@pytest.mark.django_db
def test_get_available_carriers_for_city_deduplicates(create_area, create_city) -> None:
    """
    Test that get_available_carriers_for_city only returns each carrier once,
    even if multiple active addresses share the same carrier.
    """
    area: Area = create_area.create()
    city: City = create_city.create(area=area)

    DeliveryAddress.objects.create(
        city=city,
        is_active=True,
        carrier=CarrierChoices.NOVA_POSHTA,
        address_line="A",
        office_number=1,
    )
    DeliveryAddress.objects.create(
        city=city,
        is_active=True,
        carrier=CarrierChoices.NOVA_POSHTA,
        address_line="B",
        office_number=2,
    )

    carriers: list[str] = get_available_carriers_for_city(city)
    assert carriers == [CarrierChoices.NOVA_POSHTA]


@pytest.mark.django_db
def test_get_available_carriers_only_inactive(create_area, create_city) -> None:
    """
    Test that get_available_carriers_for_city returns an empty list
    when all delivery addresses in the city are inactive.
    """
    area: Area = create_area.create()
    city: City = create_city.create(area=area)

    DeliveryAddress.objects.create(
        city=city,
        is_active=False,
        carrier=CarrierChoices.NOVA_POSHTA,
        address_line="Street 1. str",
        office_number=13,
    )

    carriers: list[str] = get_available_carriers_for_city(city)
    assert carriers == []


# get_available_carrier_offices
@pytest.mark.django_db
def test_get_available_carrier_offices_returns_data(
    mocker, create_area, create_city
) -> None:
    """
    Test that get_available_carrier_offices calls the correct gateway
    and returns the expected list of delivery addresses
    """

    area: Area = create_area.create()
    city: City = create_city.create(area=area)
    mock_offices: list[DeliveryAddress] = [
        MagicMock(spec=DeliveryAddress),
        MagicMock(spec=DeliveryAddress),
    ]

    mock_gateway = MagicMock()
    mock_gateway.fetch_offices.return_value = mock_offices

    mocked_factory = mocker.patch(
        "delivery.services.DeliveryFactory.create_gateway", return_value=mock_gateway
    )

    result: list[DeliveryAddress] = get_available_carrier_offices(
        CarrierChoices.NOVA_POSHTA, city
    )

    mock_gateway.fetch_offices_calles_once_with(city)
    mocked_factory.assert_called_once_with(CarrierChoices.NOVA_POSHTA)
    assert result == mock_offices


@pytest.mark.django_db
def test_get_offices_returns_correct_list(mocker, create_area, create_city) -> None:
    """
    Test that get_available_carrier_offices returns the exact offices list
    fetched from the gateway
    """

    area: Area = create_area.create()
    city: City = create_city.create(area=area)

    office_1: DeliveryAddress = MagicMock(spec=DeliveryAddress)
    office_2: DeliveryAddress = MagicMock(spec=DeliveryAddress)

    mock_gateway = MagicMock()
    mock_gateway.fetch_offices.return_value = [office_1, office_2]

    mocker.patch(
        "delivery.services.DeliveryFactory.create_gateway", return_value=mock_gateway
    )

    result: list[DeliveryAddress] = get_available_carrier_offices(
        CarrierChoices.PICKUP, city
    )

    assert result == [office_1, office_2]


@pytest.mark.django_db
def test_get_offices_raises_of_invalid_carrier(
    mocker, create_area, create_city
) -> None:
    """
    Test that get_available_carrier_offices raises an exception in the factory
    cannot create a gateway for the given carrier.
    """
    area: Area = create_area.create()
    city: City = create_city.create(area=area)

    mocker.patch(
        "delivery.services.DeliveryFactory.create_gateway",
        side_effect=ValueError("Invalid carrier"),
    )

    with pytest.raises(ValueError, match="Invalid carrier"):
        get_available_carrier_offices("Invalid carrier", city)


@pytest.mark.django_db
def test_build_city_options_multiple_carriers(mocker, create_area, create_city) -> None:
    """
    Test that build_city_options returns a block for each carrier
    when multiple carriers all have offices.
    """
    area: Area = create_area.create()
    city: City = create_city.create(area=area)

    # Mock two carriers
    mocker.patch(
        "delivery.services.get_available_carriers_for_city",
        return_value=[CarrierChoices.NOVA_POSHTA, CarrierChoices.PICKUP],
    )
    # Both carriers return non-empty office lists
    offices_np = [MagicMock(spec=DeliveryAddress)]
    offices_pk = [MagicMock(spec=DeliveryAddress)]
    mocker.patch(
        "delivery.services.get_available_carrier_offices",
        side_effect=[offices_np, offices_pk],
    )

    result: list[dict] = build_city_options(city)
    assert len(result) == 2

    assert result[0]["carrier"]["value"] == CarrierChoices.NOVA_POSHTA
    assert result[0]["addresses"] == offices_np

    assert result[1]["carrier"]["value"] == CarrierChoices.PICKUP
    assert result[1]["addresses"] == offices_pk


# build_city_options
@pytest.mark.django_db
def test_build_city_options_filters_and_structure(
    mocker, create_area, create_city
) -> None:
    """
      Test that that build_city_options groups addresses by carrier,
      excludes carriers with no offices, and return a list if dicts where each dict has:
    - 'carrier': {'value': <carrier>, 'display': <label>}
    - 'addresses': list of DeliveryAddress instances
    """

    area: Area = create_area.create()
    city: City = create_city.create(area=area)

    mocker.patch(
        "delivery.services.get_available_carriers_for_city",
        return_value=[CarrierChoices.NOVA_POSHTA, CarrierChoices.PICKUP],
    )

    mock_offices: list[DeliveryAddress] = [MagicMock(spec=DeliveryAddress)]
    mocker.patch(
        "delivery.services.get_available_carrier_offices",
        side_effect=[mock_offices, []],
    )

    result: list = build_city_options(city)

    assert isinstance(result, list)
    assert len(result)

    block = result[0]
    assert block["carrier"]["value"] == CarrierChoices.NOVA_POSHTA
    assert block["carrier"]["display"] == CarrierChoices.NOVA_POSHTA.label
    assert block["addresses"] == mock_offices


@pytest.mark.django_db
def test_build_city_options_empty_when_no_carrier(
    mocker, create_area, create_city
) -> None:
    """
    Test that build_city_options returns an empty list when
    get_available_carriers_for_city returns no carrier for the city.
    """
    area: Area = create_area.create()
    city: City = create_city.create(area=area)

    mocker.patch("delivery.services.get_available_carriers_for_city", return_value=[])

    result = build_city_options(city)

    assert result == []


@pytest.mark.django_db
def test_build_city_options_skips_none_offices(
    mocker, create_area, create_city
) -> None:
    """
    Test that build_city_options skips carriers for which
    get_available_carrier_offices returns None.
    """
    area: Area = create_area.create()
    city: City = create_city.create(area=area)

    mocker.patch(
        "delivery.services.get_available_carriers_for_city",
        return_value=[CarrierChoices.NOVA_POSHTA],
    )
    # Simulate a gateway that returns None
    mocker.patch("delivery.services.get_available_carrier_offices", return_value=None)

    result: list[dict] = build_city_options(city)
    assert result == []
