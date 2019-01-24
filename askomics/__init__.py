"""Define a Flask app
"""
from flask import Flask
from flask_ini import FlaskIni

app = Flask(__name__)
app.iniconfig = FlaskIni()
with app.app_context():
    app.iniconfig.read('config/askomics.ini')

app.secret_key = app.iniconfig.get('flask', 'secret_key')

import askomics.routes.views.view
import askomics.routes.api.api
import askomics.routes.api.authentication
import askomics.routes.views.catch_url