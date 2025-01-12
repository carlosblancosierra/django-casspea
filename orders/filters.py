import django_filters
from .models import Order

class OrderFilter(django_filters.FilterSet):
    created_after = django_filters.DateTimeFilter(field_name='created', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created', lookup_expr='lte')
    min_total = django_filters.NumberFilter(field_name='checkout_session__total_with_shipping', lookup_expr='gte')
    max_total = django_filters.NumberFilter(field_name='checkout_session__total_with_shipping', lookup_expr='lte')

    class Meta:
        model = Order
        fields = {
            'status': ['exact'],
            'payment_status': ['exact'],
            'created': ['exact', 'year', 'month'],
            'shipped': ['isnull'],
            'delivered': ['isnull'],
        }
