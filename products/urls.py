from django.urls import path
from .views import ProductListView, ProductDetailView

product_patterns = [
    path('/', ProductListView.as_view(), name='product-list'),
    path('/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
]

category_patterns = [
    path('/', ProductCategoryListView.as_view(), name='category-list'),
    path('/<int:pk>/', ProductCategoryDetailView.as_view(), name='category-detail'),
]
