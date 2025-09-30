from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from decimal import Decimal
from products.models import Product
from categories.models import Category
from orders.models import Order, OrderItem

User = get_user_model()

class AdminViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.product = Product.objects.create(
            name='Test Product',
            sku='TEST001',
            description='Test Description',
            price=Decimal('10.00'),
            stock_quantity=5
        )

    def test_admin_dashboard_requires_login(self):
        """Test admin dashboard requires login"""
        response = self.client.get(reverse('frontend:admin_dashboard'))
        self.assertRedirects(response, f"{reverse('frontend:login')}?next={reverse('frontend:admin_dashboard')}")

    def test_admin_dashboard_authenticated(self):
        """Test admin dashboard works for authenticated users"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('frontend:admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard')

    def test_admin_products_list(self):
        """Test admin products list view"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('frontend:admin_products'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Product')

    def test_admin_product_create_get(self):
        """Test admin product create form"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('frontend:admin_product_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Product')

    def test_admin_product_create_post(self):
        """Test admin product creation"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.post(reverse('frontend:admin_product_create'), {
            'name': 'New Product',
            'sku': 'NEW001',
            'description': 'New Description',
            'price': '15.00',
            'stock_quantity': '10',
            'categories': [self.category.id]
        })
        
        self.assertRedirects(response, reverse('frontend:admin_products'))
        self.assertTrue(Product.objects.filter(name='New Product').exists())

    def test_admin_product_edit(self):
        """Test admin product editing"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.post(reverse('frontend:admin_product_edit', args=[self.product.id]), {
            'name': 'Updated Product',
            'sku': 'TEST001',
            'description': 'Updated Description',
            'price': '12.00',
            'stock_quantity': '8',
            'is_active': 'on',
            'categories': [self.category.id]
        })
        
        self.assertRedirects(response, reverse('frontend:admin_products'))
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'Updated Product')
        self.assertEqual(self.product.price, Decimal('12.00'))

    def test_admin_product_delete(self):
        """Test admin product deletion"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.post(reverse('frontend:admin_product_delete', args=[self.product.id]))
        
        self.assertRedirects(response, reverse('frontend:admin_products'))
        self.assertFalse(Product.objects.filter(id=self.product.id).exists())

    def test_admin_categories_list(self):
        """Test admin categories list view"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('frontend:admin_categories'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Category')

    def test_admin_category_create(self):
        """Test admin category creation"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.post(reverse('frontend:admin_category_create'), {
            'name': 'New Category',
            'slug': 'new-category'
        })
        
        self.assertRedirects(response, reverse('frontend:admin_categories'))
        self.assertTrue(Category.objects.filter(name='New Category').exists())

    def test_admin_orders_list(self):
        """Test admin orders list view"""
        self.client.login(username='admin', password='adminpass123')
        
        # Create test order
        order = Order.objects.create(
            guest_name='Test Customer',
            guest_email='test@example.com',
            total_amount=Decimal('10.00')
        )
        
        response = self.client.get(reverse('frontend:admin_orders'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Customer')

    def test_admin_order_detail_status_update(self):
        """Test admin can update order status"""
        self.client.login(username='admin', password='adminpass123')
        
        order = Order.objects.create(
            guest_name='Test Customer',
            guest_email='test@example.com',
            total_amount=Decimal('10.00'),
            status='pending'
        )
        
        response = self.client.post(reverse('frontend:admin_order_detail', args=[order.id]), {
            'status': 'processing'
        })
        
        order.refresh_from_db()
        self.assertEqual(order.status, 'processing')
        
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('status updated' in str(m) for m in messages))
