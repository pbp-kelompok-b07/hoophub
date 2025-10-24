import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from catalog.models import Product
from .models import Order, OrderItem
from invoice.models import Invoice

class CartViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(username='testuser', password='testpassword')
        
        self.product1 = Product.objects.create(name="Product A", price=10000, stock=10)
        self.product2 = Product.objects.create(name="Product B", price=25000, stock=5)
        
        self.cart_url = reverse('cart:show_cart')
        self.checkout_url = reverse('cart:show_checkout')

    def _add_product_to_session_cart(self, product_id, quantity=1):
        session = self.client.session
        cart = session.get('cart', {})
        cart[str(product_id)] = {'quantity': quantity}
        session['cart'] = cart
        session.save()

    def test_show_cart_view_empty_unauthenticated(self):
        response = self.client.get(self.cart_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You must be logged in.")

    def test_show_checkout_get_request_redirects(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.checkout_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.cart_url)


    def test_add_to_cart_view(self):
        self.client.login(username='testuser', password='testpassword')
        add_url = reverse('cart:add_to_cart', args=[self.product1.pk])
        response = self.client.post(add_url, {'quantity': 2})
        
        cart = self.client.session.get('cart', {})
        self.assertEqual(cart[str(self.product1.pk)]['quantity'], 2)

    def test_remove_from_cart_view(self):
        self.client.login(username='testuser', password='testpassword')
        self._add_product_to_session_cart(self.product1.pk)
        
        remove_url = reverse('cart:remove_from_cart', args=[self.product1.pk])
        response = self.client.post(remove_url)
        
        cart = self.client.session.get('cart', {})
        self.assertNotIn(str(self.product1.pk), cart)
        self.assertRedirects(response, self.cart_url)

    def test_successful_checkout(self):
        self.client.login(username='testuser', password='testpassword')
        self._add_product_to_session_cart(self.product1.pk, 2)
        
        checkout_data = {
            'full_name': 'Test User', 'address': '123 Test St',
            'city': 'Testville', 'postal_code': '12345'
        }
        
        response = self.client.post(self.checkout_url, checkout_data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        
        json_response = json.loads(response.content)
        self.assertEqual(json_response['status'], 'success')
        
        self.assertTrue(Order.objects.filter(user=self.user).exists())
        self.assertTrue(OrderItem.objects.filter(product=self.product1).exists())
        self.assertTrue(Invoice.objects.filter(user=self.user).exists())
        
        self.assertNotIn('cart', self.client.session)

    def test_checkout_empty_cart(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(self.checkout_url, {}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)
        
        json_response = json.loads(response.content)
        self.assertEqual(json_response['status'], 'error')
        self.assertEqual(json_response['message'], 'Keranjang Anda kosong.')

    def test_checkout_missing_address(self):
        self.client.login(username='testuser', password='testpassword')
        self._add_product_to_session_cart(self.product1.pk)
        
        invalid_data = {'full_name': 'Test User'}
        response = self.client.post(self.checkout_url, invalid_data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)
        
        json_response = json.loads(response.content)
        self.assertEqual(json_response['status'], 'error')
        self.assertEqual(json_response['message'], 'Semua field alamat wajib diisi!')