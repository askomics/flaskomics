"""Api routes"""
import sys
import traceback

from askomics.api.auth import login_required
from askomics.libaskomics.FilesHandler import FilesHandler
from askomics.libaskomics.FilesUtils import FilesUtils
from askomics.libaskomics.Dataset import Dataset

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
    files_utils = FilesUtils(current_app, session)
    disk_space = files_utils.get_size_occupied_by_user() if "user" in session else None

    if session["user"]["quota"] > 0 and disk_space >= session["user"]["quota"]:
        return jsonify({
            'errorMessage': "Exceeded quota",
            "path": '',
            "error": True
        }), 500

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
    files_utils = FilesUtils(current_app, session)
    disk_space = files_utils.get_size_occupied_by_user() if "user" in session else None

    if session["user"]["quota"] > 0 and disk_space >= session["user"]["quota"]:
        return jsonify({
            'errorMessage': "Exceeded quota",
            "error": True
        }), 500

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
    task = None

    try:

        files_handler = FilesHandler(current_app, session, host_url=request.host_url)
        files_handler.handle_files([data["fileId"], ])

        for file in files_handler.files:

            dataset_info = {
                "celery_id": None,
                "file_id": file.id,
                "name": file.name,
                "graph_name": file.file_graph,
                "public": data["public"] if session["user"]["admin"] else False
            }

            dataset = Dataset(current_app, session, dataset_info)
            dataset.save_in_db()
            data["dataset_id"] = dataset.id

            task = current_app.celery.send_task('integrate', (session_dict, data, request.host_url))

            dataset.update_celery(task.id)

    except Exception as e:
        return jsonify({
            'error': True,
            'errorMessage': str(e),
            'task_id': ''
        }), 500

    return jsonify({
        'error': False,
        'errorMessage': '',
        'task_id': task.id if task else ''
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
