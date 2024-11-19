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
