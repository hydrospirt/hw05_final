from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.core.cache import cache

from posts.models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        cache.clear()

    def test_homepage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisted_page_404(self):
        response = self.guest_client.get('/unexisted_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest = Client()
        cls.user = User.objects.create_user(username='testman')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая публикация',
        )
        cls.auth_user = Client()
        cls.auth_user.force_login(cls.user)

    def setUp(self):
        super().setUp()
        cache.clear()

    def test_auth_user_urls(self):
        pages = (
            '/',
            f'/group/{self.group.slug}/',
            f'/posts/{self.post.pk}/',
            f'/profile/{self.user.username}/',
            '/create/',
            f'/posts/{self.post.pk}/edit/'
        )
        for page in pages:
            with self.subTest(page=page):
                response = self.auth_user.get(page)
                error_msg = (f'Ошибка: у {self.user.username}',
                             f'нет доступа к странице {page}')
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    error_msg
                )

    def test_urls_users_correct_tempalte(self):
        template_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html',
            'unexisted_page': 'core/404.html',
        }
        for url, template in template_url_names.items():
            with self.subTest(url=url):
                response = self.auth_user.get(url)
                error_msg = f'Ошибка: {url} ожидал шаблон {template}'
                self.assertTemplateUsed(response, template, error_msg)
