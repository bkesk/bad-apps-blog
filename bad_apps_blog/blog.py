from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
from werkzeug.exceptions import abort

from bad_apps_blog.auth import login_required
from bad_apps_blog.db import get_db

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, displayname'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            current_app.logger.info('new post created')
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            current_app.logger.info('new post successfully commited to db')
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, displayname'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    try:
        assert isinstance(id, int)
    except AssertionError:
        current_app.logger.error(f' [BUG] Recieved "id" which is not an integer : enforce with "/<int:id>/" in all routes.')

    if post is None:
        current_app.logger.info(f' [SECURITY] attempted to access post {id} which does not exist')
        abort(404, f"Post doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        current_app.logger.info(f' [SECURITY] attempted to access priviledged view of post {id} whithout authZ')
        abort(403)

    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            current_app.logger.info(f'post {id} updated')
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            current_app.logger.info(f'post {id} updates successfully commited to db')
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    current_app.logger.warning(f' [SECURITY] post {id} is being deleted')
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    current_app.logger.info(f' [SECURITY] delete post {id} successfully commited to db')
    return redirect(url_for('blog.index'))


@bp.route('/<int:id>/detail', methods=('GET',))
def detail(id):
    post = get_post(id,check_author=False)
    return render_template('blog/detail.html', post=post)