"""Api routes"""
import sys
import traceback

import json

from askomics.api.auth import api_auth, login_required
from askomics.libaskomics.FilesUtils import FilesUtils
from askomics.libaskomics.Galaxy import Galaxy

from flask import (Blueprint, current_app, jsonify, request, session)

galaxy_bp = Blueprint('galaxy', __name__, url_prefix='/')


@galaxy_bp.route('/api/galaxy/datasets', methods=['GET', 'POST'])
@api_auth
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
        if request.get_json():
            history_id = request.get_json().get("history_id")

    try:
        galaxy = Galaxy(current_app, session)
        ginfo = galaxy.get_datasets_and_histories(history_id)
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
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


@galaxy_bp.route('/api/galaxy/queries', methods=['GET', 'POST'])
@api_auth
@login_required
def get_queries():
    """Get galaxy queries (json datasets)

    Returns
    -------
    json

        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    history_id = None
    if request.method == 'POST':
        if request.get_json():
            history_id = request.get_json().get("history_id")

    try:
        galaxy = Galaxy(current_app, session)
        ginfo = galaxy.get_datasets_and_histories(history_id, query=True)
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
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
@api_auth
@login_required
def upload_datasets():
    """Download a galaxy datasets into AskOmics

    Returns
    -------
    json

        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    files_utils = FilesUtils(current_app, session)
    disk_space = files_utils.get_size_occupied_by_user() if "user" in session else None

    if session["user"]["quota"] > 0 and disk_space >= session["user"]["quota"]:
        return jsonify({
            'errorMessage': "Exceeded quota",
            "error": True
        }), 400

    data = request.get_json()
    if not (data and data.get("datasets_id")):
        return jsonify({
            'error': True,
            'errorMessage': "Missing datasets_id parameter"
        }), 400

    datasets_id = data["datasets_id"]

    try:
        galaxy = Galaxy(current_app, session)
        galaxy.download_datasets(datasets_id)
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return jsonify({
            'error': True,
            'errorMessage': str(e)
        }), 500

    return jsonify({
        'error': False,
        'errorMessage': ''
    })


@galaxy_bp.route('/api/galaxy/getdatasetcontent', methods=['POST'])
@api_auth
@login_required
def get_dataset_content():
    """Download a galaxy datasets into AskOmics

    Returns
    -------
    json
        dataset_content: content of the requested Galaxy dataset
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """

    data = request.get_json()
    if not (data and data.get("dataset_id")):
        return jsonify({
            'error': True,
            'errorMessage': "Missing dataset_id parameter"
        }), 400

    dataset_id = data["dataset_id"]

    try:
        galaxy = Galaxy(current_app, session)
        dataset_content = galaxy.get_dataset_content(dataset_id)
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return jsonify({
            'dataset_content': {},
            'error': True,
            'errorMessage': str(e)
        }), 500

    return jsonify({
        'dataset_content': json.loads(dataset_content),
        'error': False,
        'errorMessage': ''
    })
