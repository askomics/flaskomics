import os

from celery import Celery
from flask import Flask
from flask_ini import FlaskIni

from askomics.api.start import start_bp
from askomics.api.view import view_bp
from askomics.api.auth import auth_bp
from askomics.api.admin import admin_bp
from askomics.api.file import file_bp
from askomics.api.datasets import datasets_bp
from askomics.api.catch_url import catch_url_bp


__all__ = ('create_app', 'create_celery')

BLUEPRINTS = (
    start_bp,
    view_bp,
    auth_bp,
    admin_bp,
    file_bp,
    datasets_bp,
    catch_url_bp
)


def create_app(config='config/askomics.ini', app_name='askomics', blueprints=None):

    app = Flask(app_name,
        static_folder='static',
        template_folder='templates'
    )

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
    celery = Celery(app.import_name, broker=app.iniconfig.get("celery", "broker_url"))
    # celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask

    app.celery = celery
    return celery