import logging
import functools
import time
import secrets


from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.security import check_password_hash, generate_password_hash

from bad_apps_blog.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        displayname = request.form['displayname']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        
        if displayname is None or displayname == '':
            displayname = username

        # Need to validate that the requested displayname is not an existing username
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (displayname,)
        ).fetchone()

        if user is not None:
            error = f"Display name {displayname} is currently in use."
            current_app.logger.warning(f' [SECURITY] User registration failed : Reason : attempted to register an existing username ({user["username"]}) as display name')
            

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, displayname, password) VALUES (?, ?, ?)",
                    (username, displayname, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError as e:
                if 'username' in str(e):
                    error = f"User {username} is already registered."
                    current_app.logger.info(f'User registration failed : Reason : {error}')
                elif 'displayname' in str(e):
                    error = f"Display name {displayname} is currently in use."
                    current_app.logger.info(f'User registration failed : Reason : {error}')
                else:
                    error = "Registration failed."
                    current_app.logger.error(f'user registration failed due to DB integrity - error message: {e}')
            else:
                current_app.logger.info(f' [SECURITY] User {username} registered with displayname {displayname}')
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone() # this probably protects from db user dumping by forcing only one response

        if user is None:
            current_app.logger.warning(f'Failed login : Incorrect username.')
            error = 'login failed'
        elif not check_password_hash(user['password'], password):
            current_app.logger.warning(f'Failed login : Incorrect password.')
            error = 'login failed'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            current_app.logger.info(f' [SECURITY] successful login for user {username} ')
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request   # runs before the view function regardless of what URL is requested
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    current_app.logger.info(f' [SECURITY] user {g.user["username"]} logged out')
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            current_app.logger.info(f' [SECURITY] unauthenticated user attempted to access {view}')
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


def csrf_proect(view):
    '''
    Wrapper to apply token-based CSRF protection.

    on GET, should get token and render in a hidden field
    on POST, should check the token
    '''
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        user_id = session.get('user_id')

        if request.method == 'POST':
            current = get_db().execute(
            'SELECT * FROM csrf WHERE id = ?', (user_id,)).fetchone()
            
            # check that the token is not None
            try:
                # Q: do I need to process the "input" token in any way?
                # I'm not making a db query based on the token given in the form, 
                #   if there any validation needed though?
                assert current['token'] == request.form['form_number']
                current_app.logger.info(f' [SECURITY] CSRF token match for user {user_id}')
                assert current['expire'] > time.time()
                current_app.logger.info(f' [SECURITY] CSRF token is unexpired for {user_id}')
                return view(**kwargs)
            except:
                current_app.logger.error(f' [SECURITY] Possible CSRF attack : CSRF token does not match for user {user_id}')
                return redirect(url_for('index'))

        elif request.method == 'GET':
            token = gen_csrf_token()
            return view(token=token,**kwargs)
    
    return wrapped_view


def gen_csrf_token():
    '''
    Generate and track a CSRF token.
    '''
    user_id = session.get('user_id')

    db = get_db()
    current = db.execute(
            'SELECT * FROM csrf WHERE id = ?', (user_id,)
        ).fetchone()

    if current is not None:
        if current['expire'] > time.time():
            # reissue current token
            current_app.logger.info(f' [SECURITY] re-issued non-expired CSRF token to user {user_id}')
            return current['token']
        else:
            # generate / update new token
            current_app.logger.info(f' [SECURITY] updated expired CSRF token for user {user_id}')
            token = secrets.token_hex(64)
            db.execute(
                'UPDATE csrf SET token = ?, expire = ?'
                'WHERE id = ?',
                (token, time.time() + 3600.0, user_id)
            )
            db.commit()
            return token
    elif current is None:
        # TODO: use app configuration to set expiration age of CSRF tokens
        current_app.logger.info(f' [SECURITY] generated new CSRF token for user {user_id}')        
        token = secrets.token_hex(64)
        db.execute(
            'INSERT INTO csrf (id, token, expire)'
            'VALUES (?, ?, ?)',
            (user_id, token, time.time() + 3600.0 )
        )
        db.commit()
        return token
    else:
        logging.error('Failed to generate CSRF token')
        return None
