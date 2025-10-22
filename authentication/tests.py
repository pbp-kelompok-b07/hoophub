from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('authentication:register')
        self.login_url = reverse('authentication:login')
        self.logout_url = reverse('authentication:logout')

        # Buat user dummy untuk login test
        self.user = User.objects.create_user(username='dzaky', password='12345')

    # ---------- REGISTER TESTS ----------
    def test_register_page_loads(self):
        """Cek apakah halaman register GET bisa diakses"""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')

    def test_register_valid_user(self):
        """Cek apakah user baru berhasil dibuat"""
        response = self.client.post(self.register_url, {
            'username': 'newuser',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {'success': True, 'message': 'Account created successfully!'}
        )
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_invalid_user(self):
        """Cek kalau password tidak cocok"""
        response = self.client.post(self.register_url, {
            'username': 'wrongpass',
            'password1': 'abc',
            'password2': 'xyz',
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('errors', response.json())

    # ---------- LOGIN TESTS ----------
    def test_login_page_loads(self):
        """Cek halaman login GET bisa diakses"""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_login_valid_user(self):
        """Cek login berhasil dengan kredensial benar"""
        response = self.client.post(self.login_url, {
            'username': 'dzaky',
            'password': '12345'
        })
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {'success': True, 'message': 'Login successful!'}
        )

    def test_login_invalid_user(self):
        """Cek login gagal kalau password salah"""
        response = self.client.post(self.login_url, {
            'username': 'dzaky',
            'password': 'salahpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['success'])
        self.assertIn('errors', response.json())

    # ---------- LOGOUT TESTS ----------
    def test_logout_user(self):
        """Cek logout berhasil dan session dihapus"""
        self.client.login(username='dzaky', password='12345')
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {'success': True, 'message': 'Logged out successfully!'}
        )