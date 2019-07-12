"""Async task

Attributes
----------
app : Flask
    Flask app
celery : Celery
    Celery object
"""
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

    for file in files_handler.files:

        try:

            dataset_info = {
                "celery_id": self.request.id,
                "file_id": file.id,
                "name": file.name,
                "graph_name": file.file_graph,
                "public": data['public']
            }

            dataset = Dataset(app, session, dataset_info)
            dataset.save_in_db()

            if file.type == "csv/tsv":
                file.integrate(data['columns_type'], public=data['public'])
            elif file.type == "turtle":
                file.integrate(public=data["public"])
            # done
            dataset.update_in_db(ntriples=file.ntriples)
        except Exception as e:
            app.logger.error(str(e))
            dataset.update_in_db(error=True, error_message=str(e))
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
        datasets_handler.delete_datasets()

    except Exception as e:
        app.logger.error(str(e))
        return {
            'error': True,
            'errorMessage': str(e)
        }

    return {
        'error': False,
        'errorMessage': ''
    }


@celery.task(bind=True, name="query")
def query(self, session, graph_state):
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
        info = {
            "graph_state": graph_state,
            "celery_id": self.request.id
        }
        result = Result(app, session, info)

        # Save job in database database
        result.save_in_db()

        # launch query
        query_builder = SparqlQueryBuilder(app, session)
        query_launcher = SparqlQueryLauncher(app, session, get_result_query=True)
        query = query_builder.build_query_from_json(graph_state, for_editor=True)
        headers = query_builder.selects
        results = []
        if query_builder.graphs:
            headers, results = query_launcher.process_query(query)

        # write result to a file
        result.save_result_in_file(headers, results)

        # Update database status
        result.update_db_status()

    except Exception as e:
        app.logger.error(str(e))
        result.update_db_status(error=True, error_message=str(e))
        result.rollback()
        return {
            'error': True,
            'errorMessage': str(e)
        }
    return {
        'error': False,
        'errorMessage': ''
    }
