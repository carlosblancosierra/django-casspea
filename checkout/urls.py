from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CheckoutSessionViewSet
from .webhooks import stripe_webhook

router = DefaultRouter()
router.register(r'sessions', CheckoutSessionViewSet, basename='checkout-session')

urlpatterns = [
    path('', include(router.urls)),
    path('webhook/stripe/', stripe_webhook, name='stripe-webhook'),
]
