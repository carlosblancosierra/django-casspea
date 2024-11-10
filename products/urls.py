from django.urls import path
from .views import ProductListView, ProductDetailView

products_urls = [
    path('', ProductListView.as_view(), name='product-list'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
]
