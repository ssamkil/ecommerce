import jwt

from django.test                    import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile

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

        self.category = Category.objects.create(
            name='test_category',
            thumbnail=''
        )

        self.item = Item.objects.create(
            category=self.category,
            name=self.name,
            price=99,
            quantity=100,
            image='test.jpg'
        )

        self.token = jwt.encode({'id': self.user.id}, SECRET_KEY, ALGORITHM)
        self.headers = {'HTTP_Authorization': self.token}

    def test_itemview_get_success(self):
        response = self.client.get(f'/items?name={self.name}')
        self.assertEqual(response.status_code, 200)

        result_json = response.json()
        result_data = result_json['RESULT']
        item        = result_data[0]

        self.assertIn('created_at', item)
        self.assertIn('modified_at', item)

        self.assertEqual(item['name'], self.name)
        self.assertEqual(item['price'], 99.0)
        self.assertEqual(item['category_id'], self.category.id)

    def test_create_success(self):
        image = SimpleUploadedFile("new_image.jpg", b"file_content", content_type="image/jpeg")

        data = {
            'category_id': self.category.id,
            'name': 'test_item2',
            'price': 75,
            'quantity': 40,
            'image': image
        }

        response = self.client.post(
            '/items', data, **self.headers
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {'MESSAGE': 'CREATED'})

    def test_duplicate_item(self):
        post = {
            'category_id': self.category.id,
            'name': self.name,
            'price': 100,
            'quantity': 55,
            'image': ''
        }
        response = self.client.post(
            '/items', post, **self.headers
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'ERROR': 'ITEM_ALREADY_EXISTS'})

    def test_key_error(self):
        post = {
            'name': 'test_item2',
            'price': 35
        }
        response = self.client.post(
            '/items', post, **self.headers
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'ERROR': 'KEY_ERROR'})

    def test_empty_value(self):
        post = {
            'category_id': self.category.id,
            'name': '',
            'price': 100,
            'quantity': 10
        }

        response = self.client.post(
            '/items', post, **self.headers
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'ERROR': 'EMPTY_VALUE'})