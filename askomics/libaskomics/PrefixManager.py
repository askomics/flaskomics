from askomics.libaskomics.Database import Database
from askomics.libaskomics.Params import Params

import rdflib
import json


class PrefixManager(Params):
    """Manage sparql prefixes

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
        self.namespace_data = self.settings.get('triplestore', 'namespace_data')
        self.namespace_internal = self.settings.get('triplestore', 'namespace_internal')

        self.prefix = {
            ':': self.settings.get('triplestore', 'namespace_data'),
            'askomics:': self.settings.get('triplestore', 'namespace_internal'),
            'prov:': 'http://www.w3.org/ns/prov#',
            'dc:': 'http://purl.org/dc/elements/1.1/',
            'faldo:': "http://biohackathon.org/resource/faldo/",
            'rdf:': str(rdflib.RDF),
            'rdfs:': str(rdflib.RDFS),
            'owl:': str(rdflib.OWL),
            'xsd:': str(rdflib.XSD)
        }

    def get_prefix(self):
        """Get all prefixes

        Returns
        -------
        str
            prefixes
        """
        prefix_string = ''
        sorted_keys = sorted(self.prefix)  # We sort because python3.5 don't keep the dict order and it fail the unittest
        for prefix in sorted_keys:
            prefix_string += 'PREFIX {} <{}>\n'.format(prefix, self.prefix[prefix])

        return prefix_string

    def get_namespace(self, prefix):
        """Get a namespace from a prefix

        Parameters
        ----------
        prefix : string
            prefix

        Returns
        -------
        string
            The corresponding namespace
        """
        json_prefix_file = "askomics/libaskomics/prefix.cc.json"
        with open(json_prefix_file) as json_file:
            content = json_file.read()
        prefix_cc = json.loads(content)

        try:
            return prefix_cc[prefix]
        except Exception:
            prefixes = self.get_custom_prefixes(prefix)
            if prefixes:
                return prefixes[0]["namespace"]
            return ""

    def get_custom_prefixes(self, prefix=None):
        """Get custom (admin-defined) prefixes

        Returns
        -------
        list of dict
            Prefixes information
        """
        database = Database(self.app, self.session)

        query_args = ()
        subquery = ""

        if prefix:
            query_args = (prefix, )
            subquery = "WHERE prefix = ?"

        query = '''
        SELECT id, prefix, namespace
        FROM prefixes
        {}
        '''.format(subquery)

        rows = database.execute_sql_query(query, query_args)

        prefixes = []
        for row in rows:
            prefix = {
                'id': row[0],
                'prefix': row[1],
                'namespace': row[2],
            }
            prefixes.append(prefix)

        return prefixes

    def add_custom_prefix(self, prefix, namespace):
        """Create a new custom (admin-defined) prefixes

        Returns
        -------
        list of dict
            Prefixes information
        """
        database = Database(self.app, self.session)

        query = '''
        INSERT INTO prefixes VALUES(
            NULL,
            ?,
            ?
        )
        '''

        database.execute_sql_query(query, (prefix, namespace,))

    def remove_custom_prefixes(self, prefixes_id):
        """Create a new custom (admin-defined) prefixes

        Returns
        -------
        list of dict
            Prefixes information
        """
        database = Database(self.app, self.session)

        query = '''
        DELETE FROM prefixes
        WHERE id = ?
        '''

        for prefix_id in prefixes_id:
            database.execute_sql_query(query, (prefix_id,))
