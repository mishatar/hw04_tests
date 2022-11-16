from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User
from ..forms import PostForm


class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='bilbo')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )

    def setUp(self):
        self.client = Client()
        self.auth = Client()
        self.auth.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            (
                reverse('posts:group_list', kwargs={'slug': 'slug_slug'})
            ): 'posts/group_list.html',
            (
                reverse('posts:profile',
                        kwargs={'username': self.user.username})
            ): 'posts/profile.html',
            (
                reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
            ): 'posts/post_detail.html',
            (
                reverse('posts:post_edit', kwargs={'post_id': self.post.pk})
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=reverse_name):
                response = self.auth.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.auth.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        group_title_0 = first_object.group.title
        post_text_0 = first_object.text
        group_slug_0 = first_object.group.slug
        self.assertEqual(group_title_0, self.group.title)
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(group_slug_0, self.group.slug)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.auth.get(reverse(
            'posts:group_list', kwargs={'slug': 'slug_slug'}))
        first_object = response.context['page_obj'][0]
        post_group_0 = first_object.group.title
        self.assertEqual(post_group_0, PostViewsTests.group.title)
        self.assertEqual(len(response.context['page_obj']), 1)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.auth.get(reverse(
            'posts:profile', kwargs={'username': 'bilbo'}))
        first_object = response.context['page_obj'][0]
        post_group_0 = first_object.author
        self.assertEqual(post_group_0, PostViewsTests.post.author)
        self.assertEqual(len(response.context['page_obj']), 1)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.auth.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk}))
        first_object = response.context['post']
        self.assertEqual(first_object.pk, PostViewsTests.post.pk)

    def test_edit_post_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом"""
        response = self.auth.get(reverse('posts:post_edit',
                                         kwargs={'post_id': self.post.pk})
                                 )
        first_object = response.context['form']
        self.assertIsInstance(first_object, PostForm)

    def test_create_post_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.auth.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='bilbo')
        cls.group1 = Group.objects.create(
            title='Тестовая группа',
            slug='slug_slug',
            description='Тестовое описание',
        )
        posts_list = []
        for i in range(13):
            posts_list.append(Post(
                author=cls.user,
                text=f'Текстовый пост {i}',
                group=cls.group1,
                pk=i
            ))
        cls.post = Post.objects.bulk_create(posts_list)

    def setUp(self):
        self.client = Client()
        self.auth = Client()
        self.auth.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_first_page_group_list_contains_ten_records(self):
        response = self.client.get(reverse(
            'posts:group_list', kwargs={'slug': 'slug_slug'}))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_first_page_profile_contains_ten_records(self):
        response = self.auth.get(reverse(
            'posts:profile', kwargs={'username': 'bilbo'}))
        self.assertEqual(len(response.context['page_obj']), 10)
