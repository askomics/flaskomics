import sys
import traceback

from askomics.api.auth import login_required
from askomics.libaskomics.FilesUtils import FilesUtils
from askomics.libaskomics.ResultsHandler import ResultsHandler
from askomics.libaskomics.Result import Result
from askomics.libaskomics.TriplestoreExplorer import TriplestoreExplorer
from askomics.libaskomics.SparqlQueryBuilder import SparqlQueryBuilder
from askomics.libaskomics.SparqlQueryLauncher import SparqlQueryLauncher

from flask import (Blueprint, current_app, jsonify, session, request)


query_bp = Blueprint('query', __name__, url_prefix='/')


@query_bp.route('/api/query/startpoints', methods=['GET'])
def query():
    """Get start points

    Returns
    -------
    json
        startpoint: list of start points
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    try:
        # If public datasets and queries are protected, dont return anything to unlogged users
        if "user" not in session and current_app.iniconfig.getboolean("askomics", "protect_public"):
            startpoints = []
            public_queries = []
        else:
            tse = TriplestoreExplorer(current_app, session)
            results_handler = ResultsHandler(current_app, session)
            startpoints = tse.get_startpoints()
            public_queries = results_handler.get_public_queries()

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return jsonify({
            'startpoints': [],
            "publicQueries": [],
            'error': True,
            'errorMessage': str(e)
        }), 500

    return jsonify({
        'startpoints': startpoints,
        "publicQueries": public_queries,
        'error': False,
        'errorMessage': ''
    })


@query_bp.route('/api/query/abstraction', methods=['GET'])
def get_abstraction():
    """Get abstraction

    Returns
    -------
    json
        abstraction: abstraction
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    try:
        # If public datasets and queries are protected, dont return anything to unlogged users
        if "user" not in session and current_app.iniconfig.getboolean("askomics", "protect_public"):
            abstraction = []
            disk_space = None
        else:
            tse = TriplestoreExplorer(current_app, session)
            abstraction = tse.get_abstraction()
            files_utils = FilesUtils(current_app, session)
            disk_space = files_utils.get_size_occupied_by_user() if "user" in session else None
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return jsonify({
            'diskSpace': None,
            'abstraction': [],
            'error': True,
            'errorMessage': str(e)
        }), 500
    return jsonify({
        'diskSpace': disk_space,
        'abstraction': abstraction,
        'error': False,
        'errorMessage': ''
    })


@query_bp.route('/api/query/preview', methods=['POST'])
def get_preview():
    """Get a preview of query

    Returns
    -------
    json
        resultsPreview: Preview of the query results
        headerPreview: Header of the results table
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    try:
        # If public datasets and queries are protected, dont return anything to unlogged users
        if "user" not in session and current_app.iniconfig.getboolean("askomics", "protect_public"):
            preview = []
            header = []
        else:
            data = request.get_json()

            query_builder = SparqlQueryBuilder(current_app, session)

            query = query_builder.build_query_from_json(data["graphState"], preview=True, for_editor=False)
            endpoints = query_builder.endpoints
            federated = query_builder.federated

            header = query_builder.selects
            preview = []
            if query_builder.graphs:
                query_launcher = SparqlQueryLauncher(current_app, session, get_result_query=True, federated=federated, endpoints=endpoints)
                header, preview = query_launcher.process_query(query)

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return jsonify({
            'resultsPreview': [],
            'headerPreview': [],
            'error': True,
            'errorMessage': str(e)
        }), 500
    return jsonify({
        'resultsPreview': preview,
        'headerPreview': header,
        'error': False,
        'errorMessage': ''
    })


@query_bp.route('/api/query/save_result', methods=['POST'])
@login_required
def save_result():
    """Save a query in filesystem and db, using a celery task

    Returns
    -------
    json
        task_id: celery task id
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    try:
        files_utils = FilesUtils(current_app, session)
        disk_space = files_utils.get_size_occupied_by_user() if "user" in session else None

        if session["user"]["quota"] > 0 and disk_space >= session["user"]["quota"]:
            return jsonify({
                'error': True,
                'errorMessage': "Exceeded quota",
                'task_id': None
            }), 500

        # Get query and endpoints and graphs of the query
        graph_state = request.get_json()["graphState"]
        query_builder = SparqlQueryBuilder(current_app, session)
        query = query_builder.build_query_from_json(graph_state, preview=False, for_editor=False)
        endpoints = query_builder.endpoints
        graphs = query_builder.graphs

        info = {
            "graph_state": graph_state,
            "query": query,
            "graphs": graphs,
            "endpoints": endpoints,
            "celery_id": None
        }

        result = Result(current_app, session, info)
        info["id"] = result.save_in_db()

        session_dict = {"user": session["user"]}
        task = current_app.celery.send_task("query", (session_dict, info))
        result.update_celery(task.id)
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
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
