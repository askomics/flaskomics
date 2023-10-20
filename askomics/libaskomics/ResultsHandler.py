from askomics.libaskomics.Database import Database
from askomics.libaskomics.Params import Params
from askomics.libaskomics.Result import Result


class ResultsHandler(Params):
    """Handle results"""

    def __init__(self, app, session):
        """init

        Parameters
        ----------
        app : Flask
            flask app
        session :
            AskOmics session, contain the user
        """
        Params.__init__(self, app, session)

    def delete_results(self, files_id, admin=False):
        """Delete files

        Parameters
        ----------
        files_id : list
            list of file id to delete

        Returns
        -------
        list
            list of remaining files
        """
        for file_id in files_id:
            result = Result(self.app, self.session, {"id": file_id}, owner=True, admin=admin)
            if result.celery_id:
                self.app.celery.control.revoke(result.celery_id, terminate=True)
            if result.id:
                result.delete_result(admin=admin)
        if admin:
            return self.get_admin_queries()

        return self.get_files_info()

    def get_files_info(self):
        """Get files info of the user

        Returns
        -------
        list
            list of file info
        """
        database = Database(self.app, self.session)

        query = '''
        SELECT id, status, path, start, end, graph_state, nrows, error, public, template, description, size, sparql_query, traceback, has_form_attr, form
        FROM results
        WHERE user_id = ?
        '''

        rows = database.execute_sql_query(query, (self.session["user"]["id"], ))

        files = []

        for row in rows:

            exec_time = 0
            if row[4] is not None and row[3] is not None:
                exec_time = row[4] - row[3]

            files.append({
                'id': row[0],
                'status': row[1],
                'path': row[2],
                'start': row[3],
                'end': row[4],
                'execTime': exec_time,
                'graphState': row[5],
                'nrows': row[6],
                'errorMessage': row[7],
                'public': row[8],
                'template': row[9],
                'description': row[10],
                'size': row[11],
                'sparqlQuery': row[12],
                'traceback': row[13],
                'has_form_attr': row[14],
                'form': row[15]
            })

        return files

    def get_public_queries(self):
        """Get id and description of published queries

        Returns
        -------
        List
            List of published queries (id and description)
        """
        database = Database(self.app, self.session)

        where_substring = "WHERE template = ? and public = ?"
        sql_var = (True, True,)
        if "user" in self.session:
            where_substring = "WHERE template = ? and (public = ? or user_id = ?)"
            sql_var = (True, True, self.session["user"]["id"])

        query = '''
        SELECT id, description, public
        FROM results
        {}
        '''.format(where_substring)

        rows = database.execute_sql_query(query, sql_var)

        queries = []

        for row in rows:
            queries.append({
                "id": row[0],
                "description": row[1],
                "public": row[2]
            })

        return queries

    def get_public_form_queries(self):
        """Get id and description of published form queries

        Returns
        -------
        List
            List of published form queries (id and description)
        """
        database = Database(self.app, self.session)

        where_substring = "WHERE form = ? and public = ?"
        sql_var = (True, True,)
        if "user" in self.session:
            where_substring = "WHERE form = ? and (public = ? or user_id = ?)"
            sql_var = (True, True, self.session["user"]["id"])

        query = '''
        SELECT id, description, public
        FROM results
        {}
        '''.format(where_substring)

        rows = database.execute_sql_query(query, sql_var)

        queries = []

        for row in rows:
            queries.append({
                "id": row[0],
                "description": row[1],
                "public": row[2]
            })

        return queries

    def get_admin_queries(self):
        """Get id description, and owner of all queries

        Returns
        -------
        List
            List of all queries (id and description)
        """

        database = Database(self.app, self.session)

        query = '''
        SELECT results.id, results.status, results.start, results.end, results.nrows, results.public, results.description, results.size, users.username
        FROM results
        LEFT JOIN users ON results.user_id=users.user_id
        '''

        rows = database.execute_sql_query(query)

        queries = []

        for row in rows:

            exec_time = 0
            if row[3] is not None and row[2] is not None:
                exec_time = row[3] - row[2]

            queries.append({
                'id': row[0],
                'status': row[1],
                'start': row[2],
                'end': row[3],
                'execTime': exec_time,
                'nrows': row[4],
                'public': row[5],
                'description': row[6],
                'size': row[7],
                'user': row[8] if row[8] else "anonymous"
            })
        return queries

    def delete_older_results(self, delta, deltatype, user_id, status=None):
        """Delete results older than a specific delta for a specific user_id

        Returns
        -------
        List
           None
        """

        database = Database(self.app, self.session)
        date_str = '"%s", "now", "-{} {}"'.format(delta, deltatype)
        status_substr = ""
        arg_tuple = (user_id)

        if status:
            status_substr = "AND status = ?"
            arg_tuple = (user_id, status)

        query = '''
        DELETE FROM results
        WHERE user_id = ? AND start <= strftime({}) {}
        '''.format(date_str, status_substr)

        database.execute_sql_query(query, arg_tuple)
