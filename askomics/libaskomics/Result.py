import os
import csv
import json

from askomics.libaskomics.Database import Database
from askomics.libaskomics.Params import Params
from askomics.libaskomics.Utils import Utils


class Result(Params):
    """Result represent a query result file

    Attributes
    ----------
    celery_id : str
        Celery job id
    file_name : str
        file name
    file_path : str
        file path
    graph_state : dict
        The json query graph state
    id : int
        database id
    result_path : str
        results directory path
    """

    def __init__(self, app, session, graph_state, celery_id):
        """init object

        Parameters
        ----------
        app : Flask
            flask app
        session :
            AskOmics session, contain the user
        dump_graph_state : string
            The query graph state
        celery_id : str
            celery job id
        """
        Params.__init__(self, app, session)
        self.id = None
        self.dump_graph_state = json.dumps(graph_state, ensure_ascii=False)
        self.celery_id = str(celery_id)
        self.result_path = "{}/{}_{}/results".format(
            self.settings.get("askomics", "data_directory"),
            self.session['user']['id'],
            self.session['user']['username']
        )
        self.file_name = Utils.get_random_string(10)
        self.file_path = "{}/{}".format(self.result_path, self.file_name)

    def save_result_in_file(self, headers, results):
        """Save query results in a csv file

        Parameters
        ----------
        headers : list
            List of results headers
        results : list
            Query results
        """
        with open(self.file_path, 'w') as file:
            writer = csv.writer(file, delimiter="\t")
            writer.writerow(headers)
            if len(results) > 0:
                for i in results:
                    row = []
                    for header, value in i.items():
                        row.append(value)
                    writer.writerow(row)

    def save_in_db(self):
        """Save results file info into the database"""
        database = Database(self.app, self.session)

        query = '''
        INSERT INTO results VALUES(
            NULL,
            ?,
            ?,
            "started",
            NULL,
            strftime('%s', 'now'),
            NULL,
            ?,
            NULL,
            NULL
        )
        '''

        self.id = database.execute_sql_query(query, (
            self.session["user"]["id"],
            self.celery_id,
            self.dump_graph_state,
        ), get_id=True)

        # id INTEGER PRIMARY KEY AUTOINCREMENT,
        # user_id INTEGER,
        # celery_id text,
        # status text,
        # path text,
        # start int,
        # end int,
        # graph_state text,
        # nrows int,
        # error text,

    def update_db_status(self, error=False, error_message=None):
        """Update status of results in db

        Parameters
        ----------
        error : bool, optional
            True if error during integration
        error_message : bool, optional
            Error string if error is True
        """
        status = "failure" if error else "success"
        message = error_message if error else ""

        database = Database(self.app, self.session)

        query = '''
        UPDATE results SET
        status=?,
        end=strftime('%s', 'now'),
        path=?,
        nrows=?,
        error=?
        WHERE user_id=? AND id=?
        '''

        database.execute_sql_query(query, (
            status,
            self.file_path,
            0,
            message,
            self.session["user"]["id"],
            self.id
        ))

    def rollback(self):
        """Remove result file from filesystem"""
        try:
            os.remove(self.file_path)
        except:
            self.log.debug("Impossible to delete {}".format(self.file_path))
