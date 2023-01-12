import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Group, Post, Comment
from django.core.files.uploadedfile import SimpleUploadedFile

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()
SMALL_GIF = (
             b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B'
        )


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title='ТестФорм группа 1',
            slug='testform',
            description='Тестовое описание'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        super().setUp()
        self.guest = Client()
        self.user = User.objects.create_user(username='testformer')
        self.auth_user = Client()
        self.auth_user.force_login(self.user)

    def test_create_post(self):
        post_count = Post.objects.count()
        form_data = {
            'text': 'Текст публикации в форме',
            'group': self.group.pk,
            'image': self.uploaded
        }
        response = self.auth_user.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse('posts:profile',
        kwargs={'username': self.user.username}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
            text='Текст публикации в форме',
            group=self.group.pk,
            author=self.user,
            image='posts/small.gif',
            ).exists()
        )


    def test_edit_form_post(self):
        self.old_post = Post.objects.create(
            text='Текст для тестирвоания формы',
            author=self.user,
            group=self.group,
        )
        group2 = Group.objects.create(
            title='ТестФорм группа 2',
            slug='testform2',
            description='Тестовое описание',
        )
        post_count = Post.objects.count()
        form_data = {
            'text': 'Текст публикации в форме',
            'group': group2.pk,
        }
        response = self.auth_user.post(
            reverse('posts:post_edit', kwargs={'post_id': self.old_post.pk}),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotEqual(self.old_post.text, form_data['text'])
        self.assertNotEqual(self.old_post.group, form_data['group'])
        self.assertEqual(Post.objects.count(), post_count)
        self.assertEqual(group2.pk, form_data['group'])
        self.assertContains(response, form_data['text'], 1, HTTPStatus.OK)


class CommentFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest = Client()
        cls.user = User.objects.create_user(username='testcommenter')
        cls.auth_user = Client()
        cls.auth_user.force_login(cls.user)

        cls.post_c = Post.objects.create(
            text='Текст публикации',
            author=cls.user,
            group=None
        )

    def test_comment_form(self):
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый комментарий'
        }
        response = self.auth_user.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id':
                self.post_c.pk}),
                data=form_data,
                follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse('posts:post_detail',
        kwargs={'post_id': self.post_c.pk}))
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                text='Тестовый комментарий',
                author=self.user
            )
        )
    def test_comment_form_guest(self):
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Гость не может комментировать'
        }
        response = self.guest.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id':
                self.post_c.pk}),
                data=form_data,
                follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotEqual(Comment.objects.count(), comment_count + 1)
        self.assertFalse(
            Comment.objects.filter(
                text='Гость не может комментировать',
            )
        )
