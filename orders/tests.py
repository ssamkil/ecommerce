import json
import jwt
import uuid
from django.test import TestCase, Client
from my_settings import SECRET_KEY, ALGORITHM
from users.models import User
from items.models import Item, Category
from carts.models import Cart
from .models import Order, OrderItem, OrderStatus

class OrderTest(TestCase):
    def setUp(self):
        self.client = Client()

        self.user = User.objects.create(
            name='홍길동',
            email='test@test.com',
            password='12345678'
        )
        self.category = Category.objects.create(name='test_cat', thumbnail='test.jpg')
        self.item = Item.objects.create(
            name='테스트 상품',
            price=1000,
            quantity=10,
            category=self.category
        )

        OrderStatus.objects.create(id=1, status='PENDING')
        OrderStatus.objects.create(id=2, status='COMPLETED')
        OrderStatus.objects.create(id=3, status='DECLINED')

        self.token = jwt.encode({'id': self.user.id}, SECRET_KEY, ALGORITHM)
        self.headers = {'HTTP_AUTHORIZATION': self.token}

    def test_order_post_success(self):
        Cart.objects.create(user=self.user, item=self.item, quantity=2)

        data = {'address': '서울시 강남구'}
        response = self.client.post(
            '/orders/',
            data=json.dumps(data),
            content_type='application/json',
            **self.headers
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['MESSAGE'], 'ORDER_RESERVED')

        self.item.refresh_from_db()
        self.assertEqual(self.item.quantity, 8)
        self.assertFalse(Cart.objects.filter(user=self.user).exists())

    def test_order_post_empty_cart_error(self):
        data = {'address': '서울시 강남구'}
        response = self.client.post(
            '/orders/',
            data=json.dumps(data),
            content_type='application/json',
            **self.headers
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['MESSAGE'], 'EMPTY_CART')

    def test_order_post_insufficient_stock_error(self):
        Cart.objects.create(user=self.user, item=self.item, quantity=20)

        data = {'address': '서울시 강남구'}
        response = self.client.post(
            '/orders/',
            data=json.dumps(data),
            content_type='application/json',
            **self.headers
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('INSUFFICIENT_STOCK', response.json()['ERROR'])

    def test_order_get_success(self):
        order = Order.objects.create(
            user=self.user,
            address='서울시 강남구',
            order_number=str(uuid.uuid4()),
            order_status_id=1
        )
        OrderItem.objects.create(order=order, item=self.item, quantity=1)

        response = self.client.get(f'/orders/{order.id}/', **self.headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['RESULT']['address'], '서울시 강남구')
        self.assertEqual(response.json()['RESULT']['total_price'], 1000.0)

    def test_order_get_not_found_error(self):
        response = self.client.get('/orders/999/', **self.headers)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['MESSAGE'], 'ORDER_NOT_FOUND')