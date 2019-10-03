"""Api routes"""
import sys
import traceback

from askomics.api.auth import login_required, admin_required
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
        traceback.print_exc(file=sys.stdout)
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
        # Change status to queued for all datasets
        datasets_handler = DatasetsHandler(current_app, session, datasets_info=datasets_info)
        datasets_handler.handle_datasets()
        datasets_handler.update_status_in_db('queued')

        # Launch a celery task for each datasets to delete
        for dataset in datasets_handler.datasets:
            dataset_info = [{
                "id": dataset.id
            }, ]
            current_app.logger.debug(dataset_info)

            # kill integration celery task
            current_app.celery.control.revoke(dataset.celery_id, terminate=True)

            # Trigger the celery task to delete the dataset
            task = current_app.celery.send_task('delete_datasets', (session_dict, dataset_info))

            # replace the task id with the new
            dataset.update_celery(task.id)

        datasets = datasets_handler.get_datasets()

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
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


@datasets_bp.route('/api/datasets/public', methods=['POST'])
@admin_required
def toogle_public():
    """Toggle public status of a dataset

    Returns
    -------
    json
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    data = request.get_json()
    datasets_info = [{'id': data["id"]}]

    try:
        # Change status to queued for all datasets
        datasets_handler = DatasetsHandler(current_app, session, datasets_info=datasets_info)
        datasets_handler.handle_datasets()

        for dataset in datasets_handler.datasets:
            current_app.logger.debug(data["newStatus"])
            dataset.toggle_public(data["newStatus"])

        datasets = datasets_handler.get_datasets()

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
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
