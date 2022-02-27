import logging
import functools

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
            logging.warning(f'User registration failed : Reason : attempted to register and existing username ({user["username"]}) as display name')
            

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
                    logging.info(f'User registration failed : Reason : {error}')
                elif 'displayname' in str(e):
                    error = f"Display name {displayname} is currently in use."
                    logging.info(f'User registration failed : Reason : {error}')
                else:
                    error = "Registration failed."
                    logging.warning(f'user registration failed due to DB integrity - error message: {e}')
            else:
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
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

