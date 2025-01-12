from rest_framework import serializers
from .models import Order, OrderStatusHistory
from products.serializers import ProductSerializer
from addresses.models import Address

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            'full_name', 'phone', 'street_address',
            'street_address2', 'city', 'county',
            'postcode', 'country'
        ]

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    base_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    discounted_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    savings = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = 'carts.CartItem'
        fields = [
            'product', 'quantity', 'base_price',
            'discounted_price', 'savings'
        ]

class OrderStatusHistorySerializer(serializers.ModelSerializer):
    created_by = serializers.StringField(source='created_by.email', allow_null=True)

    class Meta:
        model = OrderStatusHistory
        fields = ['status', 'notes', 'created', 'created_by']

class OrderListSerializer(serializers.ModelSerializer):
    # Order details
    items = CartItemSerializer(source='checkout_session.cart.items', many=True)
    status_history = OrderStatusHistorySerializer(many=True)
    shipping_address = AddressSerializer()
    billing_address = AddressSerializer()

    # Payment details
    payment_status = serializers.CharField()
    payment_intent = serializers.CharField()

    # Totals
    base_total = serializers.DecimalField(
        source='checkout_session.cart.base_total',
        max_digits=10, decimal_places=2
    )
    total_savings = serializers.DecimalField(
        source='checkout_session.cart.total_savings',
        max_digits=10, decimal_places=2
    )
    shipping_cost = serializers.DecimalField(
        source='checkout_session.shipping_cost_pounds',
        max_digits=10, decimal_places=2
    )
    final_total = serializers.DecimalField(
        source='checkout_session.total_with_shipping',
        max_digits=10, decimal_places=2
    )

    # Discount information
    discount = serializers.SerializerMethodField()

    # Shipping information
    shipping_option = serializers.SerializerMethodField()

    # Customer information
    customer_email = serializers.CharField(source='email')
    gift_message = serializers.CharField(source='checkout_session.cart.gift_message', allow_null=True)
    shipping_date = serializers.DateField(source='checkout_session.cart.shipping_date', allow_null=True)

    class Meta:
        model = Order
        fields = [
            'order_id',
            'created',
            'updated',
            'status',
            'items',
            'status_history',
            'shipping_address',
            'billing_address',
            'payment_status',
            'payment_intent',
            'base_total',
            'total_savings',
            'shipping_cost',
            'final_total',
            'discount',
            'shipping_option',
            'customer_email',
            'gift_message',
            'shipping_date',
            'shipped',
            'delivered'
        ]

    def get_discount(self, obj):
        cart = obj.checkout_session.cart
        if not cart.discount:
            return None

        return {
            'code': cart.discount.code,
            'title': cart.discount.title,
            'type': cart.discount.discount_type,
            'amount': cart.discount.amount,
            'savings': cart.total_savings
        }

    def get_shipping_option(self, obj):
        shipping = obj.checkout_session.shipping_option
        if not shipping:
            return None

        return {
            'name': shipping.name,
            'delivery_speed': shipping.delivery_speed,
            'estimated_days': f"{shipping.estimated_days_min}-{shipping.estimated_days_max} business days",
            'cost': obj.checkout_session.shipping_cost_pounds
        }
