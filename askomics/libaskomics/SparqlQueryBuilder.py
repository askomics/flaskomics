import re
import textwrap

from askomics.libaskomics.Params import Params
from askomics.libaskomics.PrefixManager import PrefixManager
from askomics.libaskomics.SparqlQueryLauncher import SparqlQueryLauncher
from askomics.libaskomics.Utils import Utils


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

        self.graphs = []
        self.selects = []

        self.set_graphs()

    def get_froms(self):
        """Get FROM string

        Returns
        -------
        string
            FROM string
        """
        from_string = ''
        for graph in self.graphs:
            from_string += '\nFROM <{}>'.format(graph)

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

    def format_query(self, query, limit=30, replace_froms=True):
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
        froms = ''
        if replace_froms:
            froms = self.get_froms()
        query_lines = query.split('\n')

        new_query = ''

        for line in query_lines:
            # Remove all FROM and LIMIT
            if not line.upper().lstrip().startswith('FROM') and not line.upper().lstrip().startswith('LIMIT'):
                new_query += '\n{}'.format(line)
            # Add new FROM
            if line.upper().lstrip().startswith('SELECT'):
                self.selects = [i for i in line.split() if i.startswith('?')]
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

    def get_checked_asked_graphs(self, asked_graphs):
        """Check if asked graphs are present in public and private graphs

        Parameters
        ----------
        asked_graphs : list
            list of graphs asked by the user

        Returns
        -------
        list
            list of graphs asked by the user, in the public and private graphs
        """
        return Utils.intersect(asked_graphs, self.private_graphs + self.public_graphs)

    def get_froms_from_graphs(self, graphs):
        """Get FROM's form a list of graphs

        Parameters
        ----------
        graphs : list
            List of graphs

        Returns
        -------
        str
            from string
        """
        from_string = ''

        for graph in graphs:
            from_string += '\nFROM <{}>'.format(graph)

        return from_string

    def set_graphs(self, entities=None):
        """Get all public and private graphs containing the given entities

        Parameters
        ----------
        entities : list, optional
            list of entity uri
        """
        substrlst = []
        filter_entity_string = ''
        if entities:
            for entity in entities:
                substrlst.append("?entity_uri = <{}>".format(entity))
            filter_entity_string = 'FILTER (' + ' || '.join(substrlst) + ')'

        filter_public_string = 'FILTER (?public = <true>)'
        if 'user' in self.session:
            filter_public_string = 'FILTER (?public = <true> || ?creator = <{}>)'.format(self.session["user"]["username"])

        query = '''
        SELECT DISTINCT ?graph
        WHERE {{
          ?graph :public ?public .
          ?graph dc:creator ?creator .
          GRAPH ?graph {{
            ?entity_uri a :entity .
          }}
          {}
          {}
        }}
        '''.format(filter_public_string, filter_entity_string)

        query_launcher = SparqlQueryLauncher(self.app, self.session)
        header, results = query_launcher.process_query(self.prefix_query(query))
        self.graphs = []
        for res in results:
            self.graphs.append(res["graph"])

    def format_sparql_variable(self, name):
        """Format a name into a sparql variable by remove spacial char and add a ?

        Parameters
        ----------
        name : string
            name to convert

        Returns
        -------
        string
            The corresponding sparql variable
        """
        return "?{}".format(name.replace("/", "_s_").replace(":", "_c_").replace("-", "_"))

    def is_bnode(self, uri, entities):
        """Check if a node uri is a blank node

        Parameters
        ----------
        uri : string
            node uri
        entities : list
            all the entities

        Returns
        -------
        Bool
            True if uri correspond to a blank node
        """
        for entity in entities:
            if entity["uri"] == uri and entity["type"] == "bnode":
                return True
        return False

    def build_query_from_json(self, json_query, preview=False, for_editor=False):
        """Build a sparql query for the json dict of the query builder

        Parameters
        ----------
        json_query : dict
            The json query from the query builder

        Returns
        -------
        str
            SPARQL query
        """
        entities = []

        self.selects = []
        triples = []
        filters = []

        # Browse node to get graphs
        for node in json_query["nodes"]:
            if not node["suggested"]:
                entities.append(node["uri"])

        self.set_graphs(entities=entities)

        # Browse attributes
        for attribute in json_query["attr"]:
            # URI ---
            if attribute["type"] == "uri":
                subject = self.format_sparql_variable("{}{}_uri".format(attribute["entityLabel"], attribute["nodeId"]))
                predicate = attribute["uri"]
                obj = attribute["entityUri"]
                if not self.is_bnode(attribute["entityUri"], json_query["nodes"]):
                    triples.append("{} {} <{}> .".format(subject, predicate, obj))
                if attribute["visible"]:
                    self.selects.append(subject)
                # filters
                if attribute["filterValue"] != "":
                    not_exist = ""
                    if attribute["negative"]:
                        not_exist = " NOT EXISTS"
                    if attribute["filterType"] == "regexp":
                        filter_string = "FILTER{} (contains(str({}), '{}')) .".format(not_exist, subject, attribute["filterValue"])
                        filters.append(filter_string)
                    elif attribute["filterType"] == "exact":
                        filter_string = "FILTER{} (str({}) = '{}') .".format(not_exist, subject, attribute["filterValue"])
                        filters.append(filter_string)

            # Text
            if attribute["type"] == "text":
                if attribute["visible"] or attribute["filterValue"] != "":
                    subject = self.format_sparql_variable("{}{}_uri".format(attribute["entityLabel"], attribute["nodeId"]))
                    if attribute["uri"] == "rdfs:label":
                        predicate = attribute["uri"]
                    else:
                        predicate = "<{}>".format(attribute["uri"])

                    obj = self.format_sparql_variable("{}{}_{}".format(attribute["entityLabel"], attribute["nodeId"], attribute["label"]))
                    triple_string = "{} {} {} .".format(subject, predicate, obj)
                    if attribute["optional"]:
                        triple_string = "OPTIONAL {{{}}}".format(triple_string)
                    triples.append(triple_string)
                    if attribute["visible"]:
                        self.selects.append(obj)
                # filters
                if attribute["filterValue"] != "" and not attribute["optional"]:
                    negative = ""
                    if attribute["negative"]:
                        negative = "!"
                    if attribute["filterType"] == "regexp":
                        filter_string = "FILTER ({}contains(str({}), '{}')) .".format(negative, obj, attribute["filterValue"])
                        filters.append(filter_string)
                    elif attribute["filterType"] == "exact":
                        filter_string = "FILTER (str({}) {}= '{}') .".format(obj, negative, attribute["filterValue"])
                        filters.append(filter_string)

            # Numeric
            if attribute["type"] == "decimal":
                if attribute["visible"] or attribute["filterValue"] != "":
                    subject = self.format_sparql_variable("{}{}_uri".format(attribute["entityLabel"], attribute["nodeId"]))
                    predicate = "<{}>".format(attribute["uri"])
                    obj = self.format_sparql_variable("{}{}_{}".format(attribute["entityLabel"], attribute["nodeId"], attribute["label"]))
                    triple_string = "{} {} {} .".format(subject, predicate, obj)
                    if attribute["optional"]:
                        triple_string = "OPTIONAL {{{}}}".format(triple_string)
                    triples.append(triple_string)
                    if attribute["visible"]:
                        self.selects.append(obj)
                # filters
                if attribute["filterValue"] != "" and not attribute["optional"]:
                    filter_string = "FILTER ( {} {} {} ) .".format(obj, attribute["filterSign"], attribute["filterValue"])
                    filters.append(filter_string)

            # Category
            if attribute["type"] == "category":
                if attribute["visible"] or attribute["filterSelectedValues"] != []:
                    node_uri = self.format_sparql_variable("{}{}_uri".format(attribute["entityLabel"], attribute["nodeId"]))
                    category_name = "<{}>".format(attribute["uri"])
                    category_value_uri = self.format_sparql_variable("{}{}_{}Category".format(attribute["entityLabel"], attribute["nodeId"], attribute["label"]))
                    label = "rdfs:label"
                    category_label = self.format_sparql_variable("{}{}_{}".format(attribute["entityLabel"], attribute["nodeId"], attribute["label"]))
                    triple_string_1 = "{} {} {} .".format(node_uri, category_name, category_value_uri)
                    triple_string_2 = "{} {} {} .".format(category_value_uri, label, category_label)
                    if attribute["optional"]:
                        triple_string_1 = "OPTIONAL {{{} {}}}".format(triple_string_1, triple_string_2)
                        triple_string_2 = ""
                    triples.append(triple_string_1)
                    triples.append(triple_string_2)

                    if attribute["visible"]:
                        self.selects.append(category_label)
                # filters
                if attribute["filterSelectedValues"] != [] and not attribute["optional"]:
                    filter_substrings_list = []
                    for value in attribute["filterSelectedValues"]:
                        filter_substrings_list.append("({} = <{}>)".format(category_value_uri, value))
                    filter_substring = ' || '.join(filter_substrings_list)
                    filter_string = "FILTER ({})".format(filter_substring)
                    filters.append(filter_string)

        # Browse links
        for link in json_query["links"]:
            if not link["suggested"]:
                source = self.format_sparql_variable("{}{}_uri".format(link["source"]["label"], link["source"]["id"]))
                relation = "<{}>".format(link["uri"])
                target = self.format_sparql_variable("{}{}_uri".format(link["target"]["label"], link["target"]["id"]))
                triples.append("{} {} {} .".format(source, relation, target))

        from_string = self.get_froms_from_graphs(self.graphs)

        if for_editor:
            query = """
SELECT DISTINCT {}
WHERE {{
    {}
    {}

}}
            """.format(' '.join(self.selects), '\n    '.join(triples), '\n    '.join(filters))
        else:

            query = """
SELECT DISTINCT {}
{}
WHERE {{
    {}
    {}
}}
            """.format(' '.join(self.selects), from_string, '\n    '.join(triples), '\n    '.join(filters))

        if preview:
            query += "\nLIMIT {}".format(self.settings.getint('triplestore', 'preview_limit'))

        return self.prefix_query(textwrap.dedent(query))
