from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from catalog.models import Product
from review.models import Review
import json

# Create your tests here.
class ReviewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='user', 
            password='password'
        )

        self.product = Product.objects.create(
            name='product',
            brand='brand',
            category='Shoes',
            price=999,
            stock=5,
            description='good product made in indonesia',
            image='https://static.nike.com/a/images/t_PDP_864_v1/f_auto,b_rgb:f5f5f5/6a3671b8-f115-44f6-9ab6-3798d55210eb/custom-nike-air-max-97-shoes-by-you.png',
            rating=5,
            is_available=True,
            release_date='2025-10-22'
        )
        
        self.review = Review.objects.create(
            user=self.user,
            product=self.product,
            rating=5,
            review="nice product"
        )
        
        self.client = Client()
        self.client.login(username='user', password='password')

    def test_show_review(self):
        response = self.client.get(reverse('review:show_review'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'review.html')

    def test_show_json_all(self):
        response = self.client.get(reverse('review:show_json'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['review'], "nice product")

    def test_show_json_by_id(self):
        response = self.client.get(reverse('review:show_json_by_id', args=[self.review.pk]))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['rating'], 5)

    def test_create_review(self):
        new_product = Product.objects.create(name='product2', price=2, category='Shoes')
        
        response = self.client.post(reverse('review:create_review', args=[new_product.pk]), {
            'rating': 4,
            'review': 'nice product2'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Review.objects.filter(review='nice product2', product=new_product).exists())

    def test_edit_review(self):
        response = self.client.post(reverse('review:edit_review', args=[self.review.pk]), {
            'rating': 3,
            'review': 'update nice product'
        })
        
        self.assertEqual(response.status_code, 200)
        self.review.refresh_from_db()
        self.assertEqual(self.review.review, 'update nice product')
        self.assertEqual(self.review.rating, 3)

    def test_delete_review_view(self):
        response = self.client.post(reverse('review:delete_review', args=[self.review.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Review.objects.filter(pk=self.review.pk).exists())
        
    def test_unauthenticated_user_cannot_access_views(self):
        self.client.logout()
        response = self.client.get(reverse('review:show_review'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/authentication/login/', response.url)

    def test_nonexistent_page(self):
        response = Client().get('/burhan_always_exists/')
        self.assertEqual(response.status_code, 404)

    def test_review_creation(self):
        self.assertEqual(self.review.rating, 5)
        self.assertTrue(self.review.review, "nice product")

    def test_create_review_no_rating(self):
        response = self.client.post(reverse('review:create_review', args=[self.product.pk]), {
            'review': 'This review has no rating.'
        })
        
        self.assertEqual(response.status_code, 400)
        json_response = json.loads(response.content)
        self.assertFalse(json_response['status'] == 'success')
        self.assertIn('rating', json_response['errors'])

    def test_edit_review_no_review(self):
        response = self.client.post(reverse('review:edit_review', args=[self.review.pk]), {
            'rating': 3,
            'review': ''
        })
        
        self.assertEqual(response.status_code, 200)
        self.review.refresh_from_db()
        self.assertEqual(self.review.review, '')

    def test_get_doesnt_exist_review(self):
        doesnt_exist_uuid = '12345678-1234-5678-1234-567812345678'
        response = self.client.get(reverse('review:show_json_by_id', args=[doesnt_exist_uuid]))
        
        self.assertEqual(response.status_code, 404)

    def test_edit_other_user(self):
        other_user = get_user_model().objects.create_user(username='user5z', password='uvuzza12346')
        
        self.client.login(username='user5z', password='uvuzza12346')
        
        response = self.client.post(reverse('review:edit_review', args=[self.review.pk]), {
            'rating': 1,
            'review': 'hi'
        })
        
        self.assertEqual(response.status_code, 404)