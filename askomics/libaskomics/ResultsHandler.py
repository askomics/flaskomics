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

    def delete_results(self, files_id):
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
            result = Result(self.app, self.session, {"id": file_id})
            self.app.celery.control.revoke(result.celery_id, terminate=True)
            result.delete_result()

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
        SELECT id, status, path, start, end, graph_state, nrows, error, public, template, description, size, sparql_query, traceback
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
                'traceback': row[13]
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

        where_substring = ""
        sql_var = (True, )
        if "user" in self.session:
            where_substring = " or (template = ? and user_id = ?)"
            sql_var = (True, True, self.session["user"]["id"])

        query = '''
        SELECT id, description, public
        FROM results
        WHERE public = ?{}
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
