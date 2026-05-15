from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_create_comment(client, news, comment_form_data):
    url = reverse('news:detail', args=(news.pk,))
    response = client.post(url, data=comment_form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
    author_client,
    author,
    news,
    comment_form_data,
):
    url = reverse('news:detail', args=(news.pk,))
    response = author_client.post(url, data=comment_form_data)
    expected_url = f"{reverse('news:detail', args=(news.pk,))}#comments"
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.news == news
    assert new_comment.author == author
    assert new_comment.text == comment_form_data['text']


def test_user_cant_use_bad_words(author_client, news, bad_comment_form_data):
    url = reverse('news:detail', args=(news.pk,))
    response = author_client.post(url, data=bad_comment_form_data)
    form = response.context['form']
    assertFormError(form, 'text', errors=WARNING)
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(author_client, comment):
    url = reverse('news:edit', args=(comment.pk,))
    response = author_client.post(url, data={'text': 'Updated text'})
    expected_url = (
        f"{reverse('news:detail', args=(comment.news.pk,))}#comments"
    )
    assertRedirects(response, expected_url)
    comment.refresh_from_db()
    assert comment.text == 'Updated text'


def test_author_can_delete_comment(author_client, comment):
    url = reverse('news:delete', args=(comment.pk,))
    response = author_client.post(url)
    expected_url = (
        f"{reverse('news:detail', args=(comment.news.pk,))}#comments"
    )
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_other_user_cant_edit_comment(not_author_client, comment):
    url = reverse('news:edit', args=(comment.pk,))
    response = not_author_client.post(url, data={'text': 'Hack text'})
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == 'Comment text'


def test_other_user_cant_delete_comment(not_author_client, comment):
    url = reverse('news:delete', args=(comment.pk,))
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.filter(pk=comment.pk).exists()
