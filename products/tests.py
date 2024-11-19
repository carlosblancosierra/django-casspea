from django.test import TestCase
from rest_framework.test import APIClient

class BaseAPITest(TestCase):
    fixtures = [
        'initial_discounts.json',
        'initial_products.json',
        'initial_product_category.json',
        'initial_allergens.json'
    ]

    def setUp(self):
        self.client = APIClient()

class ProductAPITest(BaseAPITest):
    def test_list_products(self):
        """Test GET /api/products/ endpoint"""
        response = self.client.get('/api/products/')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.data, list))
        self.assertEqual(len(response.data), 4)  # 3 products from fixtures

        # Verify first product (48-piece box)
        product = next(p for p in response.data if p['id'] == 1)
        self.assertEqual(product['name'], "Signature Box of 48 Hand Made Chocolates")
        self.assertEqual(product['slug'], "48-bonbons")
        self.assertEqual(product['base_price'], "74.99")
        self.assertEqual(product['units_per_box'], 48)

    def test_get_product_by_slug(self):
        """Test GET /api/products/{slug}/ endpoint"""
        response = self.client.get('/api/products/48-bonbons/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], 1)
        self.assertEqual(response.data['name'], "Signature Box of 48 Hand Made Chocolates")
        self.assertEqual(response.data['base_price'], "74.99")
        self.assertEqual(response.data['category']['name'], "Signature Boxes")

    def test_get_product_invalid_slug(self):
        """Test GET /api/products/{slug}/ with invalid slug"""
        response = self.client.get('/api/products/invalid-slug/')
        self.assertEqual(response.status_code, 404)
