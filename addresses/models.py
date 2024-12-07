from django.db import models
from django.conf import settings

class Address(models.Model):
    """
    Represents an address for a user.
    """

    # Address types
    class AddressType(models.TextChoices):
        SHIPPING_ADDRESS = 'SHIPPING'
        BILLING_ADDRESS = 'BILLING'

    ADDRESS_TYPE_CHOICES = [
        (AddressType.SHIPPING_ADDRESS, 'Shipping Address'),
        (AddressType.BILLING_ADDRESS, 'Billing Address'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='addresses',
        null=True,
        blank=True
    )
    address_type = models.CharField(
        max_length=20,
        choices=ADDRESS_TYPE_CHOICES
    )

    # Address fields
    full_name = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
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
    latitude = models.CharField(max_length=20, null=True, blank=True)
    longitude = models.CharField(max_length=20, null=True, blank=True)

    # Metadata
    is_default = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # Guest user fields
    session_key = models.CharField(max_length=40, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'addresses'
        ordering = ['-is_default', '-created']
        indexes = [
            models.Index(fields=['session_key']),
            models.Index(fields=['user']),
        ]

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

    @classmethod
    def get_session_addresses(cls, session_key):
        return cls.objects.filter(session_key=session_key)
