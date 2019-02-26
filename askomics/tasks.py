
from askomics.libaskomics.FilesHandler import FilesHandler
from askomics.libaskomics.File import File

from askomics.app import create_app, create_celery

app = create_app(config='config/askomics.ini')
celery = create_celery(app)

@celery.task(bind=True, name="integrate")
def integrate(self, session, data, host_url):

    files_handler = FilesHandler(app, session, host_url=host_url)
    files_handler.handle_files([data["fileId"], ])

    for file in files_handler.files:

        try:
            file.integrate(data['columns_type'])
        except Exception as e:
            app.logger.error(str(e))
            # Rollback
            file.rollback()
            return 'error'
            return {
                'error': True,
                'errorMessage': str(e)
            }


    return {
        'error': False,
        'errorMessage': ''
    }
