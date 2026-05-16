from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

ANON_CLIENT = 'client'
AUTHOR_CLIENT = 'author_client'
NOT_AUTHOR_CLIENT = 'not_author_client'

HOME_URL = 'home_url'
LOGIN_URL = 'login_url'
SIGNUP_URL = 'signup_url'
DETAIL_URL = 'detail_url'
EDIT_URL = 'edit_url'
DELETE_URL = 'delete_url'


@pytest.mark.parametrize(
    'client_fixture, url_fixture, expected_status',
    (
        (ANON_CLIENT, HOME_URL, HTTPStatus.OK),
        (ANON_CLIENT, LOGIN_URL, HTTPStatus.OK),
        (ANON_CLIENT, SIGNUP_URL, HTTPStatus.OK),
        (ANON_CLIENT, DETAIL_URL, HTTPStatus.OK),
        (AUTHOR_CLIENT, EDIT_URL, HTTPStatus.OK),
        (AUTHOR_CLIENT, DELETE_URL, HTTPStatus.OK),
        (NOT_AUTHOR_CLIENT, EDIT_URL, HTTPStatus.NOT_FOUND),
        (NOT_AUTHOR_CLIENT, DELETE_URL, HTTPStatus.NOT_FOUND),
    ),
)
def test_pages_status_codes(
    client_fixture,
    url_fixture,
    expected_status,
    request,
):
    user_client = request.getfixturevalue(client_fixture)
    url = request.getfixturevalue(url_fixture)
    response = user_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url_fixture',
    (
        EDIT_URL,
        DELETE_URL,
    ),
)
def test_redirects_for_anonymous_user(client, url_fixture, login_url, request):
    url = request.getfixturevalue(url_fixture)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)


def test_logout_availability_for_anonymous_user(client, logout_url):
    response = client.post(logout_url)
    assert response.status_code == HTTPStatus.OK
