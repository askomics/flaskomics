"""Api routes"""
import urllib.parse
import sys
import traceback

from askomics.api.auth import api_auth
from askomics.libaskomics.SparqlQuery import SparqlQuery

from flask import (Blueprint, current_app, jsonify, session)


data_bp = Blueprint('data', __name__, url_prefix='/')


@data_bp.route('/api/data/<string:uri>', methods=['GET'])
@api_auth
def get_data(uri):
    """Get information about uri

    Returns
    -------
    json
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """

    try:
        query = SparqlQuery(current_app, session, get_graphs=True)
        graphs, endpoints = query.get_graphs_and_endpoints(all_selected=True)

        endpoints = [val['uri'] for val in endpoints.values()]

        data = []

        # If the user do not have access to any endpoint (no viewable graph), skip
        if endpoints:

            uri = urllib.parse.quote(uri)
            base_uri = current_app.iniconfig.get('triplestore', 'namespace_data')
            full_uri = "<%s%s>" % (base_uri, uri)

            data = query.get_uri_parameters(full_uri, endpoints)

    except Exception as e:
        current_app.logger.error(str(e).replace('\\n', '\n'))
        traceback.print_exc(file=sys.stdout)
        return jsonify({
            'error': True,
            'errorMessage': str(e).replace('\\n', '\n'),
            'data': []
        }), 500

    return jsonify({
        'data': data,
        'error': False,
        'errorMessage': ""
    })
