from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )

        def setUp(self):
            self.authorized_author_client = Client()
            self.authorized_author_client.force_login(self.user)

        def test_create_post(self):
            posts_count = Post.objects.count()

            form_data = {
                'text': 'Тестовый текст',
                'group': self.group
            }

            response = self.authorized_author_client.post(
                reverse('posts:post_create'),
                data=form_data,
                follow=True
            )
            self.assertRedirects(
                response, reverse(
                    'posts:profile', kwargs={'username': self.user.username}
                )
            )
            self.assertEqual(Post.objects.count(), posts_count + 1)

        def test_edit_post(self):
            form_data = {
                'text': 'Измененный текст',
                'group': self.group
            }
            response = self.authorized_author_client.post(
                reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
                data=form_data,
                follow=True
            )
            self.assertRedirects(
                response, reverse(
                    'posts:post_detail', kwargs={'post_id': self.post.id}
                )
            )
            self.assertEqual(response.context['post'].text, form_data['text'])
