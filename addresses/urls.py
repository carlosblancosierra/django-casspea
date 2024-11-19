from rest_framework.routers import DefaultRouter
from .views import AddressViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'', AddressViewSet, basename='address')

urlpatterns = [
    path('api/', include(router.urls)),
]
