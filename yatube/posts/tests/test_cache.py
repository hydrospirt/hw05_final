from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Post

User = get_user_model()


class CacheViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='cachetester')
        cls.auth_user = Client()
        cls.auth_user.force_login(cls.user)

    def test_cache_page_index(self):
        response = self.auth_user.get(reverse('posts:index'))
        posts = response.content
        Post.objects.create(
            author=self.user,
            text='КэшТектсТест'
        )
        response_again = self.auth_user.get(reverse('posts:index'))
        posts_again = response_again.content
        self.assertEqual(posts, posts_again)
        cache.clear()
        response_new = self.auth_user.get(reverse('posts:index'))
        posts_new = response_new.content
        self.assertNotEqual(posts_again, posts_new)
