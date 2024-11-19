from django.db import models
from django.core.exceptions import ValidationError
import structlog

logger = structlog.get_logger(__name__)

class CheckoutSessionManager(models.Manager):
    def get_or_create_from_request(self, request):
        """
        Get or create checkout session from request.
        Handles cart creation/retrieval internally.
        """
        from carts.models import Cart

        logger.debug(
            "creating_checkout_from_request",
            user_id=getattr(request.user, 'id', None),
            session_id=request.session.session_key
        )

        try:
            # Get or create cart first
            cart = Cart.objects.get_or_create_from_request(request)[0]

            # Try to get existing checkout session for this cart
            checkout_session = self.filter(cart=cart).order_by('-created').first()

            if checkout_session:
                logger.info(
                    "existing_checkout_session_found",
                    checkout_session_id=checkout_session.id,
                    cart_id=cart.id
                )
                # Update email if provided in request
                if not cart.user and 'email' in request.data:
                    checkout_session.email = request.data['email']
                    checkout_session.save()
                return checkout_session

            # For new session
            email = None
            if cart.user:
                email = cart.user.email
            elif 'email' in request.data:
                email = request.data['email']

            # Create new session
            checkout_session = self.create(
                cart=cart,
                email=email
            )

            logger.info(
                "new_checkout_session_created",
                checkout_session_id=checkout_session.id,
                cart_id=cart.id,
                is_guest=not cart.user,
                email=email
            )

            return checkout_session

        except Exception as e:
            logger.error(
                "checkout_session_creation_failed",
                error=str(e),
                user_id=getattr(request.user, 'id', None),
                exc_info=True
            )
            raise

    def validate_session(self, session_id):
        """
        Validate a checkout session is ready for payment.

        Args:
            session_id: ID of the checkout session

        Returns:
            CheckoutSession instance

        Raises:
            ValidationError: If session is invalid
        """
        try:
            session = self.get(id=session_id)

            if not session.shipping_address:
                raise ValidationError("Shipping address is required")

            if not session.email and not session.cart.user:
                raise ValidationError("Email is required for guest checkout")

            if not session.cart.items.exists():
                raise ValidationError("Cart is empty")

            if session.payment_status != self.model.PAYMENT_STATUS_PENDING:
                raise ValidationError("Session is not in pending status")

            logger.info(
                "checkout_session_validated",
                checkout_session_id=session.id,
                cart_id=session.cart.id
            )

            return session

        except self.model.DoesNotExist:
            logger.warning(
                "checkout_session_not_found",
                session_id=session_id
            )
            raise ValidationError("Checkout session not found")
        except ValidationError as e:
            logger.warning(
                "checkout_session_validation_failed",
                session_id=session_id,
                error=str(e)
            )
            raise
