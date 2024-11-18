from django.urls import path
from .views import SessionCartView, CartItemsView, CartItemView, CartDiscountView

carts_urls = [
    path('', SessionCartView.as_view(), name='session-cart'),
    path('items/', CartItemsView.as_view(), name='cart-items'),
    path('items/<int:pk>/', CartItemView.as_view(), name='cart-item-detail'),
    path('discounts/', CartDiscountView.as_view(), name='discounts'),
]
