from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.http import HttpResponse
from .services import RoyalMailService
from .serializers import (
    RoyalMailOrderSerializer,
    RoyalMailOrderListSerializer
)
from orders.models import Order
from users.authentication import CustomJWTAuthentication
from rest_framework.authentication import SessionAuthentication
import structlog

logger = structlog.get_logger(__name__)

class RoyalMailOrderListView(generics.ListAPIView):
    """List Royal Mail orders"""
    permission_classes = [permissions.IsAdminUser]
    authentication_classes = [CustomJWTAuthentication, SessionAuthentication]
    serializer_class = RoyalMailOrderListSerializer

    def get_queryset(self):
        return Order.objects.filter(
            tracking_number__isnull=False
        ).select_related(
            'checkout_session',
            'checkout_session__shipping_option'
        )

class RoyalMailOrderCreateView(generics.CreateAPIView):
    """Create Royal Mail shipping label"""
    permission_classes = [permissions.IsAdminUser]
    authentication_classes = [CustomJWTAuthentication, SessionAuthentication]
    serializer_class = RoyalMailOrderSerializer

    def post(self, request, order_id):
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

            return Response({
                'success': True,
                'tracking_number': tracking_number,
                'order_identifier': created_order.get('orderIdentifier'),
                'label': created_order.get('label')
            }, status=status.HTTP_201_CREATED)

        except Order.DoesNotExist:
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
    """Get Royal Mail order details"""
    permission_classes = [permissions.IsAdminUser]
    authentication_classes = [CustomJWTAuthentication, SessionAuthentication]
    serializer_class = RoyalMailOrderSerializer
    lookup_field = 'order_id'

    def get_queryset(self):
        return Order.objects.filter(tracking_number__isnull=False)

class RoyalMailLabelView(generics.GenericAPIView):
    """Download Royal Mail shipping label"""
    permission_classes = [permissions.IsAdminUser]
    authentication_classes = [CustomJWTAuthentication, SessionAuthentication]

    def get(self, request, order_id):
        try:
            order = Order.objects.get(order_id=order_id)

            if not order.tracking_number:
                return Response(
                    {'error': 'No shipping label available for this order'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            royal_mail = RoyalMailService()
            label_pdf = royal_mail.get_shipping_label(order.tracking_number)

            response = HttpResponse(label_pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="shipping_label_{order.order_id}.pdf"'
            return response

        except Order.DoesNotExist:
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
