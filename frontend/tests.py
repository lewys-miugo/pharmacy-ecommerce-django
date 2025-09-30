from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from users.forms import CustomUserCreationForm

User = get_user_model()

class AuthenticationViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            display_name='Test User'
        )
        self.customer = User.objects.create_user(
            username='customer',
            email='customer@example.com',
            password='customerpass123',
            is_customer=True,
            display_name='Customer User'
        )

    def test_login_view_get(self):
        """Test login page loads correctly"""
        response = self.client.get(reverse('frontend:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')
        self.assertContains(response, 'Username')
        self.assertContains(response, 'Password')

    def test_login_view_authenticated_user_redirect(self):
        """Test authenticated user is redirected from login page"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('frontend:login'))
        self.assertRedirects(response, reverse('frontend:home'))

    def test_login_success(self):
        """Test successful login"""
        response = self.client.post(reverse('frontend:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertRedirects(response, reverse('frontend:home'))
        
        # Check user is logged in
        user = response.wsgi_request.user
        self.assertTrue(user.is_authenticated)
        self.assertEqual(user.username, 'testuser')
        
        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('Welcome back, Test User!', str(messages[0]))

    def test_login_with_next_parameter(self):
        """Test login redirect to next parameter"""
        next_url = reverse('frontend:cart')
        response = self.client.post(f"{reverse('frontend:login')}?next={next_url}", {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertRedirects(response, next_url)

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = self.client.post(reverse('frontend:login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username or password')
        
        # Check user is not logged in
        user = response.wsgi_request.user
        self.assertFalse(user.is_authenticated)

    def test_login_missing_credentials(self):
        """Test login with missing credentials"""
        # Missing password
        response = self.client.post(reverse('frontend:login'), {
            'username': 'testuser'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please provide both username and password')
        
        # Missing username
        response = self.client.post(reverse('frontend:login'), {
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please provide both username and password')

    def test_register_view_get(self):
        """Test registration page loads correctly"""
        response = self.client.get(reverse('frontend:register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Register')
        self.assertIsInstance(response.context['form'], CustomUserCreationForm)

    def test_register_view_authenticated_user_redirect(self):
        """Test authenticated user is redirected from register page"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('frontend:register'))
        self.assertRedirects(response, reverse('frontend:home'))

    def test_register_success(self):
        """Test successful registration"""
        response = self.client.post(reverse('frontend:register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'display_name': 'New User',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        })
        self.assertRedirects(response, reverse('frontend:login'))
        
        # Check user was created
        user = User.objects.get(username='newuser')
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertEqual(user.display_name, 'New User')
        self.assertTrue(user.is_customer)
        
        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('Account created successfully for newuser', str(messages[0]))

    def test_register_invalid_form(self):
        """Test registration with invalid form data"""
        response = self.client.post(reverse('frontend:register'), {
            'username': 'testuser',  # Already exists
            'email': 'invalid-email',
            'password1': 'pass',
            'password2': 'different'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'username', 'A user with that username already exists.')

    def test_register_password_mismatch(self):
        """Test registration with password mismatch"""
        response = self.client.post(reverse('frontend:register'), {
            'username': 'newuser2',
            'email': 'newuser2@example.com',
            'password1': 'complexpass123',
            'password2': 'differentpass123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'password2', "The two password fields didn't match.")

    def test_logout_authenticated_user(self):
        """Test logout for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('frontend:logout'))
        self.assertRedirects(response, reverse('frontend:home'))
        
        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('Goodbye Test User!', str(messages[0]))

    def test_logout_anonymous_user(self):
        """Test logout for anonymous user"""
        response = self.client.get(reverse('frontend:logout'))
        self.assertRedirects(response, reverse('frontend:home'))
        
        # Should not have logout message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 0)

    def test_customer_registration_sets_is_customer_true(self):
        """Test that registration automatically sets is_customer=True"""
        self.client.post(reverse('frontend:register'), {
            'username': 'newcustomer',
            'email': 'newcustomer@example.com',
            'display_name': 'New Customer',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        })
        
        user = User.objects.get(username='newcustomer')
        self.assertTrue(user.is_customer)

    def test_login_preserves_display_name_fallback(self):
        """Test login message uses display_name or falls back to username"""
        # User without display_name
        user_no_display = User.objects.create_user(
            username='nodisplay',
            password='testpass123'
        )
        
        response = self.client.post(reverse('frontend:login'), {
            'username': 'nodisplay',
            'password': 'testpass123'
        })
        
        messages = list(get_messages(response.wsgi_request))
        self.assertIn('Welcome back, nodisplay!', str(messages[0]))


class AuthenticationIntegrationTest(TestCase):
    """Integration tests for complete auth flows"""
    
    def setUp(self):
        self.client = Client()

    def test_complete_registration_and_login_flow(self):
        """Test complete flow: register -> login -> access protected page"""
        # Step 1: Register
        response = self.client.post(reverse('frontend:register'), {
            'username': 'flowuser',
            'email': 'flowuser@example.com',
            'display_name': 'Flow User',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        })
        self.assertRedirects(response, reverse('frontend:login'))
        
        # Step 2: Login
        response = self.client.post(reverse('frontend:login'), {
            'username': 'flowuser',
            'password': 'complexpass123'
        })
        self.assertRedirects(response, reverse('frontend:home'))
        
        # Step 3: Access protected page
        response = self.client.get(reverse('frontend:cart'))
        self.assertEqual(response.status_code, 200)
        
        # Step 4: Logout
        response = self.client.get(reverse('frontend:logout'))
        self.assertRedirects(response, reverse('frontend:home'))
        
        # Step 5: Try to access protected page (should redirect to login)
        response = self.client.get(reverse('frontend:cart'))
        self.assertRedirects(response, f"{reverse('frontend:login')}?next={reverse('frontend:cart')}")

    def test_login_required_redirect_preserves_next(self):
        """Test that login_required decorator preserves next parameter"""
        # Try to access cart without login
        response = self.client.get(reverse('frontend:cart'))
        expected_redirect = f"{reverse('frontend:login')}?next={reverse('frontend:cart')}"
        self.assertRedirects(response, expected_redirect)
        
        # Create user and login with next parameter
        User.objects.create_user(username='testuser', password='testpass123')
        response = self.client.post(expected_redirect, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertRedirects(response, reverse('frontend:cart'))