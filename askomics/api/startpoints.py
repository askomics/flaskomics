import sys
import traceback

from askomics.libaskomics.TriplestoreExplorer import TriplestoreExplorer

from flask import (Blueprint, current_app, jsonify, session)


startpoints_bp = Blueprint('startpoints', __name__, url_prefix='/')


@startpoints_bp.route('/api/startpoints', methods=['GET'])
def startpoints():
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


@startpoints_bp.route('/api/startpoints/abstraction', methods=['GET'])
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
