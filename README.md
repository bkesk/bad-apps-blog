# Bad Apps : Blog
An insecure blog web app intended as a starting point for practice with basic application security.
The goal is to add features, and explore possible vulnerabilities, what they look like in code, and how 
to fix/prevent those vulnerabilities.

![Build and Test](https://github.com/bkesk/bad-apps-blog/actions/workflows/python-app.yml/badge.svg)

## About
This app is a project that I started to practice application security (AppSec),
especially designing / writing secure code.
The initial version of this blog web application is based on the official 
[Flask tutorial](https://flask.palletsprojects.com/en/2.0.x/tutorial/)
which provides a full walk-through. The finished version of that project can
be found at the official Pallets Github repo: https://github.com/pallets/flask/tree/2.0.2/examples/tutorial.
The last section of the Flask tutorial challenges the interested learner to implement a few 
additional features. In this project, I will attempt to implement
those features while "pushing left" (security-wise) in the software 
development life cycle (SDLC) of this app.

A full list of requested features can be found at the end of the Flask tutorial: https://flask.palletsprojects.com/en/2.0.x/tutorial/next/

## Disclaimer

This blog web app should not be considered secure, or safe enough to host on the internet.
I recommend running local instances in your home lab, or other test environments which can't 
be accessed from the internet.

I'm learning as I go with this project, and I'm open to constructive comments and suggestions.

Feel free to fork this repository if you would like to practice AppSec this way.

## Installation:

It is recommended that you begin with fresh virtual environment,

```
$ python -m venv bad_apps_blog_venv
$ . bad_apps_blog_venv/bin/activate
```

Bad Apps : Blog can be easily installed by cloning this repo, then using `pip`. 
```
(bad_apps_blog_venv) $ git clone https://github.com/bkesk/bad-apps-blog/
(bad_apps_blog_venv) $ pip install -e .
```

You will also need to tell Flask that you want it to run Bad Apps Blog by setting the `FLASK_APP` 
environment variable. In bash, this can be done with:

```
(bad_apps_blog_venv) $ export FLASK_APP=bad_apps_blog
```

Bad Apps : blog uses SQLite, and you will need to initialize the database in order for the web app
to work properly.

```
(bad_apps_blog_venv) $ flask db-init
```

Now you can start a (non-production) instance of the app with Flask, which uses Werkzeug as an http server, like this:

```
(bad_apps_blog_venv) $ flask run
```

## Updating Bad Apps: Blog

Bad Apps: Blog can be updated to the most recent commit using standard `$ git pull origin`, assuming it was installed as described above.
The app will need to be restarted if it was running during the update for some updates to take effect.

Some new features involve changes to the sqlite database schema.
This may break instances of Bad Apps: Blog which use older versions of the database schema.
For now, the database needs to be updated manually, or a fresh instance should be created.
[sqlitebrowser](https://sqlitebrowser.org/) is a useful tool for manually exploring/editing a sqlite database.

This web app is currently developed for practice.
For the time being, the app is not meant for any production deployments.
Because of this, graceful database updates is not a priority.
A database migration tool is planned so that future updates are more reliable and can performed "in place" for existing app instances.

## Resources:

- "Alice and Bob Learn Application Security" by Tanya Janca (@shehackspurple) : https://shehackspurple.ca/books/ : This is an introductory-level textbook on AppSec. It covers all the topics needed to get started on this project, and much more!
- the Flask website: https://flask.palletsprojects.com/en/2.0.x/ : has many useful guides on developing, testing, deploying, etc.
  - see specifically the "Security Considerations" section: https://flask.palletsprojects.com/en/2.0.x/security/

## Licensing Informaiton

This project is derivative of code which is redistributed under the original project's BSD 3-clause license. See LICENSE.rst for details.
