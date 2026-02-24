from django.test import TestCase, Client
from django.urls import reverse
from .models import Category, Product, Size, Inventory

class ProductCatalogTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Test Category', slug='test-cat')
        self.product = Product.objects.create(
            category=self.category,
            name='Test Product',
            price=100.00,
            slug='test-product'
        )

    def test_catalog_view(self):
        response = self.client.get(reverse('products:product_list'))
        print(f"Status Code: {response.status_code}")
        if response.status_code != 200:
             print("Context:", response.context)
             # print("Content:", response.content.decode('utf-8'))