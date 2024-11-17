from django.urls import path
from .views import ProductListView, ProductDetailView

products_urls = [
    path('', ProductListView.as_view(), name='product-list'),
    path('<slug:slug>/', ProductDetailView.as_view(), name='product-detail'),
]
