from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.conf import settings
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

class CheckoutSessionViewSet(viewsets.ModelViewSet):
    serializer_class = CheckoutSessionSerializer

    @action(detail=True, methods=['post'])
    def add_details(self, request, pk=None):
        checkout_session = self.get_object()
        serializer = CheckoutDetailsSerializer(checkout_session, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def create_payment(self, request, pk=None):
        checkout_session = self.get_object()

        # Create Stripe checkout session
        stripe_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            customer_email=checkout_session.email or checkout_session.cart.user.email,
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': item.product.name,
                    },
                    'unit_amount': int(item.price * 100),  # Stripe uses cents
                },
                'quantity': item.quantity,
            } for item in checkout_session.cart.items.all()],
            mode='payment',
            success_url=f"{settings.FRONTEND_URL}/checkout/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.FRONTEND_URL}/checkout/cancel",
            metadata={
                'checkout_session_id': checkout_session.id
            }
        )

        return Response({'stripe_session_id': stripe_session.id})
