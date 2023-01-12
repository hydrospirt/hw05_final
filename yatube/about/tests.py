from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class StaticURLTests(TestCase):
    def setUp(self):
        super().setUp()
        self.guest = Client()

    def test_static_pages(self):
        pages = (
            '/about/author/',
            '/about/tech/',
        )
        for page in pages:
            with self.subTest(page=page):
                response = self.guest.get(page)
                error_msg = f'Ошибка нет доступа к {page}'
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    error_msg
                )

    def test_urls_users_correct_template(self):
        template_url_names = {
            'about/author.html': '/about/author/',
            'about/tech.html': '/about/tech/'
        }
        for template, url in template_url_names.items():
            with self.subTest(url=url):
                response = self.guest.get(url)
                error_msg = f'Ошибка: {url} ожидал шаблон {template}'
                self.assertTemplateUsed(response, template, error_msg)

    def test_pages_use_correct_template(self):
        templates_page_names = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }
        for reverse_name, temp in templates_page_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest.get(reverse_name)
                self.assertTemplateUsed(response, temp)
