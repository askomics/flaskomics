from askomics.libaskomics.Params import Params
from askomics.libaskomics.SparqlQueryBuilder import SparqlQueryBuilder
from askomics.libaskomics.SparqlQueryLauncher import SparqlQueryLauncher


class TriplestoreExplorer(Params):
    """Explore the triplestore"""

    def __init__(self, app, session):
        """init

        Parameters
        ----------
        app : Flask
            flask app
        session :
            AskOmics session, contain the user
        """
        Params.__init__(self, app, session)

    def get_startpoints(self):
        """Get public and user startpoints

        Returns
        -------
        list
            Startpoints
        """
        query_launcher = SparqlQueryLauncher(self.app, self.session)
        query_builder = SparqlQueryBuilder(self.app, self.session)

        query = '''
        SELECT DISTINCT ?graph ?entity ?entity_label ?creator ?public
        WHERE {{
            ?graph :public ?public .
            ?graph dc:creator ?creator .
            GRAPH ?graph {{
                ?entity a :entity .
                ?entity a :startPoint .
                ?entity rdfs:label ?entity_label .
            }}
            FILTER (
                ?public = <true> || ?creator = <{}>
            )
        }}
        '''.format(self.session["user"]["username"])

        header, data = query_launcher.process_query(query_builder.prefix_query(query))

        return data
