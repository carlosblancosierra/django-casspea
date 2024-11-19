from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
import stripe
from orders.models import Order

def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        # Get our checkout session from metadata
        checkout_session_id = session.metadata.get('checkout_session_id')
        checkout_session = CheckoutSession.objects.get(id=checkout_session_id)

        # Create order
        order = Order.objects.create(
            checkout_session=checkout_session,
            payment_id=session.payment_intent,
            total_paid=checkout_session.cart.total,
            # Add other fields as needed
        )

        # Send confirmation email
        send_mail(
            subject='Order Confirmation',
            message=f'Thank you for your order! Order number: {order.id}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[checkout_session.email or checkout_session.cart.user.email],
            fail_silently=False,
        )

    return HttpResponse(status=200)
