"""Api routes
"""
from flask import jsonify, session
from functools import wraps
from askomics import app
from askomics.libaskomics.Start import Start

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        """Login required decorator
        """
        if 'username' not in session:
            return jsonify({"error": True, "errorMessage": "Login required"})
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/hello', methods=['GET'])
def hello():
    """Dummy routes

    Returns
    -------
    json
        A welcome message
    """
    if 'username' in session:
        data = {'message': 'Hello {}, welcome to FlaskOmics!'.format(session['username'])}
    else:
        data = {'message': 'Welcome to FlaskOmics!'}

    return jsonify(data)

@app.route('/api/start', methods=['GET'])
def start():
    """Starting route

    Returns
    -------
    json Information about a eventualy logged user, and the AskOmics version
        and a footer message
    """
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
