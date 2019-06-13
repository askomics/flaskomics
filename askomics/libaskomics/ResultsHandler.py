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
        SELECT id, status, path, start, end, graph_state, nrows, error, public
        FROM results
        WHERE user_id = ?
        '''

        rows = database.execute_sql_query(query, (self.session["user"]["id"], ))

        files = []

        for row in rows:
            files.append({
                'id': row[0],
                'status': row[1],
                'path': row[2],
                'start': row[3],
                'end': row[4],
                'graphState': row[5],
                'nrows': row[6],
                'errorMessage': row[7],
                'public': row[8]
            })

        return files
