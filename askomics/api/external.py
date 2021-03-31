"""Render external API routes (with api_key auth)"""
from flask import (Blueprint, render_template, current_app)


external_bp = Blueprint('external', __name__, url_prefix='/api_ext')

@file_bp.route('/api/files', methods=['GET', 'POST'])
@api_auth
@login_required
def get_files():
    """Get files info of the logged user

    Returns
    -------
    json
        files: list of all files of current user
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    files_id = None
    if request.method == 'POST':
        data = request.get_json()
        files_id = data['filesId']

    try:
        files_handler = FilesHandler(current_app, session)
        files = files_handler.get_files_infos(files_id=files_id)
        disk_space = files_handler.get_size_occupied_by_user()
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return jsonify({
            'files': [],
            'diskSpace': 0,
            'error': True,
            'errorMessage': str(e)
        }), 500

    return jsonify({
        'files': files,
        'diskSpace': disk_space,
        'error': False,
        'errorMessage': ''
    })
