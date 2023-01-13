from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post, Comment, Follow

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='testmodeler')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая публикация',
        )

    def test_models_have_correct_objects_names(self):
        post = PostModelTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))

    def test_verbose_name(self):
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа'
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected
                )

    def test_help_text(self):
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Заполните текст публикации',
            'author': 'Укажите автора публикации',
            'group': 'Название группы, к которой относится публикация',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected
                )


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Новая группа',
            slug='test',
            description='Тестовое описание',
        )

    def test_models_have_correct_objects_names(self):
        group = GroupModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

    def test_verbose_name(self):
        group = GroupModelTest.group
        field_verboses = {
            'title': 'Название',
            'slug': 'Слаг',
            'description': 'Описание',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected
                )

    def test_help_test(self):
        group = GroupModelTest.group
        field_help_texts = {
            'title': 'Название группы, к которой относится публикация',
            'slug': 'Уникальный фрагмент URL-адреса',
            'description': 'Укажите подробное описание группы',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected
                )


class CommentsModelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.commentor = User.objects.create_user(username='testcouser')
        cls.post = Post.objects.create(
            author=cls.commentor,
            text='Тестовая публикация',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.commentor,
            text='Мой первый комметарий',
        )

    def test_models_have_correct_objects_names(self):
        comment = CommentsModelTests.comment
        expected_object_name = f'Комментарий от {comment.author}'
        self.assertEqual(expected_object_name, str(comment))

    def test_verbose_name(self):
        comment = CommentsModelTests.comment
        field_verboses = {
            'post': 'Ссылка на публикацию',
            'author': 'Автор',
            'text': 'Текст комментария',
            'created': 'Дата комментария'
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    comment._meta.get_field(value).verbose_name, expected
                )

    def test_help_text(self):
        comment = CommentsModelTests.comment
        field_help_texts = {
            'text': 'Напишите текст комментария'
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    comment._meta.get_field(value).help_text, expected
                )


class FollowModelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.follower = User.objects.create_user(username='testfollower')
        cls.following = User.objects.create_user(username='testfollowing')
        cls.follow = Follow.objects.create(
            user=cls.follower,
            author=cls.following,
        )
        cls.post = Post.objects.create(
            author=cls.following,
            text='Моя известная публикация'
        )

    def test_models_have_correct_objects_names(self):
        follow = FollowModelTests.follow
        expected_object_name = (f'{self.follower} подписан(-а)'
                                f' на {self.following}')
        self.assertEqual(expected_object_name, str(follow))

    def test_verbose_name(self):
        follow = FollowModelTests.follow
        field_verboses = {
            'user': 'Подписчик',
            'author': 'Автор',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    follow._meta.get_field(value).verbose_name, expected
                )
