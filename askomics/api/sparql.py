from askomics.libaskomics.SparqlQueryBuilder import SparqlQueryBuilder
from askomics.libaskomics.SparqlQueryLauncher import SparqlQueryLauncher

from flask import (Blueprint, current_app, jsonify, request, session)


sparql_bp = Blueprint('sparql', __name__, url_prefix='/')


@sparql_bp.route('/api/sparql/getquery', methods=['GET'])
def prefix():
    """Get the default sparql query

    Returns
    -------
    json
        default query
    """
    try:
        query_builder = SparqlQueryBuilder(current_app, session)
        query = query_builder.get_default_query_with_prefix()

    except Exception as e:
        current_app.logger.error(str(e))
        return jsonify({
            'error': True,
            'errorMessage': str(e),
            'query': ''
        }), 500

    return jsonify({
        'error': False,
        'errorMessage': '',
        'query': query
    })


@sparql_bp.route('/api/sparql/query', methods=['POST'])
def query():
    """Perform a sparql query

    Returns
    -------
    json
        query results
    """
    q = request.get_json()['query']

    try:
        query_builder = SparqlQueryBuilder(current_app, session)
        query_launcher = SparqlQueryLauncher(current_app, session)

        query = query_builder.format_query(q)
        header, data = query_launcher.process_query(query)

    except Exception as e:
        current_app.logger.error(str(e).replace('\\n', '\n'))
        return jsonify({
            'error': True,
            'errorMessage': str(e).replace('\\n', '\n'),
            'header': [],
            'data': []
        }), 500

    return jsonify({
        'header': header,
        'data': data
    })
