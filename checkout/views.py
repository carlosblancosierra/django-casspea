from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db import transaction
from carts.models import Cart
from checkout.models import CheckoutSession
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from .serializers import CheckoutSessionSerializer, CheckoutDetailsSerializer
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import stripe
from django.conf import settings
from orders.models import Order
from shipping.models import ShippingOption
import structlog

logger = structlog.get_logger(__name__)

class CheckoutViewSet(viewsets.ViewSet):
    """
    Checkout process management.
    Handles creation and management of checkout sessions.
    """

    @extend_schema(
        summary="Create or update checkout session",
        description="Creates a new checkout session or returns existing one. Email required for guest checkout.",
        request=CheckoutDetailsSerializer,
        examples=[
            OpenApiExample(
                'Guest Checkout',
                summary="Create checkout session for guest user",
                description="Example of creating a checkout session",
                value={
                    "email": "carlosblancosierra@gmail.com"
                },
                request_only=True,
            ),
            OpenApiExample(
                'Guest Checkout Response',
                summary="Successful checkout session creation",
                description="Example response for successful checkout session creation",
                value={
                    "id": 1,
                    "email": "carlosblancosierra@gmail.com",
                    "cart": 1,
                    "payment_status": "PENDING",
                    "cart_total": "99.99",
                    "created": "2024-03-19T12:00:00Z",
                    "updated": "2024-03-19T12:00:00Z"
                },
                response_only=True,
            )
        ],
        responses={
            200: CheckoutSessionSerializer,
            400: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT
        }
    )
    def create(self, request):
        """
        Create or update checkout session
        POST /api/checkout/
        """
        logger.info(
            "checkout_create_started",
            user_id=getattr(request.user, 'id', None),
            session_id=request.session.session_key
        )

        try:
            # Get checkout session directly from request
            checkout_session = CheckoutSession.objects.get_or_create_from_request(request)

            with transaction.atomic():
                logger.debug(
                    "processing_checkout_details",
                    checkout_session_id=checkout_session.id,
                    request_data=request.data
                )

                # Only handle email update
                if 'email' in request.data and not request.user.is_authenticated:
                    checkout_session.email = request.data['email']
                    checkout_session.save()

                logger.info(
                    "checkout_created_successfully",
                    checkout_session_id=checkout_session.id,
                    cart_id=checkout_session.cart.id,
                    user_id=getattr(request.user, 'id', None)
                )

                return Response(
                    CheckoutSessionSerializer(checkout_session).data,
                    status=status.HTTP_200_OK
                )

        except ValidationError as e:
            logger.warning(
                "checkout_validation_error",
                error=str(e.detail),
                user_id=getattr(request.user, 'id', None),
                request_data=request.data
            )
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(
                "checkout_error",
                error=str(e),
                error_type=type(e).__name__,
                user_id=getattr(request.user, 'id', None),
                request_data=request.data,
                exc_info=True
            )
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, pk=None):
        """
        Get checkout session details
        GET /api/checkout/{id}/
        """
        logger.info(
            "checkout_retrieve_started",
            checkout_id=pk,
            user_id=getattr(request.user, 'id', None)
        )

        try:
            checkout_session = CheckoutSession.objects.get(id=pk)

            logger.debug(
                "checkout_session_found",
                checkout_session_id=checkout_session.id,
                cart_id=checkout_session.cart.id
            )

            serializer = CheckoutSessionSerializer(checkout_session)
            return Response(serializer.data)

        except CheckoutSession.DoesNotExist:
            logger.warning(
                "checkout_session_not_found",
                checkout_id=pk,
                user_id=getattr(request.user, 'id', None)
            )
            return Response(
                {'error': 'Checkout session not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @extend_schema(
        summary="Process Stripe webhook",
        description="Handles Stripe webhook events for payment processing",
        responses={
            200: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT
        }
    )
    @method_decorator(csrf_exempt)
    @action(detail=False, methods=['post'], url_path='webhook')
    def webhook(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

        logger.info(
            "webhook_received",
            sig_header=sig_header is not None,
            payload_size=len(payload) if payload else 0
        )

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )

            logger.info(
                "stripe_webhook_event",
                event_type=event.type,
                event_id=event.id
            )

            if event.type == 'checkout.session.completed':
                session = event.data.object

                # Get checkout session from metadata
                checkout_session = CheckoutSession.objects.get(
                    stripe_session_id=session.id
                )

                # Update checkout session status
                checkout_session.payment_status = CheckoutSession.PAYMENT_STATUS_PAID
                checkout_session.stripe_payment_intent = session.payment_intent
                checkout_session.save()

                # Mark cart as inactive
                cart = checkout_session.cart
                cart.active = False
                cart.save()

                # Create order (implement this in your Order model)
                order = Order.objects.create_from_checkout(checkout_session)

                logger.info(
                    "payment_processed_successfully",
                    checkout_session_id=checkout_session.id,
                    order_id=order.order_id,
                    stripe_session_id=session.id
                )

            # Log the full event data for testing
            logger.debug(
                "webhook_data",
                event_data=event.data
            )

            return HttpResponse(status=200)

        except ValueError as e:
            logger.error("Invalid payload", error=str(e))
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            logger.error("Invalid signature", error=str(e))
            return HttpResponse(status=400)
        except Exception as e:
            logger.error("Webhook error", error=str(e), exc_info=True)
            return HttpResponse(status=500)

    @extend_schema(
        summary="Update shipping option",
        description="Updates the shipping option for the checkout session",
        request={"shipping_option_id": "integer"},
        responses={200: CheckoutSessionSerializer}
    )
    @action(detail=True, methods=['post'], url_path='shipping-option')
    def update_shipping_option(self, request, pk=None):
        try:
            checkout_session = CheckoutSession.objects.get(id=pk)
            shipping_option_id = request.data.get('shipping_option_id')

            if not shipping_option_id:
                return Response(
                    {'error': 'shipping_option_id is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                shipping_option = ShippingOption.objects.get(
                    id=shipping_option_id,
                    active=True,
                    company__active=True
                )
            except ShippingOption.DoesNotExist:
                return Response(
                    {'error': 'Invalid shipping option'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            checkout_session.shipping_option = shipping_option
            checkout_session.save()

            return Response(
                CheckoutSessionSerializer(checkout_session).data,
                status=status.HTTP_200_OK
            )

        except CheckoutSession.DoesNotExist:
            return Response(
                {'error': 'Checkout session not found'},
                status=status.HTTP_404_NOT_FOUND
            )
