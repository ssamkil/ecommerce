import json, jwt, bcrypt

from django.test  import TestCase, Client
from users.models import User
from my_settings  import SECRET_KEY, ALGORITHM

class SignUpViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        User.objects.create(
            name='홍길동',
            email='test2@naver.com',
            password='123456789!@',
        )

    def test_signup_success(self):
        user = {
            'name': '홍홍길동',
            'email': 'test1@naver.com',
            'password': '123456789!@',
        }
        response = self.client.post(
            '/users/signUp', user, content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {'MESSAGE': 'CREATED'})

    def test_duplicated_user(self):
        user = {
            'name': '홍길동',
            'email': 'test2@naver.com',
            'password': '123456789!@',
        }
        response = self.client.post(
            '/users/signUp', user, content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'ERROR': 'ACCOUNT_ALREADY_EXISTS'})

    def test_email_format_error(self):
        user = {
            'name': '홍길동',
            'email': 'test3naver.com',
            'password': '123456789!@',
        }
        response = self.client.post(
            '/users/signUp', user, content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'ERROR': 'Email must contain @'})

    def test_password_format_error(self):
        user = {
            'name': '홍길동',
            'email': 'test4@naver.com',
            'password': '1234567',
        }
        response = self.client.post(
            '/users/signUp', user, content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'ERROR': 'Minimum length of password should be 8'})

    def test_key_error(self):
        user = {
            'name': '홍길동',
            'email': 'test5@naver.com',
        }
        response = self.client.post(
            '/users/signUp', user, content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'ERROR': 'KEY_ERROR'})


class SignInViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.email = 'test2@naver.com'
        self.password = '123456789!@'

        hashed_password = bcrypt.hashpw(
            self.password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

        self.user = User.objects.create(
            name='홍길동',
            email=self.email,
            password=hashed_password,
        )

    def test_login_success(self):
        login_data = {
            'email': self.email,
            'password': self.password,
        }
        response = self.client.post(
            '/users/signIn', login_data, content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)

        response_data = response.json()
        self.assertEqual(response_data['MESSAGE'], 'SUCCESS')

        token = response_data.get('TOKEN')
        self.assertIsNotNone(token)

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        self.assertEqual(payload['id'], self.user.id)

    def test_login_user_does_not_exist(self):
        login_data = {
            'email': 'wrong@naver.com',
            'password': '123456789!@',
        }
        response = self.client.post(
            '/users/signIn', login_data, content_type='application/json'
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {'ERROR': 'INVALID_USER'})

    def test_login_wrong_password(self):
        login_data = {
            'email': self.email,
            'password': 'wrong_password',
        }
        response = self.client.post(
            '/users/signIn', login_data, content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'ERROR': 'FAILED_TO_LOGIN'})