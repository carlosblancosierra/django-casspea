from django.db import models
from rest_framework import serializers
from checkout.models import CheckoutSession, Address

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            'id', 'street', 'city', 'state', 'zipcode', 'country'
        ]

class CheckoutSessionSerializer(serializers.ModelSerializer):
    shipping_address = AddressSerializer()
    billing_address = AddressSerializer()

    class Meta:
        model = CheckoutSession
        fields = [
            'id', 'cart', 'shipping_address', 'billing_address',
            'email', 'phone', 'status', 'created_at'
        ]
        read_only_fields = ['status', 'created_at']

    def validate(self, data):
        cart = data.get('cart')
        email = data.get('email')

        if not cart.user and not email:
            raise serializers.ValidationError({
                "email": "Email is required for guest checkout"
            })

        return data

class CheckoutDetailsSerializer(serializers.ModelSerializer):
    shipping_address = AddressSerializer()
    billing_address = AddressSerializer()

    class Meta:
        model = CheckoutSession
        fields = ['shipping_address', 'billing_address', 'email', 'phone']

    def update(self, instance, validated_data):
        # Handle shipping address
        shipping_data = validated_data.pop('shipping_address', None)
        if shipping_data:
            if instance.shipping_address:
                for attr, value in shipping_data.items():
                    setattr(instance.shipping_address, attr, value)
                instance.shipping_address.save()
            else:
                address = Address.objects.create(**shipping_data)
                if instance.cart.user:
                    address.user = instance.cart.user
                    address.save()
                instance.shipping_address = address

        # Handle billing address (similar logic)
        billing_data = validated_data.pop('billing_address', None)
        if billing_data:
            if instance.billing_address:
                for attr, value in billing_data.items():
                    setattr(instance.billing_address, attr, value)
                instance.billing_address.save()
            else:
                address = Address.objects.create(**billing_data)
                if instance.cart.user:
                    address.user = instance.cart.user
                    address.save()
                instance.billing_address = address

        return super().update(instance, validated_data)
