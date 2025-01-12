from rest_framework import serializers
from .models import Order
from checkout.models import CheckoutSession
from addresses.serializers import AddressSerializer
from carts.models import CartItem
from discounts.serializers import DiscountSerializer
from carts.models import Cart, CartItemBoxCustomization
from products.models import Product
from carts.serializers import CartItemBoxFlavorSelectionSerializer

class CartItemBoxCustomizationSerializer(serializers.ModelSerializer):
    flavor_selections = CartItemBoxFlavorSelectionSerializer(many=True)

    class Meta:
        model = CartItemBoxCustomization
        fields = ['id', 'selection_type', 'allergens', 'flavor_selections']

class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'base_price',
        ]


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    box_customization = CartItemBoxCustomizationSerializer()
    base_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discounted_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = [
            'id',
            'quantity',
            'product',
            'box_customization',
            'base_price',
            'discounted_price',
            'savings'
        ]

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    discount = DiscountSerializer(read_only=True)
    gift_message = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True)
    shipping_date = serializers.DateField(required=False, allow_null=True)
    base_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discounted_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_savings = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_discount_valid = serializers.BooleanField(read_only=True)

    class Meta:
        model = Cart
        fields = [
            'id',
            'items',
            'discount',
            'gift_message',
            'shipping_date',
            'base_total',
            'discounted_total',
            'total_savings',
        ]

    def get_total(self, obj):
        return str(sum(item.quantity * item.product.base_price for item in obj.items.all()))


class CheckoutSessionSerializer(serializers.ModelSerializer):
    shipping_address = AddressSerializer()
    billing_address = AddressSerializer()

    cart = CartSerializer()
    class Meta:
        model = CheckoutSession
        fields = '__all__'

class OrderListSerializer(serializers.ModelSerializer):
    checkout_session = CheckoutSessionSerializer()
    class Meta:
        model = Order
        fields = '__all__'
