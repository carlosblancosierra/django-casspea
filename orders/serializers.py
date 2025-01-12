from rest_framework import serializers
from .models import Order, OrderStatusHistory
from products.serializers import ProductSerializer
from addresses.models import Address

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = 'carts.CartItem'
        fields = '__all__'


class OrderStatusHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderStatusHistory
        fields = '__all__'

class OrderListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = '__all__'
