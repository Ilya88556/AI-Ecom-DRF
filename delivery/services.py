from .factory import DeliveryFactory
from .models import CarrierChoices, City, DeliveryAddress


def get_available_carriers_for_city(city: City) -> list[str]:
    """
    Returns a list of unique carrier types with active delivery addresses for the given city.
    """

    available_carriers = (
        DeliveryAddress.objects.filter(city=city, is_active=True)
        .values_list("carrier", flat=True)
        .distinct()
    )

    return list(available_carriers)


def get_available_carrier_offices(carrier: str, city: City) -> list[DeliveryAddress]:
    """
    Retrieve available delivery addresses (offices) for the specified carrier type and city.
    """
    gateway = DeliveryFactory.create_gateway(carrier)
    return gateway.fetch_offices(city)


def build_city_options(city: City) -> list[dict]:
    """
    Build a list of delivery address groups by carrier for a given city.

    For each available carrier in the specified city, retrieves all active delivery addresses
    and groups them under a carrier label with display name and value.
    """

    result: list[dict] = []
    for carrier in get_available_carriers_for_city(city):
        offices = get_available_carrier_offices(carrier, city)
        if not offices:
            continue
        result.append(
            {
                "carrier": {"value": carrier, "display": CarrierChoices(carrier).label},
                "addresses": offices,
            }
        )

    return result
