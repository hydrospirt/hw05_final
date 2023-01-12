from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class TestUserURLS(TestCase):
    def setUp(self):
        super().setUp()
        self.guest = Client()
        self.user = User.objects.create_user(username='testman')
        self.auth_user = Client()
        self.auth_user.force_login(self.user)

    def test_auth_user_urls(self):
        pages = (
            '/auth/signup/',
            '/auth/login/',
            '/auth/password_change/',
            '/auth/password_change/done/',
            '/auth/password_reset/',
            '/auth/password_reset/done/',
            '/auth/reset/<uidb64>/<token>/',
            '/auth/reset/done/',
            '/auth/logout/',
        )
        for page in pages:
            with self.subTest(page=page):
                response = self.auth_user.get(page)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                )
