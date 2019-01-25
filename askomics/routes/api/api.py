"""Api routes
"""
from flask import jsonify, session
from askomics import app, login_required
from askomics.libaskomics.Start import Start

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
        "user": None,
        "logged": False,
        "version": app.iniconfig.get('askomics', 'version'),
        "footer_message": app.iniconfig.get('askomics', 'footer_message')
    }

    if 'user' in session:
        json['user'] = session['user']
        json['logged'] = True

    return jsonify(json)
