from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()
from addresses.models import Address

from .managers import CheckoutSessionManager

# Create your models here.
class CheckoutSession(models.Model):
    PAYMENT_STATUS_PENDING = 'PENDING'
    PAYMENT_STATUS_PAID = 'PAID'
    PAYMENT_STATUS_FAILED = 'FAILED'

    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING, 'Pending'),
        (PAYMENT_STATUS_PAID, 'Paid'),
        (PAYMENT_STATUS_FAILED, 'Failed'),
    ]

    cart = models.ForeignKey('carts.Cart', on_delete=models.CASCADE)

    shipping_address = models.ForeignKey(
        Address,
        related_name='shipping_checkouts',
        on_delete=models.SET_NULL,
        null=True
    )

    billing_address = models.ForeignKey(
        Address,
        related_name='billing_checkouts',
        on_delete=models.SET_NULL,
        null=True
    )

    # Only required for guest checkouts
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )
    stripe_payment_intent = models.CharField(max_length=255, null=True, blank=True)
    stripe_session_id = models.CharField(max_length=255, null=True, blank=True)

    objects = CheckoutSessionManager()

    def save(self, *args, **kwargs):
        # If cart has a user, we don't need email/phone
        if self.cart.user:
            self.email = None
            self.phone = None
        # If no user, email is required
        elif not self.email:
            raise ValueError("Email is required for guest checkout")
        super().save(*args, **kwargs)
