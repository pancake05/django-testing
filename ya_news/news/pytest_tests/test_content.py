from django.conf import settings

import pytest

from news.forms import CommentForm

@pytest.mark.usefixtures('news_bulk')
def test_news_count_on_home_page(client, home_url):
    response = client.get(home_url)
    object_list = response.context['object_list']
    assert object_list.count() <= settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.usefixtures('news_bulk')
def test_news_sorting_on_home_page(client, home_url):
    response = client.get(home_url)
    dates = [news.date for news in response.context['object_list']]
    assert dates == sorted(dates, reverse=True)


def test_comments_sorting_on_news_detail(client, detail_url, comments_bulk):
    response = client.get(detail_url)
    comments = list(response.context['object'].comment_set.all())
    created = [comment.created for comment in comments]
    assert created == sorted(created)


def test_anonymous_user_has_no_comment_form(client, detail_url):
    response = client.get(detail_url)
    assert 'form' not in response.context


def test_authorized_user_has_comment_form(author_client, detail_url):
    response = author_client.get(detail_url)
    assert isinstance(response.context.get('form'), CommentForm)
