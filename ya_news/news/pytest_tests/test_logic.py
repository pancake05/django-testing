from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

COMMENT_TEXT = 'New comment text'
UPDATED_COMMENT_TEXT = 'Updated text'
HACK_COMMENT_TEXT = 'Hack text'
COMMENT_FORM_DATA = {'text': COMMENT_TEXT}


def test_anonymous_user_cant_create_comment(
    client,
    detail_url,
    login_url,
):
    comments_count_before = Comment.objects.count()
    response = client.post(detail_url, data=COMMENT_FORM_DATA)
    expected_url = f'{login_url}?next={detail_url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == comments_count_before


def test_user_can_create_comment(
    author_client,
    author,
    news,
    detail_url,
    detail_comments_url,
):
    comments_count_before = Comment.objects.count()
    response = author_client.post(detail_url, data=COMMENT_FORM_DATA)
    assertRedirects(response, detail_comments_url)
    assert Comment.objects.count() == comments_count_before + 1
    new_comment = Comment.objects.latest('pk')
    assert new_comment.news == news
    assert new_comment.author == author
    assert new_comment.text == COMMENT_FORM_DATA['text']


@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_user_cant_use_bad_words(author_client, detail_url, bad_word):
    bad_comment_form_data = {
        'text': f'Текст с запрещенным словом {bad_word}',
    }
    comments_count_before = Comment.objects.count()
    response = author_client.post(detail_url, data=bad_comment_form_data)
    form = response.context['form']
    assertFormError(form, 'text', errors=WARNING)
    assert Comment.objects.count() == comments_count_before


def test_author_can_edit_comment(
    author_client,
    comment,
    edit_url,
    detail_comments_url,
):
    response = author_client.post(
        edit_url,
        data={'text': UPDATED_COMMENT_TEXT},
    )
    assertRedirects(response, detail_comments_url)
    updated_comment = Comment.objects.get(pk=comment.pk)
    assert updated_comment.text == UPDATED_COMMENT_TEXT


def test_author_can_delete_comment(
    author_client,
    comment,
    delete_url,
    detail_comments_url,
):
    comments_count_before = Comment.objects.count()
    response = author_client.post(delete_url)
    assertRedirects(response, detail_comments_url)
    assert Comment.objects.count() == comments_count_before - 1
    assert not Comment.objects.filter(pk=comment.pk).exists()


def test_other_user_cant_edit_comment(not_author_client, comment, edit_url):
    comments_count_before = Comment.objects.count()
    response = not_author_client.post(
        edit_url,
        data={'text': HACK_COMMENT_TEXT},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == comments_count_before
    unchanged_comment = Comment.objects.get(pk=comment.pk)
    assert unchanged_comment.text == comment.text


def test_other_user_cant_delete_comment(
    not_author_client,
    comment,
    delete_url,
):
    comments_count_before = Comment.objects.count()
    response = not_author_client.post(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == comments_count_before
    assert Comment.objects.filter(pk=comment.pk).exists()
