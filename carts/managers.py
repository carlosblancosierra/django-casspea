from django.db import models

class CartManager(models.Manager):
    def get_or_create_from_request(self, request):
        """
        Get or create a cart based on session or user.
        """
        if request.user.is_authenticated:
            # First try to get existing active cart
            cart = self.filter(
                user=request.user,
                active=True
            ).order_by('-created').first()

            if cart:
                return cart, False

            # If no cart exists, create new one
            cart = self.create(
                user=request.user,
                active=True
            )
            return cart, True

        # For anonymous users
        if not request.session.session_key:
            request.session.create()

        # First try to get existing active cart
        cart = self.filter(
            session_id=request.session.session_key,
            active=True
        ).order_by('-created').first()

        if cart:
            return cart, False

        # If no cart exists, create new one
        cart = self.create(
            session_id=request.session.session_key,
            active=True
        )
        return cart, True
