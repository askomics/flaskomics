"""Authentication routes
"""
from flask import jsonify, request, session
from askomics import app, login_required
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
        'errorMessage': messages,
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
        'errorMessage': authentication['error_messages'],
        'user': authentication['user']
        })

@app.route('/api/update_profile', methods=['POST'])
@login_required
def update_profile():

    data = request.get_json()

    local_auth = LocalAuth(app, session)
    updated_user = local_auth.update_profile(data, session['user'])

    session['user'] = updated_user['user']

    return jsonify({
        'error': updated_user['error'],
        'errorMessage': updated_user['error_message'],
        'user': updated_user['user']
        })

@app.route('/api/update_password', methods=['POST'])
@login_required
def update_password():

    data = request.get_json()

    local_auth = LocalAuth(app, session)
    updated_user = local_auth.update_password(data, session['user'])


    return jsonify({
        'error': updated_user['error'],
        'errorMessage': updated_user['error_message'],
        'user': updated_user['user']
        })

@app.route('/api/update_apikey', methods=['GET'])
@login_required
def update_apikey():

    local_auth = LocalAuth(app, session)
    updated_user = local_auth.update_apikey(session['user'])

    session['user'] = updated_user['user']

    return jsonify({
        'error': updated_user['error'],
        'errorMessage': updated_user['error_message'],
        'user': updated_user['user']
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


    app.logger.debug(session)
    return jsonify({'user': {}, 'logged': False})
