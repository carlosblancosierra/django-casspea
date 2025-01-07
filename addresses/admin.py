from django.contrib import admin
from .models import Address

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'address_type', 'city', 'postcode', 'is_default', 'user']
    list_filter = ['address_type', 'city', 'postcode']
    search_fields = ['full_name', 'street_address', 'city', 'postcode']
    raw_id_fields = ['user']

