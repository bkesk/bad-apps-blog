# Bad Apps : Blog
An *initially* insecure blog web app intended as a starting point for practice with basic application security.
The final goal is to make the app secure enough to be exposed to the internet.

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


### using git and pip

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

### as a Container

Bad Apps: Blog can be built from the Containerfile using standard container engines like Docker, Podman, etc.
We'll use podman here, since it can run containers in rootless made, but the same commands work for Docker.

First, you will need to download the Containerfile. From the directory with the Containerfile, run:

```
$ podman build -t bad_apps .
```

You can run the container with a **nonpersistent database** using:

```
$ podman run --rm -p 5000 bad_apps:test sh -c "flask init-db; flask init-config; flask run --host=0.0.0.0"
```

When using this command, Podman (or Docker) will automatically forward a local port to port 5000 of the container.
You can check which port using: `$ podman ps`, and you can navigate to the app in your browser at `http://localhost:[port from podman ps]`.

The configuration file, `config.py` contains secrets, and should not be included in a container image.
Before, we ran in a script within the container to generate a `config.py` file within the container, but 
we may want to use a specific `config.py` in practice.
Instead, use the container engine's secret manager.

First, make a 'secret':

```
$ podman secret create [name of secret] /path/on/host/conf.py
```

To include the secret configuration file use:

```
podman run --rm -p 5000 --secret blog_conf \
       sh -c "mkdir /var/www/app/instance; ln -s /run/secrets/blog_conf /var/www/app/instance/config.py; flask init-db; flask run --host=0.0.0.0"
```

note that this will create a fresh (empty) database instance for the app within the container.

Finally, we will usually want to mount an existing database so that application data is persistent.
We can use a volume for this.

```
podman run --rm -ti -p 5000 --secret blog_conf \
           --volume /path/on/host/to/db/:/var/www/app/db/:Z \
           bad_apps sh -c "mkdir /var/www/app/instance; ln -s /run/secrets/blog_conf /var/www/app/instance/config.py; sh"
```

The `:Z` option instructs podman to relable the mounted directory for SELinux.

**Important:** We need to tell Bad Apps: Blog where to find the database, since it will not be inside the instance folder.
You can simply add the following to your `config.py` file:

```
DATABASE="/var/www/app/db/[name of db file]"
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
