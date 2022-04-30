import pytest
from bad_apps_blog.db import get_db

def test_csrf_attack(client, auth, app, caplog):
    # log our test user in
    auth.login()
    # test user triggers the following payloads on the web.
    assert client.post('/create', data={'title' : 'CSRF ATTACK!' , 'body' : 'This user was sea surfed', 'form_number' : 'abababababab'}).status_code == 403
    assert "Possible CSRF attack" in caplog.text

    # check that no post was added to the db!
    with app.app_context():   
        db = get_db()
        count = db.execute('SELECT COUNT(id) FROM post').fetchone()[0]
        assert count == 1

    assert client.post('/1/update', data={'title' : 'CSRF ATTACK!', 'body' : 'This user was sea surfed',  'form_number' : 'abababababab'}).status_code == 403
    assert "Possible CSRF attack" in caplog.text

    assert client.post('/1/delete', data = { 'form_number' : 'abababababab'}).status_code == 403
    assert "Possible CSRF attack" in caplog.text

