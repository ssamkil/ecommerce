import json
import jwt
from django.test import TestCase, Client
from django.core.cache import cache

from my_settings import SECRET_KEY, ALGORITHM
from items.models import Item, Category, Review
from users.models import User

class ItemViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.name = 'test_item'

        self.user = User.objects.create(name='홍길동', email='test@naver.com', password='...')
        self.category = Category.objects.create(name='test_category', thumbnail='')

        self.item = Item.objects.create(
            category=self.category,
            name=self.name,
            price=99.0,
            quantity=100,
            image='test.jpg'
        )

        self.token = jwt.encode({'id': self.user.id}, SECRET_KEY, ALGORITHM)
        self.headers = {'HTTP_AUTHORIZATION': self.token}
        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_item_get_cache_success(self):
        self.client.get(f'/items/?name={self.name}')
        response = self.client.get(f'/items/?name={self.name}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('MESSAGE'), 'SUCCESS (CACHE)')

    def test_item_patch_success(self):
        data = json.dumps({'price': 150, 'quantity': 80})
        response = self.client.patch(
            f'/items/{self.item.id}/',
            data=data,
            content_type='application/json',
            **self.headers
        )
        self.assertEqual(response.status_code, 200)

    def test_item_delete_success(self):
        response = self.client.delete(f'/items/{self.item.id}/', **self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('MESSAGE'), 'DELETED')
        self.assertFalse(Item.objects.filter(id=self.item.id).exists())

    def test_review_post_and_get_success(self):
        review_data = json.dumps({'body': '좋은 상품입니다!'})
        response = self.client.post(
            f'/items/review/?name={self.name}',
            data=review_data,
            content_type='application/json',
            **self.headers
        )
        self.assertEqual(response.status_code, 201)

        response = self.client.get(f'/items/review/?name={self.name}')
        self.assertEqual(response.status_code, 200)

        result = response.json().get('RESULT')
        if isinstance(result, list):
            self.assertEqual(result[0]['body'], '좋은 상품입니다!')
        else:
            self.assertEqual(result['body'], '좋은 상품입니다!')

    def test_item_post_key_error(self):
        post_data = json.dumps({'name': 'no_price_item', 'category_id': self.category.id})
        response = self.client.post(
            '/items/',
            data=post_data,
            content_type='application/json',
            **self.headers
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json().get('ERROR'), 'KEY_ERROR')