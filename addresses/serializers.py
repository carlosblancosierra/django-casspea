from rest_framework import serializers
from .models import Address

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            'id',
            'address_type',
            'full_name',
            'phone',
            'street_address',
            'street_address2',
            'city',
            'county',
            'postcode',
            'country',
            'place_id',
            'formatted_address',
            'latitude',
            'longitude',
            'is_default'
        ]
        read_only_fields = ['user']

    def validate(self, data):
        # Ensure required Google Places data is present
        if not data.get('place_id'):
            raise serializers.ValidationError(
                "Address must be selected from Google Places suggestions"
            )
        return data 
