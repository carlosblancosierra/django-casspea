from django.contrib import admin
from .models import Product, ProductCategory, ProductGalleryImage

admin.site.register(Product)
admin.site.register(ProductCategory)
admin.site.register(ProductGalleryImage)
