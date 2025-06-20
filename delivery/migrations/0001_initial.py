# Generated by Django 5.1.5 on 2025-06-04 13:01

import django.core.validators
import django.db.models.deletion
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Area",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, verbose_name="name")),
                ("is_active", models.BooleanField(default=True)),
                (
                    "nova_poshta_ref",
                    models.UUIDField(
                        blank=True,
                        null=True,
                        unique=True,
                        verbose_name="Nova Poshta Ref",
                    ),
                ),
                (
                    "time_created",
                    models.DateTimeField(
                        auto_now_add=True, db_index=True, verbose_name="Created Time"
                    ),
                ),
                (
                    "time_updated",
                    models.DateTimeField(auto_now=True, verbose_name="Updated Time"),
                ),
            ],
            options={
                "verbose_name": "Area",
                "verbose_name_plural": "Areas",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Delivery",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "tracking_number",
                    models.CharField(
                        blank=True,
                        max_length=100,
                        null=True,
                        verbose_name="Tracking Number",
                    ),
                ),
                (
                    "delivery_costs",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=9,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(Decimal("0.00"))
                        ],
                        verbose_name="Delivery Costs",
                    ),
                ),
                (
                    "time_created",
                    models.DateTimeField(
                        auto_now_add=True, db_index=True, verbose_name="Created Time"
                    ),
                ),
                (
                    "time_updated",
                    models.DateTimeField(auto_now=True, verbose_name="Updated Time"),
                ),
            ],
            options={
                "verbose_name": "Delivery",
                "verbose_name_plural": "Deliveries",
                "ordering": ["-time_created"],
            },
        ),
        migrations.CreateModel(
            name="DeliveryAddress",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "carrier",
                    models.CharField(
                        choices=[("pickup", "Pickup"), ("novaposhta", "Nova Poshta")],
                        max_length=20,
                        verbose_name="Carrier",
                    ),
                ),
                (
                    "address_line",
                    models.CharField(max_length=255, verbose_name="Address Line"),
                ),
                (
                    "description",
                    models.CharField(max_length=255, verbose_name="Description"),
                ),
                (
                    "phone",
                    models.CharField(
                        blank=True,
                        max_length=13,
                        null=True,
                        verbose_name="Phone Number",
                    ),
                ),
                (
                    "office_number",
                    models.PositiveIntegerField(
                        default=0, verbose_name="Office number"
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                (
                    "nova_poshta_ref",
                    models.UUIDField(
                        blank=True,
                        null=True,
                        unique=True,
                        verbose_name="Nova Poshta Ref",
                    ),
                ),
                (
                    "time_created",
                    models.DateTimeField(
                        auto_now_add=True, db_index=True, verbose_name="Created Time"
                    ),
                ),
                (
                    "time_updated",
                    models.DateTimeField(auto_now=True, verbose_name="Updated Time"),
                ),
            ],
            options={
                "verbose_name": "Delivery Address",
                "verbose_name_plural": "Delivery Addresses",
                "ordering": ["carrier", "city__name"],
            },
        ),
        migrations.CreateModel(
            name="City",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        db_index=True, max_length=255, verbose_name="City name"
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                (
                    "settlement_type_ua",
                    models.CharField(max_length=255, verbose_name="City type"),
                ),
                (
                    "nova_poshta_ref",
                    models.UUIDField(
                        blank=True,
                        null=True,
                        unique=True,
                        verbose_name="Nova Poshta Ref",
                    ),
                ),
                (
                    "time_created",
                    models.DateTimeField(
                        auto_now_add=True, db_index=True, verbose_name="Created Time"
                    ),
                ),
                (
                    "time_updated",
                    models.DateTimeField(auto_now=True, verbose_name="Updated Time"),
                ),
                (
                    "area",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="cities",
                        to="delivery.area",
                    ),
                ),
            ],
            options={
                "verbose_name": "City",
                "verbose_name_plural": "Cities",
                "ordering": ["name"],
            },
        ),
    ]
