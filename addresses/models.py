from django.db import models
from django.conf import settings

class Address(models.Model):
    ADDRESS_TYPE_CHOICES = [
        ('SHIPPING', 'Shipping'),
        ('BILLING', 'Billing'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='addresses'
    )
    address_type = models.CharField(
        max_length=20,
        choices=ADDRESS_TYPE_CHOICES
    )

    # Address fields
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    street_address = models.CharField(max_length=255)
    street_address2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    county = models.CharField(max_length=100, blank=True)
    postcode = models.CharField(max_length=10)
    country = models.CharField(max_length=100, default='United Kingdom')

    # Google Places data
    place_id = models.CharField(max_length=255, blank=True)
    formatted_address = models.CharField(max_length=255, blank=True)
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    # Metadata
    is_default = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'addresses'
        unique_together = [['user', 'address_type', 'is_default']]
        ordering = ['-is_default', '-created']

    def __str__(self):
        return f"{self.full_name} - {self.formatted_address}"

    def save(self, *args, **kwargs):
        # If this is being set as default, remove default from other addresses
        if self.is_default:
            Address.objects.filter(
                user=self.user,
                address_type=self.address_type,
                is_default=True
            ).update(is_default=False)
        super().save(*args, **kwargs)
