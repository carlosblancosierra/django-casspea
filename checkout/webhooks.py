from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.conf import settings
import stripe
from django.template.loader import render_to_string
from django.utils import timezone
from mails.models import EmailType, EmailSent
from orders.models import Order, OrderStatusHistory
from checkout.models import CheckoutSession
from django.core.mail import send_mail
import structlog

# Initialize structlog logger
logger = structlog.get_logger(__name__)

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    # Get the appropriate webhook secret based on environment
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    # Log the first few characters of the signature and secret for debugging
    logger.info("Webhook Debug Info",
        sig_header_preview=sig_header[:10] if sig_header else None,
        endpoint_secret_preview=endpoint_secret[:10] if endpoint_secret else None,
        payload_preview=payload[:100] if payload else None,
        content_length=request.META.get('CONTENT_LENGTH'),
        content_type=request.META.get('CONTENT_TYPE'),
        request_method=request.method
    )

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
        logger.info("Stripe webhook constructed successfully",
            event_id=event.get('id'),
            event_type=event.get('type')
        )
    except ValueError as e:
        logger.error("Invalid payload", error=str(e))
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error("Signature verification failed",
            error=str(e),
            sig_header=sig_header[:10],
            endpoint_secret_preview=endpoint_secret[:10] if endpoint_secret else None,
            full_sig_header=sig_header  # Log the full signature for debugging
        )
        return HttpResponse(status=400)

    if event and event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        logger.info("Processing checkout.session.completed event",
            session_id=session.get('id')
        )

        try:
            # Retrieve the CheckoutSession using metadata
            checkout_session_id = session['metadata'].get('checkout_session_id')
            checkout_session = CheckoutSession.objects.get(id=checkout_session_id)
            logger.info("CheckoutSession retrieved", checkout_session_id=checkout_session_id)

            # Update CheckoutSession status
            checkout_session.payment_status = CheckoutSession.PAYMENT_STATUS_PAID
            checkout_session.stripe_payment_intent = session.get('payment_intent')
            checkout_session.stripe_session_id = session.get('id')
            checkout_session.save()
            logger.info("CheckoutSession updated", checkout_session_id=checkout_session_id)

            # Create Order associated with the CheckoutSession
            order = Order.objects.create(
                checkout_session=checkout_session,
                status='processing'  # Initial status
            )
            logger.info("Order created", order_id=order.order_id)

            # Log the initial order status
            OrderStatusHistory.objects.create(
                order=order,
                status='processing',
                notes='Order has been created and is processing.',
                created_by=checkout_session.cart.user if checkout_session.cart.user else None
            )
            logger.info("OrderStatusHistory logged", order_id=order.order_id, status='processing')

            # Mark the cart as inactive
            cart = checkout_session.cart
            cart.active = False
            cart.save()
            logger.info("Cart marked as inactive", cart_id=cart.id)

            # Send Order Confirmation Email
            # Retrieve the EmailType for 'order_paid'
            try:
                email_type = EmailType.objects.get(name=EmailType.ORDER_PAID)
                logger.info("EmailType retrieved", email_type=email_type.name)
            except EmailType.DoesNotExist as etde:
                logger.error("EmailType 'order_paid' does not exist", error=str(etde))
                return HttpResponse(status=500)

            # Render the email template with context
            html_content = render_to_string('mails/order_paid.html', {
                'order': order,
                'current_year': timezone.now().year,
            })
            logger.info("Email template rendered", order_id=order.order_id)

            # Create an EmailSent entry
            email_sent = EmailSent.objects.create(
                email_type=email_type,
                content_object=order,
                status=EmailSent.SENT,
                sent=timezone.now()
            )
            logger.info("EmailSent entry created", email_sent_id=email_sent.id)

            # Send the email
            recipient_email = checkout_session.email or (checkout_session.cart.user.email if checkout_session.cart.user else None)
            if recipient_email:
                try:
                    send_mail(
                        subject='Your CassPea Order Confirmation',
                        message='Thank you for your order! Your order has been received and is being processed.',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[recipient_email],
                        html_message=html_content,
                        fail_silently=False,
                    )
                    logger.info("Order confirmation email sent", recipient_email=recipient_email, order_id=order.order_id)
                except Exception as email_exc:
                    # Update EmailSent status to failed
                    email_sent.status = EmailSent.FAILED
                    email_sent.error_message = str(email_exc)
                    email_sent.save()
                    logger.exception("Failed to send order confirmation email", error=str(email_exc), email_sent_id=email_sent.id)
            else:
                logger.warning("No recipient email found for sending order confirmation", order_id=order.order_id)

        except CheckoutSession.DoesNotExist as csde:
            logger.error("CheckoutSession does not exist", checkout_session_id=checkout_session_id, error=str(csde))
            return HttpResponse(status=404)
        except Exception as e:
            logger.exception("Unexpected error during webhook processing", error=str(e))
            return HttpResponse(status=500)

    return HttpResponse(status=200)
