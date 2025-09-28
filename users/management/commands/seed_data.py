from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from categories.models import Category
from products.models import Product
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed the database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')
        
        # Create categories
        categories_data = [
            {'name': 'Electronics', 'slug': 'electronics', 'parent': None},
            {'name': 'Clothing', 'slug': 'clothing', 'parent': None},
            {'name': 'Phones', 'slug': 'phones', 'parent': 'Electronics'},
            {'name': 'Laptops', 'slug': 'laptops', 'parent': 'Electronics'},
            {'name': "Men's Clothing", 'slug': 'mens-clothing', 'parent': 'Clothing'},
            {'name': "Women's Clothing", 'slug': 'womens-clothing', 'parent': 'Clothing'},
        ]
        
        created_categories = {}
        for cat_data in categories_data:
            parent = None
            if cat_data['parent']:
                parent = created_categories.get(cat_data['parent'])
            
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={
                    'name': cat_data['name'],
                    'parent': parent
                }
            )
            created_categories[cat_data['name']] = category
            if created:
                self.stdout.write(f'Created category: {category.name}')
        
        # Create products
        products_data = [
            {
                'sku': 'PHONE001',
                'name': 'iPhone 15',
                'description': 'Latest iPhone with advanced features',
                'price': Decimal('999.99'),
                'categories': ['Electronics', 'Phones']
            },
            {
                'sku': 'PHONE002',
                'name': 'Samsung Galaxy S24',
                'description': 'Premium Android smartphone',
                'price': Decimal('899.99'),
                'categories': ['Electronics', 'Phones']
            },
            {
                'sku': 'LAPTOP001',
                'name': 'MacBook Pro',
                'description': 'Professional laptop for developers',
                'price': Decimal('1999.99'),
                'categories': ['Electronics', 'Laptops']
            },
            {
                'sku': 'LAPTOP002',
                'name': 'Gaming Laptop X1',
                'description': 'High-performance gaming laptop',
                'price': Decimal('1499.99'),
                'categories': ['Electronics', 'Laptops']
            },
            {
                'sku': 'CLOTH001',
                'name': 'Cotton T-Shirt',
                'description': 'Comfortable cotton t-shirt',
                'price': Decimal('29.99'),
                'categories': ['Clothing', "Men's Clothing"]
            },
            {
                'sku': 'CLOTH002',
                'name': 'Summer Dress',
                'description': 'Light and comfortable summer dress',
                'price': Decimal('79.99'),
                'categories': ['Clothing', "Women's Clothing"]
            },
        ]
        
        for prod_data in products_data:
            product, created = Product.objects.get_or_create(
                sku=prod_data['sku'],
                defaults={
                    'name': prod_data['name'],
                    'description': prod_data['description'],
                    'price': prod_data['price']
                }
            )
            
            if created:
                # Add categories
                for cat_name in prod_data['categories']:
                    if cat_name in created_categories:
                        product.categories.add(created_categories[cat_name])
                
                self.stdout.write(f'Created product: {product.name}')
        
        # Create sample customer
        customer, created = User.objects.get_or_create(
            username='customer',
            defaults={
                'email': 'customer@example.com',
                'display_name': 'Sample Customer',
                'is_customer': True
            }
        )
        if created:
            customer.set_password('customer123')
            customer.save()
            self.stdout.write('Created sample customer: customer/customer123')
        
        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))
