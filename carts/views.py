from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Cart, CartItem, Product
from .serializers import CartSerializer, CartItemCreateSerializer
from products.models import Product
import logging

logger = logging.getLogger(__name__)

class SessionCartView(APIView):
    def get_cart(self, request):
        if not request.session.session_key:
            request.session.create()
        cart, _ = Cart.objects.get_or_create(session_id=request.session.session_key)
        return cart

    def get(self, request):
        """Get or create a session cart"""
        cart = self.get_cart(request)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

class CartItemsView(APIView):
    def get_cart(self, request):
        if not request.session.session_key:
            request.session.create()
        cart, _ = Cart.objects.get_or_create(session_id=request.session.session_key)
        return cart

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
