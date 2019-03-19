"""Admin routes
"""
from askomics.api.auth import admin_required
from askomics.libaskomics.LocalAuth import LocalAuth

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
        current_app.logger.error(str(e))
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

    return jsonify({'users': all_users})


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
        current_app.logger.error(str(e))
        return jsonify({
            'error': True,
            'errorMessage': str(e)
        }), 500

    return jsonify({
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
        current_app.logger.error(str(e))
        return jsonify({
            'error': True,
            'errorMessage': str(e)
        }), 500

    return jsonify({
        'error': False,
        'errorMessage': ''
    })
