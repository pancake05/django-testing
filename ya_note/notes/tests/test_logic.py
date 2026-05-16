from http import HTTPStatus

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from .common import (
    ADD_URL,
    DELETE_URL,
    EDIT_URL,
    LOGIN_URL,
    SUCCESS_URL,
    BaseTestCase,
)


class TestLogic(BaseTestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.form_data = {
            'title': 'New title',
            'text': 'New text',
            'slug': 'new-slug',
        }

    def test_user_can_create_note(self):
        notes_count_before = Note.objects.count()
        response = self.author_client.post(
            ADD_URL,
            data=self.form_data,
        )
        self.assertRedirects(response, SUCCESS_URL)
        self.assertEqual(Note.objects.count(), notes_count_before + 1)
        new_note = Note.objects.get(slug=self.form_data['slug'])
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        notes_count_before = Note.objects.count()
        response = self.anonymous_client.post(ADD_URL, data=self.form_data)
        expected_url = f'{LOGIN_URL}?next={ADD_URL}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), notes_count_before)

    def test_not_unique_slug(self):
        notes_count = Note.objects.count()
        form_data = self.form_data.copy()
        form_data['slug'] = self.note.slug
        response = self.author_client.post(
            ADD_URL,
            data=form_data,
        )
        form = response.context['form']
        error = self.note.slug + WARNING
        self.assertFormError(form, 'slug', error)
        self.assertEqual(Note.objects.count(), notes_count)

    def test_empty_slug(self):
        notes_count_before = Note.objects.count()
        form_data = self.form_data.copy()
        form_data.pop('slug')
        response = self.author_client.post(
            ADD_URL,
            data=form_data,
        )
        self.assertRedirects(response, SUCCESS_URL)
        self.assertEqual(Note.objects.count(), notes_count_before + 1)
        new_note = Note.objects.get(title=form_data['title'])
        self.assertEqual(new_note.slug, slugify(form_data['title']))

    def test_author_can_edit_note(self):
        response = self.author_client.post(
            EDIT_URL,
            data=self.form_data,
        )
        self.assertRedirects(response, SUCCESS_URL)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])

    def test_other_user_cant_edit_note(self):
        old_title = self.note.title
        old_text = self.note.text
        old_slug = self.note.slug
        notes_count_before = Note.objects.count()
        response = self.not_author_client.post(
            EDIT_URL,
            data=self.form_data,
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), notes_count_before)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, old_title)
        self.assertEqual(self.note.text, old_text)
        self.assertEqual(self.note.slug, old_slug)

    def test_author_can_delete_note(self):
        notes_count_before = Note.objects.count()
        response = self.author_client.post(
            DELETE_URL
        )
        self.assertRedirects(response, SUCCESS_URL)
        self.assertEqual(Note.objects.count(), notes_count_before - 1)

    def test_other_user_cant_delete_note(self):
        notes_count_before = Note.objects.count()
        response = self.not_author_client.post(
            DELETE_URL
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), notes_count_before)
