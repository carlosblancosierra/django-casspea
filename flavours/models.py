from django.db import models
from allergens.models import Allergen
from django.core.files.storage import default_storage
from django.utils.text import slugify
from storages.backends.s3boto3 import S3Boto3Storage

# Create S3 storage instance
s3_storage = S3Boto3Storage(location='media')

# Create your models here.
class FlavourCategoryManager(models.Manager):
    def active(self):
        return self.filter(active=True)

class FlavourCategory(models.Model):
    name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    slug = models.SlugField(unique=True)

    objects = FlavourCategoryManager()

    def __str__(self):
        return self.name

class FlavourManager(models.Manager):
    def active(self):
        return self.filter(active=True)

class Flavour(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    mini_description = models.TextField()
    allergens = models.ManyToManyField(Allergen)

    # Main images
    image = models.ImageField(
        upload_to='flavours',
        storage=s3_storage,
        help_text="Main product image",
        null=True,
        blank=True
    )
    image_webp = models.ImageField(
        upload_to='flavours/images/%Y/%m/',
        help_text="WebP version of main image",
        blank=True,
        null=True
    )

    # Thumbnails
    thumbnail = models.ImageField(
        upload_to='flavours/thumbnails/%Y/%m/',
        help_text="Thumbnail image (JPEG)",
        blank=True,
        null=True
    )
    thumbnail_webp = models.ImageField(
        upload_to='flavours/thumbnails/%Y/%m/',
        help_text="Thumbnail image (WebP)",
        blank=True,
        null=True
    )

    category = models.ForeignKey(FlavourCategory, on_delete=models.CASCADE, default=1)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = FlavourManager()

    def save(self, *args, **kwargs):
        # Check if this is an update and if the image has changed
        if self.pk:
            try:
                old_instance = Flavour.objects.get(pk=self.pk)
                image_changed = old_instance.image != self.image
            except Flavour.DoesNotExist:
                image_changed = True
        else:
            image_changed = bool(self.image)

        # If image has changed, delete old versions
        if image_changed and self.pk:
            # Delete old versions if they exist
            if old_instance.image_webp:
                default_storage.delete(old_instance.image_webp.name)
                self.image_webp = None
            if old_instance.thumbnail:
                default_storage.delete(old_instance.thumbnail.name)
                self.thumbnail = None
            if old_instance.thumbnail_webp:
                default_storage.delete(old_instance.thumbnail_webp.name)
                self.thumbnail_webp = None

        # Save the model first
        super().save(*args, **kwargs)

        # If there's an image and it's changed, create new versions
        if self.image and image_changed:
            print(f"\n=== Processing images for {self.name} ===")
            print("Creating WebP version...")
            self.create_webp_version()
            print("Creating thumbnails...")
            self.create_thumbnails()
            print("=== Image processing complete ===\n")

    def create_webp_version(self):
        """Create WebP version of the main image"""
        from PIL import Image
        import io
        from django.core.files.base import ContentFile

        # Open original image
        image = Image.open(self.image)

        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Save as WebP
        webp_io = io.BytesIO()
        image.save(webp_io, 'WEBP', quality=85)
        webp_io.seek(0)

        # Generate filename
        original_name = self.image.name.split('/')[-1]
        webp_name = f"flavours/webp/{original_name.rsplit('.', 1)[0]}.webp"

        # Save WebP version
        self.image_webp.save(
            webp_name,
            ContentFile(webp_io.read()),
            save=False
        )

        self.save(update_fields=['image_webp'])

    def create_thumbnails(self):
        """Create both JPEG and WebP thumbnails"""
        from PIL import Image
        import io
        from django.core.files.base import ContentFile

        # Open the image
        image = Image.open(self.image)

        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Create thumbnail size
        target_size = (300, 300)
        image.thumbnail(target_size, Image.Resampling.LANCZOS)

        # Get original filename
        original_name = self.image.name.split('/')[-1]
        base_name = original_name.rsplit('.', 1)[0]

        # Save JPEG thumbnail
        jpeg_io = io.BytesIO()
        image.save(jpeg_io, 'JPEG', quality=85)
        jpeg_io.seek(0)

        jpeg_name = f"flavours/thumbnails/{base_name}_thumb.jpg"
        self.thumbnail.save(
            jpeg_name,
            ContentFile(jpeg_io.read()),
            save=False
        )

        # Save WebP thumbnail
        webp_io = io.BytesIO()
        image.save(webp_io, 'WEBP', quality=85)
        webp_io.seek(0)

        webp_name = f"flavours/thumbnails/{base_name}_thumb.webp"
        self.thumbnail_webp.save(
            webp_name,
            ContentFile(webp_io.read()),
            save=False
        )

        self.save(update_fields=['thumbnail', 'thumbnail_webp'])

    def delete(self, *args, **kwargs):
        # Delete all image versions
        if self.image:
            default_storage.delete(self.image.name)
        if self.image_webp:
            default_storage.delete(self.image_webp.name)
        if self.thumbnail:
            default_storage.delete(self.thumbnail.name)
        if self.thumbnail_webp:
            default_storage.delete(self.thumbnail_webp.name)
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.name

class FlavourSelection(models.Model):
    flavour = models.ForeignKey(Flavour, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.flavour.name} x {self.quantity}"

class FlavourBox(models.Model):
    selections = models.ManyToManyField(FlavourSelection)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Box {self.id}"
