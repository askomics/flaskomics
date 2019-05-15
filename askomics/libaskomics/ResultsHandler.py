from askomics.libaskomics.Database import Database
from askomics.libaskomics.Params import Params


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

    def get_files_info(self):
        """Get files info of the user

        Returns
        -------
        list
            list of file info
        """
        database = Database(self.app, self.session)

        query = '''
        SELECT id, status, path, start, end, graph_state, error
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
                'errorMessage': row[6]
            })

        return files
