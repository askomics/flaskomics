"""Api routes
"""

from askomics.api.auth import login_required
from askomics.libaskomics.DatasetsHandler import DatasetsHandler

from flask import (Blueprint, current_app, jsonify, request, session)


datasets_bp = Blueprint('datasets', __name__, url_prefix='/')


@datasets_bp.route('/api/datasets', methods=['GET'])
@login_required
def get_datasets():
    """Get datasets information

    Returns
    -------
    json
        datasets: list of all datasets of current user
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    try:
        datasets_handler = DatasetsHandler(current_app, session)
        datasets = datasets_handler.get_datasets()
    except Exception as e:
        current_app.logger.error(str(e))
        return jsonify({
            'datasets': [],
            'error': True,
            'errorMessage': str(e)
        }), 500

    return jsonify({
        'datasets': datasets,
        'error': False,
        'errorMessage': ''
    })


@datasets_bp.route('/api/datasets/delete', methods=['POST'])
@login_required
def delete_datasets():
    """Delete some datasets (db and triplestore) with a celery task

    Returns
    -------
    json
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    data = request.get_json()
    datasets_info = []
    for dataset_id in data['datasetsIdToDelete']:
        datasets_info.append({'id': dataset_id})

    session_dict = {'user': session['user']}

    try:
        # Change status into database
        datasets_handler = DatasetsHandler(current_app, session, datasets_info=datasets_info)
        datasets_handler.handle_datasets()
        datasets_handler.update_status_in_db('deleting')
        # Trigger the celery task to delete it in the ts, and in db
        current_app.celery.send_task('delete_datasets', (session_dict, datasets_info))
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
