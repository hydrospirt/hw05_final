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

    def test_follow_mode(self):
        response = self.auth_user.get(
            reverse('posts:profile_follow',
            kwargs={'username': self.author.username}
            )
        )
        self.assertEqual(Follow.objects.count(), 1)
        response = self.auth_user.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(
            response.context['page_obj'][0], self.post
        )

        response = self.auth_user.get(
            reverse('posts:profile_unfollow',
            kwargs={'username': self.author.username}
            )
        )
        self.assertEqual(Follow.objects.count(), 0)
        self.assertFalse(
            response.context, None
        )