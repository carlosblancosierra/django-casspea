import structlog
from django.db import models

logger = structlog.get_logger(__name__)

class OrderManager(models.Manager):
    def create_from_checkout(self, checkout_session):
        """
        Create a new order from a completed checkout session
        """
        try:
            # Check if order already exists
            if self.filter(checkout_session=checkout_session).exists():
                logger.info(
                    "order_already_exists",
                    checkout_session_id=checkout_session.id
                )
                return self.objects.get(checkout_session=checkout_session)

            logger.info(
                "creating_order_from_checkout",
                checkout_session_id=checkout_session.id,
                cart_id=checkout_session.cart.id
            )

            # Create the order
            order = self.create(
                checkout_session=checkout_session,
                status='processing'
            )

            logger.info(
                "order_created_successfully",
                order_id=order.order_id,
                checkout_session_id=checkout_session.id
            )

            return order

        except Exception as e:
            logger.error(
                "order_creation_failed",
                error=str(e),
                checkout_session_id=checkout_session.id,
                exc_info=True
            )
            raise
