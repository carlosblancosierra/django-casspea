from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()
from addresses.models import Address

# Create your models here.
class CheckoutSession(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    cart = models.OneToOneField('carts.Cart', on_delete=models.CASCADE)
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

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # If cart has a user, we don't need email/phone
        if self.cart.user:
            self.email = None
            self.phone = None
        # If no user, email is required
        elif not self.email:
            raise ValueError("Email is required for guest checkout")
        super().save(*args, **kwargs)
