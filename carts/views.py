from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Cart, CartItem, Product
from .serializers import CartSerializer, CartItemCreateSerializer, CartUpdateSerializer, CartItemQuantityUpdateSerializer
from products.models import Product
import logging
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, inline_serializer
from drf_spectacular.types import OpenApiTypes
from discounts.models import Discount
from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

logger = logging.getLogger(__name__)

class CartView(APIView):
    def get_cart(self, request):
        cart, _ = Cart.objects.get_or_create_from_request(request)
        return cart

    @extend_schema(
        summary="Get or create session cart",
        description="Returns the current cart for the session or creates a new one",
        responses={200: CartSerializer}
    )
    def get(self, request):
        """Get or create a session cart"""
        cart = self.get_cart(request)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @extend_schema(
        summary="Update cart details",
        request=inline_serializer(
            name='CartDetailsUpdate',
            fields={
                'gift_message': serializers.CharField(
                    required=False,
                    allow_null=True,
                    help_text="Optional gift message"
                ),
                'shipping_date': serializers.DateField(
                    required=False,
                    allow_null=True,
                    help_text="Optional shipping date (YYYY-MM-DD)"
                ),
                'discount_code': serializers.CharField(
                    required=False,
                    allow_null=True,
                    help_text="Discount code to apply"
                ),
                'remove_discount': serializers.BooleanField(
                    required=False,
                    help_text="Set to true to remove the current discount"
                )
            }
        ),
        responses={
            200: CartSerializer,
            400: OpenApiTypes.OBJECT
        },
        examples=[
            OpenApiExample(
                'Complete Example',
                value={
                    'gift_message': 'Happy Birthday!',
                    'shipping_date': '2024-12-25',
                    'discount_code': 'BLACK24'
                },
                request_only=True,
            ),
            OpenApiExample(
                'Remove Discount Example',
                value={'remove_discount': True},
                request_only=True,
            ),
            OpenApiExample(
                'Gift Message Example',
                value={'gift_message': 'Happy Birthday!'},
                request_only=True,
            ),
            OpenApiExample(
                'Shipping Date Example',
                value={'shipping_date': '2024-12-25'},
                request_only=True,
            ),
            OpenApiExample(
                'Discount Example',
                value={'discount_code': 'SUMMER2023'},
                request_only=True,
            ),

        ],
        description="Update cart with optional gift message, shipping date, and/or discount code"
    )
    def post(self, request):
        """Update cart details"""
        cart = self.get_cart(request)

        # Create a mutable copy of the request data
        data = request.data.copy()
        logger.debug(f"Update request data: {data}")
        # Handle discount removal first
        if data.get('remove_discount'):
            cart.discount = None
            cart.save()
            data.pop('remove_discount', None)

        serializer = CartUpdateSerializer(cart, data=data, partial=True)

        if serializer.is_valid():
            cart = serializer.save()
            return Response({
                "detail": "Cart updated successfully",
                "cart": CartSerializer(cart).data
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CartItemViewSet(viewsets.ViewSet):

    @extend_schema(
        summary="Add item to cart",
        request=CartItemCreateSerializer,
        responses={201: CartSerializer},
        examples=[
            OpenApiExample(
                'Random Box Example',
                value={
                    "product": 1,
                    "quantity": 3,
                    "box_customization": {
                        "selection_type": "RANDOM",
                        "allergens": [
                            1
                        ]
                    }
                },
                request_only=True,
            ),
            OpenApiExample(
                'Custom Box Example',
                value={
                    "product": 1,
                    "quantity": 3,
                    "box_customization": {
                        "selection_type": "CUSTOM",
                        "flavor_selections": [
                            {
                                "flavor": 1,
                                "quantity": 48
                            }
                        ]
                    }
                },
                request_only=True,
            )
        ]
    )
    def create(self, request):
        """POST /items/"""
        cart, _ = Cart.objects.get_or_create_from_request(request)
        serializer = CartItemCreateSerializer(data=request.data)

        # Validate product ID and quantity
        product_id = request.data.get('product')
        quantity = int(request.data.get('quantity', 1))

        try:
            product = Product.objects.get(pk=product_id)
            if quantity < 1:
                return Response(
                    {"detail": "Quantity must be greater than 0"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Product.DoesNotExist:
            return Response(
                {"detail": "Product not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        logger.debug(f"CartItemView post request data: {request.data}")

        if serializer.is_valid():
            try:
                cart_item = serializer.save(cart=cart)
                cart.refresh_from_db()
                return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Error creating cart item: {str(e)}")
                return Response(
                    {"detail": str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )

        logger.debug(f"Validation errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Update cart item",
        request=CartItemCreateSerializer,
        responses={200: CartSerializer}
    )
    def update(self, request, pk=None):
        """PUT /items/{pk}/"""
        cart = self.get_cart(request)
        cart_item = CartItem.objects.get(pk=pk, cart=cart)

        product_id = request.data.get('product')
        quantity = request.data.get('quantity')

        if product_id:
            try:
                product = Product.objects.get(pk=product_id)
            except Product.DoesNotExist:
                return Response(
                    {"detail": "Product not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

        if quantity is not None and int(quantity) < 1:
            return Response(
                {"detail": "Quantity must be greater than 0"},
                status=status.HTTP_400_BAD_REQUEST
            )

        logger.debug(f"Update request data: {request.data}")
        serializer = CartItemCreateSerializer(cart_item, data=request.data, partial=True)

        if serializer.is_valid():
            cart_item = serializer.save()
            cart.refresh_from_db()
            return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

        logger.debug(f"Update validation errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Delete cart item",
        responses={200: CartSerializer}
    )
    def destroy(self, request, pk=None):
        """DELETE /items/{pk}/"""
        cart = self.get_cart(request)
        cart_item = CartItem.objects.get(pk=pk, cart=cart)
        cart_item.delete()
        cart.refresh_from_db()
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete'], url_path='remove', url_name='remove')
    @extend_schema(
        summary="Remove cart item",
        responses={200: CartSerializer},
        description="Removes a specific item from the cart."
    )
    def remove(self, request, pk=None):
        """
        Remove a cart item from the cart.
        """
        cart, _ = Cart.objects.get_or_create_from_request(request)
        cart_item = get_object_or_404(CartItem, pk=pk, cart=cart)
        cart_item.delete()
        cart.refresh_from_db()
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='change-quantity', url_name='change_quantity')
    @extend_schema(
        summary="Change quantity of a cart item",
        request=CartItemQuantityUpdateSerializer,
        responses={200: CartSerializer},
        description="Updates the quantity of a specific cart item."
    )
    def change_quantity(self, request, pk=None):
        """
        Change the quantity of a cart item.
        """
        cart, _ = Cart.objects.get_or_create_from_request(request)
        cart_item = get_object_or_404(CartItem, pk=pk, cart=cart)
        serializer = CartItemQuantityUpdateSerializer(cart_item, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            cart.refresh_from_db()
            return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
