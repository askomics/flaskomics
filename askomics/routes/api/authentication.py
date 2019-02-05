"""Authentication routes
"""
from flask import jsonify, request, session
from askomics import app, login_required, admin_required
from askomics.libaskomics.LocalAuth import LocalAuth

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """Register a new user

    Returns
    -------
    json
        Info about the user
    """

    user = {}

    data = request.get_json()

    local_auth = LocalAuth(app, session)
    local_auth.check_inputs(data)

    if not local_auth.get_error():
        user = local_auth.persist_user(data)
        local_auth.create_user_directories(user['id'], user['username'])
        session['user'] = user

    return jsonify({
        'error': local_auth.get_error(),
        'errorMessage': local_auth.get_error_message(),
        'user': user
    })

@app.route('/api/auth/login', methods=['POST'])
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

@app.route('/api/auth/profile', methods=['POST'])
@login_required
def update_profile():
    """Update user profile (names and email)

    Returns
    -------
    json
        The updated user
    """
    data = request.get_json()

    local_auth = LocalAuth(app, session)
    updated_user = local_auth.update_profile(data, session['user'])

    session['user'] = updated_user['user']

    return jsonify({
        'error': updated_user['error'],
        'errorMessage': updated_user['error_message'],
        'user': updated_user['user']
        })

@app.route('/api/auth/password', methods=['POST'])
@login_required
def update_password():
    """Update the user passord

    Returns
    -------
    json
        The user
    """
    data = request.get_json()

    local_auth = LocalAuth(app, session)
    updated_user = local_auth.update_password(data, session['user'])


    return jsonify({
        'error': updated_user['error'],
        'errorMessage': updated_user['error_message'],
        'user': updated_user['user']
        })

@app.route('/api/auth/apikey', methods=['GET'])
@login_required
def update_apikey():
    """Update the user apikey

    Returns
    -------
    json
        The user with his new apikey
    """
    local_auth = LocalAuth(app, session)
    updated_user = local_auth.update_apikey(session['user'])

    session['user'] = updated_user['user']

    return jsonify({
        'error': updated_user['error'],
        'errorMessage': updated_user['error_message'],
        'user': updated_user['user']
        })


@app.route('/api/auth/logout', methods=['GET'])
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
