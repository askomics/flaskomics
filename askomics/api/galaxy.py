"""Api routes"""
from askomics.api.auth import login_required
from askomics.libaskomics.Galaxy import Galaxy

from flask import (Blueprint, current_app, jsonify, request, session)

galaxy_bp = Blueprint('galaxy', __name__, url_prefix='/')


@galaxy_bp.route('/api/galaxy/datasets', methods=['GET', 'POST'])
@login_required
def get_datasets():
    """Get galaxy datasets and histories of a user

    Returns
    -------
    json

        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    history_id = None
    if request.method == 'POST':
        history_id = request.get_json()["history_id"]

    try:
        galaxy = Galaxy(current_app, session)
        ginfo = galaxy.get_datasets_and_histories(history_id)
    except Exception as e:
        current_app.logger.error(str(e))
        return jsonify({
            'datasets': [],
            'histories': [],
            'error': True,
            'errorMessage': str(e)
        }), 500

    return jsonify({
        'datasets': ginfo['datasets'],
        'histories': ginfo['histories'],
        'error': False,
        'errorMessage': ''
    })


@galaxy_bp.route('/api/galaxy/upload_datasets', methods=['POST'])
@login_required
def upload_datasets():
    """Download a galaxy datasets into AskOmics

    Returns
    -------
    json

        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    datasets_id = request.get_json()["datasets_id"]

    try:
        galaxy = Galaxy(current_app, session)
        galaxy.download_datasets(datasets_id)
    except Exception as e:
        current_app.logger.error(str(e))
        return jsonify({
            'error': True,
            'errorMessage': str(e)
        }), 500

    return jsonify({
        'error': False,
        'errorMessage': ''
    })
