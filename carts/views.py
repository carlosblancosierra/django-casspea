from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Cart, CartItem, Product
from .serializers import CartSerializer, CartItemCreateSerializer, CartUpdateSerializer
from products.models import Product
import logging
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, inline_serializer
from drf_spectacular.types import OpenApiTypes
from discounts.models import Discount
from rest_framework import serializers

logger = logging.getLogger(__name__)

class SessionCartView(APIView):
    def get_cart(self, request):
        if not request.session.session_key:
            request.session.create()
        cart, _ = Cart.objects.get_or_create(session_id=request.session.session_key)
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
                    help_text="Discount code to apply (empty string to remove)"
                )
            }
        ),
        responses={
            200: CartSerializer,
            400: OpenApiTypes.OBJECT
        },
        examples=[
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
            OpenApiExample(
                'Remove Discount Example',
                value={'discount_code': ''},
                request_only=True,
            ),
            OpenApiExample(
                'Complete Example',
                value={
                    'gift_message': 'Happy Birthday!',
                    'shipping_date': '2024-12-25',
                    'discount_code': 'BLACK24'
                },
                request_only=True,
            )
        ],
        description="Update cart with optional gift message, shipping date, and/or discount code"
    )
    def post(self, request):
        """Update cart details"""
        cart = self.get_cart(request)
        serializer = CartUpdateSerializer(cart, data=request.data, partial=True)

        if serializer.is_valid():
            cart = serializer.save()
            return Response({
                "detail": "Cart updated successfully",
                "cart": CartSerializer(cart).data
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CartItemsView(APIView):
    def get_cart(self, request):
        if not request.session.session_key:
            request.session.create()
        cart, _ = Cart.objects.get_or_create(session_id=request.session.session_key)
        return cart

    @extend_schema(
        summary="Add item to cart",
        request=CartItemCreateSerializer,
        responses={
            201: CartSerializer,
            400: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT
        },
        examples=[
            OpenApiExample(
                'Valid Request',
                value={
                    "product": 1,
                    "quantity": 1,
                    "box_customization": {
                        "selection_type": "PICK_AND_MIX",
                        "allergens": [1],
                        "flavor_selections": [
                            {"flavor": 1, "quantity": 24},
                            {"flavor": 2, "quantity": 24}
                        ]
                    }
                }
            )
        ]
    )
    def post(self, request):
        """Add item to cart"""
        cart = self.get_cart(request)
        serializer = CartItemCreateSerializer(data=request.data)

        # Validate product ID and quantity
        product_id = request.data.get('product')
        quantity = int(request.data.get('quantity', 1))

        #
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

        logger.debug(f"CartItemsView post request data: {request.data}")

        if serializer.is_valid():
            try:
                cart_item = serializer.save(cart=cart)
                cart.refresh_from_db()
                cart_serializer = CartSerializer(cart)
                return Response(cart_serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Error creating cart item: {str(e)}")
                return Response(
                    {"detail": str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )

        logger.debug(f"Validation errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CartItemView(APIView):
    def get_cart(self, request):
        if not request.session.session_key:
            request.session.create()
        cart, _ = Cart.objects.get_or_create(session_id=request.session.session_key)
        return cart

    @extend_schema(
        summary="Update cart item",
        parameters=[
            OpenApiParameter(
                name='pk',
                type=int,
                location=OpenApiParameter.PATH,
                description='Cart item ID'
            )
        ],
        request=CartItemCreateSerializer,
        responses={
            200: CartSerializer,
            400: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT
        }
    )
    def put(self, request, pk):
        """Update cart item"""
        try:
            cart = self.get_cart(request)
            cart_item = CartItem.objects.get(pk=pk, cart=cart)

            # Validate product ID and quantity if provided
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

            # Debug logging
            logger.debug(f"Update request data: {request.data}")

            serializer = CartItemCreateSerializer(cart_item, data=request.data, partial=True)

            if serializer.is_valid():
                cart_item = serializer.save()
                cart.refresh_from_db()
                cart_serializer = CartSerializer(cart)
                return Response(cart_serializer.data, status=status.HTTP_200_OK)

            # Debug logging
            logger.debug(f"Update validation errors: {serializer.errors}")
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        except CartItem.DoesNotExist:
            return Response(
                {"detail": "Cart item not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error updating cart item: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        summary="Delete cart item",
        parameters=[
            OpenApiParameter(
                name='pk',
                type=int,
                location=OpenApiParameter.PATH,
                description='Cart item ID'
            )
        ],
        responses={
            200: CartSerializer,
            404: OpenApiTypes.OBJECT
        }
    )
    def delete(self, request, pk):
        """Remove item from cart"""
        try:
            cart = self.get_cart(request)
            cart_item = CartItem.objects.get(pk=pk, cart=cart)
            cart_item.delete()
            cart.refresh_from_db()
            cart_serializer = CartSerializer(cart)
            return Response(cart_serializer.data, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            return Response(
                {"detail": "Cart item not found"},
                status=status.HTTP_404_NOT_FOUND
            )

class CartDiscountView(APIView):
    def get_cart(self, request):
        """Get or create session cart"""
        if not request.session.session_key:
            request.session.create()
        cart, _ = Cart.objects.get_or_create(session_id=request.session.session_key)
        return cart

    @extend_schema(
        summary="Apply discount to cart",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'code': {'type': 'string', 'description': 'Discount code'}
                },
                'required': ['code']
            }
        },
        responses={
            200: CartSerializer,
            400: {"type": "object", "properties": {"detail": {"type": "string"}}}
        }
    )
    def post(self, request):
        """Apply discount to cart"""
        code = request.data.get('code')
        if not code:
            return Response(
                {"detail": "Discount code is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart = self.get_cart(request)

        # Validate discount using manager
        is_valid, message, discount = Discount.objects.validate_discount_for_cart(code, cart)

        if not is_valid:
            return Response(
                {"detail": message},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Replace any existing discount
        cart.discount = discount
        cart.save()

        # Format discount amount for message
        discount_amount = (
            f"{discount.amount}%"
            if discount.discount_type == Discount.PERCENTAGE
            else f"£{discount.amount}"
        )

        return Response({
            "detail": message,
            "cart": CartSerializer(cart).data
        })

    @extend_schema(
        summary="Remove discount from cart",
        responses={
            200: {"type": "object", "properties": {
                "detail": {"type": "string"},
                "cart": {"type": "object"}
            }}
        }
    )
    def delete(self, request):
        """Remove discount from cart"""
        cart = self.get_cart(request)

        if not cart.discount:
            return Response({
                "detail": "No discount applied to cart",
                "cart": CartSerializer(cart).data
            })

        cart.discount = None
        cart.save()

        return Response({
            "detail": "Discount removed from cart",
            "cart": CartSerializer(cart).data
        })
