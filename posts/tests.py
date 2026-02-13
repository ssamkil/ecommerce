import json, jwt

from django.test  import TestCase, Client

from my_settings  import SECRET_KEY, ALGORITHM
from posts.models import Post
from users.models import User
# Create your tests here.
class PostViewTest(TestCase):
    def setUp(self):
        self.client = Client()

        User.objects.create(
            name='홍길동2',
            email='test2@naver.com',
            password='123456789!@2',
        )

        self.user = User.objects.create(
            name='홍길동',
            email='test@naver.com',
            password='123456789!@',
        )

        Post.objects.create(
            title='Test for post',
            body='hello this is test code for post view heuh',
            user_id=self.user.id
        )

        self.token = jwt.encode({'id': self.user.id}, SECRET_KEY, ALGORITHM)
        self.headers = {'HTTP_Authorization': self.token}

    def test_create_success(self):
        post = {
            'title': 'Test for post2',
            'body': 'hello this is test code for post view heuh heuh heuh',
        }
        response = self.client.post(
            '/posts', post, content_type="application/json", **self.headers
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {'MESSAGE': 'CREATED'})

    def test_key_error(self):
        post = {
            'title':'Test for post',
        }
        response = self.client.post(
            '/posts', post, content_type="application/json", **self.headers
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'ERROR': 'KEY_ERROR'})

    def test_get_list_success(self):
        for i in range(5):
            Post.objects.create(
                title=f'Test Post {i}',
                body='Body',
                user=self.user
            )

        response = self.client.get('/posts?page=1')

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data['MESSAGE'], 'SUCCESS')

        self.assertEqual(len(data['RESULT']), 3)

        self.assertEqual(data['PAGES']['TOTAL'], 2)

        latest_post_id = Post.objects.last().id
        self.assertEqual(data['RESULT'][0]['id'], latest_post_id)