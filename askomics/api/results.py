import traceback
import sys

from askomics.api.auth import login_required, admin_required
from askomics.libaskomics.ResultsHandler import ResultsHandler
from askomics.libaskomics.Result import Result
from askomics.libaskomics.SparqlQueryBuilder import SparqlQueryBuilder

from flask import (Blueprint, current_app, jsonify, session, request, send_from_directory)


results_bp = Blueprint('results', __name__, url_prefix='/')


@login_required
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
        triplestore_max_rows = None
        try:
            triplestore_max_rows = current_app.iniconfig.getint("triplestore", "result_set_max_rows")
        except Exception:
            pass
    except Exception as e:
        current_app.logger.error(str(e))
        return jsonify({
            'files': [],
            'triplestoreMaxRows': triplestore_max_rows,
            'error': True,
            'errorMessage': str(e)
        }), 500

    return jsonify({
        'files': files,
        'triplestoreMaxRows': triplestore_max_rows,
        'error': False,
        'errorMessage': ''
    })


@admin_required
@results_bp.route('/api/results/setpublic', methods=['POST'])
def set_public():
    """Change public status of a file, and return all files

    Returns
    -------
    json
        files: list of all files of current user
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    try:
        json = request.get_json()
        result = Result(current_app, session, {"id": json["fileId"]})
        results_handler = ResultsHandler(current_app, session)

        result.update_public_status(json["public"])
        files = results_handler.get_files_info()
        try:
            triplestore_max_rows = current_app.iniconfig.getint("triplestore", "result_set_max_rows")
        except Exception:
            triplestore_max_rows = None
    except Exception as e:
        current_app.logger.error(str(e))
        return jsonify({
            'files': [],
            'triplestoreMaxRows': triplestore_max_rows,
            'error': True,
            'errorMessage': str(e)
        }), 500

    return jsonify({
        'files': files,
        'triplestoreMaxRows': triplestore_max_rows,
        'error': False,
        'errorMessage': ''
    })


@login_required
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
        graph_state = result.get_graph_state(formated=True)

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


@login_required
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


@login_required
@results_bp.route('/api/results/delete', methods=['POST'])
def delete_result():
    """Summary

    Returns
    -------
    json
        files: list of all files of current user
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    try:
        files_id = request.get_json()["filesIdToDelete"]
        results_handler = ResultsHandler(current_app, session)
        remaining_files = results_handler.delete_results(files_id)
    except Exception as e:
        current_app.logger.error(str(e))
        return jsonify({
            'remainingFiles': {},
            'error': True,
            'errorMessage': str(e)
        }), 500

    return jsonify({
        'remainingFiles': remaining_files,
        'error': False,
        'errorMessage': ''
    })


@login_required
@results_bp.route('/api/results/sparqlquery', methods=['POST'])
def get_sparql_query():
    """Get sparql query of result for the query editor

    Returns
    -------
    json
        query: the sparql query
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    try:
        file_id = request.get_json()["fileId"]
        result_info = {"id": file_id}

        result = Result(current_app, session, result_info)
        query_builder = SparqlQueryBuilder(current_app, session)

        graph_state = result.get_graph_state()
        query = query_builder.build_query_from_json(graph_state, for_editor=True)

    except Exception as e:
        current_app.logger.error(str(e))
        traceback.print_exc(file=sys.stdout)
        return jsonify({
            'query': {},
            'error': True,
            'errorMessage': str(e)
        }), 500

    return jsonify({
        'query': query,
        'error': False,
        'errorMessage': ''
    })


@admin_required
@results_bp.route('/api/results/publish', methods=['POST'])
def publish_query():
    """Publish a query template from a result

    Returns
    -------
    json
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    try:
        json = request.get_json()
        result_info = {"id": json["id"]}

        result = Result(current_app, session, result_info)
        result.publish_query(json["description"], json["public"])

        results_handler = ResultsHandler(current_app, session)
        files = results_handler.get_files_info()

    except Exception as e:
        current_app.logger.error(str(e))
        traceback.print_exc(file=sys.stdout)

        return jsonify({
            'files': [],
            'error': True,
            'errorMessage': 'Failed to publish query: \n{}'.format(str(e))
        }), 500

    return jsonify({
        'files': files,
        'error': False,
        'errorMessage': ''
    })


@results_bp.route('/api/results/send2galaxy', methods=['POST'])
@login_required
def send2galaxy():
    """Send a result file into Galaxy

    Returns
    -------
    json
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    try:
        json = request.get_json()
        result_info = {"id": json["fileId"]}
        result = Result(current_app, session, result_info)
        result.send2galaxy(json["fileToSend"])
    except Exception as e:
        current_app.logger.error(str(e))
        traceback.print_exc(file=sys.stdout)

        return jsonify({
            'error': True,
            'errorMessage': 'Failed to publish query: \n{}'.format(str(e))
        }), 500

    return jsonify({
        'error': False,
        'errorMessage': ''
    })
