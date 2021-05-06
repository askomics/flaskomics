import traceback
import sys

from askomics.api.auth import api_auth, login_required, admin_required
from askomics.libaskomics.FilesUtils import FilesUtils
from askomics.libaskomics.ResultsHandler import ResultsHandler
from askomics.libaskomics.Result import Result
from askomics.libaskomics.SparqlQuery import SparqlQuery

from flask import (Blueprint, current_app, jsonify, session, request, send_from_directory)


results_bp = Blueprint('results', __name__, url_prefix='/')


def can_access(user):
    login_allowed = current_app.iniconfig.getboolean('askomics', 'enable_sparql_console', fallback=False)
    return login_allowed or user['admin']


@results_bp.route('/api/results', methods=['GET'])
@api_auth
@login_required
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
        traceback.print_exc(file=sys.stdout)
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


@results_bp.route('/api/results/preview', methods=['POST'])
@api_auth
@login_required
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
        data = request.get_json()
        if not (data and data.get("fileId")):
            return jsonify({
                'preview': [],
                'header': [],
                'id': None,
                'error': True,
                'errorMessage': "Missing file Id"
            }), 400

        file_id = data["fileId"]
        result_info = {"id": file_id}
        result = Result(current_app, session, result_info)
        headers, preview = result.get_file_preview()

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
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


@results_bp.route('/api/results/getquery', methods=["POST"])
@api_auth
def get_graph_and_sparql_query():
    """Get query (graphState or Sparql)

    Returns
    -------
    json
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    try:
        data = request.get_json()
        if not (data and data.get("fileId")):
            return jsonify({
                'graphState': {},
                'sparqlQuery': "",
                'graphs': [],
                'endpoints': [],
                'diskSpace': 0,
                'error': True,
                'errorMessage': "Missing fileId parameter"
            }), 400

        file_id = data["fileId"]
        result_info = {"id": file_id}
        result = Result(current_app, session, result_info)

        # Get graph state and sparql query
        graph_state = result.get_graph_state(formated=True)
        sparql_query = result.get_sparql_query()

        # Get disk space
        files_utils = FilesUtils(current_app, session)
        disk_space = files_utils.get_size_occupied_by_user() if "user" in session else None

        # Get graphs and endpoints
        graphs = result.graphs
        endpoints = result.endpoints
        # Get all graphs and endpoint, and mark as selected the used one
        query = SparqlQuery(current_app, session)
        graphs, endpoints = query.get_graphs_and_endpoints(selected_graphs=graphs, selected_endpoints=endpoints)

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return jsonify({
            'graphState': {},
            'sparqlQuery': "",
            'graphs': [],
            'endpoints': [],
            'diskSpace': 0,
            'error': True,
            'errorMessage': str(e)
        }), 500

    return jsonify({
        'graphState': graph_state,
        'sparqlQuery': sparql_query,
        'graphs': graphs,
        'endpoints': endpoints,
        'diskSpace': disk_space,
        'error': False,
        'errorMessage': ''
    })


@results_bp.route('/api/results/graphstate', methods=['POST'])
@api_auth
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
        data = request.get_json()
        if not (data and data.get("fileId")):
            return jsonify({
                'graphState': {},
                'id': None,
                'error': True,
                'errorMessage': "Missing fileId parameter"
            }), 400

        file_id = data["fileId"]
        formated = data.get("formated", True)

        result_info = {"id": file_id}
        result = Result(current_app, session, result_info)
        graph_state = result.get_graph_state(formated=formated)

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
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
@api_auth
@login_required
def download_result():
    """Download result file"""
    try:
        data = request.get_json()
        if not (data and data.get("fileId")):
            return jsonify({
                'error': True,
                'errorMessage': "Missing fileId parameter"
            }), 400

        file_id = data["fileId"]
        result_info = {"id": file_id}
        result = Result(current_app, session, result_info)
        dir_path = result.get_dir_path()
        file_name = result.get_file_name()

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return jsonify({
            'error': True,
            'errorMessage': str(e)
        }), 500

    return(send_from_directory(dir_path, file_name))


@results_bp.route('/api/results/delete', methods=['POST'])
@api_auth
@login_required
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
        data = request.get_json()
        if not (data and data.get("filesIdToDelete")):
            return jsonify({
                'remainingFiles': {},
                'error': True,
                'errorMessage': "Missing filesIdToDelete parameter"
            }), 400

        files_id = data["filesIdToDelete"]
        results_handler = ResultsHandler(current_app, session)
        remaining_files = results_handler.delete_results(files_id)
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
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


@results_bp.route('/api/results/sparqlquery', methods=['POST'])
@api_auth
@login_required
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
        files_utils = FilesUtils(current_app, session)
        disk_space = files_utils.get_size_occupied_by_user() if "user" in session else None

        data = request.get_json()
        if not (data and data.get("fileId")):
            return jsonify({
                'query': {},
                'graphs': [],
                'endpoints': [],
                'diskSpace': 0,
                'error': True,
                'errorMessage': "Missing fileId parameter"
            }), 400

        file_id = data["fileId"]
        result_info = {"id": file_id}

        result = Result(current_app, session, result_info)
        query = SparqlQuery(current_app, session)

        sparql = result.get_sparql_query()

        # get graphs and endpoints used in the query
        graphs = result.graphs
        endpoints = result.endpoints
        # Get all graphs and endpoint, and mark as selected the used one
        graphs, endpoints = query.get_graphs_and_endpoints(selected_graphs=graphs, selected_endpoints=endpoints)

        console_enabled = can_access(session['user'])

        # Build sparql query from json if needed
        if sparql is None:
            query.json = result.get_graph_state()
            query.build_query_from_json(for_editor=True)
            sparql = query.sparql

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return jsonify({
            'query': {},
            'graphs': [],
            'endpoints': [],
            'diskSpace': 0,
            'error': True,
            'errorMessage': str(e)
        }), 500

    return jsonify({
        'query': sparql,
        'graphs': graphs,
        'endpoints': endpoints,
        'diskSpace': disk_space,
        'console_enabled': console_enabled,
        'error': False,
        'errorMessage': ''
    })


@results_bp.route('/api/results/description', methods=['POST'])
@api_auth
@login_required
def set_description():
    """Update a result description

    Returns
    -------
    json
        files: all files
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    try:
        data = request.get_json()
        if not (data and data.get("id") and data.get("newDesc")):
            return jsonify({
                'files': [],
                'error': True,
                'errorMessage': "Missing parameters"
            }), 400

        result_info = {"id": data["id"]}
        new_desc = data["newDesc"]

        result = Result(current_app, session, result_info)
        result.update_description(new_desc)

        results_handler = ResultsHandler(current_app, session)
        files = results_handler.get_files_info()

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


@results_bp.route('/api/results/publish', methods=['POST'])
@api_auth
@admin_required
def publish_query():
    """Publish a query template from a result

    Returns
    -------
    json
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    try:
        data = request.get_json()
        if not (data and data.get("id")):
            return jsonify({
                'files': [],
                'error': True,
                'errorMessage': "Missing id parameter"
            }), 400

        result_info = {"id": data["id"]}

        result = Result(current_app, session, result_info)
        if not(result.template or result.simple_template):
            return jsonify({
                'files': [],
                'error': True,
                'errorMessage': "Failed to publish query: \nMust enable template or simple template to publicize result"
            }), 400

        result.publish_query(data.get("public", False))

        results_handler = ResultsHandler(current_app, session)
        files = results_handler.get_files_info()

    except Exception as e:
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


@results_bp.route('/api/results/template', methods=['POST'])
@api_auth
@login_required
def template_query():
    """Template a query from a result

    Returns
    -------
    json
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    try:
        data = request.get_json()
        if not (data and data.get("id")):
            return jsonify({
                'files': [],
                'error': True,
                'errorMessage': "Missing id parameter"
            }), 400

        result_info = {"id": data["id"]}

        result = Result(current_app, session, result_info)
        result.template_query(data.get("template", False))

        results_handler = ResultsHandler(current_app, session)
        files = results_handler.get_files_info()

    except Exception as e:
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


@results_bp.route('/api/results/simple_template', methods=['POST'])
@api_auth
@login_required
def simple_template_query():
    """Simple Template a query from a result

    Returns
    -------
    json
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    try:
        data = request.get_json()
        if not (data and data.get("id")):
            return jsonify({
                'files': [],
                'error': True,
                'errorMessage': "Missing id parameter"
            }), 400

        result_info = {"id": data["id"]}

        result = Result(current_app, session, result_info)
        result.simple_template_query(data.get("template", False))

        results_handler = ResultsHandler(current_app, session)
        files = results_handler.get_files_info()

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return jsonify({
            'files': [],
            'error': True,
            'errorMessage': 'Failed to create simple template query: \n{}'.format(str(e))
        }), 500

    return jsonify({
        'files': files,
        'error': False,
        'errorMessage': ''
    })


@results_bp.route('/api/results/send2galaxy', methods=['POST'])
@api_auth
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
        data = request.get_json()
        if not (data and data.get("fileId") and data.get("fileToSend")):
            return jsonify({
                'error': True,
                'errorMessage': "Missing parameters"
            }), 400

        result_info = {"id": data["fileId"]}
        result = Result(current_app, session, result_info)
        result.send2galaxy(data["fileToSend"])
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return jsonify({
            'error': True,
            'errorMessage': 'Failed to publish query: \n{}'.format(str(e))
        }), 500

    return jsonify({
        'error': False,
        'errorMessage': ''
    })
