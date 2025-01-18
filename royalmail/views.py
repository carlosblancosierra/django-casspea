from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from .services import RoyalMailService
from .serializers import (
    RoyalMailOrderSerializer,
    RoyalMailOrderResponseSerializer,
    RoyalMailErrorSerializer,
    RoyalMailOrderListSerializer
)
from orders.models import Order
from users.authentication import CustomJWTAuthentication
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiTypes
import structlog
from rest_framework.authentication import SessionAuthentication

logger = structlog.get_logger(__name__)

class RoyalMailOrderListView(generics.ListAPIView):
    """
    List Royal Mail orders
    """
    permission_classes = [permissions.IsAdminUser]
    authentication_classes = [CustomJWTAuthentication, SessionAuthentication]
    serializer_class = RoyalMailOrderListSerializer

    @extend_schema(
        description="List all orders with Royal Mail shipping",
        responses={200: RoyalMailOrderListSerializer(many=True)},
        tags=["Royal Mail"]
    )
    def get_queryset(self):
        return Order.objects.filter(
            tracking_number__isnull=False
        ).select_related(
            'checkout_session',
            'checkout_session__shipping_option'
        )

class RoyalMailOrderCreateView(generics.CreateAPIView):
    """
    Create Royal Mail shipping label
    """
    permission_classes = [permissions.IsAdminUser]
    authentication_classes = [CustomJWTAuthentication, SessionAuthentication]
    serializer_class = RoyalMailOrderSerializer

    @extend_schema(
        description="Create a shipping label for an order",
        responses={
            201: RoyalMailOrderResponseSerializer,
            400: RoyalMailErrorSerializer,
            404: RoyalMailErrorSerializer,
            500: RoyalMailErrorSerializer,
        },
        tags=["Royal Mail"]
    )
    def post(self, request, order_id):
        """Create shipping label for order"""
        logger.info(
            "royal_mail_order_creation_started",
            order_id=order_id,
            user_id=request.user.id
        )

        try:
            order = Order.objects.select_related(
                'checkout_session',
                'checkout_session__cart',
                'checkout_session__shipping_address',
                'checkout_session__shipping_option'
            ).get(order_id=order_id)

            royal_mail = RoyalMailService()
            response = royal_mail.create_order(order)

            created_order = response.get('createdOrders', [{}])[0]
            tracking_number = created_order.get('trackingNumber')

            if tracking_number:
                order.tracking_number = tracking_number
                order.status = 'processing'
                order.save()

            response_data = {
                'success': True,
                'tracking_number': tracking_number,
                'order_identifier': created_order.get('orderIdentifier'),
                'label': created_order.get('label')
            }

            serializer = RoyalMailOrderResponseSerializer(data=response_data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Order.DoesNotExist:
            logger.error("royal_mail_order_not_found", order_id=order_id)
            return Response(
                {'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.exception("royal_mail_order_creation_failed", error=str(e))
            return Response(
                {'error': 'Failed to create shipping label'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class RoyalMailOrderDetailView(generics.RetrieveAPIView):
    """
    Retrieve Royal Mail order details
    """
    permission_classes = [permissions.IsAdminUser]
    authentication_classes = [CustomJWTAuthentication, SessionAuthentication]
    serializer_class = RoyalMailOrderSerializer
    lookup_field = 'order_id'

    @extend_schema(
        description="Get Royal Mail shipping details for an order",
        responses={
            200: RoyalMailOrderSerializer,
            404: RoyalMailErrorSerializer,
        },
        tags=["Royal Mail"]
    )
    def get_queryset(self):
        return Order.objects.filter(tracking_number__isnull=False)

class RoyalMailLabelView(generics.GenericAPIView):
    """
    Download Royal Mail shipping label
    """
    permission_classes = [permissions.IsAdminUser]
    authentication_classes = [CustomJWTAuthentication, SessionAuthentication]

    @extend_schema(
        description="Download a shipping label PDF",
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.BINARY,
                description="PDF file containing the shipping label",
                media_type="application/pdf"
            ),
            400: RoyalMailErrorSerializer,
            404: RoyalMailErrorSerializer,
            500: RoyalMailErrorSerializer,
        },
        tags=["Royal Mail"]
    )
    def get(self, request, order_id):
        """Download shipping label PDF"""
        logger.info(
            "royal_mail_label_download_started",
            order_id=order_id,
            user_id=request.user.id
        )

        try:
            order = Order.objects.get(order_id=order_id)

            if not order.tracking_number:
                logger.warning("royal_mail_no_label_available", order_id=order_id)
                return Response(
                    {'error': 'No shipping label available for this order'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            royal_mail = RoyalMailService()
            label_pdf = royal_mail.get_shipping_label(order.tracking_number)

            logger.info(
                "royal_mail_label_downloaded",
                order_id=order_id,
                tracking_number=order.tracking_number
            )

            response = HttpResponse(label_pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="shipping_label_{order.order_id}.pdf"'
            return response

        except Order.DoesNotExist:
            logger.error("royal_mail_order_not_found", order_id=order_id)
            return Response(
                {'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.exception("royal_mail_label_download_failed", error=str(e))
            return Response(
                {'error': 'Failed to download shipping label'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
