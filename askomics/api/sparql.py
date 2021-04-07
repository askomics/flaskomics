import traceback
import sys
from askomics.api.auth import login_required
from askomics.libaskomics.FilesUtils import FilesUtils
from askomics.libaskomics.Result import Result
from askomics.libaskomics.SparqlQuery import SparqlQuery
from askomics.libaskomics.SparqlQueryLauncher import SparqlQueryLauncher

from flask import (Blueprint, current_app, jsonify, request, session)

sparql_bp = Blueprint('sparql', __name__, url_prefix='/')


def can_access(user):
    login_allowed = current_app.iniconfig.getboolean('askomics', 'enable_sparql_console', fallback=False)
    return login_allowed or user['admin']


@sparql_bp.route("/api/sparql/init", methods=["GET"])
@login_required
def init():
    """Get the default sparql query

    Returns
    -------
    json
    """
    try:
        # Disk space
        files_utils = FilesUtils(current_app, session)
        disk_space = files_utils.get_size_occupied_by_user() if "user" in session else None

        # Get graphs and endpoints
        query = SparqlQuery(current_app, session)
        graphs, endpoints = query.get_graphs_and_endpoints(all_selected=True)

        # Default query
        default_query = query.prefix_query(query.get_default_query())

        console_enabled = can_access(session['user'])

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return jsonify({
            "error": True,
            "errorMessage": str(e),
            "defaultQuery": "",
            "graphs": {},
            "endpoints": {},
            "diskSpace": None,
            "console_enabled": False
        }), 500

    return jsonify({
        "error": False,
        "errorMessage": "",
        "defaultQuery": default_query,
        "graphs": graphs,
        "endpoints": endpoints,
        "diskSpace": disk_space,
        "console_enabled": console_enabled
    })


@sparql_bp.route('/api/sparql/previewquery', methods=['POST'])
@login_required
def query():
    """Perform a sparql query

    Returns
    -------
    json
        query results
    """

    if not can_access(session['user']):
        return jsonify({"error": True, "errorMessage": "Admin required"}), 401

    data = request.get_json()
    if not (data and data.get("query")):
        return jsonify({
            'error': True,
            'errorMessage': "Missing query parameter",
            'header': [],
            'data': []
        }), 400

    q = data['query']
    graphs = data.get('graphs', [])
    endpoints = data.get('endpoints', [])

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
        }), 400

    # No endpoint selected
    if not endpoints:
        return jsonify({
            'error': True,
            'errorMessage': "No endpoint selected",
            'header': [],
            'data': []
        }), 400

    try:
        query = SparqlQuery(current_app, session)

        query.set_graphs_and_endpoints(graphs=graphs, endpoints=endpoints)

        federated = query.is_federated()
        replace_froms = query.replace_froms()

        sparql = query.format_query(q, replace_froms=replace_froms, federated=federated)
        # header, data = query_launcher.process_query(query)
        header = query.selects
        data = []
        if query.graphs or query.endpoints:
            query_launcher = SparqlQueryLauncher(current_app, session, get_result_query=True, federated=federated, endpoints=endpoints)
            header, data = query_launcher.process_query(sparql)

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
@login_required
def save_query():
    """Perform a sparql query

    Returns
    -------
    json
        query results
    """

    if not can_access(session['user']):
        return jsonify({"error": True, "errorMessage": "Admin required"}), 401

    data = request.get_json()
    if not (data and data.get("query")):
        return jsonify({
            'error': True,
            'errorMessage': "Missing query parameter",
            'header': [],
            'data': []
        }), 400

    q = data['query']
    graphs = data.get('graphs', [])
    endpoints = data.get('endpoints', [])

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
        }), 400

    # No endpoint selected
    if not endpoints:
        return jsonify({
            'error': True,
            'errorMessage': "No endpoint selected",
            'task_id': None
        }), 400

    try:
        files_utils = FilesUtils(current_app, session)
        disk_space = files_utils.get_size_occupied_by_user() if "user" in session else None

        if session["user"]["quota"] > 0 and disk_space >= session["user"]["quota"]:
            return jsonify({
                'error': True,
                'errorMessage': "Exceeded quota",
                'task_id': None
            }), 400

        # Is query federated?
        query = SparqlQuery(current_app, session)
        query.set_graphs_and_endpoints(graphs=graphs, endpoints=endpoints)

        federated = query.is_federated()
        replace_froms = query.replace_froms()

        formatted_query = query.format_query(q, limit=None, replace_froms=replace_froms, federated=federated)

        info = {
            "sparql_query": q,  # Store the non formatted query in db
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
