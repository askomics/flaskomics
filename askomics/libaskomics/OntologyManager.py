from askomics.libaskomics.Database import Database
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
        SELECT id, name, uri, full_name, type
        FROM ontologies
        '''

        rows = database.execute_sql_query(query)

        ontologies = []
        for row in rows:
            prefix = {
                'id': row[0],
                'name': row[1],
                'uri': row[2],
                'full_name': row[3],
                'type': row[4]
            }
            ontologies.append(prefix)

        return ontologies

    def get_ontology(self, ontology_name):
        """Get a specific ontology based on name

        Returns
        -------
        dict
            ontology
        """

        database = Database(self.app, self.session)

        query = '''
        SELECT id, name, uri, full_name, type
        FROM ontologies
        WHERE name = ?
        '''

        rows = database.execute_sql_query(query, (ontology_name,))

        if not rows:
            return None

        ontology = rows[0]
        return {
                'id': ontology[0],
                'name': ontology[1],
                'uri': ontology[2],
                'full_name': ontology[3],
                'type': ontology[4]
            }

    def add_ontology(self, name, uri, full_name, type="local"):
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

        database.execute_sql_query(query, (name, uri, full_name, type,))

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
