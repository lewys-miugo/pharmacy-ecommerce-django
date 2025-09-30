from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from categories.models import Category
from products.models import Product
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed the database with pharmacy sample data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database with pharmacy data...')
        
        # Create pharmacy categories
        categories_data = [
            {'name': 'Prescription Medicines', 'slug': 'prescription-medicines'},
            {'name': 'Over-the-Counter', 'slug': 'over-the-counter'},
            {'name': 'Vitamins & Supplements', 'slug': 'vitamins-supplements'},
            {'name': 'Personal Care', 'slug': 'personal-care'},
            {'name': 'Medical Devices', 'slug': 'medical-devices'},
        ]
        
        created_categories = {}
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={'name': cat_data['name']}
            )
            created_categories[cat_data['name']] = category
            if created:
                self.stdout.write(f'Created category: {category.name}')
        
        # Create pharmacy products
        products_data = [
            {
                'name': 'Amoxicillin 500mg (Capsules)',
                'sku': 'RX001',
                'description': 'Broad-spectrum antibiotic used to treat bacterial infections. Requires prescription.',
                'price': Decimal('9.99'),
                'stock_quantity': 200,
                'categories': ['Prescription Medicines']
            },
            {
                'name': 'Ibuprofen 200mg (Tablets)',
                'sku': 'OTC001',
                'description': 'Pain reliever and fever reducer. Available over the counter.',
                'price': Decimal('4.99'),
                'stock_quantity': 500,
                'categories': ['Over-the-Counter']
            },
            {
                'name': 'Vitamin C 1000mg (30 Tablets)',
                'sku': 'VIT001',
                'description': 'Supports immune system health. Daily dietary supplement.',
                'price': Decimal('7.49'),
                'stock_quantity': 300,
                'categories': ['Vitamins & Supplements']
            },
            {
                'name': 'Multivitamin Gummies (60 Count)',
                'sku': 'VIT002',
                'description': 'Chewable multivitamins with essential nutrients for daily health.',
                'price': Decimal('12.99'),
                'stock_quantity': 150,
                'categories': ['Vitamins & Supplements']
            },
            {
                'name': 'Hand Sanitizer 500ml',
                'sku': 'CARE001',
                'description': 'Kills 99.9% of germs. Contains moisturizing aloe.',
                'price': Decimal('3.49'),
                'stock_quantity': 400,
                'categories': ['Personal Care']
            },
            {
                'name': 'Blood Pressure Monitor',
                'sku': 'DEV001',
                'description': 'Digital blood pressure monitor for home use.',
                'price': Decimal('49.99'),
                'stock_quantity': 40,
                'categories': ['Medical Devices']
            },
            {
                'name': 'Digital Thermometer',
                'sku': 'DEV002',
                'description': 'Quick-read thermometer with flexible tip.',
                'price': Decimal('14.99'),
                'stock_quantity': 80,
                'categories': ['Medical Devices']
            },
        ]
        
        for prod_data in products_data:
            product, created = Product.objects.get_or_create(
                sku=prod_data['sku'],
                defaults={
                    'name': prod_data['name'],
                    'description': prod_data['description'],
                    'price': prod_data['price'],
                    'stock_quantity': prod_data['stock_quantity']
                }
            )
            
            if created:
                for cat_name in prod_data['categories']:
                    if cat_name in created_categories:
                        product.categories.add(created_categories[cat_name])
                
                self.stdout.write(f'Created product: {product.name}')
        
        # Create a sample admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@pharmacy.com',
                'display_name': 'Pharmacy Admin',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write('Created admin user: admin/admin123')
        
        # Create a sample customer
        customer, created = User.objects.get_or_create(
            username='customer',
            defaults={
                'email': 'customer@pharmacy.com',
                'display_name': 'Jane Customer',
                'is_customer': True
            }
        )
        if created:
            customer.set_password('customer123')
            customer.save()
            self.stdout.write('Created customer: customer/customer123')
        
        # Create a test user for testing functionalities
        test_user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@pharmacy.com',
                'display_name': 'Test User',
                'is_customer': True
            }
        )
        if created:
            test_user.set_password('test123')
            test_user.save()
            self.stdout.write('Created test user: testuser/test123')
        
        self.stdout.write(self.style.SUCCESS('Pharmacy database seeded successfully!'))
