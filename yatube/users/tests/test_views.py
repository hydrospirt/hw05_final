from http import HTTPStatus

from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UsersPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='testuser')
        cls.guest = Client()
        cls.auth_user = Client()
        cls.auth_user.force_login(cls.user)

    def setUp(self):
        super().setUp()
        self.first_name = 'Василий'
        self.last_name = 'Васильев'
        self.username = 'singuper'
        self.email = 'vasilii@django.ru'
        self.password = 'Vasiliiy6465cd'

    def test_pages_correct_tempalte_guest(self):
        templates_page_names = {
            reverse('users:signup'): 'users/signup.html',
            reverse('users:login'): 'users/login.html',
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_correct_tempalte_user(self):
        templates_page_names = {
            reverse(
                'users:password_change'
            ): 'users/password_change_form.html',
            reverse(
                'users:password_change_done'
            ): 'users/password_change_done.html',
            reverse(
                'users:password_reset_form'
            ): 'users/password_reset_form.html',
            reverse(
                'users:password_reset_done'
            ): 'users/password_reset_done.html',
            reverse(
                'users:password_reset_complete'
            ): 'users/password_reset_complete.html',
            reverse('users:logout'): 'users/logged_out.html',
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.auth_user.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_correct_context_form(self):
        response = self.guest.get(reverse('users:signup'))
        form_fields = {
            'first_name': forms.CharField,
            'last_name': forms.CharField,
            'username': forms.CharField,
            'email': forms.EmailField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_correct_form_signup(self):
        users = User.objects.all().count()
        form_data = {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'username': self.username,
            'email': self.email,
            'password1': self.password,
            'password2': self.password,
        }
        response = self.guest.post(
            reverse('users:signup'),
            data=form_data,
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(
            User.objects.filter(username=form_data['username']).exists()
        )
        self.assertEqual(User.objects.all().count(), users + 1)
