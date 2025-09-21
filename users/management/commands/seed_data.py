from django.core.management.base import BaseCommand
from django.utils.text import slugify
from categories.models import Category
from products.models import Product
from decimal import Decimal

class Command(BaseCommand):
    help = 'Seed database with sample categories and products (idempotent)'

    def handle(self, *args, **options):
        # Create category tree (4 levels)
        root, _ = Category.objects.get_or_create(
            slug='all-products',
            defaults={'name': 'All Products'}
        )

        # Level 2
        electronics, _ = Category.objects.get_or_create(
            slug='electronics', defaults={'name': 'Electronics', 'parent': root}
        )
        clothing, _ = Category.objects.get_or_create(
            slug='clothing', defaults={'name': 'Clothing', 'parent': root}
        )

        # Level 3
        phones, _ = Category.objects.get_or_create(
            slug='phones', defaults={'name': 'Phones', 'parent': electronics}
        )
        laptops, _ = Category.objects.get_or_create(
            slug='laptops', defaults={'name': 'Laptops', 'parent': electronics}
        )
        mens, _ = Category.objects.get_or_create(
            slug='mens-clothing', defaults={'name': "Men's Clothing", 'parent': clothing}
        )
        womens, _ = Category.objects.get_or_create(
            slug='womens-clothing', defaults={'name': "Women's Clothing", 'parent': clothing}
        )

        # Level 4
        smartphones, _ = Category.objects.get_or_create(
            slug='smartphones', defaults={'name': 'Smartphones', 'parent': phones}
        )
        gaming_laptops, _ = Category.objects.get_or_create(
            slug='gaming-laptops', defaults={'name': 'Gaming Laptops', 'parent': laptops}
        )

        # Create sample products (safe create_or_update)
        products_data = [
            {'sku': 'SKU001', 'name': 'iPhone 15', 'price': Decimal('999.99'), 'categories': [smartphones]},
            {'sku': 'SKU002', 'name': 'Samsung Galaxy S24', 'price': Decimal('899.99'), 'categories': [smartphones]},
            {'sku': 'SKU003', 'name': 'MacBook Pro', 'price': Decimal('1999.99'), 'categories': [laptops]},
            {'sku': 'SKU004', 'name': 'Gaming Laptop X1', 'price': Decimal('1499.99'), 'categories': [gaming_laptops]},
            {'sku': 'SKU005', 'name': 'Cotton T-Shirt', 'price': Decimal('29.99'), 'categories': [mens]},
            {'sku': 'SKU006', 'name': 'Summer Dress', 'price': Decimal('79.99'), 'categories': [womens]},
        ]

        for data in products_data:
            product, created = Product.objects.update_or_create(
                sku=data['sku'],
                defaults={
                    'name': data['name'],
                    'description': f'Description for {data["name"]}',
                    'price': data['price']
                }
            )
            product.categories.set(data['categories'])

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed completed: {Category.objects.count()} categories, {Product.objects.count()} products"
            )
        )
