"""

Bad Apps Blog

Author: Brandon Eskridge (a.k.a. 7UR7L3)

(Initial commit is based on the official Flask tutorial)

About: This app began as an (essentially) exact copy
of the official Flask tutorial (linke below). It is
intented as an opportunity to practice application
security, secure design, and secure coding techniques.
At the end of the Flask tutorial, the interested student
is challenged to implement several features. In order to
achive that goal, we will attempt to implement those features
while "pushing left" (security-wise) in the process.

Official Flask tutorial : https://flask.palletsprojects.com/en/2.0.x/tutorial/
"""

import os

from flask import Flask

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'bad_apps_blog.sqlite')
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # register the DBs with the current app instance
    from . import db
    db.init_app(app)

    # register the authorization blueprint
    from . import auth
    app.register_blueprint(auth.bp)

    # register the blog blueprint
    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')
    
    return app


