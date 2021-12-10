import requests

from collections import defaultdict
from urllib.parse import quote_plus


from askomics.libaskomics.Database import Database
from askomics.libaskomics.SparqlQuery import SparqlQuery
from askomics.libaskomics.Params import Params


class OntologyManager(Params):
    """Manage ontologies

    Attributes
    ----------
    namespace_internal : str
        askomics namespace, from config file
    namespace_data : str
        askomics prefix, from config file
    prefix : dict
        dict of all prefixes
    """

    def __init__(self, app, session):
        """init

        Parameters
        ----------
        app : Flask
            Flask app
        session :
            AskOmics session
        """
        Params.__init__(self, app, session)

    def list_ontologies(self):
        """Get all ontologies

        Returns
        -------
        list
            ontologies
        """

        database = Database(self.app, self.session)

        query = '''
        SELECT id, name, uri, short_name, type
        FROM ontologies
        '''

        rows = database.execute_sql_query(query)

        ontologies = []
        for row in rows:
            prefix = {
                'id': row[0],
                'name': row[1],
                'uri': row[2],
                'short_name': row[3],
                'type': row[4]
            }
            ontologies.append(prefix)

        return ontologies

    def list_full_ontologies(self):
        """Get all ontologies for admin

        Returns
        -------
        list
            ontologies
        """

        database = Database(self.app, self.session)

        query = '''
        SELECT ontologies.id, ontologies.name, ontologies.uri, ontologies.short_name, ontologies.type, datasets.id, datasets.name, ontologies.graph
        FROM ontologies
        INNER JOIN datasets ON datasets.id=ontologies.dataset_id
        '''

        rows = database.execute_sql_query(query)

        ontologies = []
        for row in rows:
            prefix = {
                'id': row[0],
                'name': row[1],
                'uri': row[2],
                'short_name': row[3],
                'type': row[4],
                'dataset_id': row[5],
                'dataset_name': row[6],
                'graph': row[7]
            }
            ontologies.append(prefix)

        return ontologies

    def get_ontology(self, short_name):
        """Get a specific ontology based on short name

        Returns
        -------
        dict
            ontology
        """

        database = Database(self.app, self.session)

        query = '''
        SELECT id, name, uri, short_name, type, dataset_id, graph
        FROM ontologies
        WHERE short_name = ?
        '''

        rows = database.execute_sql_query(query, (short_name,))

        if not rows:
            return None

        ontology = rows[0]
        return {
            'id': ontology[0],
            'name': ontology[1],
            'uri': ontology[2],
            'short_name': ontology[3],
            'type': ontology[4],
            'dataset_id': ontology[5],
            'graph': ontology[6]
        }

    def add_ontology(self, name, uri, short_name, dataset_id, graph, type="local"):
        """Create a new ontology

        Returns
        -------
        list of dict
            Prefixes information
        """
        database = Database(self.app, self.session)

        query = '''
        INSERT INTO ontologies VALUES(
            NULL,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?
        )
        '''

        database.execute_sql_query(query, (name, uri, short_name, type, dataset_id, graph))

        query = '''
        UPDATE datasets SET
        ontology=1
        WHERE id=?
        '''

        database.execute_sql_query(query, (dataset_id,))

    def remove_ontologies(self, ontology_ids):
        """Remove ontologies

        Returns
        -------
        None
        """
        # Make sure we only remove the 'ontology' tag to datasets without any ontologies
        ontologies = self.list_full_ontologies()
        datasets = defaultdict(set)
        datasets_to_modify = set()
        ontos_to_delete = [ontology['id'] for ontology in ontology_ids]

        for onto in ontologies:
            datasets[onto['dataset_id']].add(onto['id'])

        for key, values in datasets.items():
            if values.issubset(ontos_to_delete):
                datasets_to_modify.add(key)

        database = Database(self.app, self.session)

        query = '''
        DELETE FROM ontologies
        WHERE id = ?
        '''

        dataset_query = '''
        UPDATE datasets SET
        ontology=0
        WHERE id=?
        '''

        for ontology in ontology_ids:
            database.execute_sql_query(query, (ontology['id'],))
            if ontology['dataset_id'] in datasets_to_modify:
                database.execute_sql_query(dataset_query, (ontology['dataset_id'],))

    def test_ols_ontology(self, shortname):
        base_url = "https://www.ebi.ac.uk/ols/api/ontologies/" + quote_plus(shortname.lower())

        r = requests.get(base_url)
        return r.status_code == 200

    def autocomplete(self, ontology_uri, ontology_type, query_term, onto_short_name, onto_graph):
        """Search in ontology

        Returns
        -------
        list of dict
            Results
        """
        if ontology_type == "local":
            query = SparqlQuery(self.app, self.session, get_graphs=False)
            # TODO: Actually store the graph in the ontology to quicken search
            query.set_graphs([onto_graph])
            return query.autocomplete_local_ontology(ontology_uri, query_term)
        elif ontology_type == "ols":
            base_url = "https://www.ebi.ac.uk/ols/api/suggest"
            arguments = {
                "q": query_term,
                "ontology": quote_plus(onto_short_name.lower()),
                "rows": 5
            }

            r = requests.get(base_url, params=arguments)

            data = []

            if not r.status_code == 200:
                return data

            res = r.json()
            if res['response']['docs']:
                data = [term['autosuggest'] for term in res['response']['docs']]

            return data
