from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertFalse(user.is_customer)
        self.assertEqual(user.display_name, '')
    
    def test_create_customer(self):
        user = User.objects.create_user(
            username='customer',
            email='customer@example.com',
            password='testpass123',
            is_customer=True,
            display_name='John Doe'
        )
        self.assertTrue(user.is_customer)
        self.assertEqual(user.display_name, 'John Doe')
        self.assertEqual(str(user), 'John Doe')