from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ShippingOptionsViewSet

router = DefaultRouter()
router.register(r'options', ShippingOptionsViewSet, basename='shipping-options')

urlpatterns = [
    path('', include(router.urls)),
]
