"""Authentication routes"""

import traceback
import sys

from functools import wraps

from askomics.libaskomics.LocalAuth import LocalAuth
from askomics.libaskomics.Utils import Utils

from flask import (Blueprint, current_app, jsonify, request, session, render_template)

auth_bp = Blueprint('auth', __name__, url_prefix='/')


def login_required(f):
    """Login required function"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        """Login required decorator"""
        if 'user' in session:
            if not session['user']['blocked']:
                return f(*args, **kwargs)
            return jsonify({"error": True, "errorMessage": "Blocked account"}), 401
        return jsonify({"error": True, "errorMessage": "Login required"}), 401

    return decorated_function


def login_required_query(f):
    """Login required function"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        """Login required decorator"""
        if 'user' in session:
            if not session['user']['blocked']:
                return f(*args, **kwargs)
            return jsonify({"error": True, "errorMessage": "Blocked account"}), 401
        elif current_app.iniconfig.get('askomics', 'anonymous_query', fallback=False):
            session['user'] = {'id': 0, 'username': "anonymous", "quota": Utils.humansize_to_bytes(current_app.config.get("askomics", "quota"))}
            return f(*args, **kwargs)
        return jsonify({"error": True, "errorMessage": "Login required"}), 401

    return decorated_function


def api_auth(f):
    """Get info from token"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        """Login required decorator"""
        if request.headers.get("X-API-KEY"):
            key = request.headers.get("X-API-KEY")
            local_auth = LocalAuth(current_app, session)
            authentication = local_auth.authenticate_user_with_apikey(key)
            if not authentication["error"]:
                session["user"] = authentication["user"]
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    """Login required function"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        """Login required decorator"""
        if 'user' in session:
            if session['user']['admin']:
                return f(*args, **kwargs)
            return jsonify({"error": True, "errorMessage": "Admin required"}), 401
        return jsonify({"error": True, "errorMessage": "Login required"}), 401

    return decorated_function


def local_required(f):
    """Local required function"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        """Local required decorator"""
        if "user" in session:
            current_app.logger.debug(session["user"])
            if not session["user"]["ldap"]:
                return f(*args, **kwargs)
            return jsonify({"error": True, "errorMessage": "Local user required"}), 401
        return jsonify({"error": True, "errorMessage": "Login required"}), 401

    return decorated_function


@auth_bp.route('/api/auth/signup', methods=['POST'])
def signup():
    """Register a new user

    Returns
    -------
    json
        Info about the user
    """
    if current_app.iniconfig.getboolean("askomics", "disable_account_creation"):
        return jsonify({
            'error': True,
            'errorMessage': "Account creation is disabled",
            'user': {}
        }), 400

    user = {}

    data = request.get_json()
    if not data:
        return jsonify({
            'error': True,
            'errorMessage': "Missing parameters",
            'user': {}
        }), 400

    local_auth = LocalAuth(current_app, session)
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


@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    """Log a user

    Returns
    -------
    json
        Information about the logged user
    """
    data = request.get_json()
    if not (data and data.get("login") and data.get("password")):
        return jsonify({
            'error': True,
            'errorMessage': "Missing login or password",
            'user': None
        }), 400

    local_auth = LocalAuth(current_app, session)
    authentication = local_auth.authenticate_user(data["login"], data["password"])

    user = {}
    if not authentication['error']:
        session['user'] = authentication['user']
        user = authentication['user']

    return jsonify({
        'error': authentication['error'],
        'errorMessage': authentication['error_messages'],
        'user': user
    })


@auth_bp.route('/loginapikey/<path:key>', methods=["GET"])
def login_api_key(key):
    """Log user with his API key

    Parameters
    ----------
    key : string
        User API key

    Returns
    -------
    json
        Information about the logged user
    """
    local_auth = LocalAuth(current_app, session)
    authentication = local_auth.authenticate_user_with_apikey(key)

    if not authentication["error"]:
        session["user"] = authentication["user"]

        proxy_path = "/"
        try:
            proxy_path = current_app.iniconfig.get('askomics', 'reverse_proxy_path')
        except Exception:
            pass

        title = "AskOmics"
        try:
            subtitle = current_app.iniconfig.get('askomics', 'subtitle')
            title = "AskOmics | {}".format(subtitle)
        except Exception:
            pass

        return render_template('index.html', title=title, proxy_path=proxy_path, redirect="/")

    else:

        return jsonify({
            'error': authentication['error'],
            'errorMessage': authentication['error_messages'],
            'user': authentication['user']
        })


@auth_bp.route('/api/auth/profile', methods=['POST'])
@local_required
def update_profile():
    """Update user profile (names and email)

    Returns
    -------
    json
        The updated user
    """
    data = request.get_json()
    if not (data and any([key in data for key in ["newFname", "newLname", "newEmail"]])):
        return jsonify({
            "error": True,
            "errorMessage": "Missing parameters"
        }), 400

    local_auth = LocalAuth(current_app, session)
    updated_user = local_auth.update_profile(data, session['user'])

    session['user'] = updated_user['user']

    return jsonify({
        'error': updated_user['error'],
        'errorMessage': updated_user['error_message'],
        'user': updated_user['user']
    })


@auth_bp.route('/api/auth/password', methods=['POST'])
@local_required
def update_password():
    """Update the user passord

    Returns
    -------
    json
        The user
    """
    data = request.get_json()
    if not (data and all([key in data for key in ["oldPassword", "newPassword", "confPassword"]])):
        return jsonify({
            "error": True,
            "errorMessage": "Missing parameters"
        }), 400

    local_auth = LocalAuth(current_app, session)
    updated_user = local_auth.update_password(data, session['user'])

    return jsonify({
        'error': updated_user['error'],
        'errorMessage': updated_user['error_message'],
        'user': updated_user['user']
    })


@auth_bp.route('/api/auth/apikey', methods=['GET'])
@login_required
def update_apikey():
    """Update the user apikey

    Returns
    -------
    json
        The user with his new apikey
    """
    local_auth = LocalAuth(current_app, session)
    updated_user = local_auth.update_apikey(session['user'])

    session['user'] = updated_user['user']

    return jsonify({
        'error': updated_user['error'],
        'errorMessage': updated_user['error_message'],
        'user': updated_user['user']
    })


@auth_bp.route('/api/auth/galaxy', methods=['POST'])
def update_galaxy():
    """Update the user apikey

    Returns
    -------
    json
        The user with his new apikey
    """
    data = request.get_json()
    if not (data and data.get("gurl") and data.get("gkey")):
        return jsonify({
            'error': True,
            'errorMessage': "Missing parameters",
            'user': session["user"]
        }), 400

    local_auth = LocalAuth(current_app, session)
    if session["user"]["galaxy"]:
        updated_user = local_auth.update_galaxy_account(session["user"], data["gurl"], data["gkey"])
    else:
        updated_user = local_auth.add_galaxy_account(session["user"], data["gurl"], data["gkey"])

    session["user"] = updated_user["user"]
    current_app.logger.debug(updated_user["user"])

    return jsonify({
        'error': updated_user['error'],
        'errorMessage': updated_user['error_message'],
        'user': updated_user['user']
    })


@auth_bp.route('/api/auth/logout', methods=['GET'])
def logout():
    """Logout the current user

    Returns
    -------
    json
        no username and logged false
    """
    session.pop('user', None)

    current_app.logger.debug(session)
    return jsonify({'user': {}, 'logged': False})


@auth_bp.route("/api/auth/reset_password", methods=["POST"])
def reset_password():
    """Reset password route"""
    data = request.get_json()
    if not data:
        return jsonify({
            "error": True,
            "errorMessage": "Missing parameters"
        }), 400

    # Send a reset link
    if "login" in data:
        try:
            local_auth = LocalAuth(current_app, session)
            local_auth.send_reset_link(data["login"])
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            return jsonify({
                "error": True,
                "errorMessage": str(e)
            }), 500

        return jsonify({
            "error": False,
            "errorMessage": ""
        })

    # check if token is valid
    elif "token" in data and "password" not in data:
        try:
            local_auth = LocalAuth(current_app, session)
            result = local_auth.check_token(data["token"])
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            return jsonify({
                "token": None,
                "username": None,
                "fname": None,
                "lname": None,
                "error": True,
                "errorMessage": str(e)
            }), 500

        return jsonify({
            "token": data["token"],
            "username": result["username"],
            "fname": result["fname"],
            "lname": result["lname"],
            "error": False if result["username"] else True,
            "errorMessage": result["message"]
        })

    # Update password
    elif all([key in data for key in ["token", "password", "passwordConf"]]):
        try:
            local_auth = LocalAuth(current_app, session)
            result = local_auth.reset_password_with_token(data["token"], data["password"], data["passwordConf"])
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            return jsonify({
                "error": True,
                "errorMessage": str(e)
            }), 500

        return jsonify({
            "error": result["error"],
            "errorMessage": result["message"]
        })
    else:
        return jsonify({
            "error": True,
            "errorMessage": "Missing parameters"
        }), 400


@auth_bp.route("/api/auth/delete_account", methods=["GET"])
@login_required
def delete_account():
    """Remove account"""
    try:
        # Remove user from database
        local_auth = LocalAuth(current_app, session)
        local_auth.delete_user_database(session["user"]["username"])

        # Celery task to delete user's data from filesystem and rdf triplestore
        session_dict = {'user': session['user']}
        current_app.celery.send_task('delete_users_data', (session_dict, [session["user"], ], True))

        # Remove user from session
        session.pop('user', None)

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return jsonify({
            "error": True,
            "errorMessage": str(e)
        }), 500

    return jsonify({
        "error": False,
        "errorMessage": ""
    })


@auth_bp.route("/api/auth/reset_account", methods=["GET"])
@login_required
def reset_account():
    """Reset account"""
    try:
        # Remove user from database
        local_auth = LocalAuth(current_app, session)
        local_auth.delete_user_database(session["user"]["username"], delete_user=False)

        # Celery task to delete user's data from filesystem and rdf triplestore
        session_dict = {'user': session['user']}
        current_app.celery.send_task('delete_users_data', (session_dict, [session["user"], ], False))

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return jsonify({
            "error": True,
            "errorMessage": str(e)
        }), 500

    return jsonify({
        "error": False,
        "errorMessage": ""
    })
