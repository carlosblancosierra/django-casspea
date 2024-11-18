from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Cart, CartItem
from products.models import Product, ProductCategory
from flavours.models import Flavour, FlavourCategory
from allergens.models import Allergen
from decimal import Decimal

import logging

logger = logging.getLogger(__name__)

class CartAPITests(APITestCase):
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.cart_url = reverse('session-cart')
        self.items_url = reverse('cart-items')

        # Create test product category
        self.category = ProductCategory.objects.create(
            name="Test Category",
            slug="test-category",
            description="Test Description"
        )

        # Create test product
        self.product = Product.objects.create(
            name="Test Chocolate Box",
            description="Test Description",
            category=self.category,
            base_price=Decimal('19.99'),
            stripe_price_id="price_test123",
            slug="test-chocolate-box",
            weight=250,
            units_per_box=12,
            main_color="#000000",
            secondary_color="#FFFFFF",
            seo_title="Test SEO Title",
            seo_description="Test SEO Description"
        )

        # Create test flavour category
        self.flavour_category = FlavourCategory.objects.create(
            name="Test Flavour Category",
            slug="test-flavour-category"
        )

        # Create test flavours
        self.flavour1 = Flavour.objects.create(
            name="Dark Chocolate",
            slug="dark-chocolate",
            description="Test Description",
            mini_description="Mini Description",
            category=self.flavour_category
        )

        self.flavour2 = Flavour.objects.create(
            name="Milk Chocolate",
            slug="milk-chocolate",
            description="Test Description",
            mini_description="Mini Description",
            category=self.flavour_category
        )

        # Create test allergen
        self.allergen = Allergen.objects.create(
            name="Nuts",
            slug="nuts",
        )

    def test_create_session_cart(self):
        """Test creating a new session cart"""
        response = self.client.get(self.cart_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['items'], [])
        self.assertEqual(response.data['total'], '0')

    def test_get_existing_session_cart(self):
        """Test retrieving an existing session cart"""
        # First request creates the cart
        first_response = self.client.get(self.cart_url)
        cart_id = first_response.data['id']

        # Second request should retrieve the same cart
        second_response = self.client.get(self.cart_url)

        self.assertEqual(second_response.status_code, status.HTTP_200_OK)
        self.assertEqual(second_response.data['id'], cart_id)

    def test_session_persistence(self):
        """Test that the cart persists across requests"""
        # Create initial cart
        response = self.client.get(self.cart_url)
        session_id = self.client.session.session_key

        # Verify cart exists in database
        cart = Cart.objects.get(session_id=session_id)
        self.assertIsNotNone(cart)

        # Make another request
        response = self.client.get(self.cart_url)
        self.assertEqual(response.data['id'], cart.id)

    def test_add_item_to_cart(self):
        """Test adding an item to the cart"""
        # First create a cart
        cart_response = self.client.get(self.cart_url)
        cart_id = cart_response.data['id']

        # Add test for adding items once you implement the add_item endpoint
        # This is a placeholder for future implementation
        self.assertTrue(True)

    def test_anonymous_user_cart(self):
        """Test cart creation for anonymous user"""
        response = self.client.get(self.cart_url)

        self.assertIsNotNone(response.data['id'])
        self.assertIsNone(Cart.objects.get(id=response.data['id']).user)

    def test_add_customized_item_to_cart(self):
        """Test adding a customized item to cart"""
        # First create a cart
        self.client.get(self.cart_url)

        data = {
            "product": self.product.id,
            "quantity": 1,
            "box_customization": {
                "selection_type": "PICK_AND_MIX",
                "allergens": [self.allergen.id],
                "flavor_selections": [
                    {"flavor": self.flavour1.id, "quantity": 6},
                    {"flavor": self.flavour2.id, "quantity": 6}
                ]
            }
        }

        response = self.client.post(
            self.items_url,
            data=data,
            format='json'
        )

        logger.debug(f"Cart data: {response.data}")
        print(f"Cart data: {response.data}")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('items', response.data)
        self.assertEqual(len(response.data['items']), 1)
        item = response.data['items'][0]
        self.assertEqual(item['quantity'], 1)
        self.assertEqual(item['product']['id'], self.product.id)
        self.assertIn('box_customization', item)
