from flask import jsonify, request, redirect, escape, session, url_for
from functools import wraps
from askomics import app
from askomics.libaskomics.Start import Start

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return jsonify({"error": True, "errorMessage": "Login required"})
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/hello', methods=['GET'])
def hello():

    if 'username' in session:
        data = {'message': 'Hello {}, welcome to FlaskOmics!'.format(session['username'])}
    else:
        data = {'message': 'Welcome to FlaskOmics!'}

    return jsonify(data)

@app.route('/api/start', methods=['GET'])
def start():

    starter = Start(app, session)
    starter.start()

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