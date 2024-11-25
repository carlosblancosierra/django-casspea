from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from products.models import Product
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class DiscountManager(models.Manager):
    def get_valid_discounts(self):
        """Returns all currently valid discounts"""
        now = timezone.now()
        return self.filter(
            active=True
        ).filter(
            models.Q(start_date__isnull=True) | models.Q(start_date__lte=now)
        ).filter(
            models.Q(end_date__isnull=True) | models.Q(end_date__gte=now)
        )

    def is_valid(self, discount_instance) -> bool:
        """
        Check if a specific discount instance is currently valid

        Args:
            discount_instance (Discount): The discount instance to check

        Returns:
            bool: True if the discount is valid, False otherwise
        """
        if not discount_instance:
            return False

        now = timezone.now()

        if not discount_instance.active:
            return False

        if discount_instance.start_date and discount_instance.start_date > now:
            return False

        if discount_instance.end_date and discount_instance.end_date < now:
            return False

        return True

class Discount(models.Model):
    PERCENTAGE = "PERCENTAGE"
    FIXED_AMOUNT = "FIXED_AMOUNT"
    DISCOUNT_TYPES = [
        (PERCENTAGE, "Percentage off"),
        (FIXED_AMOUNT, "Fixed amount off"),
    ]

    title = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True, help_text="Discount code that customers will enter")
    stripe_id = models.CharField(max_length=255, help_text="Stripe Coupon ID")
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES, default=PERCENTAGE, help_text="Type of discount to apply")
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Discount amount")
    exclusions = models.ManyToManyField(Product, blank=True, help_text="Excluded products")
    active = models.BooleanField(default=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    min_order_value = models.IntegerField(default=0, help_text="Minimum order value required to use this discount")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = DiscountManager()

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f"{self.title} ({self.code})"

    def clean(self):
        """Validate the model"""
        if self.start_date and self.end_date:
            if self.start_date >= self.end_date:
                raise ValidationError({
                    'end_date': 'End date must be after start date'
                })

        if self.discount_type == self.PERCENTAGE and self.amount > 100:
            raise ValidationError({
                'amount': 'Percentage discount cannot be greater than 100%'
            })

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @property
    def is_valid(self) -> bool:
        """Check if this discount is currently valid"""
        return Discount.objects.is_valid(self)

    @property
    def status(self) -> str:
        """Returns the current status of the discount"""
        if not self.active:
            return "inactive"

        now = timezone.now()

        if self.start_date and self.start_date > now:
            return "scheduled"

        if self.end_date and self.end_date < now:
            return "expired"

        return "active"
