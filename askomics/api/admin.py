"""Admin routes"""
import sys
import traceback

from askomics.api.auth import api_auth, admin_required
from askomics.libaskomics.DatasetsHandler import DatasetsHandler
from askomics.libaskomics.FilesHandler import FilesHandler
from askomics.libaskomics.LocalAuth import LocalAuth
from askomics.libaskomics.Mailer import Mailer
from askomics.libaskomics.Result import Result
from askomics.libaskomics.ResultsHandler import ResultsHandler

from flask import (Blueprint, current_app, jsonify, request, session)

admin_bp = Blueprint('admin', __name__, url_prefix='/')


@admin_bp.route('/api/admin/getusers', methods=['GET'])
@api_auth
@admin_required
def get_users():
    """Get all users

    Returns
    -------
    json
        users: list of all users info
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    try:
        local_auth = LocalAuth(current_app, session)
        all_users = local_auth.get_all_users()
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return jsonify({
            'users': [],
            'error': True,
            'errorMessage': str(e)
        }), 500

    return jsonify({
        'users': all_users,
        'error': False,
        'errorMessage': ''
    })


@admin_bp.route('/api/admin/getdatasets', methods=['GET'])
@api_auth
@admin_required
def get_datasets():
    """Get all datasets

    Returns
    -------
    json
        users: list of all datasets
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    try:
        datasets_handler = DatasetsHandler(current_app, session)
        datasets = datasets_handler.get_all_datasets()
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


@admin_bp.route('/api/admin/getfiles', methods=['GET'])
@api_auth
@admin_required
def get_files():
    """Get all files info
    Returns
    -------
    json
        files: list of all files
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """

    try:
        files_handler = FilesHandler(current_app, session)
        files = files_handler.get_all_files_infos()

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return jsonify({
            'files': [],
            'error': True,
            'errorMessage': str(e)
        }), 500

    return jsonify({
        'files': files,
        'error': False,
        'errorMessage': ''
    })


@admin_bp.route('/api/admin/getqueries', methods=['GET'])
@api_auth
@admin_required
def get_queries():
    """Get all public queries

    Returns
    -------
    json
        startpoint: list of public queries
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    try:
        results_handler = ResultsHandler(current_app, session)
        public_queries = results_handler.get_admin_public_queries()

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return jsonify({
            "queries": [],
            'error': True,
            'errorMessage': str(e)
        }), 500

    return jsonify({
        "queries": public_queries,
        'error': False,
        'errorMessage': ''
    })


@admin_bp.route('/api/admin/setadmin', methods=['POST'])
@api_auth
@admin_required
def set_admin():
    """change admin status of a user

    Returns
    -------
    json
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    data = request.get_json()

    try:
        local_auth = LocalAuth(current_app, session)
        local_auth.set_admin(data['newAdmin'], data['username'])
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


@admin_bp.route('/api/admin/setquota', methods=["POST"])
@api_auth
@admin_required
def set_quota():
    """Change quota of a user

    Returns
    -------
    json
        users: updated users
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    data = request.get_json()

    try:
        local_auth = LocalAuth(current_app, session)
        local_auth.set_quota(data['quota'], data['username'])
        all_users = local_auth.get_all_users()
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return jsonify({
            'users': [],
            'error': True,
            'errorMessage': str(e)
        }), 500

    return jsonify({
        'users': all_users,
        'error': False,
        'errorMessage': ''
    })


@admin_bp.route('/api/admin/setblocked', methods=['POST'])
@api_auth
@admin_required
def set_blocked():
    """Change blocked status of a user

    Returns
    -------
    json
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    data = request.get_json()

    try:
        local_auth = LocalAuth(current_app, session)
        local_auth.set_blocked(data['newBlocked'], data['username'])
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


@admin_bp.route('/api/admin/publicize_dataset', methods=['POST'])
@api_auth
@admin_required
def toogle_public_dataset():
    """Toggle public status of a dataset

    Returns
    -------
    json
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    data = request.get_json()
    datasets_info = [{'id': data["datasetId"]}]

    try:
        # Change status to queued for all datasets
        datasets_handler = DatasetsHandler(current_app, session, datasets_info=datasets_info)
        datasets_handler.handle_datasets(admin=True)

        for dataset in datasets_handler.datasets:
            current_app.logger.debug(data["newStatus"])
            dataset.toggle_public(data["newStatus"], admin=True)

        datasets = datasets_handler.get_all_datasets()

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


@admin_bp.route('/api/admin/publicize_query', methods=['POST'])
@api_auth
@admin_required
def togle_public_query():
    """Publish a query template from a result

    Returns
    -------
    json
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    try:
        json = request.get_json()
        result_info = {"id": json["queryId"]}

        result = Result(current_app, session, result_info)
        result.publish_query(json["newStatus"], admin=True)

        results_handler = ResultsHandler(current_app, session)
        public_queries = results_handler.get_admin_public_queries()

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return jsonify({
            'queries': [],
            'error': True,
            'errorMessage': 'Failed to publish query: \n{}'.format(str(e))
        }), 500

    return jsonify({
        'queries': public_queries,
        'error': False,
        'errorMessage': ''
    })


@admin_bp.route("/api/admin/adduser", methods=["POST"])
@api_auth
@admin_required
def add_user():
    """Change blocked status of a user

    Returns
    -------
    json
        instanceUrl: The instance URL
        user: the new created user
        displayPassword: Display password on the interface ?
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    data = request.get_json()

    user = {}
    display_password = True

    try:
        local_auth = LocalAuth(current_app, session)
        local_auth.check_inputs(data, admin_add=True)

        if not local_auth.get_error():
            # Create a user
            user = local_auth.persist_user_admin(data)
            local_auth.create_user_directories(user['id'], user['username'])
            # Send a email to this user (if askomics can send emails)

            mailer = Mailer(current_app, session)
            if mailer.check_mailer():
                display_password = False
                current_app.celery.send_task('send_mail_new_user', ({'user': session['user']}, user))
                # Don't send password user to frontend
                user.pop("password")

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return jsonify({
            'instanceUrl': "",
            'user': user,
            'displayPassword': False,
            'error': True,
            'errorMessage': str(e)
        }), 500

    return jsonify({
        'instanceUrl': current_app.iniconfig.get("askomics", "instance_url"),
        'user': user,
        'displayPassword': display_password,
        'error': local_auth.get_error(),
        'errorMessage': local_auth.get_error_message()
    })


@admin_bp.route("/api/admin/delete_users", methods=["POST"])
@api_auth
@admin_required
def delete_users():
    """Delete users data

    Returns
    -------
    json
        users: remaining users
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    data = request.get_json()

    try:
        usernames = data["usersToDelete"]
        users = []

        # Remove current user from the list
        if session["user"]["username"] in usernames:
            usernames.remove(session["user"]["username"])

        # Remove users from database
        local_auth = LocalAuth(current_app, session)
        for username in usernames:
            # Get user info
            users.append(local_auth.get_user(username))
            local_auth.delete_user_database(username)

        # Celery task to delete users' data from filesystem and rdf triplestore
        session_dict = {'user': session['user']}
        current_app.celery.send_task('delete_users_data', (session_dict, users, True))

        # Get remaining users
        users = local_auth.get_all_users()

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return jsonify({
            'users': [],
            'error': True,
            'errorMessage': str(e)
        }), 500

    return jsonify({
        'users': users,
        'error': local_auth.get_error(),
        'errorMessage': local_auth.get_error_message()
    })


@admin_bp.route("/api/admin/delete_files", methods=["POST"])
@api_auth
@admin_required
def delete_files():
    """Delete files

    Returns
    -------
    json
        files: list of all files of current user
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    data = request.get_json()

    try:
        files = FilesHandler(current_app, session)
        remaining_files = files.delete_files(data['filesIdToDelete'], admin=True)
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return jsonify({
            'files': [],
            'error': True,
            'errorMessage': str(e)
        }), 500

    return jsonify({
        'files': remaining_files,
        'error': False,
        'errorMessage': ''
    })


@admin_bp.route("/api/admin/delete_datasets", methods=["POST"])
@api_auth
@admin_required
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
        datasets_handler.handle_datasets(admin=True)
        datasets_handler.update_status_in_db('queued', admin=True)

        # Launch a celery task for each datasets to delete
        for dataset in datasets_handler.datasets:
            dataset_info = [{
                "id": dataset.id
            }, ]
            current_app.logger.debug(dataset_info)

            # kill integration celery task
            current_app.celery.control.revoke(dataset.celery_id, terminate=True)

            # Trigger the celery task to delete the dataset
            task = current_app.celery.send_task('delete_datasets', (session_dict, dataset_info, True))

            # replace the task id with the new
            dataset.update_celery(task.id, admin=True)

        datasets = datasets_handler.get_all_datasets()

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
