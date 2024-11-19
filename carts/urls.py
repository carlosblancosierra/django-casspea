from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import CartView, CartItemViewSet

router = DefaultRouter()
router.register(r'items', CartItemViewSet, basename='cart-items')

carts_urls = [
    path('', CartView.as_view(), name='cart'),
] + router.urls
