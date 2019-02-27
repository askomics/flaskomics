"""Api routes
"""
from flask import (Blueprint, current_app, jsonify, session, request)
from askomics.api.auth import login_required

from askomics.libaskomics.DatasetsHandler import DatasetsHandler

datasets_bp = Blueprint('datasets', __name__, url_prefix='/')

@datasets_bp.route('/api/datasets', methods=['GET'])
@login_required
def get_datasets():


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
        task = current_app.celery.send_task('delete_datasets', (session_dict, datasets_info))
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
