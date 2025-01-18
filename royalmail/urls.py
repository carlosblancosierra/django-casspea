from django.urls import path
from . import views

app_name = 'royalmail'

urlpatterns = [
    path('orders/<str:order_id>/shipping/',
         views.RoyalMailOrderView.as_view(),
         name='order-shipping'),
]
