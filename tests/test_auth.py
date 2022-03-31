import pytest
from flask import g, session
from bad_apps_blog.db import get_db


def test_register(client, app):
    assert client.get('/auth/register').status_code == 200
    response = client.post(
        '/auth/register', data={'username': 'a', 'displayname' : 'user1' ,'password': 'a'}
    )
    assert '/auth/login' == response.headers['Location']

    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM user WHERE username = 'a'",
        ).fetchone() is not None


@pytest.mark.parametrize(('username', 'displayname', 'password', 'message'), (
    ('', '', '', b'Username is required.'),
    ('a', '', '', b'Password is required.'),
    ('test','a unique display name','test', b'already registered'),
    ('test_another','Alice','test', b'currently in use.'),
    ('test_another','test','test', b'currently in use.')
))
def test_register_validate_input(client, username, displayname, password, message):
    response = client.post(
        '/auth/register',
        data={'username': username, 'displayname' : displayname , 'password': password}
    )
    assert message in response.data


def test_login(client, auth):
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    assert response.headers['Location'] == '/'

    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user['username'] == 'test'


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', b'login failed'),
    ('test', 'a', b'login failed'),
))
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data


def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session

