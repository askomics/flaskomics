import requests

from askomics.libaskomics.Database import Database
from askomics.libaskomics.Dataset import Dataset
from askomics.libaskomics.Params import Params
from askomics.libaskomics.Utils import Utils
from askomics.libaskomics.SparqlQueryLauncher import SparqlQueryLauncher


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

    def handle_datasets(self):
        """Handle datasets"""
        for info in self.datasets_info:
            dataset = Dataset(self.app, self.session, dataset_info=info)
            dataset.set_info_from_db()
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
            dataset = {
                'id': row[0],
                'name': row[1],
                'public': True if int(row[2] == 1) else False,
                'status': row[3],
                'start': row[4],
                'end': row[5],
                'ntriples': row[6],
                'error_message': row[7],
                'traceback': row[8],
                'percent': row[9]
            }
            datasets.append(dataset)

        return datasets

    def update_status_in_db(self, status):
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

        query = '''
        UPDATE datasets SET
        status=?
        WHERE user_id=?
        AND {}
        '''.format(where_str)

        database.execute_sql_query(query, (status, self.session['user']['id']) + tuple(datasets_id))

        return self.get_datasets()

    def delete_datasets_in_db(self):
        """Delete datasets of the database"""
        database = Database(self.app, self.session)

        where_str = '(' + ' OR '.join(['id = ?'] * len(self.datasets)) + ')'
        datasets_id = [dataset.id for dataset in self.datasets]

        query = '''
        DELETE FROM datasets
        WHERE user_id=?
        AND {}
        '''.format(where_str)

        database.execute_sql_query(query, (self.session['user']['id'], ) + tuple(datasets_id))

    def delete_datasets(self):
        """delete the datasets from the database and the triplestore"""
        sparql = SparqlQueryLauncher(self.app, self.session)
        for dataset in self.datasets:
            # Delete from triplestore
            Utils.redo_if_failure(self.log, 3, 1, sparql.drop_dataset, dataset.graph_name)
            # Delete from db
            dataset.delete_from_db()
