from django.http import HttpResponse
from django.conf import settings
import stripe
from django.template.loader import render_to_string
from django.utils import timezone
from mails.models import EmailType, EmailSent
from orders.models import Order
from checkout.models import CheckoutSession
from django.core.mail import send_mail

def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        try:
            # Retrieve the CheckoutSession using metadata
            checkout_session = CheckoutSession.objects.get(
                id=session.metadata.get('checkout_session_id')
            )

            # Update CheckoutSession status
            checkout_session.payment_status = 'paid'
            checkout_session.stripe_payment_intent = session.payment_intent
            checkout_session.stripe_session_id = session.id
            checkout_session.save()

            # Create Order associated with the CheckoutSession
            order = Order.objects.create(
                checkout_session=checkout_session,
                status='processing'  # Initial status
            )

            # Mark the cart as inactive
            cart = checkout_session.cart
            cart.active = False
            cart.save()

            # Send Order Confirmation Email
            # Retrieve the EmailType for 'order_paid'
            try:
                email_type = EmailType.objects.get(name=EmailType.ORDER_PAID)
            except EmailType.DoesNotExist:
                # If the EmailType does not exist, you might want to log this incident
                return HttpResponse(status=500)

            # Render the email template with context
            html_content = render_to_string('mails/order_paid.html', {
                'order': order,
                'current_year': timezone.now().year,
            })

            # Create an EmailSent entry
            email_sent = EmailSent.objects.create(
                email_type=email_type,
                content_object=order,
                status=EmailSent.SENT,
                sent=timezone.now()
            )

            send_mail(
                subject='Your CassPea Order Confirmation',
                message='Thank you for your order! Your order has been received and is being processed.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[checkout_session.email or checkout_session.cart.user.email],
                html_message=html_content,
                fail_silently=False,
            )

        except CheckoutSession.DoesNotExist:
            return HttpResponse(status=404)
        except Exception as e:

            return HttpResponse(status=500)

    return HttpResponse(status=200)
