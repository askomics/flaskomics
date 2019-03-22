import re
import textwrap

from askomics.libaskomics.Database import Database
from askomics.libaskomics.Params import Params
from askomics.libaskomics.PrefixManager import PrefixManager


class SparqlQueryBuilder(Params):
    """Format a sparql query

    Attributes
    ----------
    private_graphs : list
        all user private graph
    public_graphs : list
        all public graph
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

        self.public_graphs = []
        self.private_graphs = []

        self.set_graphs_from_db()

    def set_graphs_from_db(self):
        """Get named graph from the db"""
        database = Database(self.app, self.session)
        query = '''
        SELECT graph_name, user_id, public
        FROM datasets
        WHERE (user_id = ? OR public = ? )
        '''
        rows = database.execute_sql_query(query, (self.session['user']['id'], True))

        for row in rows:
            if row[2]:
                self.public_graphs.append(row[0])
            else:
                self.private_graphs.append(row[0])

    def get_froms(self, public=True, private=True):
        """Get FROM clauses

        Parameters
        ----------
        public : bool, optional
            if True, use all public graph
        private : bool, optional
            if True, use all private graph

        Returns
        -------
        str
            FROM clauses
        """
        from_string = ''
        if public:
            for public_graph in self.public_graphs:
                from_string += '\nFROM <{}> # public'.format(public_graph)

        if private:
            for private_graph in self.private_graphs:
                from_string += '\nFROM <{}>'.format(private_graph)

        return from_string

    def get_default_query(self):
        """Get the default query

        Returns
        -------
        str
            the default query
        """
        query = textwrap.dedent(
            '''
            SELECT DISTINCT ?s ?p ?o
            WHERE {
                ?s ?p ?o
            }
            LIMIT 25
            '''
        )

        return query

    def prefix_query(self, query):
        """Add prefix and dedent a sparql query string

        Parameters
        ----------
        query : string
            The sparql query

        Returns
        -------
        string
            Formatted query
        """
        prefix_manager = PrefixManager(self.app, self.session)
        query = textwrap.dedent(query)
        return '{}{}'.format(
            prefix_manager.get_prefix(),
            query
        )

    def get_default_query_with_prefix(self):
        """Get default query with the prefixes

        Returns
        -------
        str
            default query with prefixes
        """
        prefix_manager = PrefixManager(self.app, self.session)
        return '{}{}'.format(
            prefix_manager.get_prefix(),
            self.get_default_query()
        )

    def format_query(self, query, limit=30):
        """Format the Sparql query

        - remove all FROM
        - add FROM <graph> (public graph and user graph)
        - set a limit if not (or if its to big)

        Parameters
        ----------
        query : string
            sparql query to format
        limit : int, optional
            Description

        Returns
        -------
        string
            formatted sparql query
        """
        froms = self.get_froms()
        query_lines = query.split('\n')

        new_query = ''

        for line in query_lines:
            # Remove all FROM and LIMIT
            if not line.upper().lstrip().startswith('FROM') and not line.upper().lstrip().startswith('LIMIT'):
                new_query += '\n{}'.format(line)
            # Add new FROM
            if line.upper().lstrip().startswith('SELECT'):
                new_query += froms
            # Compute the limit
            if line.upper().lstrip().startswith('LIMIT') and limit:
                given_lim = int(re.findall(r'\d+', line)[0])
                if given_lim < limit and given_lim != 0:
                    limit = given_lim
                continue

        # Add limit
        if limit:
            new_query += '\nLIMIT {}'.format(limit)

        return new_query
