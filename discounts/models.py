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

    def validate_discount_for_cart(self, code: str, cart) -> tuple[bool, str, 'Discount']:
        """
        Validates if a discount can be applied to a cart

        Args:
            code (str): Discount code
            cart (Cart): Cart instance to validate against

        Returns:
            tuple: (is_valid: bool, message: str, discount: Optional[Discount])
        """
        try:
            # Check if discount exists and is valid
            discount = self.get_valid_discounts().get(code__iexact=code)

            # Calculate cart total for eligible items
            excluded_products = discount.exclusions.all()
            eligible_total = sum(
                item.quantity * item.product.base_price
                for item in cart.items.all()
                if item.product not in excluded_products
            )

            # Check minimum order value on eligible items
            if eligible_total < Decimal(str(discount.min_order_value)):
                return False, f"Eligible order total must be at least {discount.min_order_value} to use this discount", None

            # Calculate how many items are eligible vs excluded
            total_items = cart.items.count()
            excluded_items = sum(1 for item in cart.items.all() if item.product in excluded_products)

            # Add a warning message if some items are excluded
            message = "Discount is valid"
            if excluded_items > 0:
                message = f"Discount will be applied to {total_items - excluded_items} out of {total_items} items"

            return True, message, discount

        except self.model.DoesNotExist:
            return False, "Invalid or expired discount code", None
        except Exception as e:
            logger.error(f"Error validating discount code {code}: {str(e)}")
            return False, "Error validating discount code", None

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
