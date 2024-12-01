from rest_framework import serializers
from .models import EmailType, EmailSent
from django.contrib.contenttypes.models import ContentType

class EmailTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailType
        fields = ['id', 'name', 'description']
        read_only_fields = ['id']

class EmailSentSerializer(serializers.ModelSerializer):
    email_type = EmailTypeSerializer(read_only=True)
    email_type_id = serializers.PrimaryKeyRelatedField(
        queryset=EmailType.objects.all(),
        source='email_type',
        write_only=True
    )
    content_object = serializers.SerializerMethodField()

    class Meta:
        model = EmailSent
        fields = '__all__'

    def get_content_object(self, obj):
        return str(obj.content_object)
