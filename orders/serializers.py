from rest_framework import serializers
from .models import Order
from checkout.models import CheckoutSession
from addresses.serializers import AddressSerializer
from carts.serializers import CartSerializer

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
