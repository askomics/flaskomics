"""Api routes"""
import sys
import traceback

from askomics.api.auth import login_required
from askomics.libaskomics.FilesHandler import FilesHandler

from flask import (Blueprint, current_app, jsonify, request, send_from_directory, session)

file_bp = Blueprint('file', __name__, url_prefix='/')


@file_bp.route('/api/files', methods=['GET', 'POST'])
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
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return jsonify({
            'files': [],
            'error': True,
            'errorMessage': str(e)
        }), 500

    return jsonify({
        'files': files,
        'error': False,
        'errorMessage': ''
    })


@file_bp.route('/api/files/upload_chunk', methods=['POST'])
@login_required
def upload_chunk():
    """Upload a file chunk

    Returns
    -------
    json
        path: name of the local file. To append the next chunk into it
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    data = request.get_json()

    try:
        files = FilesHandler(current_app, session)
        path = files.persist_chunk(data)
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return jsonify({
            "path": '',
            "error": True,
            "errorMessage": str(e)
        }), 500
    return jsonify({
        "path": path,
        "error": False,
        "errorMessage": ""
    })


@file_bp.route('/api/files/upload_url', methods=["POST"])
def upload_url():
    """Upload a distant file with an URL

    Returns
    -------
    json
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    data = request.get_json()

    try:
        files = FilesHandler(current_app, session)
        files.download_url(data["url"])
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


@file_bp.route('/api/files/upload', methods=['POST'])
@login_required
def upload():
    """Upload files

    Returns
    -------
    json
        uploadedFiles: list of all files of current user
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    inputs = request.files

    try:
        files = FilesHandler(current_app, session)
        uploaded_files = files.persist_files(inputs)
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return jsonify({
            'uploadedFiles': [],
            'error': True,
            'errorMessage': str(e)
        }), 500

    return jsonify({
        'uploadedFiles': uploaded_files,
        'error': False,
        'errorMessage': ''
    })


@file_bp.route('/api/files/preview', methods=['POST'])
@login_required
def get_preview():
    """Get files preview

    Returns
    -------
    json
        previewFiles: preview of selected files
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    data = request.get_json()

    try:
        files_handler = FilesHandler(current_app, session)
        files_handler.handle_files(data['filesId'])

        results = []
        for file in files_handler.files:
            file.set_preview()
            res = file.get_preview()
            results.append(res)
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        raise e
        return jsonify({
            'previewFiles': [],
            'error': True,
            'errorMessage': str(e)
        }), 500

    return jsonify({
        'previewFiles': results,
        'error': False,
        'errorMessage': ''
    })


@file_bp.route('/api/files/delete', methods=['POST'])
@login_required
def delete_files():
    """Delete files

    Returns
    -------
    json
        files: list of all files of current user
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    data = request.get_json()

    try:
        files = FilesHandler(current_app, session)
        remaining_files = files.delete_files(data['filesIdToDelete'])
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return jsonify({
            'files': [],
            'error': True,
            'errorMessage': str(e)
        }), 500

    return jsonify({
        'files': remaining_files,
        'error': False,
        'errorMessage': ''
    })


@file_bp.route('/api/files/integrate', methods=['POST'])
@login_required
def integrate():
    """Integrate a file

    Returns
    -------
    json
        task_id: celery task id
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    data = request.get_json()

    session_dict = {'user': session['user']}

    try:
        task = current_app.celery.send_task('integrate', (session_dict, data, request.host_url))
        # task = async_integrate.delay(data, request.host_url)
        current_app.logger.debug(task)
    except Exception as e:
        return jsonify({
            'error': True,
            'errorMessage': str(e),
            'task_id': None
        }), 500

    return jsonify({
        'error': False,
        'errorMessage': '',
        'task_id': task.id
    })


@file_bp.route('/api/files/ttl/<path:user_id>/<path:username>/<path:path>', methods=['GET'])
def serve_file(path, user_id, username):
    """Serve a static ttl file of a user

    Parameters
    ----------
    path : string
        The file path to serve
    user_id : int
        user id
    username : string
        username

    Returns
    -------
    file
        the file
    """
    dir_path = "{}/{}_{}/ttl".format(
        current_app.iniconfig.get('askomics', 'data_directory'),
        user_id,
        username
    )

    return(send_from_directory(dir_path, path))
