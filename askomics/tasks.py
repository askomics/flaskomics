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
from askomics.libaskomics.Result import Result
from askomics.libaskomics.SparqlQueryBuilder import SparqlQueryBuilder
from askomics.libaskomics.SparqlQueryLauncher import SparqlQueryLauncher


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
    files_handler = FilesHandler(app, session, host_url=host_url)
    files_handler.handle_files([data["fileId"], ])

    public = data["public"] if session["user"]["admin"] else False

    for file in files_handler.files:

        try:

            dataset_info = {
                "celery_id": self.request.id,
                "id": data["dataset_id"],
                "file_id": file.id,
                "name": file.name,
                "graph_name": file.file_graph,
                "public": public
            }

            dataset = Dataset(app, session, dataset_info)
            dataset.update_in_db("started")

            if file.type == "csv/tsv":
                file.integrate(data['columns_type'], public=public)
            elif file.type == "gff/gff3":
                file.integrate(data["entities"], public=public)
            elif file.type == "turtle":
                file.integrate(public=public)
            elif file.type == "bed":
                file.integrate(data["entity_name"], public=public)
            # done
            dataset.update_in_db("success", ntriples=file.ntriples)
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            dataset.update_in_db("failure", error=True, error_message=str(e))
            # Rollback
            file.rollback()
            return {
                'error': True,
                'errorMessage': str(e)
            }

    return {
        'error': False,
        'errorMessage': ''
    }


@celery.task(bind=True, name='delete_datasets')
def delete_datasets(self, session, datasets_info):
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
        datasets_handler.handle_datasets()
        datasets_handler.update_status_in_db("deleting")
        datasets_handler.delete_datasets()

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

        # Save job in database database
        result.set_celery_id(self.request.id)
        result.update_db_status("started", update_celery=True)

        # launch query
        query_builder = SparqlQueryBuilder(app, session)
        query_launcher = SparqlQueryLauncher(app, session, get_result_query=True)
        query = query_builder.build_query_from_json(info["graph_state"], for_editor=False)
        headers = query_builder.selects
        results = []
        if query_builder.graphs:
            headers, results = query_launcher.process_query(query)

        # write result to a file
        file_size = result.save_result_in_file(headers, results)

        # Update database status
        result.update_db_status("success", size=file_size)

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        result.update_db_status("error", error=True, error_message=str(e))
        result.rollback()
        return {
            'error': True,
            'errorMessage': str(e)
        }
    return {
        'error': False,
        'errorMessage': ''
    }
