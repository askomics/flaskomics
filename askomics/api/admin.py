"""Admin routes"""
import sys
import traceback

from askomics.api.auth import admin_required
from askomics.libaskomics.LocalAuth import LocalAuth
from askomics.libaskomics.Mailer import Mailer

from flask import (Blueprint, current_app, jsonify, request, session)

admin_bp = Blueprint('admin', __name__, url_prefix='/')


@admin_bp.route('/api/admin/getusers', methods=['GET'])
@admin_required
def get_users():
    """Get all users

    Returns
    -------
    json
        users: list of all users info
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    try:
        local_auth = LocalAuth(current_app, session)
        all_users = local_auth.get_all_users()
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return jsonify({
            'users': [],
            'error': True,
            'errorMessage': str(e)
        }), 500

    return jsonify({
        'users': all_users,
        'error': False,
        'errorMessage': ''
    })


@admin_bp.route('/api/admin/setadmin', methods=['POST'])
@admin_required
def set_admin():
    """change admin status of a user

    Returns
    -------
    json
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    data = request.get_json()

    try:
        local_auth = LocalAuth(current_app, session)
        local_auth.set_admin(data['newAdmin'], data['username'])
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return jsonify({
            'error': True,
            'errorMessage': str(e)
        }), 500

    return jsonify({
        'error': False,
        'errorMessage': ''
    })


@admin_bp.route('/api/admin/setquota', methods=["POST"])
@admin_required
def set_quota():
    """Change quota of a user

    Returns
    -------
    json
        users: updated users
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    data = request.get_json()

    try:
        local_auth = LocalAuth(current_app, session)
        local_auth.set_quota(data['quota'], data['username'])
        all_users = local_auth.get_all_users()
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return jsonify({
            'users': [],
            'error': True,
            'errorMessage': str(e)
        }), 500

    return jsonify({
        'users': all_users,
        'error': False,
        'errorMessage': ''
    })


@admin_bp.route('/api/admin/setblocked', methods=['POST'])
@admin_required
def set_blocked():
    """Change blocked status of a user

    Returns
    -------
    json
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    data = request.get_json()

    try:
        local_auth = LocalAuth(current_app, session)
        local_auth.set_blocked(data['newBlocked'], data['username'])
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return jsonify({
            'error': True,
            'errorMessage': str(e)
        }), 500

    return jsonify({
        'error': False,
        'errorMessage': ''
    })


@admin_bp.route("/api/admin/adduser", methods=["POST"])
@admin_required
def add_user():
    """Change blocked status of a user

    Returns
    -------
    json
        instanceUrl: The instance URL
        user: the new created user
        displayPassword: Display password on the interface ?
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    data = request.get_json()

    user = {}
    display_password = True

    try:
        local_auth = LocalAuth(current_app, session)
        local_auth.check_inputs(data, admin_add=True)

        if not local_auth.get_error():
            # Create a user
            user = local_auth.persist_user_admin(data)
            local_auth.create_user_directories(user['id'], user['username'])
            # Send a email to this user (if askomics can send emails)

            mailer = Mailer(current_app, session)
            if mailer.check_mailer():
                display_password = False
                current_app.celery.send_task('send_mail_new_user', ({'user': session['user']}, user))
                # Don't send password user to frontend
                user.pop("password")

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return jsonify({
            'instanceUrl': "",
            'user': user,
            'displayPassword': False,
            'error': True,
            'errorMessage': str(e)
        }), 500

    return jsonify({
        'instanceUrl': current_app.iniconfig.get("askomics", "instance_url"),
        'user': user,
        'displayPassword': display_password,
        'error': local_auth.get_error(),
        'errorMessage': local_auth.get_error_message()
    })


@admin_bp.route("/api/admin/delete_users", methods=["POST"])
@admin_required
def delete_users():
    """Delete users data

    Returns
    -------
    json
        users: remaining users
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    data = request.get_json()

    try:
        usernames = data["usersToDelete"]
        users = []

        # Remove current user from the list
        if session["user"]["username"] in usernames:
            usernames.remove(session["user"]["username"])

        # Remove users from database
        local_auth = LocalAuth(current_app, session)
        for username in usernames:
            # Get user info
            users.append(local_auth.get_user(username))
            local_auth.delete_user_database(username)

        # Celery task to delete users' data from filesystem and rdf triplestore
        session_dict = {'user': session['user']}
        current_app.celery.send_task('delete_users_data', (session_dict, users, True))

        # Get remaining users
        users = local_auth.get_all_users()

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return jsonify({
            'users': [],
            'error': True,
            'errorMessage': str(e)
        }), 500

    return jsonify({
        'users': users,
        'error': local_auth.get_error(),
        'errorMessage': local_auth.get_error_message()
    })
