from askomics.libaskomics.Database import Database
from askomics.libaskomics.Params import Params
from askomics.libaskomics.SparqlQuery import SparqlQuery
from askomics.libaskomics.TriplestoreExplorer import TriplestoreExplorer


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
        self.start = dataset_info["start"] if "start" in dataset_info else None
        self.end = dataset_info["end"] if "end" in dataset_info else None
        self.ontology = dataset_info["ontology"] if "ontology" in dataset_info else False

    def set_info_from_db(self, admin=False):
        """Set the info in from the database"""
        database = Database(self.app, self.session)

        if admin and self.session['user']['admin']:
            query_params = (self.id,)
            where_query = ""
        else:
            query_params = (self.id, self.session['user']['id'])
            where_query = "AND user_id = ?"

        query = '''
        SELECT celery_id, file_id, name, graph_name, public, start, end, ontology, endpoint
        FROM datasets
        WHERE id = ?
        {}
        '''.format(where_query)

        rows = database.execute_sql_query(query, query_params)

        self.celery_id = rows[0][0]
        self.file_id = rows[0][1]
        self.name = rows[0][2]
        self.graph_name = rows[0][3]
        self.public = rows[0][4]
        self.start = rows[0][5]
        self.end = rows[0][6]
        self.ontology = rows[0][7]
        self.endpoint = rows[0][8]

    def save_in_db(self, endpoint, set_graph=False):
        """Save the dataset into the database"""
        database = Database(self.app, self.session)

        subquery = "NULL"
        args = (
            self.session["user"]["id"],
            self.celery_id,
            self.file_id,
            self.name,
            self.public,
            0,
            endpoint
        )

        if set_graph:
            subquery = "?"
            args = (
                self.session["user"]["id"],
                self.celery_id,
                self.file_id,
                self.name,
                self.graph_name,
                self.public,
                0,
                endpoint
            )

        query = '''
        INSERT INTO datasets VALUES(
            NULL,
            ?,
            ?,
            ?,
            ?,
            {},
            ?,
            "queued",
            strftime('%s', 'now'),
            NULL,
            ?,
            NULL,
            NULL,
            NULL,
            0,
            ?
        )
        '''.format(subquery)

        self.id = database.execute_sql_query(query, args, get_id=True)

    def toggle_public(self, new_status, admin=False):
        """Change public status of a dataset (triplestore and db)

        Parameters
        ----------
        new_status : bool
            True if public
        """
        # Update in TS
        query = SparqlQuery(self.app, self.session)
        tse = TriplestoreExplorer(self.app, self.session)
        string_status = "true" if new_status else "false"
        query.toggle_public(self.graph_name, string_status)

        if admin and self.session['user']['admin']:
            query_params = (new_status, self.id)
            where_query = ""
        else:
            query_params = (new_status, self.id, self.session["user"]["id"])
            where_query = "AND user_id = ?"

        # Update in DB
        database = Database(self.app, self.session)
        query = '''
        UPDATE datasets SET
        public=?
        WHERE id = ?
        {}
        '''.format(where_query)

        database.execute_sql_query(query, query_params)

        # Uncache abstraction
        tse.uncache_abstraction()

    def update_celery(self, celery_id, admin=False):
        """Update celery id of dataset in database

        Parameters
        ----------
        celery_id : string
            DescriThe celery idption
        """

        if admin and self.session['user']['admin']:
            query_params = (celery_id, self.id)
            where_query = ""
        else:
            query_params = (celery_id, self.id, self.session['user']['id'])
            where_query = "AND user_id = ? "
        database = Database(self.app, self.session)

        query = '''
        UPDATE datasets SET
        celery_id=?
        WHERE id = ?
        {}
        '''.format(where_query)

        database.execute_sql_query(query, query_params)

    def update_in_db(self, status, update_celery=False, update_date=False, update_graph=False, error=False, error_message=None, ntriples=0, traceback=None):
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
        update_date_substr = "start=strftime('%s', 'now')," if update_date else ""
        update_graph_substr = "graph_name=?," if update_graph else ""

        database = Database(self.app, self.session)

        query = '''
        UPDATE datasets SET
        {}
        {}
        {}
        status=?,
        end=strftime('%s', 'now'),
        ntriples=?,
        error_message=?,
        traceback=?
        WHERE user_id = ? AND id=?
        '''.format(update_celery_id_substr, update_date_substr, update_graph_substr)

        variables = [status, ntriples, message, traceback, self.session['user']['id'], self.id]

        if update_graph:
            variables.insert(0, self.graph_name)

        if update_celery:
            variables.insert(0, self.celery_id)

        database.execute_sql_query(query, tuple(variables))

    def delete_from_db(self, admin=False):
        """Delete a dataset from the database"""
        database = Database(self.app, self.session)

        if admin and self.session['user']['admin']:
            query_params = (self.id,)
            where_query = ""
        else:
            query_params = (self.id, self.session['user']['id'])
            where_query = "AND user_id = ?"

        query = '''
        DELETE FROM datasets
        WHERE id = ?
        {}
        '''.format(where_query)

        database.execute_sql_query(query, query_params)

        query = '''
        DELETE FROM ontologies
        WHERE dataset_id = ?
        '''

        database.execute_sql_query(query, (self.id,))
