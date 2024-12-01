from django.contrib import admin
from .models import EmailType, EmailSent

@admin.register(EmailType)
class EmailTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'template_name']
    search_fields = ['name']

@admin.register(EmailSent)
class EmailSentAdmin(admin.ModelAdmin):
    list_display = ['email_type', 'get_related_object', 'status', 'sent', 'created']
    list_filter = ['email_type', 'status', 'sent']
    search_fields = ['email_type__name', 'content_object__email']

    def get_related_object(self, obj):
        return obj.content_object
    get_related_object.short_description = 'Related Object'
