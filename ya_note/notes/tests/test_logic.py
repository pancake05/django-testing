from http import HTTPStatus

from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestLogic(TestCase):

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
        cls.form_data = {
            'title': 'New title',
            'text': 'New text',
            'slug': 'new-slug',
        }

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.not_author_client = Client()
        self.not_author_client.force_login(self.not_author)

    def test_user_can_create_note(self):
        Note.objects.all().delete()
        response = self.author_client.post(
            reverse('notes:add'),
            data=self.form_data,
        )
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        Note.objects.all().delete()
        url = reverse('notes:add')
        response = self.client.post(url, data=self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_not_unique_slug(self):
        notes_count = Note.objects.count()
        form_data = self.form_data.copy()
        form_data['slug'] = self.note.slug
        response = self.author_client.post(
            reverse('notes:add'),
            data=form_data,
        )
        form = response.context['form']
        error = self.note.slug + WARNING
        self.assertFormError(form, 'slug', error)
        self.assertEqual(Note.objects.count(), notes_count)

    def test_empty_slug(self):
        Note.objects.all().delete()
        form_data = self.form_data.copy()
        form_data.pop('slug')
        response = self.author_client.post(
            reverse('notes:add'),
            data=form_data,
        )
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.slug, slugify(form_data['title']))

    def test_author_can_edit_note(self):
        response = self.author_client.post(
            reverse('notes:edit', args=(self.note.slug,)),
            data=self.form_data,
        )
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])

    def test_other_user_cant_edit_note(self):
        old_title = self.note.title
        old_text = self.note.text
        old_slug = self.note.slug
        response = self.not_author_client.post(
            reverse('notes:edit', args=(self.note.slug,)),
            data=self.form_data,
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, old_title)
        self.assertEqual(self.note.text, old_text)
        self.assertEqual(self.note.slug, old_slug)

    def test_author_can_delete_note(self):
        response = self.author_client.post(
            reverse('notes:delete', args=(self.note.slug,))
        )
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_delete_note(self):
        response = self.not_author_client.post(
            reverse('notes:delete', args=(self.note.slug,))
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
