from django.urls import path
from . import views

app_name = 'royalmail'

urlpatterns = [
    # List all Royal Mail orders
    path('orders/',
         views.RoyalMailOrderListView.as_view(),
         name='order-list'),

    # Get specific order details
    path('orders/<str:order_id>/',
         views.RoyalMailOrderDetailView.as_view(),
         name='order-detail'),

    # Create shipping label for order
    path('orders/<str:order_id>/create/',
         views.RoyalMailOrderCreateView.as_view(),
         name='order-create'),

    # Download shipping label PDF
    path('orders/<str:order_id>/label/',
         views.RoyalMailLabelView.as_view(),
         name='order-label'),
]
