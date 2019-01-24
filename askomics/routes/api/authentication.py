"""Authentication routes
"""
from flask import jsonify, request, session
from askomics import app
from askomics.libaskomics.LocalAuth import LocalAuth

@app.route('/api/signup', methods=['POST'])
def signup():
    """Register a new user

    Returns
    -------
    json
        Info about the user
    """
    data = request.get_json()

    local_auth = LocalAuth(app, session)
    error, messages = local_auth.check_inputs(data)

    user = {}
    if not error:
        user = local_auth.persist_user(data)
        session['user'] = user

    return jsonify({
        'error': error,
        'errorMessage': '\n'.join(messages),
        'user': user
        })

@app.route('/api/login', methods=['POST'])
def login():
    """Log a user

    Returns
    -------
    json
        Information about the logged user
    """
    data = request.get_json()

    local_auth = LocalAuth(app, session)
    authentication = local_auth.authenticate_user(data)

    if not authentication['error']:
        session['user'] = authentication['user']

    return jsonify({
        'error': authentication['error'],
        'errorMessage': '\n'.join(authentication['error_messages']),
        'user': authentication['user']
        })



@app.route('/api/logout', methods=['GET'])
def logout():
    """Logout the current user

    Returns
    -------
    json
        no username and logged false
    """
    session.pop('user', None)
    return jsonify({'user': {}, 'logged': False})