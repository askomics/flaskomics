from askomics.libaskomics.Database import Database
from askomics.libaskomics.Params import Params


class FilesUtils(Params):
    """Contain methods usefull in FilesHandler and ResultsdHandler"""

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

    def get_size_occupied_by_user(self):
        """Get disk size occuped by file user (uploaded files and results)

        Returns
        -------
        int
            size un bytes
        """
        database = Database(self.app, self.session)

        query = '''
        SELECT SUM(size)
        FROM (
            SELECT size
            FROM results
            WHERE user_id = ?
            UNION ALL
            SELECT size
            FROM files
            WHERE user_id = ?
        )
        '''

        result = database.execute_sql_query(query, (self.session["user"]["id"], self.session["user"]["id"]))

        return 0 if result[0][0] is None else result[0][0]
