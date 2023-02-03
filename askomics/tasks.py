"""Async task

Attributes
----------
app : Flask
    Flask app
celery : Celery
    Celery object
"""
import sys
import traceback

from askomics.app import create_app, create_celery
from askomics.libaskomics.Dataset import Dataset
from askomics.libaskomics.DatasetsHandler import DatasetsHandler
from askomics.libaskomics.FilesHandler import FilesHandler
from askomics.libaskomics.LocalAuth import LocalAuth
from askomics.libaskomics.Result import Result
from askomics.libaskomics.ResultsHandler import ResultsHandler
from askomics.libaskomics.SparqlQuery import SparqlQuery
from askomics.libaskomics.SparqlQueryLauncher import SparqlQueryLauncher

from celery.schedules import crontab

app = create_app(config='config/askomics.ini')
celery = create_celery(app)


@celery.task(bind=True, name="integrate")
def integrate(self, session, data, host_url):
    """Integrate a file into the triplestore

    Parameters
    ----------
    session : dict
        AskOmics session
    data : dict
        fileId: file to integrate
        public: integrate as public or private data
    host_url : string
        AskOmics host url

    Returns
    -------
    dict
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    files_handler = FilesHandler(app, session, host_url=host_url, external_endpoint=data["externalEndpoint"], custom_uri=data["customUri"], external_graph=data['externalGraph'])
    files_handler.handle_files([data["fileId"], ])

    public = (data.get("public", False) if session["user"]["admin"] else False) or app.iniconfig.getboolean("askomics", "single_tenant", fallback=False)

    for file in files_handler.files:

        try:

            dataset_info = {
                "celery_id": self.request.id,
                "id": data["dataset_id"],
                "file_id": file.id,
                "name": file.human_name,
                "graph_name": file.file_graph,
                "public": public
            }

            dataset = Dataset(app, session, dataset_info)
            dataset.update_in_db("started", update_date=True, update_graph=True)

            if file.type == "csv/tsv":
                file.integrate(data["dataset_id"], data.get('columns_type'), data.get('header_names'), public=public)
            elif file.type == "gff/gff3":
                file.integrate(data["dataset_id"], data.get("entities"), public=public)
            elif file.type in ('rdf/ttl', 'rdf/xml', 'rdf/nt'):
                file.integrate(public=public)
            elif file.type == "bed":
                file.integrate(data["dataset_id"], data.get("entity_name"), public=public)
            # done
            dataset.update_in_db("success", ntriples=file.ntriples)
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            trace = traceback.format_exc()
            dataset.update_in_db("failure", error=True, error_message=str(e), traceback=trace)
            # Rollback
            file.rollback()
            raise e
            return {
                'error': True,
                'errorMessage': str(e)
            }

    return {
        'error': False,
        'errorMessage': ''
    }


@celery.task(bind=True, name='delete_datasets')
def delete_datasets(self, session, datasets_info, admin=False):
    """Delete datasets from database and triplestore

    Parameters
    ----------
    session : dict
        AskOmics session
    datasets_info : list of dict
        Ids of datasets to delete

    Returns
    -------
    dict
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    try:
        datasets_handler = DatasetsHandler(app, session, datasets_info=datasets_info)
        datasets_handler.handle_datasets(admin=admin)
        datasets_handler.update_status_in_db("deleting", admin=admin)
        datasets_handler.delete_datasets(admin=admin)

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        raise e
        return {
            'error': True,
            'errorMessage': str(e)
        }

    return {
        'error': False,
        'errorMessage': ''
    }


@celery.task(bind=True, name="query")
def query(self, session, info):
    """Save the query results in filesystem and db

    Parameters
    ----------
    session : dict
        AskOmics session
    graph_state : dict
        JSON graph state

    Returns
    -------
    dict
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    try:
        info["celery_id"] = self.request.id
        result = Result(app, session, info, force_no_db=True)

        query = SparqlQuery(app, session, info["graph_state"])
        query.build_query_from_json(preview=False, for_editor=False)
        federated = query.is_federated()
        result.populate_db(query.graphs, query.endpoints)

        info["query"] = query.sparql
        info["graphs"] = query.graphs
        info["endpoints"] = query.endpoints
        info["federated"] = federated
        info["selects"] = query.selects

        # Save job in database database
        result.set_celery_id(self.request.id)
        result.update_db_status("started", update_celery=True, update_date=True)

        # launch query

        headers = info["selects"]
        results = []
        if info["graphs"] or app.iniconfig.getboolean("askomics", "single_tenant", fallback=False):
            query_launcher = SparqlQueryLauncher(app, session, get_result_query=True, federated=info["federated"], endpoints=info["endpoints"])
            headers, results = query_launcher.process_query(info["query"], isql_api=True)

        # write result to a file
        file_size = result.save_result_in_file(headers, results)

        # Update database status
        result.update_db_status("success", size=file_size)

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        trace = traceback.format_exc()
        result.update_db_status("error", error=True, error_message=str(e), traceback=trace)
        result.rollback()
        raise e
        return {
            'error': True,
            'errorMessage': str(e)
        }
    return {
        'error': False,
        'errorMessage': ''
    }


@celery.task(bind=True, name="sparql_query")
def sparql_query(self, session, info):
    """Save the sparql query results in filesystem and db

    Parameters
    ----------
    session : dict
        AskOmics session
    info : dict
        sparql query

    Returns
    -------
    dict
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    try:
        info["celery"] = self.request.id
        result = Result(app, session, info, force_no_db=True)

        # Save job in db
        result.set_celery_id(self.request.id)
        result.update_db_status("started", update_celery=True)

        query_launcher = SparqlQueryLauncher(app, session, get_result_query=True, federated=info["federated"], endpoints=info["endpoints"])
        header, data = query_launcher.process_query(info["sparql_query"], isql_api=True)

        # Write results in file
        file_size = result.save_result_in_file(header, data)

        # Update database status
        result.update_db_status("success", size=file_size)

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        trace = traceback.format_exc()
        result.update_db_status("error", error=True, error_message=str(e), traceback=trace)
        raise e
        return {
            'error': True,
            'errorMessage': str(e)
        }
    return {
        'error': False,
        'errorMessage': ''
    }


@celery.task(bind=True, name="delete_users_data")
def delete_users_data(self, session, users, delete_user):
    """Delete users directory and RDF data

    Parameters
    ----------
    session : dict
        AskOmics session
    users : list
        list of user to delete
    delete_user : boolean
        True if delete all user or juste his data

    Returns
    -------
    dict
        error: True if error, else False
        errorMessage: the error message of error, else an empty string
    """
    try:
        local_auth = LocalAuth(app, session)

        for user in users:
            local_auth.delete_user_directory(user, delete_user)
            local_auth.delete_user_rdf(user["username"])

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return {
            'error': True,
            'errorMessage': str(e)
        }
    return {
        'error': False,
        'errorMessage': ''
    }


@celery.task(bind=True, name="send_mail_new_user")
def send_mail_new_user(self, session, user):
    """Send a mail to the new user

    Parameters
    ----------
    session : dict
        AskOmics session
    user : dict
        New user
    """
    local_auth = LocalAuth(app, session)
    local_auth.send_mail_to_new_user(user)


@celery.task(bind=True, name="download_file")
def download_file(self, session, url):
    """Send a mail to the new user

    Parameters
    ----------
    session : dict
        AskOmics session
    user : dict
        New user
    """
    files = FilesHandler(app, session)
    files.download_url(url, download_file.request.id)


@celery.on_after_configure.connect
def cron_cleanup(sender, **kwargs):
    print("Cron triggered")
    sender.add_periodic_task(
#        crontab(hour=0, minute=0, day_of_week=1),
        crontab(hours='*/1'),
        cleanup_anonymous_data.s(),
    )

@celery.task(bind=True, name="cleanup_anonymous")
def cleanup_anonymous_data(self):
    print("Cleanup triggered")
    periodicity = app.iniconfig.getint('askomics', 'anonymous_query_cleanup', fallback=60)
    handler = ResultsHandler(app, {})
    handler.delete_older_results(periodicity, "0")
    # Cleanup failed jobs
    handler.delete_older_results(1, "0", "error")
