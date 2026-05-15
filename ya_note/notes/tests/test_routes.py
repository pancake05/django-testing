from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.not_author = User.objects.create(username='not_author')
        cls.note = Note.objects.create(
            title='Title',
            text='Text',
            slug='note-slug',
            author=cls.author,
        )

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.not_author_client = Client()
        self.not_author_client.force_login(self.not_author)

    def test_pages_availability_for_anonymous_user(self):
        for name in ('notes:home', 'users:login', 'users:signup'):
            with self.subTest(name=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, HTTPStatus.OK)

        response = self.client.post(reverse('users:logout'))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_pages_availability_for_auth_user(self):
        for name in ('notes:list', 'notes:add', 'notes:success'):
            with self.subTest(name=name):
                response = self.not_author_client.get(reverse(name))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_different_users(self):
        test_cases = (
            (self.author_client, HTTPStatus.OK),
            (self.not_author_client, HTTPStatus.NOT_FOUND),
        )
        for name in ('notes:detail', 'notes:edit', 'notes:delete'):
            for user_client, expected_status in test_cases:
                with self.subTest(name=name, status=expected_status):
                    url = reverse(name, args=(self.note.slug,))
                    response = user_client.get(url)
                    self.assertEqual(response.status_code, expected_status)

    def test_redirects_for_anonymous_user(self):
        login_url = reverse('users:login')
        names_with_args = (
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )
        for name, args in names_with_args:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                expected_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, expected_url)
