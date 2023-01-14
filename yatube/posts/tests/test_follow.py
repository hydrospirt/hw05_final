from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Follow

User = get_user_model()


class FollowViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='followtester')
        cls.auth_user = Client()
        cls.auth_user.force_login(cls.user)
        cls.author = User.objects.create_user(username='authortester')

    def setUp(self):
        super().setUp()
        self.post = Post.objects.create(
            author=self.author,
            text='Хороший текст'
        )

    def test_follow(self):
        self.auth_user.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.author.username})
        )
        self.assertTrue(Follow.objects.filter(
            user=self.user, author=self.author).exists())

    def test_unfollow(self):
        Follow.objects.create(
            user=self.user,
            author=self.author
        )
        self.auth_user.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.author.username})
        )
        self.assertFalse(Follow.objects.filter(
            user=self.user, author=self.author).exists())

    def test_follow_view_context(self):
        Follow.objects.create(
            user=self.user,
            author=self.author
        )
        response = self.auth_user.get(
            reverse('posts:follow_index')
        )
        f_object = response.context['page_obj'][0]
        post_context = {
            f_object.text: self.post.text,
            f_object.author: self.post.author,
            f_object.id: self.post.id
        }
        for key, value in post_context.items():
            with self.subTest(key=key):
                self.assertEqual(key, value)
