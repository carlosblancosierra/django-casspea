from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()
from addresses.models import Address
from shipping.models import ShippingOption

from .managers import CheckoutSessionManager

# Create your models here.
class CheckoutSession(models.Model):
    PAYMENT_STATUS_PENDING = 'pending'
    PAYMENT_STATUS_PAID = 'paid'
    PAYMENT_STATUS_FAILED = 'failed'

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
        default=PAYMENT_STATUS_PENDING
    )
    stripe_payment_intent = models.CharField(max_length=255, null=True, blank=True)
    stripe_session_id = models.CharField(max_length=255, null=True, blank=True)

    shipping_option = models.ForeignKey(
        ShippingOption,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

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

    @property
    def shipping_cost(self):
        if not self.shipping_option:
            return 0

        # Free shipping logic for Regular 48
        if (self.shipping_option.delivery_speed == 'REGULAR' and
            self.cart.base_total >= 45):
            return 0

        return self.shipping_option.cents

    @property
    def shipping_cost_float(self):
        if not self.shipping_cost:
            return 0
        return float(self.shipping_cost / 100)

    @property
    def total_with_shipping(self):
        return float(self.cart.total) + float(self.shipping_cost_float)

    @property
    def shipping_stripe_format(self):
        if not self.shipping_option:
            return None

        amount = self.shipping_cost
        display_name = self.shipping_option.name
        min_days = self.shipping_option.estimated_days_min
        max_days = self.shipping_option.estimated_days_max

        return {
            "shipping_rate_data": {
                "type": "fixed_amount",
                "fixed_amount": {"amount": amount, "currency": "gbp"},
                "display_name": display_name,
                "delivery_estimate": {
                    "minimum": {"unit": "business_day", "value": min_days},
                    "maximum": {"unit": "business_day", "value": max_days},
                },
            },
        }


