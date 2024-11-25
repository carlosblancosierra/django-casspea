from django.db import models
from allergens.models import Allergen
from django.utils.text import slugify
from storages.backends.s3boto3 import S3Boto3Storage
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import os

s3_storage = S3Boto3Storage(location='media')

class ProductCategoryManager(models.Manager):
    def active(self):
        return self.filter(active=True)

class ProductCategory(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    active = models.BooleanField(default=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = ProductCategoryManager()

    def __str__(self):
        return self.name


class ProductManager(models.Manager):
    def active(self):
        return self.filter(active=True)

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)

    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_price_id = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    weight = models.IntegerField(help_text="Weight in grams")

    active = models.BooleanField(default=True)
    sold_out = models.BooleanField(default=False)

    units_per_box = models.IntegerField(help_text="Number of chocolates in the box")

    main_color = models.CharField(max_length=255)
    secondary_color = models.CharField(max_length=255)

    seo_title = models.CharField(max_length=255)
    seo_description = models.CharField(max_length=255)

    image = models.ImageField(
        upload_to='flavours',
        storage=s3_storage,
        help_text="Main product image",
        null=True,
        blank=True
    )
    image_webp = models.ImageField(
        upload_to='products/images/%Y/%m/',
        help_text="WebP version of main image",
        blank=True,
        null=True
    )
    # Thumbnails
    thumbnail = models.ImageField(
        upload_to='products/thumbnails/%Y/%m/',
        help_text="Thumbnail image (JPEG)",
        blank=True,
        null=True
    )
    thumbnail_webp = models.ImageField(
        upload_to='products/thumbnails/%Y/%m/',
        help_text="Thumbnail image (WebP)",
        blank=True,
        null=True
    )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = ProductManager()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-base_price']

    def create_webp_version(self, image_field, webp_field, is_thumbnail=False):
        """Create WebP version of the image"""
        if not image_field:
            return

        # Open image using PIL
        img = Image.open(image_field)

        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')

        # Resize if it's a thumbnail
        if is_thumbnail:
            img.thumbnail((300, 300))  # Adjust size as needed

        # Save as WebP
        webp_io = BytesIO()
        img.save(webp_io, 'WEBP', quality=85, optimize=True)
        webp_io.seek(0)

        # Generate filename
        original_name = os.path.splitext(image_field.name)[0]
        webp_filename = f"{original_name}.webp"

        # Save the WebP version
        webp_field.save(
            webp_filename,
            ContentFile(webp_io.getvalue()),
            save=False
        )

    def create_thumbnail(self, image_field, thumbnail_field):
        """Create thumbnail version of the image"""
        if not image_field:
            return

        # Open image using PIL
        img = Image.open(image_field)

        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')

        # Create thumbnail
        img.thumbnail((300, 300))  # Adjust size as needed

        # Save as JPEG
        thumb_io = BytesIO()
        img.save(thumb_io, 'JPEG', quality=85, optimize=True)
        thumb_io.seek(0)

        # Generate filename
        original_name = os.path.splitext(image_field.name)[0]
        thumbnail_filename = f"{original_name}_thumb.jpg"

        # Save the thumbnail
        thumbnail_field.save(
            thumbnail_filename,
            ContentFile(thumb_io.getvalue()),
            save=False
        )

    def save(self, *args, **kwargs):
        # Check if this is a new instance or if the image has changed
        if self.pk:
            original = Product.objects.get(pk=self.pk)
            if original.image != self.image and self.image:
                # Create WebP version of main image
                self.create_webp_version(self.image, self.image_webp)
                # Create thumbnail and its WebP version
                self.create_thumbnail(self.image, self.thumbnail)
                self.create_webp_version(self.thumbnail, self.thumbnail_webp, is_thumbnail=True)
        else:
            if self.image:
                # Create WebP version of main image
                self.create_webp_version(self.image, self.image_webp)
                # Create thumbnail and its WebP version
                self.create_thumbnail(self.image, self.thumbnail)
                self.create_webp_version(self.thumbnail, self.thumbnail_webp, is_thumbnail=True)

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Delete all associated images
        if self.image:
            self.image.delete()
        if self.image_webp:
            self.image_webp.delete()
        if self.thumbnail:
            self.thumbnail.delete()
        if self.thumbnail_webp:
            self.thumbnail_webp.delete()
        super().delete(*args, **kwargs)
