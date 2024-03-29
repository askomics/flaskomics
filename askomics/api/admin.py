"""Admin routes"""
import sys
import traceback

from askomics.api.auth import api_auth, admin_required
from askomics.libaskomics.DatasetsHandler import DatasetsHandler
from askomics.libaskomics.FilesHandler import FilesHandler
from askomics.libaskomics.LocalAuth import LocalAuth
from askomics.libaskomics.Mailer import Mailer
from askomics.libaskomics.PrefixManager import PrefixManager
from askomics.libaskomics.OntologyManager import OntologyManager
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
    (And anonymous queries)
    Returns
    -------
    json
        startpoint: list of public queries
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    try:
        results_handler = ResultsHandler(current_app, session)
        queries = results_handler.get_admin_queries()

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return jsonify({
            "queries": [],
            'error': True,
            'errorMessage': str(e)
        }), 500

    return jsonify({
        "queries": queries,
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
            if (not data.get("newStatus", False) and dataset.ontology):
                return jsonify({
                    'datasets': [],
                    'error': True,
                    'errorMessage': "Cannot unpublicize a dataset linked to an ontology"
                }), 400
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
def toggle_public_query():
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
        public_queries = results_handler.get_admin_queries()

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


@admin_bp.route('/api/admin/update_description', methods=['POST'])
@api_auth
@admin_required
def update_query_description():
    """Update a query description

    Returns
    -------
    json
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    try:
        data = request.get_json()
        if not (data and data.get("queryId") and data.get("newDesc")):
            return jsonify({
                'files': [],
                'error': True,
                'errorMessage': "Missing parameters"
            }), 400

        result_info = {"id": data["queryId"]}
        new_desc = data["newDesc"]

        result = Result(current_app, session, result_info, admin=True)
        if not result:
            return jsonify({
                'files': [],
                'error': True,
                'errorMessage': "You do not have access to this result"
            }), 500
        result.update_description(new_desc, admin=True)

        results_handler = ResultsHandler(current_app, session)
        queries = results_handler.get_admin_queries()

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return jsonify({
            'queries': [],
            'error': True,
            'errorMessage': 'Failed to update description: \n{}'.format(str(e))
        }), 500

    return jsonify({
        'queries': queries,
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


@admin_bp.route("/api/admin/delete_queries", methods=["POST"])
@api_auth
@admin_required
def delete_queries():
    """Delete queries

    Returns
    -------
    json
        queries: list of all queries (either public or anonymous)
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    data = request.get_json()
    if not data.get("queriesIdToDelete"):
        return jsonify({
            'queries': [],
            'error': True,
            'errorMessage': "Missing queriesIdToDelete key"
        }), 400

    try:
        queries_id = data["queriesIdToDelete"]
        results_handler = ResultsHandler(current_app, session)
        remaining_queries = results_handler.delete_results(queries_id, admin=True)

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return jsonify({
            'queries': [],
            'error': True,
            'errorMessage': str(e)
        }), 500

    return jsonify({
        'queries': remaining_queries,
        'error': False,
        'errorMessage': ''
    })


@admin_bp.route("/api/admin/getprefixes", methods=["GET"])
@api_auth
@admin_required
def get_prefixes():
    """Get all custom prefixes

    Returns
    -------
    json
        prefixes: list of all custom prefixes
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    try:
        pm = PrefixManager(current_app, session)
        prefixes = pm.get_custom_prefixes()
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return jsonify({
            'prefixes': [],
            'error': True,
            'errorMessage': str(e)
        }), 500

    return jsonify({
        'prefixes': prefixes,
        'error': False,
        'errorMessage': ''
    })


@admin_bp.route("/api/admin/addprefix", methods=["POST"])
@api_auth
@admin_required
def add_prefix():
    """Create a new prefix

    Returns
    -------
    json
        prefixes: list of all custom prefixes
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """

    data = request.get_json()
    if not data or not (data.get("prefix") and data.get("namespace")):
        return jsonify({
            'prefixes': [],
            'error': True,
            'errorMessage': "Missing parameter"
        }), 400

    pm = PrefixManager(current_app, session)
    prefixes = pm.get_custom_prefixes()

    prefix = data.get("prefix")
    namespace = data.get("namespace")

    if any([prefix == custom['prefix'] for custom in prefixes]):
        return jsonify({
            'prefixes': [],
            'error': True,
            'errorMessage': "Prefix {} is already in use".format(prefix)
        }), 400

    try:
        pm.add_custom_prefix(prefix, namespace)
        prefixes = pm.get_custom_prefixes()
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return jsonify({
            'prefixes': [],
            'error': True,
            'errorMessage': str(e)
        }), 500

    return jsonify({
        'prefixes': prefixes,
        'error': False,
        'errorMessage': ''
    })


@admin_bp.route("/api/admin/delete_prefixes", methods=["POST"])
@api_auth
@admin_required
def delete_prefix():
    """Delete a prefix

    Returns
    -------
    json
        prefixes: list of all custom prefixes
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """

    data = request.get_json()
    if not data or not data.get("prefixesIdToDelete"):
        return jsonify({
            'prefixes': [],
            'error': True,
            'errorMessage': "Missing prefixesIdToDelete parameter"
        }), 400

    pm = PrefixManager(current_app, session)
    try:
        pm.remove_custom_prefixes(data.get("prefixesIdToDelete"))
        prefixes = pm.get_custom_prefixes()
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return jsonify({
            'prefixes': [],
            'error': True,
            'errorMessage': str(e)
        }), 500

    return jsonify({
        'prefixes': prefixes,
        'error': False,
        'errorMessage': ''
    })


@admin_bp.route("/api/admin/getontologies", methods=["GET"])
@api_auth
@admin_required
def get_ontologies():
    """Get all ontologies

    Returns
    -------
    json
        prefixes: list of all custom prefixes
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    try:
        om = OntologyManager(current_app, session)
        ontologies = om.list_full_ontologies()
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return jsonify({
            'ontologies': [],
            'error': True,
            'errorMessage': str(e)
        }), 500

    return jsonify({
        'ontologies': ontologies,
        'error': False,
        'errorMessage': ''
    })


@admin_bp.route("/api/admin/addontology", methods=["POST"])
@api_auth
@admin_required
def add_ontology():
    """Create a new ontology

    Returns
    -------
    json
        ontologies: list of all ontologies
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """

    data = request.get_json()
    if not data or not (data.get("name") and data.get("uri") and data.get("shortName") and data.get("type") and data.get("datasetId") and data.get("labelUri")):
        return jsonify({
            'ontologies': [],
            'error': True,
            'errorMessage': "Missing parameter"
        }), 400

    name = data.get("name").strip()
    uri = data.get("uri").strip()
    short_name = data.get("shortName")
    type = data.get("type").strip()
    dataset_id = data.get("datasetId")
    label_uri = data.get("labelUri").strip()

    om = OntologyManager(current_app, session)

    if type == "ols" and not om.test_ols_ontology(short_name):
        return jsonify({
            'ontologies': [],
            'error': True,
            'errorMessage': "{} ontology not found in OLS".format(short_name)
        }), 400

    om = OntologyManager(current_app, session)
    ontologies = om.list_full_ontologies()

    if type not in ["none", "local", "ols"]:
        return jsonify({
            'ontologies': [],
            'error': True,
            'errorMessage': "Invalid type"
        }), 400

    datasets_info = [{'id': dataset_id}]

    try:
        datasets_handler = DatasetsHandler(current_app, session, datasets_info=datasets_info)
        datasets_handler.handle_datasets()
    except IndexError:
        return jsonify({
            'ontologies': [],
            'error': True,
            'errorMessage': "Dataset {} not found".format(dataset_id)
        }), 400

    if not len(datasets_handler.datasets) == 1 or not datasets_handler.datasets[0].public:
        return jsonify({
            'ontologies': [],
            'error': True,
            'errorMessage': "Invalid dataset id"
        }), 400

    dataset = datasets_handler.datasets[0]

    if any([name == onto['name'] or short_name == onto['short_name'] for onto in ontologies]):
        return jsonify({
            'ontologies': [],
            'error': True,
            'errorMessage': "Name and short name must be unique"
        }), 400

    if any([dataset_id == onto['dataset_id'] for onto in ontologies]):
        return jsonify({
            'ontologies': [],
            'error': True,
            'errorMessage': "Dataset is already linked to another ontology"
        }), 400

    try:
        om.add_ontology(name, uri, short_name, dataset.id, dataset.graph_name, dataset.endpoint, remote_graph=dataset.remote_graph, type=type, label_uri=label_uri)
        ontologies = om.list_full_ontologies()
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return jsonify({
            'ontologies': [],
            'error': True,
            'errorMessage': str(e)
        }), 500

    return jsonify({
        'ontologies': ontologies,
        'error': False,
        'errorMessage': ''
    })


@admin_bp.route("/api/admin/delete_ontologies", methods=["POST"])
@api_auth
@admin_required
def delete_ontologies():
    """Delete one or more ontologies

    Returns
    -------
    json
        ontologies: list of all ontologies
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """

    data = request.get_json()
    if not data or not data.get("ontologiesIdToDelete"):
        return jsonify({
            'ontologies': [],
            'error': True,
            'errorMessage': "Missing ontologiesIdToDelete parameter"
        }), 400

    om = OntologyManager(current_app, session)

    ontologies = om.list_full_ontologies()
    onto_to_delete = [{"id": ontology['id'], "dataset_id": ontology['dataset_id']} for ontology in ontologies if ontology['id'] in data.get("ontologiesIdToDelete")]

    try:
        om.remove_ontologies(onto_to_delete)
        ontologies = om.list_full_ontologies()
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return jsonify({
            'ontologies': [],
            'error': True,
            'errorMessage': str(e)
        }), 500

    return jsonify({
        'ontologies': ontologies,
        'error': False,
        'errorMessage': ''
    })
