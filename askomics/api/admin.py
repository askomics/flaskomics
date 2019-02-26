"""Admin routes
"""
from flask import (Blueprint, current_app, jsonify, request, session)
from askomics.api.auth import login_required, admin_required
from askomics.libaskomics.LocalAuth import LocalAuth

admin_bp = Blueprint('admin', __name__, url_prefix='/')

@admin_bp.route('/api/admin/getusers', methods=['GET'])
@admin_required
def get_users():
    """Get all users

    Returns
    -------
    json
        all users infos
    """
    local_auth = LocalAuth(current_app, session)
    all_users = local_auth.get_all_users()

    return jsonify({'users': all_users})

    
@admin_bp.route('/api/admin/setadmin', methods=['POST'])
@admin_required
def set_admin():
    """change admin status of a user

    Returns
    -------
    json
        Description
    """
    data = request.get_json()

    local_auth = LocalAuth(current_app, session)
    local_auth.set_admin(data['newAdmin'], data['username'])

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
        Description
    """
    data = request.get_json()

    local_auth = LocalAuth(current_app, session)
    local_auth.set_blocked(data['newBlocked'], data['username'])

    return jsonify({
        'error': False,
        'errorMessage': ''
    })