from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
import json

# Create your tests here.
User = get_user_model()

class AuthenticationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('authentication:register')
        self.login_url = reverse('authentication:login')
        self.logout_url = reverse('authentication:logout')
        
        self.username = 'user'
        self.password = 'klmpkpbp1234'
        
        self.valid_register_data = {
            'username': self.username,
            'password1': self.password,
            'password2': self.password
        }
        
        self.invalid_register_data = {
            'username': 'user2',
            'password1': 'password1',
            'password2': 'password2'
        }

    def test_register_page(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')

    def test_login_page(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_register_success(self):
        response = self.client.post(self.register_url, self.valid_register_data)
        self.assertEqual(response.status_code, 200)
        
        json_response = json.loads(response.content)
        self.assertTrue(json_response['success'])
        
        self.assertTrue(User.objects.filter(username=self.username).exists())

    def test_register_fail_password(self):
        response = self.client.post(self.register_url, self.invalid_register_data)
        self.assertEqual(response.status_code, 400)
        
        json_response = json.loads(response.content)
        self.assertFalse(json_response['success'])
        self.assertIn('password2', json_response['errors'])

    def test_login_success(self):
        User.objects.create_user(username=self.username, password=self.password)
        
        response = self.client.post(self.login_url, {'username': self.username, 'password': self.password})
        self.assertEqual(response.status_code, 200)
        
        json_response = json.loads(response.content)
        self.assertTrue(json_response['success'])
        
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_login_fail(self):
        response = self.client.post(self.login_url, {'username': 'wronguser', 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, 200)
        
        json_response = json.loads(response.content)
        self.assertFalse(json_response['success'])
        self.assertIn('__all__', json_response['errors'])

    def test_logout_success(self):
        self.client.login(username=self.username, password=self.password)
        
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, 200)
        
        json_response = json.loads(response.content)
        self.assertTrue(json_response['success'])
        
        self.assertFalse('_auth_user_id' in self.client.session)