import pytest
from django.urls import reverse

from pythonpro.django_assertions import dj_assert_contains
from pythonpro.domain.user_facade import find_user_interactions
from pythonpro.launch.views import LAUNCH_STATUS_CPL1, LAUNCH_STATUS_OPEN_CART, LAUNCH_STATUS_PPL


@pytest.fixture
def tag_as_mock(mocker):
    return mocker.patch('pythonpro.domain.user_facade._email_marketing_facade.tag_as')


@pytest.fixture
def launch_status_as_mock(mocker):
    return mocker.patch(
        'pythonpro.launch.views._get_launch_status', return_value=LAUNCH_STATUS_CPL1
    )


@pytest.fixture
def resp(client, tag_as_mock, launch_status_as_mock):
    return client.get(reverse('launch:cpl1'), secure=True)


def test_status_code(resp):
    assert 200 == resp.status_code


def test_email_marketing_tag_not_called(resp, tag_as_mock):
    assert tag_as_mock.call_count == 0


def test_cpl_video_is_present(resp):
    dj_assert_contains(resp, 'https://www.youtube.com/embed/')


def test_facebook_comments_is_present(resp):
    dj_assert_contains(resp, f'<div class="fb-comments"')


@pytest.fixture
def resp_with_user(client_with_user, tag_as_mock):
    return client_with_user.get(reverse('launch:cpl1'), secure=True)


def test_user_interaction(resp_with_user, logged_user):
    assert 'CPL1' in [i.category for i in find_user_interactions(logged_user)]


def test_email_marketing_tag(resp_with_user, logged_user, tag_as_mock):
    tag_as_mock.assert_called_once_with(logged_user.email, logged_user.id, 'cpl1')


@pytest.fixture
def resp_with_user_with_launch_status_open_cart(
        client_with_user, tag_as_mock, launch_status_as_mock
):
    launch_status_as_mock.return_value = LAUNCH_STATUS_OPEN_CART
    return client_with_user.get(reverse('launch:cpl1'), secure=True)


def test_should_redirect_to_subscribe(resp_with_user_with_launch_status_open_cart, resp_with_user):
    assert resp_with_user.status_code == 302


@pytest.fixture
def resp_with_user_with_launch_status_ppl(
        client_with_user, tag_as_mock, launch_status_as_mock
):
    launch_status_as_mock.return_value = LAUNCH_STATUS_PPL
    return client_with_user.get(reverse('launch:cpl1'), secure=True)


def test_should_redirect_to_ppl(resp_with_user_with_launch_status_ppl, resp_with_user):
    assert resp_with_user.status_code == 302
