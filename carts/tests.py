import json, jwt

from django.test  import TestCase, Client

from my_settings  import SECRET_KEY, ALGORITHM
from items.models import Item, Category
from carts.models import Cart
from users.models import User
class CartViewTest(TestCase):
    def setUp(self):
        self.client = Client()

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
            name='test_item',
            price=99,
            quantity=120,
            image=''
        )

        self.item2 = Item.objects.create(
            category=self.category,
            name='test_item2',
            price=125,
            quantity=50,
            image=''
        )

        self.cart = Cart.objects.create(
            user=self.user,
            item=self.item,
            quantity=50
        )

        self.token = jwt.encode({'id': self.user.id}, SECRET_KEY, ALGORITHM)
        self.headers = {'HTTP_Authorization': self.token}

    def test_get_cart_success(self):
        response = self.client.get(
            '/carts', **self.headers
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['MESSAGE'], 'SUCCESS')

        self.assertEqual(response.json()['TOTAL_PRICE'], 4950)

    def test_create_success(self):
        post = {
            'id': self.item2.id,
            'quantity': 50
        }
        response = self.client.post(
            '/carts', post, content_type="application/json", **self.headers
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {'MESSAGE': 'CREATED'})

    def test_update_success(self):
        post = {
            'id': self.item.id,
            'quantity': 50
        }
        response = self.client.post(
            '/carts', post, content_type="application/json", **self.headers
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'MESSAGE': 'UPDATED'})

    def test_item_does_not_exist(self):
        post = {
            'id': 9999,
            'quantity': 50
        }
        response = self.client.post(
            '/carts', post, content_type="application/json", **self.headers
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {'ERROR': 'ITEM_DOES_NOT_EXIST'})

    def test_item_stock_unavailable(self):
        post = {
            'id': self.item.id,
            'quantity': 500
        }
        response = self.client.post(
            '/carts', post, content_type="application/json", **self.headers
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'ERROR': 'ITEM_STOCK_UNAVAILABLE'})

    def test_delete_cart_item_success(self):
        post = {
            'id': self.cart.id
        }
        response = self.client.delete(
            '/carts', post, content_type='application/json', **self.headers
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'MESSAGE': 'DELETED'})

        self.assertFalse(Cart.objects.filter(id=self.cart.id).exists())

    def test_delete_cart_does_not_exist(self):
        post = {
            'id': 99999
        }
        response = self.client.delete(
            '/carts', post, content_type='application/json', **self.headers
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {'ERROR': 'CART_DOES_NOT_EXIST'})

    def test_key_error(self):
        post = {
            'id': self.item.id
        }
        response = self.client.post(
            '/carts', post, content_type="application/json", **self.headers
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'ERROR': 'KEY_ERROR'})