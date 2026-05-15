from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

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

    def test_note_in_list_for_author(self):
        response = self.author_client.get(reverse('notes:list'))
        self.assertIn(self.note, response.context['object_list'])

    def test_note_not_in_list_for_another_user(self):
        response = self.not_author_client.get(reverse('notes:list'))
        self.assertNotIn(self.note, response.context['object_list'])

    def test_pages_contains_form(self):
        names_with_args = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for name, args in names_with_args:
            with self.subTest(name=name):
                response = self.author_client.get(reverse(name, args=args))
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
