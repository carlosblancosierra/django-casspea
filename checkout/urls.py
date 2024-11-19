from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CheckoutViewSet
# from payment.views import PaymentViewSet
from checkout.stripe_views import StripeCheckoutSessionView
from checkout.webhooks import stripe_webhook

router = DefaultRouter()
router.register(r'session', CheckoutViewSet, basename='session')
# router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
    path('stripe/create-checkout-session', StripeCheckoutSessionView.as_view(), name='stripe-create-checkout-session'),
    # path('/webhook/stripe/', stripe_webhook, name='stripe-webhook'),
]
