from django.test import TestCase
from rest_framework.test import APIClient

class BaseAPITest(TestCase):
    fixtures = [
        'initial_discounts.json',
        'initial_products.json',
        'initial_product_category.json',
        'initial_allergens.json',
        'initial_flavours.json',
        'initial_flavour_categories.json'
    ]

    def setUp(self):
        self.client = APIClient()
