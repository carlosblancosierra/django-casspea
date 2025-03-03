# Generated by Django 5.1.4 on 2024-12-11 20:05

import django.db.models.deletion
import storages.backends.s3
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ProductCategory",
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
                ("name", models.CharField(max_length=255)),
                ("slug", models.SlugField(unique=True)),
                ("description", models.TextField()),
                ("active", models.BooleanField(default=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="Product",
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
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField()),
                ("base_price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("stripe_price_id", models.CharField(max_length=255)),
                ("slug", models.SlugField(unique=True)),
                ("weight", models.IntegerField(help_text="Weight in grams")),
                ("active", models.BooleanField(default=True)),
                ("sold_out", models.BooleanField(default=False)),
                (
                    "units_per_box",
                    models.IntegerField(help_text="Number of chocolates in the box"),
                ),
                ("main_color", models.CharField(max_length=255)),
                ("secondary_color", models.CharField(max_length=255)),
                ("seo_title", models.CharField(max_length=255)),
                ("seo_description", models.CharField(max_length=255)),
                (
                    "image",
                    models.ImageField(
                        blank=True,
                        help_text="Main product image",
                        null=True,
                        storage=storages.backends.s3.S3Storage(location="media"),
                        upload_to="flavours",
                    ),
                ),
                (
                    "image_webp",
                    models.ImageField(
                        blank=True,
                        help_text="WebP version of main image",
                        null=True,
                        upload_to="products/images/%Y/%m/",
                    ),
                ),
                (
                    "thumbnail",
                    models.ImageField(
                        blank=True,
                        help_text="Thumbnail image (JPEG)",
                        null=True,
                        upload_to="products/thumbnails/%Y/%m/",
                    ),
                ),
                (
                    "thumbnail_webp",
                    models.ImageField(
                        blank=True,
                        help_text="Thumbnail image (WebP)",
                        null=True,
                        upload_to="products/thumbnails/%Y/%m/",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="products.productcategory",
                    ),
                ),
            ],
            options={
                "ordering": ["-base_price"],
            },
        ),
        migrations.CreateModel(
            name="ProductGalleryImage",
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
                    "image",
                    models.ImageField(
                        help_text="Gallery image",
                        storage=storages.backends.s3.S3Storage(location="media"),
                        upload_to="products/gallery/%Y/%m/",
                    ),
                ),
                (
                    "image_webp",
                    models.ImageField(
                        blank=True,
                        help_text="WebP version of gallery image",
                        null=True,
                        storage=storages.backends.s3.S3Storage(location="media"),
                        upload_to="products/gallery/%Y/%m/",
                    ),
                ),
                (
                    "thumbnail",
                    models.ImageField(
                        blank=True,
                        help_text="Thumbnail image (JPEG)",
                        null=True,
                        storage=storages.backends.s3.S3Storage(location="media"),
                        upload_to="products/gallery/thumbnails/%Y/%m/",
                    ),
                ),
                (
                    "thumbnail_webp",
                    models.ImageField(
                        blank=True,
                        help_text="Thumbnail image (WebP)",
                        null=True,
                        storage=storages.backends.s3.S3Storage(location="media"),
                        upload_to="products/gallery/thumbnails/%Y/%m/",
                    ),
                ),
                (
                    "alt_text",
                    models.CharField(
                        blank=True,
                        help_text="Alternative text for image",
                        max_length=255,
                    ),
                ),
                (
                    "order",
                    models.PositiveIntegerField(
                        default=0, help_text="Order of images in gallery"
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="gallery_images",
                        to="products.product",
                    ),
                ),
            ],
            options={
                "ordering": ["order", "created"],
                "unique_together": {("product", "order")},
            },
        ),
    ]
