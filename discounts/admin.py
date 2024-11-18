from django.contrib import admin
from django.contrib.admin import register
from .models import Discount


@register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('title', 'code', 'discount_type', 'amount', 'start_date', 'end_date', 'min_order_value')
    search_fields = ('title', 'code')
    list_filter = ('discount_type', 'start_date', 'end_date')
