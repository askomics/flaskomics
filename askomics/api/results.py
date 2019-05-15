from askomics.libaskomics.ResultsHandler import ResultsHandler
from askomics.libaskomics.Result import Result

from flask import (Blueprint, current_app, jsonify, session, request, send_from_directory)


results_bp = Blueprint('results', __name__, url_prefix='/')


@results_bp.route('/api/results', methods=['GET'])
def get_results():
    """Get ...

    Returns
    -------
    json
        files: list of all files of current user
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    try:
        results_handler = ResultsHandler(current_app, session)
        files = results_handler.get_files_info()
    except Exception as e:
        current_app.logger.error(str(e))
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


@results_bp.route('/api/results/preview', methods=['POST'])
def get_preview():
    """Summary

    Returns
    -------
    json
        preview: list of result preview
        header: result header
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    try:
        file_id = request.get_json()["fileId"]
        result_info = {"id": file_id}
        result = Result(current_app, session, result_info)
        headers, preview = result.get_file_preview()

    except Exception as e:
        current_app.logger.error(str(e))
        return jsonify({
            'preview': [],
            'header': [],
            'id': file_id,
            'error': True,
            'errorMessage': str(e)
        }), 500

    return jsonify({
        'preview': preview,
        'header': headers,
        'id': file_id,
        'error': False,
        'errorMessage': ''
    })


@results_bp.route('/api/results/graphstate', methods=['POST'])
def get_graph_state():
    """Summary

    Returns
    -------
    json
        preview: list of result preview
        header: result header
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    try:
        file_id = request.get_json()["fileId"]
        result_info = {"id": file_id}
        result = Result(current_app, session, result_info)
        graph_state = result.get_graph_state()

    except Exception as e:
        current_app.logger.error(str(e))
        return jsonify({
            'graphState': {},
            'id': file_id,
            'error': True,
            'errorMessage': str(e)
        }), 500

    return jsonify({
        'graphState': graph_state,
        'id': file_id,
        'error': False,
        'errorMessage': ''
    })


@results_bp.route('/api/results/download', methods=['POST'])
def download_result():
    """Download result file"""
    try:
        file_id = request.get_json()["fileId"]
        result_info = {"id": file_id}
        result = Result(current_app, session, result_info)
        dir_path = result.get_dir_path()
        file_name = result.get_file_name()

    except Exception as e:
        current_app.logger.error(str(e))
        return jsonify({
            'error': True,
            'errorMessage': str(e)
        }), 500

    return(send_from_directory(dir_path, file_name))
