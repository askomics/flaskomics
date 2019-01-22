from flask import Flask
from flask import render_template
from flask import jsonify
from flask import request
from flask import redirect
from flask import escape
from flask import session
from flask import url_for
from flask_ini import FlaskIni

app = Flask(__name__)
app.iniconfig = FlaskIni()
with app.app_context():
    app.iniconfig.read('config/askomics.ini')

app.secret_key = app.iniconfig.get('flask', 'secret_key')

@app.route('/')
def home():
    return render_template('index.html', project="AskOmics")

@app.route('/api/hello', methods=['GET', 'POST'])
def hello():

    if request.method == 'POST':
        json = request.get_json()
        data = {'message': 'Hello {}!'.format(json['name'])}
    else:
        data = {'message': 'Welcome to FlaskOmics!'}

    return jsonify(data)

@app.route('/api/user', methods=['GET'])
def user():

    json = {
        "username": None,
        "logged": False
    }

    if 'username' in session:
        json = {
            "username": session['username'],
            "logged": True
        }

    return jsonify(json)
