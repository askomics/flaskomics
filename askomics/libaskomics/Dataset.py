from askomics.libaskomics.Params import Params
from askomics.libaskomics.Database import Database

class Dataset(Params):

    def __init__(self, app, session, dataset_info={}):
        Params.__init__(self, app, session)

        self.id = dataset_info["id"] if "id" in dataset_info else None
        self.celery_id = dataset_info["celery_id"] if "celery_id" in dataset_info else None
        self.file_id = dataset_info["file_id"] if "file_id" in dataset_info else None
        self.name = dataset_info["name"] if "name" in dataset_info else None

    def save_in_db(self):

        database = Database(self.app, self.session)

        query = '''
        INSERT INTO datasets VALUES(
            NULL,
            ?,
            ?,
            ?,
            ?,
            "started",
            strftime('%s', 'now'),
            NULL,
            ?,
            NULL
        )
        '''

        self.id = database.execute_sql_query(query, (
            self.session["user"]["id"],
            self.celery_id,
            self.file_id,
            self.name,
            0
        ), get_id=True)

    def update_in_db(self, error=False, error_message=None):

        status = "failure" if error else "success"
        message = error_message if error else ""

        database = Database(self.app, self.session)

        query = '''
        UPDATE datasets SET
        status=?,
        end=strftime('%s', 'now'),
        ntriples=?,
        error_message=?
        WHERE id=?
        '''

        database.execute_sql_query(query, (status, 0, message, self.id))
