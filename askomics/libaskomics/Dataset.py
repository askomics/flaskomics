from askomics.libaskomics.Database import Database
from askomics.libaskomics.Params import Params
from askomics.libaskomics.SparqlQueryBuilder import SparqlQueryBuilder


class Dataset(Params):
    """Dataset

    Attributes
    ----------
    celery_id : string
        celery id
    file_id : int
        database file id
    graph_name : string
        graph name
    id : int
        database dataset id
    name : string
        dataset name
    public : bool
        Public
    """

    def __init__(self, app, session, dataset_info={}):
        """init

        Parameters
        ----------
        app : Flask
            Flask app
        session :
            AskOmics session
        dataset_info : dict, optional
            Dataset info
        """
        Params.__init__(self, app, session)

        self.id = dataset_info["id"] if "id" in dataset_info else None
        self.celery_id = dataset_info["celery_id"] if "celery_id" in dataset_info else None
        self.file_id = dataset_info["file_id"] if "file_id" in dataset_info else None
        self.name = dataset_info["name"] if "name" in dataset_info else None
        self.graph_name = dataset_info["graph_name"] if "graph_name" in dataset_info else None
        self.public = dataset_info["public"] if "public" in dataset_info else False

    def set_info_from_db(self):
        """Set the info in from the database"""
        database = Database(self.app, self.session)

        query = '''
        SELECT celery_id, file_id, name, graph_name, public
        FROM datasets
        WHERE user_id = ?
        AND id = ?
        '''

        rows = database.execute_sql_query(query, (self.session['user']['id'], self.id))

        self.celery_id = rows[0][0]
        self.file_id = rows[0][1]
        self.name = rows[0][2]
        self.graph_name = rows[0][3]
        self.public = rows[0][4]

    def save_in_db(self):
        """Save the dataset into the database"""
        database = Database(self.app, self.session)

        query = '''
        INSERT INTO datasets VALUES(
            NULL,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            "queued",
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
            self.graph_name,
            self.public,
            0
        ), get_id=True)

    def toggle_public(self, new_status):
        """Change public status of a dataset (triplestore and db)

        Parameters
        ----------
        new_status : bool
            True if public
        """
        # Update in TS
        query_builder = SparqlQueryBuilder(self.app, self.session)
        string_status = "true" if new_status else "false"
        query_builder.toggle_public(self.graph_name, string_status)

        # Update in DB
        database = Database(self.app, self.session)
        query = '''
        UPDATE datasets SET
        public=?
        WHERE user_id = ? AND id = ?
        '''
        database.execute_sql_query(query, (new_status, self.session["user"]["id"], self.id))

    def update_in_db(self, status, update_celery=False, error=False, error_message=None, ntriples=0):
        """Update the dataset when integration is done

        Parameters
        ----------
        error : bool, optional
            True if error during integration
        error_message : None, optional
            Error string if error is True
        ntriples : int, optional
            Number of triples integrated
        """
        message = error_message if error else ""
        update_celery_id_substr = "celery_id=?," if update_celery else ""

        database = Database(self.app, self.session)

        query = '''
        UPDATE datasets SET
        {}
        status=?,
        end=strftime('%s', 'now'),
        ntriples=?,
        error_message=?
        WHERE user_id = ? AND id=?
        '''.format(update_celery_id_substr)

        if update_celery:
            database.execute_sql_query(query, (self.celery_id, status, ntriples, message, self.session['user']['id'], self.id))
        else:
            database.execute_sql_query(query, (status, ntriples, message, self.session['user']['id'], self.id))

    def delete_from_db(self):
        """Delete a dataset from the database"""
        database = Database(self.app, self.session)

        query = '''
        DELETE FROM datasets
        WHERE user_id = ?
        AND id = ?
        '''

        database.execute_sql_query(query, (self.session['user']['id'], self.id))
