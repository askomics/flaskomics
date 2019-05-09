"""AskOmics app

Attributes
----------
BLUEPRINTS : Tuple
    Flask blueprints
"""

from askomics.api.admin import admin_bp
from askomics.api.auth import auth_bp
from askomics.api.datasets import datasets_bp
from askomics.api.file import file_bp
from askomics.api.sparql import sparql_bp
from askomics.api.start import start_bp
from askomics.api.query import query_bp
from askomics.api.view import view_bp

from celery import Celery

from flask import Flask

from flask_ini import FlaskIni


__all__ = ('create_app', 'create_celery')

BLUEPRINTS = (
    sparql_bp,
    start_bp,
    view_bp,
    auth_bp,
    admin_bp,
    file_bp,
    datasets_bp,
    query_bp
)


def create_app(config='config/askomics.ini', app_name='askomics', blueprints=None):
    """Create the AskOmics app

    Parameters
    ----------
    config : str, optional
        Path to the config file
    app_name : str, optional
        Application name
    blueprints : None, optional
        Flask blueprints

    Returns
    -------
    Flask
        AskOmics Flask application
    """
    app = Flask(app_name, static_folder='static', template_folder='templates')

    app.iniconfig = FlaskIni()

    with app.app_context():

        app.iniconfig.read(config)
        app.secret_key = app.iniconfig.get('flask', 'secret_key')

        if blueprints is None:
            blueprints = BLUEPRINTS

        for blueprint in blueprints:
            app.register_blueprint(blueprint)

    return app


def create_celery(app):
    """Create the celery object

    Parameters
    ----------
    app : Flask
        AskOmics Flask application

    Returns
    -------
    Celery
        Celery object
    """
    celery = Celery(app.import_name, broker=app.iniconfig.get("celery", "broker_url"))
    # celery.conf.update(app.config)
    task_base = celery.Task

    class ContextTask(task_base):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return task_base.__call__(self, *args, **kwargs)
    celery.Task = ContextTask

    app.celery = celery
    return celery
