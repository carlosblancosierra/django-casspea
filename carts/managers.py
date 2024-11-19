import structlog
from django.db import models

logger = structlog.get_logger(__name__)

class CartManager(models.Manager):
    def get_or_create_from_request(self, request):
        """
        Get or create a cart based on session or user.
        """
        logger.info(
            "cart_request_started",
            user_id=getattr(request.user, 'id', None),
            session_id=request.session.session_key,
            is_authenticated=request.user.is_authenticated
        )

        if request.user.is_authenticated:
            # First try to get existing active cart
            cart = self.filter(
                user=request.user,
                active=True
            ).order_by('-created').first()

            if cart:
                logger.info(
                    "found_existing_user_cart",
                    cart_id=cart.id,
                    user_id=request.user.id,
                    items_count=cart.items.count()
                )
                return cart, False

            # Create new cart for user
            logger.info(
                "creating_new_user_cart",
                user_id=request.user.id
            )
            cart = self.create(
                user=request.user,
                session_id=None,
                active=True
            )

            logger.info(
                "new_user_cart_created",
                cart_id=cart.id,
                user_id=cart.user_id,
                session_id=cart.session_id
            )
            return cart, True

        # For anonymous users only
        if not request.session.session_key:
            request.session.create()
            logger.info(
                "created_new_session",
                session_id=request.session.session_key
            )

        # Check existing session carts
        existing_carts = self.filter(
            session_id=request.session.session_key,
            user__isnull=True,
            active=True
        ).order_by('-created')

        logger.debug(
            "existing_session_carts",
            session_id=request.session.session_key,
            carts_count=existing_carts.count(),
            carts=[{
                'id': c.id,
                'created': c.created,
                'items_count': c.items.count()
            } for c in existing_carts]
        )

        cart = existing_carts.first()
        if cart:
            logger.info(
                "found_existing_session_cart",
                cart_id=cart.id,
                session_id=request.session.session_key,
                items_count=cart.items.count(),
                created=cart.created
            )
            return cart, False

        logger.info(
            "creating_new_session_cart",
            session_id=request.session.session_key
        )
        cart = self.create(
            session_id=request.session.session_key,
            user=None,
            active=True
        )
        return cart, True
