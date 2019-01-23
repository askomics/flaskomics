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

@app.route('/api/hello', methods=['GET'])
def hello():

    if 'username' in session:
        data = {'message': 'Hello {}, welcome to FlaskOmics!'.format(session['username'])}
    else:
        data = {'message': 'Welcome to FlaskOmics!'}

    return jsonify(data)

@app.route('/api/start', methods=['GET'])
def start():

    json = {
        "username": None,
        "logged": False,
        "version": app.iniconfig.get('askomics', 'version'),
        "footer_message": app.iniconfig.get('askomics', 'footer_message')
    }

    if 'username' in session:
        json['username'] = session['username']
        json['logged'] = True

    return jsonify(json)

@app.route('/api/login', methods=['POST'])
def login():

    data = request.get_json()

    if data['login'] == 'imx' and data['password'] == 'imx' :
        session['username'] = 'Xavier Garnier'
        app.logger.debug(session['username'])
        return jsonify({'username': session["username"]})

@app.route('/api/logout', methods=['GET'])
def logout():

    session.pop('username', None)
    return jsonify({'username': '', 'logged': False})


@app.route('/<path:path>')
def catch_all(path):
    return redirect(url_for('home'))