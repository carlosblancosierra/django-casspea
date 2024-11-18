from django.db import models
from django.conf import settings
from products.models import Product, Allergen
from flavours.models import Flavour

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    session_id = models.CharField(max_length=255, null=True, blank=True)  # For anonymous users
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['session_id']),
        ]


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        indexes = [
            models.Index(fields=['cart', 'product']),
        ]


class CartItemBoxCustomization(models.Model):
    SELECTION_TYPE_CHOICES = [
        ('RANDOM', 'Random'),
        ('PICK_AND_MIX', 'Pick and Mix'),
    ]

    cart_item = models.OneToOneField(CartItem, related_name='box_customization', on_delete=models.CASCADE)
    selection_type = models.CharField(max_length=20, choices=SELECTION_TYPE_CHOICES)
    allergens = models.ManyToManyField(Allergen, blank=True)

    def __str__(self):
        return f"{self.cart_item.product.name} Box Customization"

class CartItemBoxFlavorSelection(models.Model):
    box_customization = models.ForeignKey(
        CartItemBoxCustomization,
        related_name='flavor_selections',
        on_delete=models.CASCADE
    )
    flavor = models.ForeignKey(Flavour, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.flavor.name} x {self.quantity} in {self.box_customization}"
