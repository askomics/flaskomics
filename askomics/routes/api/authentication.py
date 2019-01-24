"""Authentication routes
"""
from flask import jsonify, request, session
from askomics import app

@app.route('/api/login', methods=['POST'])
def login():
    """Log a user

    Returns
    -------
    json
        Information about the logged user
    """
    data = request.get_json()

    if data['login'] == 'imx' and data['password'] == 'imx' :
        session['username'] = 'Xavier Garnier'
        app.logger.debug(session['username'])
        return jsonify({'username': session["username"]})

@app.route('/api/logout', methods=['GET'])
def logout():
    """Logout the current user

    Returns
    -------
    json
        no username and logged false
    """
    session.pop('username', None)
    return jsonify({'username': '', 'logged': False})