import logging

from celery import shared_task
from django.db import transaction

from .gateways.novaposhta import NovaPoshtaGateway
from .models import Area, CarrierChoices, City, DeliveryAddress

logger = logging.getLogger("project")


# utils
def _bulk_upsert(batch: list[dict]):
    """
    Performs a bulk upsert (update or create) of delivery addresses in a single atomic transaction.

    - Iterates over a batch of dictionaries representing delivery address data.
    - Ensures the 'carrier' field is a string before database operation.
    - Uses 'nova_poshta_ref' as the unique identifier for upsert.
    - All operations are wrapped in a transaction to ensure atomicity.

    Args:
        batch (list[dict]): A list of dictionaries containing delivery address data.

    Raises:
        Any exception raised within the transaction will cause a full rollback.
    """
    with transaction.atomic():
        for item in batch:
            item["carrier"] = str(item["carrier"])

            DeliveryAddress.objects.update_or_create(
                nova_poshta_ref=item.get("nova_poshta_ref"), defaults=item
            )


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def sync_novaposhta_areas(self):
    """
    Celery task to synchronize area data from the Nova Poshta API.

    - Retrieves area data using the NovaPoshtaGateway.
    - Updates or creates Area model instances using the 'Ref' as a unique key.
    - Automatically retries the entire task up to 3 times with a 60-second delay if the API request fails.
    - Logs errors for both API failures and database update issues.

    This task ensures the local database stays in sync with Nova Poshta's current list of areas.
    """
    gateway = NovaPoshtaGateway()
    try:
        areas = gateway.get_areas()
    except Exception as e:
        logger.error("Couldn't get areas from Novaposhta gateway", e)
        raise self.retry(exс=e)

    for area in areas:
        ref = area.get("Ref")
        description = area.get("Description")

        try:
            Area.objects.update_or_create(
                nova_poshta_ref=ref,
                defaults={"name": description},
            )

        except Exception as e:
            logger.error("Error saving area %s: %s", area.get("Ref"), e)
            continue


@shared_task(bind=True, max_retries=3, default_delay=60)
def sync_novaposhta_cities(self):
    """
    Celery task to synchronize cities data from the Nova Poshta API.

    - Retrieves cities data using the NovaPoshtaGateway.
    - Updates or creates City model instances using the 'Ref' as a unique key.
    - Automatically retries the entire task up to 3 times with a 60-second delay if the API request fails.
    - Logs errors for both API failures and database update issues.

    This task ensures the local database stays in sync with Nova Poshta's current list of areas.
    """
    gateway = NovaPoshtaGateway()
    try:
        cities = gateway.get_cites(limit=100)
    except Exception as e:
        logger.error("Couldn't get cities from Novaposhta gateway", e)
        raise self.retry(exс=e)

    areas = Area.objects.all()
    area_map = {str(area.nova_poshta_ref): area for area in areas}

    for city in cities:
        ref = city.get("Ref")
        description = city.get("Description")
        area_ref = city.get("Area")
        settlement_type_ua = city.get("SettlementTypeDescription")

        area = area_map.get(area_ref)

        if not area:
            logger.warning(
                "Area with ref %s not found, skipping city %s", area_ref, ref
            )
            continue

        try:
            City.objects.update_or_create(
                nova_poshta_ref=ref,
                defaults={
                    "name": description,
                    "area": area,
                    "is_active": True,
                    "settlement_type_ua": settlement_type_ua,
                },
            )

        except Exception as e:
            logger.error("Error saving area %s: %s", city.get("Ref"), e)
            continue


@shared_task(
    bind=True, rate_limit="30/m", autoretry_for=(Exception,), retry_backoff=True
)
def sync_novaposhta_addresses(self):
    """
    Celery task to synchronize delivery addresses (warehouses) from the Nova Poshta API.

    - Deactivates all existing DeliveryAddress records before sync.
    - Retrieves all cities and builds a reference map for lookup.
    - Iterates over warehouses returned from the Nova Poshta API.
    - Skips warehouses without valid city reference or missing 'Ref'.
    - For each valid warehouse, prepares a delivery address dict with relevant fields.
    - Uses batching to upsert addresses in chunks (default 500).
    - Final leftover batch is also inserted at the end.

    Logs:
        - Warnings if a warehouse references a missing city or lacks a Ref.
        - Errors (if any) are handled inside `_bulk_upsert`.

    This task ensures that the local delivery addresses reflect the current state of Nova Poshta warehouses.
    """
    gateway = NovaPoshtaGateway()
    batch, batch_size = [], 500

    DeliveryAddress.objects.update(is_active=False)

    cities = City.objects.all()
    cities_map = {str(city.nova_poshta_ref): city for city in cities}

    for warehouse in gateway.get_warehouses(limit=500):
        city_ref = warehouse.get("CityRef")
        city_obj = cities_map.get(city_ref)
        ref = warehouse.get("Ref")

        if not city_obj:
            logger.warning(
                "City %r doesn't exists in database, skip warehouse %r",
                city_ref,
                warehouse.get("Ref"),
            )
            continue

        if not ref:
            logger.warning("Skipping warehouse without Ref: %r", warehouse)
            continue

        batch.append(
            {
                "nova_poshta_ref": ref,
                "address_line": warehouse.get("ShortAddress"),
                "carrier": CarrierChoices.NOVA_POSHTA.value,
                "description": warehouse.get("Description"),
                "city_id": city_obj.pk,
                "office_number": warehouse.get("Number"),
                "phone": warehouse.get("Phone"),
                "is_active": True,
            }
        )

        if len(batch) >= batch_size:
            _bulk_upsert(batch)
            batch.clear()

    if batch:
        _bulk_upsert(batch)
