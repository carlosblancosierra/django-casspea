from django.shortcuts import render
from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Order
from .serializers import OrderListSerializer
from .filters import OrderFilter

class OrderListView(generics.ListAPIView):
    """
    List all orders with filtering and search capabilities
    GET /api/orders/
    """
    serializer_class = OrderListSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = OrderFilter
    search_fields = ['order_id', 'checkout_session__email',
                    'checkout_session__shipping_address__full_name',
                    'checkout_session__shipping_address__postcode']
    ordering_fields = ['created', 'status', 'checkout_session__total_with_shipping']
    ordering = ['-created']

    def get_queryset(self):
        return Order.objects.select_related(
            'checkout_session',
            'checkout_session__cart',
            'checkout_session__shipping_address',
            'checkout_session__billing_address',
            'checkout_session__shipping_option'
        ).prefetch_related(
            'status_history',
            'checkout_session__cart__items',
            'checkout_session__cart__items__product'
        )

class OrderDetailView(generics.RetrieveAPIView):
    """
    Retrieve a specific order
    GET /api/orders/<order_id>/
    """
    queryset = Order.objects.all()
    serializer_class = OrderListSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'order_id'

    def get_queryset(self):
        return Order.objects.select_related(
            'checkout_session',
            'checkout_session__cart',
            'checkout_session__shipping_address',
            'checkout_session__billing_address',
            'checkout_session__shipping_option'
        ).prefetch_related(
            'status_history',
            'checkout_session__cart__items',
            'checkout_session__cart__items__product'
        )
