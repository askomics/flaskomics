from askomics.libaskomics.Params import Params
from askomics.libaskomics.Database import Database
from askomics.libaskomics.Dataset import Dataset
from askomics.libaskomics.SparqlQuery import SparqlQuery

class DatasetsHandler(Params):

    def __init__(self, app, session, datasets_info=[]):
        Params.__init__(self, app, session)
        self.datasets_info = datasets_info
        self.datasets = []

    def handle_datasets(self):

        for info in self.datasets_info:
            dataset = Dataset(self.app, self.session, dataset_info=info)
            dataset.set_info_from_db()
            self.datasets.append(dataset)

    def get_datasets(self):

        database = Database(self.app, self.session)


        query = '''
        SELECT id, name, public, status, start, end, error_message
        FROM datasets
        WHERE user_id = ?
        '''

        rows = database.execute_sql_query(query, (self.session['user']['id'], ))

        datasets = []
        for row in rows:
            dataset = {
                'id': row[0],
                'name': row[1],
                'public': row[2],
                'status': row[3],
                'start': row[4],
                'end': row[5],
                'error_message': row[6]
            }
            datasets.append(dataset)

        return datasets

    def update_status_in_db(self, status):

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

    def delete_datasets_in_db(self):

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

        sparql = SparqlQuery(self.app, self.session)
        for dataset in self.datasets:
            # Delete from triplestore
            sparql.drop_dataset(dataset.graph_name)
            # Delete from db
            dataset.delete_from_db()
