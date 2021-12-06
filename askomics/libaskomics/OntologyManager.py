import requests

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

    def get_ontology(self, short_name):
        """Get a specific ontology based on short name

        Returns
        -------
        dict
            ontology
        """

        database = Database(self.app, self.session)

        query = '''
        SELECT id, name, uri, short_name, type
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
            'type': ontology[4]
        }

    def add_ontology(self, name, uri, short_name, type="local"):
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
            ?
        )
        '''

        database.execute_sql_query(query, (name, uri, short_name, type,))

    def remove_ontologies(self, ontology_ids):
        """Remove ontologies

        Returns
        -------
        None
        """
        database = Database(self.app, self.session)

        query = '''
        DELETE FROM ontologies
        WHERE id = ?
        '''

        for ontology_id in ontology_ids:
            database.execute_sql_query(query, (ontology_id,))

    def autocomplete(self, ontology_uri, ontology_type, query_term, onto_short_name):
        """Search in ontology

        Returns
        -------
        list of dict
            Results
        """
        if ontology_type == "local":
            query = SparqlQuery(self.app, self.session, get_graphs=False)
            # TODO: Actually store the graph in the ontology to quicken search
            query.set_graphs_and_endpoints(entities=[ontology_uri])
            return query.autocomplete_local_ontology(ontology_uri, query_term, query.endpoints)
        elif ontology_type == "ols":
            base_url = "https://www.ebi.ac.uk/ols/api/search"
            arguments = {
                "q": query_term,
                "ontology": onto_short_name,
                "rows": 5,
                "queryFields": "label",
                "type": "class",
                "fieldList": "label"
            }

            r = requests.get(base_url, params=arguments)

            data = []

            if not r.status_code == 200:
                return data

            res = r.json()
            if res['response']['docs']:
                data = [term['label'] for term in res['response']['docs']]

            return data

        elif ontology_type == "ols":
            base_url = "https://www.ebi.ac.uk/ols/api/search"
            arguments = {
                "q": query_term,
                "ontology": onto_short_name,
                "rows": 5,
                "queryFields": "label",
                "type": "class",
                "fieldList": "label"
            }

            r = requests.get(base_url, params=arguments)

            data = []

            if not r.status_code == 200:
                return data

            res = r.json()
            if res['response']['docs']:
                data = [term['label'] for term in res['response']['docs']]

            return data
