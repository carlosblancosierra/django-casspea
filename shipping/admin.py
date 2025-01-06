from django.contrib import admin
from .models import ShippingOption, ShippingCompany

# Register your models here.
admin.site.register(ShippingOption)
admin.site.register(ShippingCompany)
