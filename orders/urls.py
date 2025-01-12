from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.OrderListView.as_view(), name='order-list'),
    path('<str:order_id>/', views.OrderDetailView.as_view(), name='order-detail'),
]
