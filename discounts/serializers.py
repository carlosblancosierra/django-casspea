from rest_framework import serializers
from .models import Discount
from products.serializers import ProductSerializer

class DiscountSerializer(serializers.ModelSerializer):
    exclusions = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Discount
        fields = '__all__'

class DiscountValidateSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=50)
    order_total = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
