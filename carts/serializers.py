from rest_framework import serializers
from flavours.models import Flavour
from flavours.serializers import FlavourSerializer
from allergens.models import Allergen
from allergens.serializers import AllergenSerializer
from .models import Cart, CartItem, CartItemBoxCustomization, CartItemBoxFlavorSelection
from products.models import Product
from products.serializers import ProductSerializer
from discounts.serializers import DiscountSerializer
from django.utils import timezone
# Read-only serializers (for GET requests)
class CartItemBoxFlavorSelectionSerializer(serializers.ModelSerializer):
    flavor = FlavourSerializer()

    class Meta:
        model = CartItemBoxFlavorSelection
        fields = ['id', 'flavor', 'quantity']

class CartItemBoxCustomizationSerializer(serializers.ModelSerializer):
    allergens = AllergenSerializer(many=True)
    flavor_selections = CartItemBoxFlavorSelectionSerializer(many=True)

    class Meta:
        model = CartItemBoxCustomization
        fields = ['id', 'selection_type', 'allergens', 'flavor_selections']

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    box_customization = CartItemBoxCustomizationSerializer()

    class Meta:
        model = CartItem
        fields = ['id', 'quantity', 'product', 'box_customization']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()
    discount = DiscountSerializer(read_only=True)
    gift_message = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True)
    shipping_date = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = Cart
        fields = [
            'id',
            'items',
            'total',
            'discount',
            'gift_message',
            'shipping_date'
        ]

    def validate_shipping_date(self, value):
        """
        Validate shipping date is not in the past
        """
        if value and value < timezone.now().date():
            raise serializers.ValidationError("Shipping date cannot be in the past")
        return value

    def get_total(self, obj):
        return str(sum(item.quantity * item.product.base_price for item in obj.items.all()))


# Write serializers (for POST/PUT requests)
class CartItemBoxFlavorSelectionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItemBoxFlavorSelection
        fields = ['flavor', 'quantity']

class CartItemBoxCustomizationCreateSerializer(serializers.ModelSerializer):
    flavor_selections = CartItemBoxFlavorSelectionCreateSerializer(many=True)
    allergens = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Allergen.objects.all(),
        required=False
    )

    class Meta:
        model = CartItemBoxCustomization
        fields = ['selection_type', 'allergens', 'flavor_selections']

class CartItemCreateSerializer(serializers.ModelSerializer):
    box_customization = CartItemBoxCustomizationCreateSerializer(required=False)
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = CartItem
        fields = ['product', 'quantity', 'box_customization']

    def validate(self, data):
        """Validate the complete data set"""
        product = data['product']

        box_customization = data.get('box_customization', None)
        if box_customization:
            flavor_selections = box_customization.get('flavor_selections', [])
            total_quantity = sum(fs['quantity'] for fs in flavor_selections)

            if total_quantity != product.units_per_box:
                raise serializers.ValidationError({
                    'box_customization': {
                        'flavor_selections': f"Total flavor quantity must equal {product.units_per_box} (got {total_quantity})"
                    }
                })
        return data

    def create(self, validated_data):
        """Create a cart item"""
        # Initialize variables
        box_customization_data = None
        flavor_selections_data = []
        allergens_data = []

        # Pop optional box customization data if it exists
        if 'box_customization' in validated_data:
            box_customization_data = validated_data.pop('box_customization')
            flavor_selections_data = box_customization_data.pop('flavor_selections', [])
            allergens_data = box_customization_data.pop('allergens', [])

        # Create cart item
        cart_item = CartItem.objects.create(**validated_data)

        # Create box customization and related data only if box_customization_data exists
        if box_customization_data:
            # Create box customization
            box_customization = CartItemBoxCustomization.objects.create(
                cart_item=cart_item,
                **box_customization_data
            )

            # Add allergens if any
            if allergens_data:
                box_customization.allergens.set(allergens_data)

            # Create flavor selections
            for flavor_data in flavor_selections_data:
                CartItemBoxFlavorSelection.objects.create(
                    box_customization=box_customization,
                    **flavor_data
                )

        return cart_item

    def update(self, instance, validated_data):
        box_customization_data = validated_data.pop('box_customization', None)

        # Update cart item fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if box_customization_data:
            box_customization = instance.box_customization
            flavor_selections_data = box_customization_data.pop('flavor_selections', None)

            # Update box customization
            for attr, value in box_customization_data.items():
                if attr == 'allergens':
                    box_customization.allergens.set(value)
                else:
                    setattr(box_customization, attr, value)
            box_customization.save()

            if flavor_selections_data:
                # Delete existing flavor selections
                box_customization.flavor_selections.all().delete()
                # Create new flavor selections
                for flavor_data in flavor_selections_data:
                    CartItemBoxFlavorSelection.objects.create(
                        box_customization=box_customization,
                        **flavor_data
                    )

        return instance
