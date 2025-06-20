# Generated by Django 5.1.5 on 2025-06-04 13:01

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Cart",
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
                    "status",
                    models.CharField(
                        choices=[
                            ("active", "Active"),
                            ("abandoned", "Abandoned"),
                            ("ordered", "Ordered"),
                        ],
                        default="active",
                        max_length=10,
                    ),
                ),
                ("time_created", models.DateTimeField(auto_now_add=True)),
                ("time_updated", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Cart",
                "verbose_name_plural": "Carts",
            },
        ),
        migrations.CreateModel(
            name="CartItem",
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
                ("quantity", models.PositiveIntegerField(default=1)),
            ],
            options={
                "verbose_name": "Item",
                "verbose_name_plural": "Items",
            },
        ),
    ]
