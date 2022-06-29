"""Api routes"""
import requests
import sys
import traceback
import urllib

from askomics.api.auth import login_required, api_auth
from askomics.libaskomics.FilesHandler import FilesHandler
from askomics.libaskomics.FilesUtils import FilesUtils
from askomics.libaskomics.Dataset import Dataset
from askomics.libaskomics.RdfFile import RdfFile

from flask import (Blueprint, current_app, jsonify, request, send_from_directory, session)

file_bp = Blueprint('file', __name__, url_prefix='/')


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
        if data:
            files_id = data.get('filesId')

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


@file_bp.route('/api/files/editname', methods=['POST'])
@api_auth
@login_required
def edit_file():
    """Edit file name

    Returns
    -------
    json
        files: list of all files of current user
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    data = request.get_json()
    current_app.logger.debug(data)
    if not (data and data.get("id") and data.get("newName")):
        return jsonify({
            'files': [],
            'diskSpace': 0,
            'error': True,
            'errorMessage': "Missing parameters"
        }), 400

    files_id = [data["id"]]
    new_name = data["newName"]

    try:
        files_handler = FilesHandler(current_app, session)
        files_handler.handle_files(files_id)

        for file in files_handler.files:
            file.edit_name_in_db(new_name)
        files = files_handler.get_files_infos()

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
        'diskSpace': files_handler.get_size_occupied_by_user(),
        'error': False,
        'errorMessage': ''
    })


@file_bp.route('/api/files/upload_chunk', methods=['POST'])
@api_auth
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
        }), 400

    data = request.get_json()
    if not (data and all([key in data for key in ["first", "last", "size", "name", "type", "size", "chunk"]])):
        return jsonify({
            "path": '',
            "error": True,
            "errorMessage": "Missing parameters"
        }), 400

    if not (data["first"] or data.get("path")):
        return jsonify({
            "path": '',
            "error": True,
            "errorMessage": "Missing path parameter"
        }), 400

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
@api_auth
@login_required
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
        }), 400

    data = request.get_json()
    if not (data and data.get("url")):
        return jsonify({
            "error": True,
            "errorMessage": "Missing url parameter"
        }), 400

    try:
        if session["user"]["quota"] > 0:
            with requests.get(data["url"], stream=True) as r:
                # Check header for total size, and check quota.
                if r.headers.get('Content-length'):
                    total_size = int(r.headers.get('Content-length')) + disk_space
                    if total_size >= session["user"]["quota"]:
                        return jsonify({
                            'errorMessage': "File will exceed quota",
                            "error": True
                        }), 400

        session_dict = {'user': session['user']}
        current_app.celery.send_task('download_file', (session_dict, data["url"]))
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
@api_auth
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
    if not (data and data.get('filesId')):
        return jsonify({
            'previewFiles': [],
            'error': True,
            'errorMessage': "Missing filesId parameter"
        }), 400

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
@api_auth
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
    if not (data and data.get('filesIdToDelete')):
        return jsonify({
            'files': [],
            'error': True,
            'errorMessage': "Missing filesIdToDelete parameter"
        }), 400

    try:
        files = FilesHandler(current_app, session)
        remaining_files = files.delete_files(data.get('filesIdToDelete', []))
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
@api_auth
@login_required
def integrate():
    """Integrate a file

    Returns
    -------
    json
        datasets_id: dataset ids
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    data = request.get_json()
    if not (data and data.get("fileId")):
        return jsonify({
            'error': True,
            'errorMessage': "Missing fileId parameter",
            'dataset_ids': None
        }), 400

    session_dict = {'user': session['user']}
    task = None
    dataset_ids = []

    try:

        files_handler = FilesHandler(current_app, session, host_url=request.host_url)
        files_handler.handle_files([data["fileId"], ])

        for file in files_handler.files:

            data["externalEndpoint"] = data["externalEndpoint"] if (data.get("externalEndpoint") and isinstance(file, RdfFile)) else None
            data["externalGraph"] = data["externalGraph"] if (data.get("externalGraph") and isinstance(file, RdfFile)) else None
            data["customUri"] = data["customUri"] if (data.get("customUri") and not isinstance(file, RdfFile)) else None

            dataset_info = {
                "celery_id": None,
                "file_id": file.id,
                "name": file.human_name,
                "graph_name": file.file_graph,
                "public": (data.get("public", False) if session["user"]["admin"] else False) or current_app.iniconfig.getboolean("askomics", "single_tenant", fallback=False)
            }

            endpoint = data["externalEndpoint"] or current_app.iniconfig.get('triplestore', 'endpoint')

            dataset = Dataset(current_app, session, dataset_info)
            dataset.save_in_db(endpoint, data["externalGraph"])
            data["dataset_id"] = dataset.id
            dataset_ids.append(dataset.id)
            task = current_app.celery.send_task('integrate', (session_dict, data, request.host_url))

            dataset.update_celery(task.id)

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return jsonify({
            'error': True,
            'errorMessage': str(e),
            'dataset_ids': None
        }), 500

    return jsonify({
        'error': False,
        'errorMessage': '',
        'dataset_ids': dataset_ids
    })


@file_bp.route('/api/files/ttl/<path:user_id>/<path:username>/<path:path>', methods=['GET'])
@api_auth
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
    # Re-encode the path because we stored the encoded file name
    path = urllib.parse.quote(path)

    dir_path = "{}/{}_{}/ttl".format(
        current_app.iniconfig.get('askomics', 'data_directory'),
        user_id,
        username
    )

    return(send_from_directory(dir_path, path))


@file_bp.route('/api/files/columns', methods=['GET'])
def get_column_types():
    """Give the list of available column types

    Returns
    -------
    json
        types: list of available column types
    """

    data = ["numeric", "text", "category", "boolean", "date", "reference", "strand", "start", "end", "general_relation", "symetric_relation", "label"]

    return jsonify({
        "types": data
    })
