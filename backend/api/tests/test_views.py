from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from api.models import Category, Course, Cart, CartOrder, Profile, Teacher, Review, Question_Answer, Wishlist, Notification, Coupon
from decimal import Decimal
import json

User = get_user_model()

class AuthenticationViewTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = "/api/v1/user/register/"
        self.login_url = "/api/v1/user/token/"
        self.user_data = {
            'full_name': 'Test User',
            'email': 'test@example.com',
            'password': 'TestPassword123!',
            'password2': 'TestPassword123!'
        }
        
    # Correct Input Tests
    def test_user_registration_success(self):
        """Test successful user registration with valid data"""
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email=self.user_data['email']).exists())
        
    def test_user_login_success(self):
        """Test successful user login with valid credentials"""
        # Create user first
        self.client.post(self.register_url, self.user_data, format='json')
        
        # Attempt login
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        
    # Incorrect Input Tests
    def test_user_registration_password_mismatch(self):
        """Test user registration with mismatched passwords"""
        self.user_data['password2'] = 'DifferentPassword123!'
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
        
    def test_user_registration_invalid_email(self):
        """Test user registration with invalid email format"""
        self.user_data['email'] = 'invalid-email'
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_user_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        login_data = {
            'email': 'wrong@example.com',
            'password': 'WrongPassword123!'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    # Sanity Tests
    def test_user_registration_duplicate_email(self):
        """Test registration with duplicate email"""
        # Create first user
        self.client.post(self.register_url, self.user_data, format='json')
        
        # Try to create second user with same email
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_user_login_empty_fields(self):
        """Test login with empty fields"""
        login_data = {
            'email': '',
            'password': ''
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

