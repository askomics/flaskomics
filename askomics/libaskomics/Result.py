import os
import csv
import json
import time

from bioblend import galaxy

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

    def __init__(self, app, session, result_info, force_no_db=False):
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

        if "user" in self.session:
            self.result_path = "{}/{}_{}/results".format(
                self.settings.get("askomics", "data_directory"),
                self.session['user']['id'],
                self.session['user']['username']
            )

        if "id" in result_info and not force_no_db:
            self.id = result_info["id"]
            self.set_info_from_db_with_id()
        else:
            self.id = result_info["id"] if "id" in result_info else None
            self.graph_state = result_info["graph_state"] if "graph_state" in result_info else None
            self.celery_id = result_info["celery_id"] if "celery_id" in result_info else None
            self.file_name = result_info["file_name"] if "file_name" in result_info else Utils.get_random_string(10)
            self.file_path = "{}/{}".format(self.result_path, self.file_name)
            self.start = None
            self.end = None
            self.nrows = 0

    def clean_node(self, node):
        """Clean a node by removing coordinates and other stuff

        Parameters
        ----------
        node : dict
            A graph node

        Returns
        -------
        dict
            Cleaned node
        """
        node.pop("__indexColor")
        node.pop("index")
        node.pop("x")
        node.pop("y")
        node.pop("vx")
        node.pop("vy")

        return node

    def clean_link(self, link):
        """Clean a link by removing coordinates and other stuff

        Parameters
        ----------
        link : dict
            A graph link

        Returns
        -------
        dict
            Cleaned link
        """
        link.pop("__indexColor")
        link.pop("__controlPoints")
        link.pop("index")

        # link["source"] = self.clean_node(link["source"])
        # link["target"] = self.clean_node(link["target"])

        link["source"] = link["source"]["id"]
        link["target"] = link["target"]["id"]

        return link

    def format_graph_state(self, d3_graph_state):
        """Format Graph state

        Remove coordinates and other things

        Parameters
        ----------
        d3_graph_state : dict
            The d3 graph state

        Returns
        -------
        dict
            formatted graph state
        """
        new_nodes = []
        new_links = []

        for node in d3_graph_state["nodes"]:

            if node["suggested"]:
                continue

            new_node = self.clean_node(node)
            new_nodes.append(new_node)

        for link in d3_graph_state["links"]:

            if link["suggested"]:
                continue

            new_link = self.clean_link(link)
            new_links.append(new_link)

        return {
            "nodes": new_nodes,
            "links": new_links,
            "attr": d3_graph_state["attr"]
        }

    def get_file_name(self):
        """Get file name

        Returns
        -------
        str
            file name
        """
        return self.file_name

    def get_dir_path(self):
        """Get directory path

        Returns
        -------
        str
            directory path
        """
        return self.result_path

    def get_graph_state(self, formated=False):
        """Get get_graph_state

        Returns
        -------
        dict
            graph state
        """
        if formated:
            return self.format_graph_state(self.graph_state)
        return self.graph_state

    def set_celery_id(self, celery_id):
        """Set celery id

        Parameters
        ----------
        celery_id : string
            The celery id
        """
        self.celery_id = celery_id

    def set_info_from_db_with_id(self):
        """Set result info from the db"""
        database = Database(self.app, self.session)

        if "user" in self.session:
            query = '''
            SELECT celery_id, path, graph_state, start, end, nrows
            FROM results
            WHERE (user_id = ? OR public = ?) AND id = ?
            '''

            rows = database.execute_sql_query(query, (self.session["user"]["id"], True, self.id))

        else:
            query = '''
            SELECT celery_id, path, graph_state, start, end, nrows
            FROM results
            WHERE public = ? AND id = ?
            '''

            rows = database.execute_sql_query(query, (True, self.id))

        self.celery_id = rows[0][0] if rows[0][0] else ''
        self.file_path = rows[0][1] if rows[0][1] else ''
        self.file_name = os.path.basename(self.file_path)
        self.graph_state = json.loads(rows[0][2])
        self.start = rows[0][3]
        self.end = rows[0][4]
        self.nrows = rows[0][5]

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
                    self.nrows += 1
                    for header, value in i.items():
                        row.append(value)
                    writer.writerow(row)

    def save_in_db(self):
        """Save results file info into the database"""
        database = Database(self.app, self.session)

        self.start = int(time.time())

        query = '''
        INSERT INTO results VALUES(
            NULL,
            ?,
            ?,
            "queued",
            NULL,
            ?,
            NULL,
            ?,
            NULL,
            NULL,
            ?,
            ?
        )
        '''

        self.id = database.execute_sql_query(query, (
            self.session["user"]["id"],
            self.celery_id,
            self.start,
            json.dumps(self.graph_state),
            False,
            "Query"  # FIXME: use id here
        ), get_id=True)

        return self.id

    def update_public_status(self, public):
        """Change public status

        Parameters
        ----------
        public : bool
            New public status
        """
        database = Database(self.app, self.session)

        query = '''
        UPDATE results SET
        public=?
        WHERE user_id=? AND id=?
        '''

        database.execute_sql_query(query, (
            public,
            self.session["user"]["id"],
            self.id
        ))

    def update_db_status(self, status, update_celery=False, error=False, error_message=None):
        """Update status of results in db

        Parameters
        ----------
        error : bool, optional
            True if error during integration
        error_message : bool, optional
            Error string if error is True
        """
        message = error_message if error else ""
        update_celery_substr = ""
        if update_celery:
            update_celery_substr = "celery_id=?,"

        self.end = int(time.time())

        database = Database(self.app, self.session)

        query = '''
        UPDATE results SET
        {}
        status=?,
        end=?,
        path=?,
        nrows=?,
        error=?
        WHERE user_id=? AND id=?
        '''.format(update_celery_substr)

        if update_celery:
            database.execute_sql_query(query, (
                self.celery_id,
                status,
                self.end,
                self.file_path,
                self.nrows,
                message,
                self.session["user"]["id"],
                self.id
            ))
        else:
            database.execute_sql_query(query, (
                status,
                self.end,
                self.file_path,
                self.nrows,
                message,
                self.session["user"]["id"],
                self.id
            ))

    def rollback(self):
        """Delete file"""
        self.delete_file_from_filesystem(self)

    def delete_result(self):
        """Remove results from db and filesystem"""
        self.delete_db_entry()
        self.delete_file_from_filesystem()

    def delete_db_entry(self):
        """Delete results from db"""
        database = Database(self.app, self.session)

        query = '''
        DELETE FROM results
        WHERE id = ? AND user_id = ?
        '''

        database.execute_sql_query(query, (self.id, self.session["user"]["id"]))

    def delete_file_from_filesystem(self):
        """Remove result file from filesystem"""
        try:
            os.remove(self.file_path)
        except Exception:
            self.log.debug("Impossible to delete {}".format(self.file_path))

    def publish_query(self, public):
        """Insert query id and desc in the published_query table"""
        database = Database(self.app, self.session)

        query = '''
        UPDATE results SET
        public=?
        WHERE user_id=? AND id=?
        '''

        database.execute_sql_query(query, (
            public,
            self.session["user"]["id"],
            self.id
        ))

    def update_description(self, description):
        """Change the result description"""
        database = Database(self.app, self.session)

        query = '''
        UPDATE results SET
        description=?
        WHERE user_id=? AND id=?
        '''

        database.execute_sql_query(query, (
            description,
            self.session["user"]["id"],
            self.id
        ))

    def send2galaxy(self, file2send):
        """Send files to Galaxy"""
        if file2send == "result":
            self.send_result_to_galaxy()
        elif file2send == "query":
            self.send_query_to_galaxy()

    def send_result_to_galaxy(self):
        """Send a result file to Galaxy"""
        filename = "AskOmics_result_{}.tsv".format(self.id)

        galaxy_instance = galaxy.GalaxyInstance(self.session["user"]["galaxy"]["url"], self.session["user"]["galaxy"]["apikey"])
        last_history = galaxy_instance.histories.get_most_recently_used_history()
        galaxy_instance.tools.upload_file(self.file_path, last_history['id'], file_name=filename, file_type='tabular')

    def send_query_to_galaxy(self):
        """Send the json query to a galaxy dataset"""
        galaxy_instance = galaxy.GalaxyInstance(self.session["user"]["galaxy"]["url"], self.session["user"]["galaxy"]["apikey"])
        last_history_id = galaxy_instance.histories.get_most_recently_used_history()['id']

        # Name of the json file
        name = "AskOmics_query_{}.json".format(self.id)

        # Load the file into Galaxy
        galaxy_instance.tools.paste_content(json.dumps(self.get_graph_state(formated=True)), last_history_id, file_type='json', file_name=name)
