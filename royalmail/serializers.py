from rest_framework import serializers
from orders.models import Order

class RoyalMailOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['order_id', 'tracking_number', 'status']
        read_only_fields = fields

class RoyalMailOrderResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    tracking_number = serializers.CharField(allow_null=True)
    order_identifier = serializers.CharField(allow_null=True)
    label = serializers.CharField(allow_null=True)

class RoyalMailErrorSerializer(serializers.Serializer):
    error = serializers.CharField()

class RoyalMailOrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['order_id', 'tracking_number', 'status']
        read_only_fields = fields
