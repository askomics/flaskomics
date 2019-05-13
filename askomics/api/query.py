import sys
import traceback

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
        startpoints = tse.get_startpoints()
    except Exception as e:
        current_app.logger.error(str(e))
        return jsonify({
            'startpoints': [],
            'error': True,
            'errorMessage': str(e)
        }), 500

    return jsonify({
        'startpoints': startpoints,
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
        abstraction: abstraction
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    try:
        data = request.get_json()
        current_app.logger.debug(data["graphState"])

        query_builder = SparqlQueryBuilder(current_app, session)
        # query_launcher = SparqlQueryLauncher(current_app, session)

        query = query_builder.build_query_from_json(data["graphState"])
        # header, data = query_launcher.process_query(query)

        current_app.logger.debug(query)

        result_preview = ["a", "b", "c"]
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return jsonify({
            'resultsPreview': [],
            'error': True,
            'errorMessage': str(e)
        }), 500
    return jsonify({
        'resultsPreview': result_preview,
        'error': False,
        'errorMessage': ''
    })
