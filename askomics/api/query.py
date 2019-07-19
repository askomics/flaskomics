import sys
import traceback

from askomics.api.auth import login_required
from askomics.libaskomics.ResultsHandler import ResultsHandler
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
        tse = TriplestoreExplorer(current_app, session)
        results_handler = ResultsHandler(current_app, session)

        startpoints = tse.get_startpoints()
        public_queries = results_handler.get_public_queries()
    except Exception as e:
        current_app.logger.error(str(e))
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
        tse = TriplestoreExplorer(current_app, session)
        abstraction = tse.get_abstraction()
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return jsonify({
            'abstraction': [],
            'error': True,
            'errorMessage': str(e)
        }), 500
    return jsonify({
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
        data = request.get_json()

        query_builder = SparqlQueryBuilder(current_app, session)
        query_launcher = SparqlQueryLauncher(current_app, session, get_result_query=True)

        query = query_builder.build_query_from_json(data["graphState"], preview=True, for_editor=True)
        header = query_builder.selects
        preview = []
        if query_builder.graphs:
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


@login_required
@query_bp.route('/api/query/save_result', methods=['POST'])
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
        graph_state = request.get_json()["graphState"]
        session_dict = {"user": session["user"]}
        task = current_app.celery.send_task("query", (session_dict, graph_state))
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
