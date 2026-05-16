from http import HTTPStatus

from django.contrib.auth import get_user

from .common import (
    ADD_URL,
    DELETE_URL,
    DETAIL_URL,
    EDIT_URL,
    HOME_URL,
    LIST_URL,
    LOGIN_URL,
    LOGOUT_URL,
    SIGNUP_URL,
    SUCCESS_URL,
    BaseTestCase,
)


class TestRoutes(BaseTestCase):

    def test_status_codes(self):
        test_cases = (
            (HOME_URL, self.anonymous_client, HTTPStatus.OK),
            (LOGIN_URL, self.anonymous_client, HTTPStatus.OK),
            (SIGNUP_URL, self.anonymous_client, HTTPStatus.OK),
            (LIST_URL, self.author_client, HTTPStatus.OK),
            (ADD_URL, self.author_client, HTTPStatus.OK),
            (SUCCESS_URL, self.author_client, HTTPStatus.OK),
            (DETAIL_URL, self.author_client, HTTPStatus.OK),
            (EDIT_URL, self.author_client, HTTPStatus.OK),
            (DELETE_URL, self.author_client, HTTPStatus.OK),
            (LIST_URL, self.not_author_client, HTTPStatus.OK),
            (ADD_URL, self.not_author_client, HTTPStatus.OK),
            (SUCCESS_URL, self.not_author_client, HTTPStatus.OK),
            (DETAIL_URL, self.not_author_client, HTTPStatus.NOT_FOUND),
            (EDIT_URL, self.not_author_client, HTTPStatus.NOT_FOUND),
            (DELETE_URL, self.not_author_client, HTTPStatus.NOT_FOUND),
        )
        for url, client, expected_status in test_cases:
            client_username = get_user(client).username or 'anonymous'
            with self.subTest(
                url=url,
                client=client_username,
                expected_status=expected_status,
            ):
                response = client.get(url)
                self.assertEqual(response.status_code, expected_status)

    def test_redirects_for_anonymous_user(self):
        urls = (
            LIST_URL,
            ADD_URL,
            SUCCESS_URL,
            DETAIL_URL,
            EDIT_URL,
            DELETE_URL,
        )
        for url in urls:
            expected_url = f'{LOGIN_URL}?next={url}'
            with self.subTest(url=url, expected_status=HTTPStatus.FOUND):
                response = self.anonymous_client.get(url)
                self.assertRedirects(response, expected_url)

    def test_logout_for_anonymous_user(self):
        response = self.anonymous_client.post(LOGOUT_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)
