from askomics.libaskomics.Database import Database
from askomics.libaskomics.Dataset import Dataset
from askomics.libaskomics.Params import Params
from askomics.libaskomics.Utils import Utils
from askomics.libaskomics.SparqlQueryLauncher import SparqlQueryLauncher
from askomics.libaskomics.TriplestoreExplorer import TriplestoreExplorer


class DatasetsHandler(Params):
    """Summary

    Attributes
    ----------
    datasets : list
        Description
    datasets_info : TYPE
        Description
    """

    def __init__(self, app, session, datasets_info=[]):
        """init

        Parameters
        ----------
        app : Flask
            Flask app
        session :
            AskOmics session
        datasets_info : list, optional
            Dataset info
        """
        Params.__init__(self, app, session)
        self.datasets_info = datasets_info
        self.datasets = []

    def handle_datasets(self, admin=False):
        """Handle datasets"""
        for info in self.datasets_info:
            dataset = Dataset(self.app, self.session, dataset_info=info)
            dataset.set_info_from_db(admin=admin)
            self.datasets.append(dataset)

    def get_datasets(self):
        """Get info about the datasets

        Returns
        -------
        list of dict
            Datasets informations
        """
        database = Database(self.app, self.session)

        query = '''
        SELECT id, name, public, status, start, end, ntriples, error_message, traceback, percent
        FROM datasets
        WHERE user_id = ?
        '''

        rows = database.execute_sql_query(query, (self.session['user']['id'], ))

        datasets = []
        for row in rows:

            exec_time = 0
            if row[5] is not None and row[4] is not None:
                exec_time = row[5] - row[4]

            dataset = {
                'id': row[0],
                'name': row[1],
                'public': True if int(row[2] == 1) else False,
                'status': row[3],
                'start': row[4],
                'end': row[5],
                'exec_time': exec_time,
                'ntriples': row[6],
                'error_message': row[7],
                'traceback': row[8],
                'percent': row[9]
            }
            datasets.append(dataset)

        return datasets

    def get_all_datasets(self):
        """Get info about the datasets

        Returns
        -------
        list of dict
            Datasets informations
        """

        if not self.session['user']['admin']:
            return []

        database = Database(self.app, self.session)

        query = '''
        SELECT datasets.id, datasets.name, datasets.public, datasets.status, datasets.start, datasets.end, datasets.ntriples, datasets.error_message, datasets.traceback, datasets.percent, users.username
        FROM datasets
        INNER JOIN users ON datasets.user_id=users.user_id
        '''

        rows = database.execute_sql_query(query, ())

        datasets = []
        for row in rows:

            exec_time = 0
            if row[5] is not None and row[4] is not None:
                exec_time = row[5] - row[4]

            dataset = {
                'id': row[0],
                'name': row[1],
                'public': True if int(row[2] == 1) else False,
                'status': row[3],
                'start': row[4],
                'end': row[5],
                'exec_time': exec_time,
                'ntriples': row[6],
                'error_message': row[7],
                'traceback': row[8],
                'percent': row[9],
                'user': row[10]
            }
            datasets.append(dataset)

        return datasets

    def update_status_in_db(self, status, admin=False):
        """Update the status of a datasets in the database

        Parameters
        ----------
        status : string
            The new status (started, success or deleting)

        Returns
        -------
        list
            Remaining datasets
        """
        database = Database(self.app, self.session)

        where_str = '(' + ' OR '.join(['id = ?'] * len(self.datasets)) + ')'
        datasets_id = [dataset.id for dataset in self.datasets]

        if admin:
            query_params = (status,)  + tuple(datasets_id)
            query = '''
            UPDATE datasets SET
            status=?
            WHERE {}
            '''.format(where_str)
        else:
            query_params = (status, self.session['user']['id']) + tuple(datasets_id)
            query = '''
            UPDATE datasets SET
            status=?
            WHERE user_id=?
            AND {}
            '''.format(where_str)

        database.execute_sql_query(query, query_params)

        return self.get_datasets()

    def delete_datasets(self, admin=False):
        """delete the datasets from the database and the triplestore"""
        sparql = SparqlQueryLauncher(self.app, self.session)
        tse = TriplestoreExplorer(self.app, self.session)

        for dataset in self.datasets:
            # Delete from triplestore
            if dataset.graph_name:
                Utils.redo_if_failure(self.log, 3, 1, sparql.drop_dataset, dataset.graph_name)
            # Delete from db
            dataset.delete_from_db(admin=admin)

            # Uncache abstraction
            tse.uncache_abstraction(public=dataset.public)
