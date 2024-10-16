"""AskOmics app

Attributes
----------
BLUEPRINTS : Tuple
    Flask blueprints
"""

import configparser
import os

from askomics.api.admin import admin_bp
from askomics.api.auth import auth_bp
from askomics.api.data import data_bp
from askomics.api.datasets import datasets_bp
from askomics.api.file import file_bp
from askomics.api.sparql import sparql_bp
from askomics.api.start import start_bp
from askomics.api.query import query_bp
from askomics.api.view import view_bp
from askomics.api.results import results_bp
from askomics.api.galaxy import galaxy_bp
from askomics.api.ontology import onto_bp
from askomics.middleware import PrefixMiddleware

from celery import Celery
from kombu import Exchange, Queue

from flask import Flask

from pkg_resources import get_distribution

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.celery import CeleryIntegration

import logging

__all__ = ('create_app', 'create_celery')

BLUEPRINTS = (
    sparql_bp,
    start_bp,
    view_bp,
    auth_bp,
    admin_bp,
    file_bp,
    data_bp,
    datasets_bp,
    query_bp,
    results_bp,
    galaxy_bp,
    onto_bp
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
    conf = configparser.ConfigParser()
    conf.read(config)

    sentry_dsn = None
    try:
        sentry_dsn = conf['sentry']['server_dsn']
    except Exception:
        pass

    if sentry_dsn:
        version = get_distribution('askomics').version
        name = get_distribution('askomics').project_name
        sentry_sdk.init(
            dsn=sentry_dsn,
            release="{}@{}".format(name, version),
            integrations=[FlaskIntegration(), CeleryIntegration()]
        )

    app = Flask(app_name, static_folder='static', template_folder='templates')

    app.iniconfig = conf
    app.secret_key = app.iniconfig.get("flask", "secret_key")

    with app.app_context():

        proxy_path = None
        try:
            proxy_path = app.iniconfig.get('askomics', 'reverse_proxy_path')
            app.config['REVERSE_PROXY_PATH'] = proxy_path
        except Exception:
            pass

        if blueprints is None:
            blueprints = BLUEPRINTS

        for blueprint in blueprints:
            app.register_blueprint(blueprint)

        is_gunicorn = "gunicorn" in os.environ.get("SERVER_SOFTWARE", "")
        app.config['DEBUG'] = app.iniconfig.getboolean('askomics', 'debug')

        if is_gunicorn:
            log_level = 10 if app.config['DEBUG'] else 20
            gunicorn_logger = logging.getLogger('gunicorn.error')
            app.logger.handlers = gunicorn_logger.handlers
            app.logger.setLevel(log_level)

    if proxy_path:
        app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix=proxy_path.rstrip("/"))

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
    celery = Celery(app.import_name, backend=app.iniconfig.get("celery", "result_backend"), broker=app.iniconfig.get("celery", "broker_url"))
    # celery.conf.update(app.config)
    task_base = celery.Task

    default_exchange = Exchange('default', type='direct')

    celery.conf.task_queues = (
        Queue('default', default_exchange, routing_key='default'),
    )
    celery.conf.task_default_queue = 'default'

    class ContextTask(task_base):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return task_base.__call__(self, *args, **kwargs)
    celery.Task = ContextTask

    app.celery = celery
    return celery
