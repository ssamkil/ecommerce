import json, jwt

from django.utils import timezone
from django.test  import TestCase, Client

from my_settings  import SECRET_KEY, ALGORITHM
from items.models import Item, Category
from users.models import User
class ItemViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.name = 'test_item'

        self.user = User.objects.create(
            name='홍길동',
            email='test@naver.com',
            password='123456789!@',
        )

        Category.objects.create(
            name='test_category',
            thumbnail=''
        )

        Item.objects.create(
            category=self.category,
            name=self.name,
            price=99,
            quantity=100,
            image=''
        )

        self.token = jwt.encode({'id': self.user.id}, SECRET_KEY, ALGORITHM)

    def test_itemview_get_success(self):
        response = self.client.get(f'/items?name={self.name}')
        self.assertEqual(response.status_code, 200)

        result_json = response.json()
        result_data = result_json['RESULT']

        self.assertIn('created_at', result_data)
        self.assertIn('modified_at', result_data)

        self.assertEqual(result_data['name'], self.name)
        self.assertEqual(result_data['price'], 99.0)
        self.assertEqual(result_data['category'], self.category.id)

    def test_create_success(self):
        headers = {'HTTP_Authorization' : self.token}
        post = {
            'category_id': self.category.id,
            'name': 'test_item2',
            'price': 75,
            'quantity': 40,
            'image': ''
        }
        response = self.client.post(
            '/items', json.dumps(post), content_type="application/json", **headers
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {'MESSAGE': 'Created'})

    def test_duplicate_item(self):
        headers = {'HTTP_Authorization': self.token}
        post = {
            'category_id': self.category.id,
            'name': 'test_item',
            'price': 100,
            'quantity': 55,
            'image': ''
        }
        response = self.client.post(
            '/items', post, content_type="application/json", **headers
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'ERROR' : 'Item already exist'})

    def test_key_error(self):
        headers = {'HTTP_Authorization' : self.token}
        post = {
            'name': 'test_item2',
            'price': 35
        }
        response = self.client.post(
            '/items', json.dumps(post), content_type="application/json", **headers
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'ERROR': 'KEY_ERROR'})