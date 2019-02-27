
from askomics.libaskomics.FilesHandler import FilesHandler
from askomics.libaskomics.File import File
from askomics.libaskomics.Dataset import Dataset
from askomics.libaskomics.DatasetsHandler import DatasetsHandler

from askomics.app import create_app, create_celery

app = create_app(config='config/askomics.ini')
celery = create_celery(app)

@celery.task(bind=True, name="integrate")
def integrate(self, session, data, host_url):

    files_handler = FilesHandler(app, session, host_url=host_url)
    files_handler.handle_files([data["fileId"], ])

    app.logger.debug(data)

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

            file.integrate(data['columns_type'], public=data['public'])

            # done
            dataset.update_in_db()
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
