from datetime import timedelta

import pytest
from django.conf import settings
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


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
def news_bulk():
    today = timezone.now().date()
    total_news = settings.NEWS_COUNT_ON_HOME_PAGE + 5
    news_list = [
        News(
            title=f'News {index}',
            text='Text',
            date=today - timedelta(days=index),
        )
        for index in range(total_news)
    ]
    News.objects.bulk_create(news_list)


@pytest.fixture
def comments_bulk(news, author):
    created_base = timezone.now()
    for index in range(2):
        current_comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Comment {index}',
        )
        current_comment.created = created_base + timedelta(seconds=index)
        current_comment.save(update_fields=['created'])


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def logout_url():
    return reverse('users:logout')


@pytest.fixture
def signup_url():
    return reverse('users:signup')


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.pk,))


@pytest.fixture
def detail_comments_url(news):
    return f"{reverse('news:detail', args=(news.pk,))}#comments"


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.pk,))


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.pk,))
