# Generated by Django 5.1.3 on 2024-11-19 17:07

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("products", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Discount",
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
                ("title", models.CharField(max_length=255)),
                (
                    "code",
                    models.CharField(
                        help_text="Discount code that customers will enter",
                        max_length=50,
                        unique=True,
                    ),
                ),
                (
                    "stripe_id",
                    models.CharField(help_text="Stripe Coupon ID", max_length=255),
                ),
                (
                    "discount_type",
                    models.CharField(
                        choices=[
                            ("PERCENTAGE", "Percentage off"),
                            ("FIXED_AMOUNT", "Fixed amount off"),
                        ],
                        default="PERCENTAGE",
                        help_text="Type of discount to apply",
                        max_length=20,
                    ),
                ),
                (
                    "amount",
                    models.DecimalField(
                        decimal_places=2, help_text="Discount amount", max_digits=10
                    ),
                ),
                ("active", models.BooleanField(default=True)),
                ("start_date", models.DateTimeField(blank=True, null=True)),
                ("end_date", models.DateTimeField(blank=True, null=True)),
                (
                    "min_order_value",
                    models.IntegerField(
                        default=0,
                        help_text="Minimum order value required to use this discount",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                (
                    "exclusions",
                    models.ManyToManyField(
                        blank=True, help_text="Excluded products", to="products.product"
                    ),
                ),
            ],
            options={
                "ordering": ["-created"],
            },
        ),
    ]