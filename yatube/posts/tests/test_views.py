import shutil
import tempfile

from django import forms
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from django.conf import settings
from posts.models import Group, Post, Comment


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
POST_COUNT = 14
User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.guest = Client()
        cls.user = User.objects.create_user(username='testviewer')
        cls.follower = User.objects.create_user(username='testfollower')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание'
        )
        cls.group_2 = Group.objects.create(
            title='Не нужная группа',
            slug='test2',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая публикация 0',
            group=cls.group,
            image=cls.uploaded,
        )
        cls.auth_user = Client()
        cls.auth_user.force_login(cls.user)
        cls.auth_follower = Client()
        cls.auth_follower.force_login(cls.follower)

    def setUp(self):
        super().setUp()
        cache.clear()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_pages_use_correct_tempalte(self):
        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': 'test'}): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id':
                        self.post.pk}): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id':
                        self.post.pk}): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.auth_user.get(reverse_name)
                error_msg = f'Ошибка: в {reverse_name}'
                self.assertTemplateUsed(response, template, error_msg)

    def test_follow_pages_use_correct_template(self):
        templates_page_names = {
            reverse('posts:profile_follow',
                    kwargs={'username': self.user.username}
                    ): 'posts/profile.html',
            reverse('posts:follow_index'): 'posts/follow.html',
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.user.username}
                    ): 'posts/profile.html',
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.auth_follower.get(reverse_name, follow=True)
                error_msg = f'Ошибка: в {reverse_name}'
                self.assertTemplateUsed(response, template, error_msg)

    def test_index_correct_context(self):
        response = self.auth_user.get(
            reverse('posts:index')
        )
        self.check_correct_context(response)

    def test_group_list_correct_context(self):
        response = self.auth_user.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': 'test'}
            )
        )
        self.check_correct_context(response)

    def test_profile_correct_context(self):
        response = self.auth_user.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            )
        )
        self.check_correct_context(response)

    def test_post_detail_correct_context(self):
        response = self.auth_user.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}))
        post_text = {
            response.context['post'].text: self.post.text,
            response.context['post'].author: self.post.author,
            response.context['post'].group: self.post.group,
            response.context['post'].image: self.post.image,
        }
        for key, value in post_text.items():
            with self.subTest(key=key):
                self.assertEqual(key, value)

    def check_correct_context(self, response):
        first_object = response.context['page_obj'][0]
        context_objects = {
            self.post.author.id: first_object.author.id,
            self.post.text: first_object.text,
            self.group.slug: first_object.group.slug,
            self.post.id: first_object.id,
            self.post.image: first_object.image
        }
        for key, value in context_objects.items():
            with self.subTest(key=key):
                self.assertEqual(key, value)

    def test_edit_post_correct_context(self):
        response = self.auth_user.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}
            )
        )
        self.check_form_correct_context(response)

    def test_create_post_correct_context(self):
        response = self.auth_user.get(
            reverse('posts:post_create')
        )
        self.check_form_correct_context(response)

    def check_form_correct_context(self, response):
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for key, value in form_fields.items():
            with self.subTest(key=key):
                form_field = response.context['form'].fields[key]
                self.assertIsInstance(form_field, value)

    def test_post_added_correct(self):
        self.new_post = Post.objects.create(
            author=self.user,
            group=self.group,
            text='Тест на корректность',
        )
        group_count = Group.objects.count()
        response = [
            (self.auth_user.get(
                reverse('posts:index'))),
            (self.auth_user.get(
                reverse(
                    'posts:group_list',
                    kwargs={'slug': 'test'}))),
            (self.auth_user.get(
                reverse(
                    'posts:profile',
                    kwargs={'username': self.user.username}))),
        ]
        for i in response:
            self.assertContains(i, self.new_post.text, 1, status_code=200)
        self.assertEqual(Group.objects.count(), group_count)

    def test_group_post_added_correct(self):
        self.test_post_added_correct()
        group_check = Post.objects.filter(
            group=self.group_2
        ).count()
        self.assertEqual(group_check, 0)
        self.assertNotEqual(self.new_post.group, self.group_2)


class PaginatorViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='pagitester')
        cls.auth_user = Client()
        cls.auth_user.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовая группа 2',
            slug='test2',
            description='Тестовое описание 2')
        posts_paginator = []
        for i in range(0, POST_COUNT):
            posts_paginator.append(Post(text=f'Тестовая публикация {i}',
                                        author=cls.user,
                                        group=cls.group))
        cls.post_p = Post.objects.bulk_create(posts_paginator)

    def setUp(self):
        super().setUp()
        cache.clear()

    def test_correct_page_paginator(self):
        pages = (
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}),
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username})

        )
        for page in pages:
            response_page_1 = self.auth_user.get(page)
            response_page_2 = self.auth_user.get(page + '?page=2')
            count_posts_1 = len(response_page_1.context['page_obj'])
            count_posts_2 = len(response_page_2.context['page_obj'])
            self.assertEqual(count_posts_1, int(settings.NUMBER_SHOW))
            self.assertEqual(
                count_posts_2,
                (POST_COUNT - int(settings.NUMBER_SHOW))
            )


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class CommentsViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.commentator = User.objects.create_user(username='testcommentator')
        cls.post = Post.objects.create(
            author=cls.commentator,
            text='Обычная публикация',
            group=None,
            image=None
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.commentator,
            text='Тестовый комментарий'
        )
        cls.auth_comment_user = Client()
        cls.auth_comment_user.force_login(cls.commentator)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_comment_correct_context(self):
        response = self.auth_comment_user.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id':
                        self.post.pk}))
        comment_text = {
            response.context['comments'][0].author: self.comment.author,
            response.context['comments'][0].text: self.comment.text,
        }
        for key, value in comment_text.items():
            with self.subTest(key=key):
                self.assertEqual(key, value)

    def test_comment_form_context(self):
        response = self.auth_comment_user.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id':
                        self.post.pk})
        )
        form_field = {
            'text': forms.fields.CharField
        }
        for key, value in form_field.items():
            with self.subTest(key=key):
                form_field = response.context['form'].fields[key]
                self.assertIsInstance(form_field, value)
