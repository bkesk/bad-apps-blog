import os
import secrets
import click
from flask import current_app, g
from flask.cli import with_appcontext

def init_config():
    # respect current settings if already set
    if current_app.config['SECRET_KEY'] is None:
        current_app.logger.info(f' {__name__} : Configuration is incomplete : generating configuration file in instance folder')
        with open(os.path.join(current_app.instance_path, 'config.py'), 'a') as f:
            f.write('SECRET_KEY="'+secrets.token_hex(32)+'"')
        return "Initialized config.py"
    else:
        current_app.logger.info(f' {__name__} : Configuration is complete : no action necessary')
        return "Nothing to initialize."


@click.command('init-config')
@with_appcontext
def init_config_command():
    """Clear the existing data and create new tables."""
    output = init_config()
    click.echo(output)


def init_app(app):
    app.cli.add_command(init_config_command)

