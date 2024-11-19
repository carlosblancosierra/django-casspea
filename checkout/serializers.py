from django.db import models  # type: ignore
from rest_framework import serializers  # type: ignore
from checkout.models import CheckoutSession
from addresses.serializers import AddressSerializer
from django.utils import timezone # type: ignore
from datetime import timedelta
from addresses.models import Address

class CheckoutSessionSerializer(serializers.ModelSerializer):
    shipping_address = AddressSerializer(read_only=True)
    billing_address = AddressSerializer(read_only=True)
    cart_total = serializers.DecimalField(
        source='cart.total',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = CheckoutSession
        fields = '__all__'

    def validate(self, data):
        cart = data.get('cart')
        email = data.get('email')

        if not cart.user and not email:
            raise serializers.ValidationError({
                "email": "Email is required for guest checkout"
            })

        return data

class CheckoutDetailsSerializer(serializers.ModelSerializer):
    shipping_address_id = serializers.IntegerField(required=True)
    billing_address_id = serializers.IntegerField(required=False)

    class Meta:
        model = CheckoutSession
        fields = ['shipping_address_id', 'billing_address_id', 'email', 'phone']

    def validate(self, data):
        request = self.context['request']

        # Validate shipping address
        shipping_id = data.get('shipping_address_id')
        try:
            if request.user.is_authenticated:
                Address.objects.get(id=shipping_id, user=request.user)
            else:
                Address.objects.get(
                    id=shipping_id,
                    session_key=request.session.session_key,
                    created__gte=timezone.now() - timedelta(hours=24)
                )
        except Address.DoesNotExist:
            raise serializers.ValidationError({
                "shipping_address_id": "Invalid shipping address ID"
            })

        # Validate billing address if provided
        billing_id = data.get('billing_address_id')
        if billing_id:
            try:
                if request.user.is_authenticated:
                    Address.objects.get(id=billing_id, user=request.user)
                else:
                    Address.objects.get(
                        id=billing_id,
                        session_key=request.session.session_key,
                        created__gte=timezone.now() - timedelta(hours=24)
                    )
            except Address.DoesNotExist:
                raise serializers.ValidationError({
                    "billing_address_id": "Invalid billing address ID"
                })

        return data

    def update(self, instance, validated_data):
        shipping_id = validated_data.pop('shipping_address_id', None)
        billing_id = validated_data.pop('billing_address_id', None)

        if shipping_id:
            instance.shipping_address_id = shipping_id
            # Use billing address same as shipping if not provided
            if not billing_id:
                instance.billing_address_id = shipping_id

        if billing_id:
            instance.billing_address_id = billing_id

        return super().update(instance, validated_data)
