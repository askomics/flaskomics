"""Api routes
"""
from flask import jsonify, session
from askomics import app, login_required
from askomics.libaskomics.Start import Start
from askomics.libaskomics.LocalAuth import LocalAuth

@app.route('/api/hello', methods=['GET'])
def hello():
    """Dummy routes

    Returns
    -------
    json
        A welcome message
    """
    if 'user' in session:
        data = {
            'message':
            'Hello {} {}, welcome to FlaskOmics!'.format(session['user']['fname'],
                                                         session['user']['lname'])
        }
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
        "user": None,
        "logged": False,
        "version": app.iniconfig.get('askomics', 'version'),
        "footer_message": app.iniconfig.get('askomics', 'footer_message')
    }

    if 'user' in session:
        local_auth = LocalAuth(app, session)
        user = local_auth.get_user(session['user']['username'])
        session['user'] = user
        json['user'] = user
        json['logged'] = True

    return jsonify(json)
