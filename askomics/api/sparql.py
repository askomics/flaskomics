import traceback
import sys
from askomics.libaskomics.FilesUtils import FilesUtils
from askomics.libaskomics.Result import Result
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
        traceback.print_exc(file=sys.stdout)
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


@sparql_bp.route('/api/sparql/previewquery', methods=['POST'])
def query():
    """Perform a sparql query

    Returns
    -------
    json
        query results
    """
    q = request.get_json()['query']
    graphs = request.get_json()['graphs']
    endpoints = request.get_json()['endpoints']

    local_endpoint_f = current_app.iniconfig.get('triplestore', 'endpoint')
    try:
        local_endpoint_f = current_app.iniconfig.get('federation', 'local_endpoint')
    except Exception:
        pass

    # No graph selected in local TS
    if not graphs and local_endpoint_f in endpoints:
        return jsonify({
            'error': True,
            'errorMessage': "No graph selected in local triplestore",
            'header': [],
            'data': []
        }), 500

    # No endpoint selected
    if not endpoints:
        return jsonify({
            'error': True,
            'errorMessage': "No endpoint selected",
            'header': [],
            'data': []
        }), 500

    try:
        query_builder = SparqlQueryBuilder(current_app, session)

        query_builder.set_graphs_and_endpoints(graphs=graphs, endpoints=endpoints)

        federated = query_builder.is_federated()
        replace_froms = query_builder.replace_froms()

        query = query_builder.format_query(q, replace_froms=replace_froms, federated=federated)
        # header, data = query_launcher.process_query(query)
        header = query_builder.selects
        data = []
        if query_builder.graphs or query_builder.endpoints:
            query_launcher = SparqlQueryLauncher(current_app, session, get_result_query=True, federated=federated, endpoints=endpoints)
            header, data = query_launcher.process_query(query)

    except Exception as e:
        current_app.logger.error(str(e).replace('\\n', '\n'))
        traceback.print_exc(file=sys.stdout)
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


@sparql_bp.route('/api/sparql/savequery', methods=["POST"])
def save_query():
    """Perform a sparql query

    Returns
    -------
    json
        query results
    """
    query = request.get_json()['query']
    graphs = request.get_json()['graphs']
    endpoints = request.get_json()['endpoints']

    local_endpoint_f = current_app.iniconfig.get('triplestore', 'endpoint')
    try:
        local_endpoint_f = current_app.iniconfig.get('federation', 'local_endpoint')
    except Exception:
        pass

    # No graph selected in local TS
    if not graphs and local_endpoint_f in endpoints:
        return jsonify({
            'error': True,
            'errorMessage': "No graph selected in local triplestore",
            'task_id': None
        }), 500

    # No endpoint selected
    if not endpoints:
        return jsonify({
            'error': True,
            'errorMessage': "No endpoint selected",
            'task_id': None
        }), 500

    try:
        files_utils = FilesUtils(current_app, session)
        disk_space = files_utils.get_size_occupied_by_user() if "user" in session else None

        if session["user"]["quota"] > 0 and disk_space >= session["user"]["quota"]:
            return jsonify({
                'error': True,
                'errorMessage': "Exceeded quota",
                'task_id': None
            }), 500

        # Is query federated?
        query_builder = SparqlQueryBuilder(current_app, session)
        query_builder.set_graphs_and_endpoints(graphs=graphs, endpoints=endpoints)

        federated = query_builder.is_federated()
        replace_froms = query_builder.replace_froms()

        formatted_query = query_builder.format_query(query, limit=None, replace_froms=replace_froms, federated=federated)

        info = {
            "sparql_query": query,  # Store the non formatted query in db
            "graphs": graphs,
            "endpoints": endpoints,
            "federated": federated,
            "celery_id": None
        }

        result = Result(current_app, session, info)
        info["id"] = result.save_in_db()

        # execute the formatted query
        info["sparql_query"] = formatted_query

        session_dict = {"user": session["user"]}
        task = current_app.celery.send_task("sparql_query", (session_dict, info))
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
