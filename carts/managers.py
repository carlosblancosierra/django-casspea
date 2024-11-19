from django.db import models

class CartManager(models.Manager):
    def get_or_create_from_request(self, request):
        """
        Get or create a cart based on session or user.

        Args:
            request: The HTTP request object

        Returns:
            Cart: The retrieved or newly created cart
        """
        # If user is authenticated, get/create cart by user
        if request.user.is_authenticated:
            return self.get_or_create(user=request.user, active=True)

        # For anonymous users, use session
        if not request.session.session_key:
            request.session.create()

        return self.get_or_create(
            session_id=request.session.session_key,
            active=True
        )
