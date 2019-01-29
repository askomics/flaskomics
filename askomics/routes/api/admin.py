"""Admin routes
"""
from flask import jsonify, request, session
from askomics import app, login_required, admin_required
from askomics.libaskomics.LocalAuth import LocalAuth

@app.route('/api/admin/getusers', methods=['GET'])
@admin_required
def get_users():
    """Get all users

    Returns
    -------
    json
        all users infos
    """
    local_auth = LocalAuth(app, session)
    all_users = local_auth.get_all_users()

    return jsonify({'users': all_users})

    
@app.route('/api/admin/setadmin', methods=['POST'])
@admin_required
def set_admin():
    """change admin status of a user

    Returns
    -------
    json
        Description
    """
    data = request.get_json()

    local_auth = LocalAuth(app, session)
    local_auth.set_admin(data['newAdmin'], data['username'])

    return jsonify({
        'error': False,
        'errorMessage': ''
    })

@app.route('/api/admin/setblocked', methods=['POST'])
@admin_required
def set_blocked():
    """Change blocked status of a user

    Returns
    -------
    json
        Description
    """
    data = request.get_json()

    local_auth = LocalAuth(app, session)
    local_auth.set_blocked(data['newBlocked'], data['username'])

    return jsonify({
        'error': False,
        'errorMessage': ''
    })