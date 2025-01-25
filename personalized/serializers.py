from rest_framework import serializers
from django.utils.text import slugify

from .models import (
    LayerColor,
    LayerType,
    ChocolateTemplate,
    TemplateLayerSlot,
    ChocolateLayer,
)


class LayerColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = LayerColor
        fields = ['name', 'slug', 'hex_code']


class LayerTypeSerializer(serializers.ModelSerializer):
    colors = serializers.SerializerMethodField()

    class Meta:
        model = LayerType
        fields = ['name', 'colors']

    def get_colors(self, obj):
        """
        Generate color data dynamically, including slugs and image paths.
        """
        all_colors = LayerColor.objects.all()
        color_data = []
        for color in all_colors:
            layer_type_slug = slugify(obj.name)
            color_slug = color.slug

            top_image_path = f"/personalized/{layer_type_slug}/{color_slug}/top.png"
            side_image_path = f"/personalized/{layer_type_slug}/{color_slug}/side.png"

            color_data.append({
                "name": color.name,
                "slug": color.slug,
                "hex_code": color.hex_code,
                "top_image": top_image_path,
                "side_image": side_image_path,
            })
        return color_data


class TemplateLayerSlotSerializer(serializers.ModelSerializer):
    layer_type = LayerTypeSerializer()

    class Meta:
        model = TemplateLayerSlot
        fields = ['layer_type', 'name', 'order']


class ChocolateTemplateListSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChocolateTemplate
        fields = ['title', 'slug']


class ChocolateTemplateDetailSerializer(serializers.ModelSerializer):
    layers = serializers.SerializerMethodField()

    class Meta:
        model = ChocolateTemplate
        fields = ['title', 'slug', 'layers']

    def get_layers(self, obj):
        slots = TemplateLayerSlot.objects.filter(template=obj).select_related(
            'layer_type',
        ).order_by('order')
        layers = TemplateLayerSlotSerializer(slots, many=True)
        return layers.data


class ChocolateLayerSerializer(serializers.ModelSerializer):
    layer_type = LayerTypeSerializer()
    color = LayerColorSerializer()

    class Meta:
        model = ChocolateLayer
        fields = ['layer_type', 'color', 'top_image', 'side_image']