# Generated by Django 5.1.4 on 2024-12-11 20:05

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ShippingCompany",
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
                ("name", models.CharField(max_length=100)),
                ("code", models.SlugField(unique=True)),
                ("active", models.BooleanField(default=True)),
                ("website", models.URLField(blank=True)),
                ("track_url", models.URLField(blank=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name_plural": "Shipping Companies",
            },
        ),
        migrations.CreateModel(
            name="ShippingOption",
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
                ("name", models.CharField(max_length=100)),
                ("delivery_speed", models.CharField(max_length=20)),
                (
                    "price",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=6,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                (
                    "cents",
                    models.PositiveIntegerField(blank=True, default=499, null=True),
                ),
                (
                    "estimated_days_min",
                    models.PositiveSmallIntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(30),
                        ]
                    ),
                ),
                (
                    "estimated_days_max",
                    models.PositiveSmallIntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(30),
                        ]
                    ),
                ),
                ("active", models.BooleanField(default=True)),
                ("description", models.TextField(blank=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                (
                    "company",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="options",
                        to="shipping.shippingcompany",
                    ),
                ),
            ],
        ),
    ]
