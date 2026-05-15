from django.conf import settings
from django.urls import reverse

import pytest

from news.forms import CommentForm

pytestmark = pytest.mark.django_db


@pytest.mark.usefixtures('news_bulk')
def test_news_count_on_home_page(client):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    assert len(object_list) <= settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.usefixtures('news_bulk')
def test_news_sorting_on_home_page(client):
    url = reverse('news:home')
    response = client.get(url)
    dates = [news.date for news in response.context['object_list']]
    assert dates == sorted(dates, reverse=True)


def test_comments_sorting_on_news_detail(client, news, comments_bulk):
    url = reverse('news:detail', args=(news.pk,))
    response = client.get(url)
    comments = list(response.context['object'].comment_set.all())
    created = [comment.created for comment in comments]
    assert created == sorted(created)


@pytest.mark.parametrize(
    'client_fixture, has_form',
    (
        ('client', False),
        ('author_client', True),
    ),
)
def test_comment_form_availability(client_fixture, has_form, news, request):
    user_client = request.getfixturevalue(client_fixture)
    url = reverse('news:detail', args=(news.pk,))
    response = user_client.get(url)
    assert ('form' in response.context) is has_form
    if has_form:
        assert isinstance(response.context['form'], CommentForm)
