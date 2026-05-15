from datetime import timedelta

import pytest
from django.test import Client
from django.utils import timezone

from news.forms import BAD_WORDS
from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='author')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='not_author')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    return News.objects.create(
        title='News title',
        text='News text',
        date=timezone.now().date(),
    )


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Comment text',
    )


@pytest.fixture
def comment_form_data():
    return {'text': 'New comment text'}


@pytest.fixture
def bad_comment_form_data():
    return {'text': f'????? ? ??????????? ?????? {BAD_WORDS[0]}'}


@pytest.fixture
def news_bulk():
    today = timezone.now().date()
    news_list = [
        News(
            title=f'News {index}',
            text='Text',
            date=today - timedelta(days=index),
        )
        for index in range(15)
    ]
    News.objects.bulk_create(news_list)
    return News.objects.order_by('-date')


@pytest.fixture
def comments_bulk(news, author):
    first = Comment.objects.create(news=news, author=author, text='First')
    second = Comment.objects.create(news=news, author=author, text='Second')
    Comment.objects.filter(pk=first.pk).update(
        created=timezone.now() - timedelta(days=1)
    )
    Comment.objects.filter(pk=second.pk).update(created=timezone.now())
    first.refresh_from_db()
    second.refresh_from_db()
    return first, second
