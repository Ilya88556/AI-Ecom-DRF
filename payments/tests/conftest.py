import pytest
from rest_framework.test import APIClient

from orders.tests.conftest import create_order, create_order_item
from store.tests.conftest import (create_category, create_industry,
                                  create_product, create_product_type,
                                  create_vendor)


@pytest.fixture
def api_client():
    """
    Api client fixture.
    """
    return APIClient()


@pytest.fixture
def create_filled_products(
    create_vendor, create_industry, create_product_type, create_category, create_product
):
    category = create_category.create()
    industry = create_industry.create()
    vendor = create_vendor.create()
    product_type = create_product_type.create()

    product = create_product.create(
        category=category, vendor=vendor, is_active=True, price=15
    )

    product.industry.set(
        [
            industry,
        ]
    )
    product.product_type.set(
        [
            product_type,
        ]
    )

    product2 = create_product.create(
        category=category, vendor=vendor, is_active=True, price=20
    )

    product2.industry.set(
        [
            industry,
        ]
    )
    product2.product_type.set(
        [
            product_type,
        ]
    )

    product.save()
    product2.save()

    return product, product2
