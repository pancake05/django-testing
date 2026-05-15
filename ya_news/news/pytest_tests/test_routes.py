from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize('name', ('news:home', 'users:login', 'users:signup'))
def test_pages_availability_for_anonymous_user(client, name):
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_logout_availability_for_anonymous_user(client):
    url = reverse('users:logout')
    response = client.post(url)
    assert response.status_code == HTTPStatus.OK


def test_news_detail_availability_for_anonymous_user(client, news):
    url = reverse('news:detail', args=(news.pk,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('name', ('news:edit', 'news:delete'))
def test_pages_availability_for_author(author_client, name, comment):
    url = reverse(name, args=(comment.pk,))
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'client_fixture, expected_status',
    (
        ('not_author_client', HTTPStatus.NOT_FOUND),
        ('author_client', HTTPStatus.OK),
    ),
)
@pytest.mark.parametrize('name', ('news:edit', 'news:delete'))
def test_pages_availability_for_different_users(
    client_fixture,
    name,
    comment,
    expected_status,
    request,
):
    user_client = request.getfixturevalue(client_fixture)
    url = reverse(name, args=(comment.pk,))
    response = user_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize('name', ('news:edit', 'news:delete'))
def test_redirects_for_anonymous_user(client, name, comment):
    url = reverse(name, args=(comment.pk,))
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
