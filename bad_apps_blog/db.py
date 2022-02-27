import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext

def gen_db():
    db = sqlite3.connect(
        current_app.config['DATABASE'],
        detect_types=sqlite3.PARSE_DECLTYPES
    )
    db.row_factory = sqlite3.Row
    return db

def get_db():
    if 'db' not in g:
        g.db = gen_db()

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db(db=None):
    if db is None:
        db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

    db.execute(
        'INSERT INTO app_details (detail_id, db_version, app_version)'
        ' VALUES (?, ?, ?)',
        (0, current_app.config['DB_VERSION'],current_app.config['APP_VERSION'])
        )


# TODO: Add Database Migration click command

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

# we need this since we are using an application factory (and not a global instance)
# so that we can register the dbs with the app instance created.
def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)



