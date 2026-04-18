from django.test import TestCase

from shop.models import Product, ProductCategory


class ProductModelTests(TestCase):
    def test_product_str(self):
        category = ProductCategory.objects.create(
            name="Test_Category",
        )
        product = Product.objects.create(
            name="Test_Product",
            category=category,
            price=200,
        )
        self.assertEqual(
            str(product),
            "Test_Product"
        )

class ProductCategoryModelTests(TestCase):
    def test_product_str(self):
        category = ProductCategory.objects.create(
            name="Test_Category",
        )
        self.assertEqual(
            str(category),
            "Test_Category"
        )