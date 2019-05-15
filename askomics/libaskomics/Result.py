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

    def __init__(self, app, session, result_info):
        """init object

        Parameters
        ----------
        app : Flask
            flask app
        session :
            AskOmics session, contain the user
        result_info : dict
            Result file info
        """
        Params.__init__(self, app, session)

        self.result_path = "{}/{}_{}/results".format(
            self.settings.get("askomics", "data_directory"),
            self.session['user']['id'],
            self.session['user']['username']
        )

        if "id" in result_info:
            self.id = result_info["id"]
            self.set_info_from_db_with_id()
        else:
            self.graph_state = result_info["graph_state"] if "graph_state" in result_info else None
            self.celery_id = result_info["celery_id"] if "celery_id" in result_info else None
            file_name = result_info["file_name"] if "file_name" in result_info else Utils.get_random_string(10)
            self.file_path = "{}/{}".format(self.result_path, file_name)

    def set_info_from_db_with_id(self):
        """Set result info from the db"""
        database = Database(self.app, self.session)

        query = '''
        SELECT celery_id, path, graph_state
        FROM results
        WHERE user_id = ? AND id = ?
        '''

        rows = database.execute_sql_query(query, (self.session["user"]["id"], self.id))

        self.celery_id = rows[0][0]
        self.file_path = rows[0][1]
        self.graph_state = json.loads(rows[0][2])

    def get_file_preview(self):
        """Get a preview of the results file

        Returns
        -------
        list, list
            headers and preview
        """
        with open(self.file_path) as file:
            spamreader = csv.reader(file, delimiter='\t')
            first = True
            preview_limit = self.settings.getint("triplestore", "preview_limit")
            row_number = 0
            headers = []
            data = []
            for row in spamreader:
                # header
                if first:
                    headers = row
                    first = False
                    continue

                # rows
                row_dict = {}
                for i in range(len(row)):
                    row_dict[headers[i]] = row[i]
                data.append(row_dict)
                row_number += 1
                if row_number >= preview_limit:
                    break

            return headers, data

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
            json.dumps(self.graph_state),
        ), get_id=True)

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
