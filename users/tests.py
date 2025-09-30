from django.test import TestCase
from django.contrib.auth import get_user_model
from .forms import CustomUserCreationForm

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

    def test_str_method_fallback(self):
        """Test __str__ method falls back to username when no display_name"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(str(user), 'testuser')


class CustomUserCreationFormTest(TestCase):
    def test_form_valid_data(self):
        """Test form with valid data"""
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'display_name': 'Test User',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_save(self):
        """Test form save creates user with correct attributes"""
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'display_name': 'Test User',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        user = form.save()
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.display_name, 'Test User')
        self.assertTrue(user.is_customer)
        self.assertTrue(user.check_password('complexpass123'))

    def test_form_save_without_display_name(self):
        """Test form save works without display_name"""
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'display_name': '',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        user = form.save()
        self.assertEqual(user.display_name, '')
        self.assertTrue(user.is_customer)

    def test_form_missing_email(self):
        """Test form validation fails without email"""
        form_data = {
            'username': 'testuser',
            'display_name': 'Test User',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_form_invalid_email(self):
        """Test form validation fails with invalid email"""
        form_data = {
            'username': 'testuser',
            'email': 'invalid-email',
            'display_name': 'Test User',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_form_password_mismatch(self):
        """Test form validation fails with password mismatch"""
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'display_name': 'Test User',
            'password1': 'complexpass123',
            'password2': 'differentpass123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_form_duplicate_username(self):
        """Test form validation fails with duplicate username"""
        # Create existing user
        User.objects.create_user(username='testuser', email='existing@example.com')
        
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'display_name': 'Test User',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_form_fields_present(self):
        """Test all required fields are present in form"""
        form = CustomUserCreationForm()
        expected_fields = ['username', 'email', 'display_name', 'password1', 'password2']
        for field in expected_fields:
            self.assertIn(field, form.fields)

    def test_form_help_text(self):
        """Test form help text is set correctly"""
        form = CustomUserCreationForm()
        self.assertEqual(
            form.fields['display_name'].help_text,
            'Optional: How you want to be displayed'
        )
