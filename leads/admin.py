from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Lead

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['email', 'lead_type', 'unsubscribed', 'created']
    list_filter = ['lead_type', 'unsubscribed', 'created']
    search_fields = ['email']
