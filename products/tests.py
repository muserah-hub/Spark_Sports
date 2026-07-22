from django.test import TestCase
from products.models import Category, Product

class ProductModelTest(TestCase):
    """
    Test suite for Categories and Products.
    """
    def setUp(self):
        # Create Category
        self.category = Category.objects.create(
            name="Cricket Bats",
            description="Premium English Willow Bats"
        )
        # Create Product
        self.product = Product.objects.create(
            category=self.category,
            name="Spark Pro Edition 2026",
            price=25000.00,
            discount_price=22000.00,
            stock=10,
            available=True
        )

    def test_slug_auto_generation(self):
        """
        Verify slugs are auto-generated from product/category names.
        """
        self.assertEqual(self.category.slug, "cricket-bats")
        self.assertEqual(self.product.slug, "spark-pro-edition-2026")

    def test_pricing_helpers(self):
        """
        Verify that active price returns discount price if it exists.
        """
        self.assertEqual(self.product.get_price, 22000.00)
        self.assertEqual(self.product.saving_amount, 3000.00)

    def test_stock_helpers(self):
        """
        Verify that inventory levels are tracked correctly.
        """
        self.assertTrue(self.product.is_in_stock)
        
        # Test out of stock helper
        self.product.stock = 0
        self.product.save()
        self.assertFalse(self.product.is_in_stock)
