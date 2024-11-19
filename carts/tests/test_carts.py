from decimal import Decimal
from .test_base import BaseAPITest
from carts.models import Cart

class CartAPITest(BaseAPITest):
    def test_get_or_create_cart(self):
        """Test GET /api/carts/ endpoint"""
        response = self.client.get('/api/carts/')

        self.assertEqual(response.status_code, 200)
        self.assertIn('id', response.data)
        self.assertIn('items', response.data)
        self.assertIn('total', response.data)

        # Verify cart was created
        cart_id = response.data['id']
        self.assertTrue(Cart.objects.filter(id=cart_id).exists())

        # Test session persistence
        response2 = self.client.get('/api/carts/')
        self.assertEqual(response2.data['id'], cart_id)

    def test_add_item_to_cart_pick_and_mix(self):
        """Test POST /api/carts/items/ endpoint"""
        # First create a cart
        cart_response = self.client.get('/api/carts/')

        # Add 9-piece box to cart
        data = {
            "product": 4,  # 9-piece box
            "quantity": 2,
            "box_customization": {
                "selection_type": "PICK_AND_MIX",
                "allergens": [1],  # Milk solids
                "flavor_selections": [
                    {
                        "flavor": 1,
                        "quantity": 9
                    }
                ]
            }
        }

        response = self.client.post('/api/carts/items/', data, format='json')
        print("Response status:", response.status_code)
        print("Response data:", response.data)  # This will show the validation errors

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(response.data['items']), 1)
        self.assertEqual(response.data['items'][0]['product']['id'], 4)  # Changed to match product ID
        self.assertEqual(response.data['items'][0]['quantity'], 2)
        self.assertEqual(response.data['total'], '29.98')  # 14.99 * 2

    def test_add_item_to_cart_random(self):
        """Test POST /api/carts/items/ endpoint"""
        # First create a cart
        cart_response = self.client.get('/api/carts/')

        # Add 9-piece box to cart
        data = {
            "product": 4,  # 9-piece box
            "quantity": 2,
            "box_customization": {
                "selection_type": "RANDOM",
                "allergens": [1],  # Milk solids
            }
        }

        response = self.client.post('/api/carts/items/', data, format='json')
        print("Response status:", response.status_code)
        print("Response data:", response.data)  # This will show the validation errors

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(response.data['items']), 1)

        # Verify cart total
        self.assertEqual(response.data['total'], '29.98')  # 14.99 * 2

    def test_update_cart_details(self):
        """Test POST /api/carts/ endpoint"""
        # First create a cart
        cart_response = self.client.get('/api/carts/')

        # Update cart details
        data = {
            "discount_code": "NEWS10",  # Changed from discount to discount_code
            "gift_message": "Happy Birthday!",
            "shipping_date": "2024-12-25"
        }

        response = self.client.post('/api/carts/', data, format='json')
        print("Response status:", response.status_code)
        print("Response data:", response.data)

        self.assertEqual(response.status_code, 200)

        # Access the nested cart data
        cart_data = response.data['cart']
        self.assertEqual(cart_data['gift_message'], "Happy Birthday!")
        self.assertEqual(cart_data['shipping_date'], "2024-12-25")

        # If you need to verify the discount was applied
        if 'discount' in cart_data and cart_data['discount']:
            self.assertEqual(cart_data['discount']['code'], "NEWS10")
