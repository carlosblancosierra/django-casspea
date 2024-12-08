from rest_framework import serializers
from .models import Product, ProductCategory, ProductGalleryImage

class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = '__all__'

class ProductGalleryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductGalleryImage
        fields = [
            'id',
            'image',
            'image_webp',
            'thumbnail',
            'thumbnail_webp',
            'alt_text',
            'order'
        ]

class ProductSerializer(serializers.ModelSerializer):
    category = ProductCategorySerializer()
    gallery_images = ProductGalleryImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'description',
            'category',
            'base_price',
            'stripe_price_id',
            'slug',
            'weight',
            'active',
            'sold_out',
            'units_per_box',
            'main_color',
            'secondary_color',
            'seo_title',
            'seo_description',
            'image',
            'image_webp',
            'thumbnail',
            'thumbnail_webp',
            'gallery_images',
            'created',
            'updated'
        ]
