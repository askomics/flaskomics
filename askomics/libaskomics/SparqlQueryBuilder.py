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

    def toggle_public(self, graph, public):
        """Change public status of data into the triplestore

        Parameters
        ----------
        graph : string
            Graph to update public status
        public : string
            true or false (string)
        """
        query = '''
        WITH GRAPH <{graph}>
        DELETE {{
            <{graph}> :public ?public .
        }}
        INSERT {{
            <{graph}> :public <{public}> .
        }}
        WHERE {{
            <{graph}> :public ?public .
        }}
        '''.format(graph=graph, public=public)

        query_launcher = SparqlQueryLauncher(self.app, self.session)
        query_launcher.process_query(self.prefix_query(query))

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
        return "?{}".format(re.sub(r'[^a-zA-Z0-9]+', '_', name))

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

    def triple_dict_to_string(self, triple_dict):
        """Convert a triple dict into a triple string

        Parameters
        ----------
        triple_dict : dict
            The triple dict

        Returns
        -------
        string
            The triple string
        """
        triple = "{} {} {} .".format(triple_dict["subject"], triple_dict["predicate"], triple_dict["object"])
        if triple_dict["optional"]:
            triple = "OPTIONAL {{{}}}".format(triple)

        return triple

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
        attributes = {}
        linked_attributes = []

        self.selects = []
        triples_relations = []
        triples_attributes = []
        values = []
        filters = []
        start_end = []
        strands = []

        var_to_replace = []

        # Browse node to get graphs
        for node in json_query["nodes"]:
            if not node["suggested"]:
                entities.append(node["uri"])

        self.set_graphs(entities=entities)

        # self.log.debug(json_query)

        # Browse links (relations)
        for link in json_query["links"]:
            if not link["suggested"]:
                source = self.format_sparql_variable("{}{}_uri".format(link["source"]["label"], link["source"]["id"]))
                target = self.format_sparql_variable("{}{}_uri".format(link["target"]["label"], link["target"]["id"]))

                # Position
                if link["uri"] in ('included_in', 'overlap_with'):
                    common_block = self.format_sparql_variable("block_{}_{}".format(link["source"]["id"], link["target"]["id"]))
                    # Get start & end sparql variables
                    for attr in json_query["attr"]:
                        if not attr["faldo"]:
                            continue
                        if attr["nodeId"] == link["source"]["id"]:
                            if attr["faldo"].endswith("faldoStart"):
                                start_end.append(attr["id"])
                                start_1 = self.format_sparql_variable("{}{}_{}".format(attr["entityLabel"], attr["nodeId"], attr["label"]))
                            if attr["faldo"].endswith("faldoEnd"):
                                start_end.append(attr["id"])
                                end_1 = self.format_sparql_variable("{}{}_{}".format(attr["entityLabel"], attr["nodeId"], attr["label"]))
                            if attr["faldo"].endswith("faldoStrand"):
                                strand_1 = self.format_sparql_variable("{}{}_{}_faldoStrand".format(attr["entityLabel"], attr["nodeId"], attr["label"]))
                                strands.append(attr["id"])
                        if attr["nodeId"] == link["target"]["id"]:
                            if attr["faldo"].endswith("faldoStart"):
                                start_end.append(attr["id"])
                                start_2 = self.format_sparql_variable("{}{}_{}".format(attr["entityLabel"], attr["nodeId"], attr["label"]))
                            if attr["faldo"].endswith("faldoEnd"):
                                start_end.append(attr["id"])
                                end_2 = self.format_sparql_variable("{}{}_{}".format(attr["entityLabel"], attr["nodeId"], attr["label"]))
                            if attr["faldo"].endswith("faldoStrand"):
                                strand_2 = self.format_sparql_variable("{}{}_{}_faldoStrand".format(attr["entityLabel"], attr["nodeId"], attr["label"]))
                                strands.append(attr["id"])

                    triples_relations.append({
                        "subject": source,
                        "predicate": "askomics:{}".format("includeInReference" if link["sameRef"] else "includeIn"),
                        "object": common_block,
                        "optional": False
                    })

                    triples_relations.append({
                        "subject": target,
                        "predicate": "askomics:{}".format("includeInReference" if link["sameRef"] else "includeIn"),
                        "object": common_block,
                        "optional": False
                    })

                    if link["sameStrand"]:
                        var_to_replace.append((strand_1, strand_2))
                    else:
                        strands = []

                    equal_sign = "" if link["strict"] else "="

                    if link["uri"] == "included_in":
                        filters.append("FILTER ({start1} >{equalsign} {start2} && {end1} <{equalsign} {end2}) .".format(
                            start1=start_1,
                            start2=start_2,
                            end1=end_1,
                            end2=end_2,
                            equalsign=equal_sign
                        ))
                    elif link["uri"] == "overlap_with":
                        filters.append("FILTER (({start2} >{equalsign} {start1} && {start2} <{equalsign} {end1}) || ({end2} >{equalsign} {start1} && {end2} <{equalsign} {end1}))".format(
                            start1=start_1,
                            start2=start_2,
                            end1=end_1,
                            end2=end_2,
                            equalsign=equal_sign
                        ))

                # Classic relation
                else:
                    relation = "<{}>".format(link["uri"])
                    triples_relations.append({
                        "subject": source,
                        "predicate": relation,
                        "object": target,
                        "optional": False
                    })

        # Store linked attributes
        for attribute in json_query["attr"]:
            attributes[attribute["id"]] = {
                "label": attribute["label"],
                "entity_label": attribute["entityLabel"],
                "entity_id": attribute["nodeId"]
            }
            if attribute["linked"]:
                linked_attributes.extend((attribute["id"], attribute["linkedWith"]))

        # Browse attributes
        for attribute in json_query["attr"]:
            # URI ---
            if attribute["type"] == "uri":
                subject = self.format_sparql_variable("{}{}_uri".format(attribute["entityLabel"], attribute["nodeId"]))
                predicate = attribute["uri"]
                obj = "<{}>".format(attribute["entityUri"])
                if not self.is_bnode(attribute["entityUri"], json_query["nodes"]):
                    triples_attributes.append({
                        "subject": subject,
                        "predicate": predicate,
                        "object": obj,
                        "optional": False
                    })
                if attribute["visible"]:
                    self.selects.append(subject)
                # filters
                if attribute["filterValue"] != "" and not attribute["linked"]:
                    not_exist = ""
                    if attribute["negative"]:
                        not_exist = " NOT EXISTS"
                    if attribute["filterType"] == "regexp":
                        filter_string = "FILTER{} (contains(str({}), '{}')) .".format(not_exist, subject, attribute["filterValue"])
                        filters.append(filter_string)
                    elif attribute["filterType"] == "exact":
                        filter_string = "FILTER{} (str({}) = '{}') .".format(not_exist, subject, attribute["filterValue"])
                        filters.append(filter_string)
                if attribute["linked"]:
                    var_2 = self.format_sparql_variable("{}{}_uri".format(
                        attributes[attribute["linkedWith"]]["entity_label"],
                        attributes[attribute["linkedWith"]]["entity_id"]
                    ))
                    var_to_replace.append((subject, var_2))

            # Text
            if attribute["type"] == "text":
                if attribute["visible"] or attribute["filterValue"] != "" or attribute["id"] in linked_attributes:
                    subject = self.format_sparql_variable("{}{}_uri".format(attribute["entityLabel"], attribute["nodeId"]))
                    if attribute["uri"] == "rdfs:label":
                        predicate = attribute["uri"]
                    else:
                        predicate = "<{}>".format(attribute["uri"])

                    obj = self.format_sparql_variable("{}{}_{}".format(attribute["entityLabel"], attribute["nodeId"], attribute["label"]))

                    triples_attributes.append({
                        "subject": subject,
                        "predicate": predicate,
                        "object": obj,
                        "optional": True if attribute["optional"] else False
                    })
                    if attribute["visible"]:
                        self.selects.append(obj)
                # filters
                if attribute["filterValue"] != "" and not attribute["optional"] and not attribute["linked"]:
                    negative = ""
                    if attribute["negative"]:
                        negative = "!"
                    if attribute["filterType"] == "regexp":
                        filter_string = "FILTER ({}contains(str({}), '{}')) .".format(negative, obj, attribute["filterValue"])
                        filters.append(filter_string)
                    elif attribute["filterType"] == "exact":
                        filter_string = "FILTER (str({}) {}= '{}') .".format(obj, negative, attribute["filterValue"])
                        filters.append(filter_string)
                if attribute["linked"]:
                    var_2 = self.format_sparql_variable("{}{}_{}".format(
                        attributes[attribute["linkedWith"]]["entity_label"],
                        attributes[attribute["linkedWith"]]["entity_id"],
                        attributes[attribute["linkedWith"]]["label"]
                    ))
                    var_to_replace.append((obj, var_2))

            # Numeric
            if attribute["type"] == "decimal":
                if attribute["visible"] or attribute["filterValue"] != "" or attribute["id"] in start_end or attribute["id"] in linked_attributes:
                    subject = self.format_sparql_variable("{}{}_uri".format(attribute["entityLabel"], attribute["nodeId"]))
                    if attribute["faldo"]:
                        predicate = "faldo:location/faldo:{}/faldo:position".format("begin" if attribute["faldo"].endswith("faldoStart") else "end")
                    else:
                        predicate = "<{}>".format(attribute["uri"])
                    obj = self.format_sparql_variable("{}{}_{}".format(attribute["entityLabel"], attribute["nodeId"], attribute["label"]))
                    triples_attributes.append({
                        "subject": subject,
                        "predicate": predicate,
                        "object": obj,
                        "optional": True if attribute["optional"] else False
                    })
                    if attribute["visible"]:
                        self.selects.append(obj)
                # filters
                if attribute["filterValue"] != "" and not attribute["optional"] and not attribute["linked"]:
                    filter_string = "FILTER ( {} {} {} ) .".format(obj, attribute["filterSign"], attribute["filterValue"])
                    filters.append(filter_string)
                if attribute["linked"]:
                    var_2 = self.format_sparql_variable("{}{}_{}".format(
                        attributes[attribute["linkedWith"]]["entity_label"],
                        attributes[attribute["linkedWith"]]["entity_id"],
                        attributes[attribute["linkedWith"]]["label"]
                    ))
                    var_to_replace.append((obj, var_2))

            # Category
            if attribute["type"] == "category":
                if attribute["visible"] or attribute["filterSelectedValues"] != [] or attribute["id"] in strands or attribute["id"] in linked_attributes:
                    node_uri = self.format_sparql_variable("{}{}_uri".format(attribute["entityLabel"], attribute["nodeId"]))
                    category_value_uri = self.format_sparql_variable("{}{}_{}Category".format(attribute["entityLabel"], attribute["nodeId"], attribute["label"]))
                    category_label = self.format_sparql_variable("{}{}_{}".format(attribute["entityLabel"], attribute["nodeId"], attribute["label"]))
                    faldo_strand = self.format_sparql_variable("{}{}_{}_faldoStrand".format(attribute["entityLabel"], attribute["nodeId"], attribute["label"]))
                    label = "rdfs:label"
                    if attribute["faldo"] and attribute["faldo"].endswith("faldoReference"):
                        category_name = 'faldo:location/faldo:begin/faldo:reference'
                        triples_attributes.append({
                            "subject": node_uri,
                            "predicate": category_name,
                            "object": category_value_uri,
                            "optional": True if attribute["optional"] else False
                        })
                        triples_attributes.append({
                            "subject": category_value_uri,
                            "predicate": label,
                            "object": category_label,
                            "optional": True if attribute["optional"] else False
                        })
                    elif attribute["faldo"] and attribute["faldo"].endswith("faldoStrand"):
                        category_name = 'faldo:location/faldo:begin/rdf:type'
                        triples_attributes.append({
                            "subject": node_uri,
                            "predicate": category_name,
                            "object": category_value_uri,
                            "optional": True if attribute["optional"] else False
                        })
                        triples_attributes.append({
                            "subject": faldo_strand,
                            "predicate": "a",
                            "object": category_value_uri,
                            "optional": True if attribute["optional"] else False
                        })
                        triples_attributes.append({
                            "subject": faldo_strand,
                            "predicate": "rdfs:label",
                            "object": category_label,
                            "optional": False
                        })
                        values.append("VALUES {} {{ faldo:ReverseStrandPosition faldo:ForwardStrandPosition }} .".format(category_value_uri))
                    else:
                        category_name = "<{}>".format(attribute["uri"])
                        triples_attributes.append({
                            "subject": node_uri,
                            "predicate": category_name,
                            "object": category_value_uri,
                            "optional": True if attribute["optional"] else False
                        })
                        triples_attributes.append({
                            "subject": category_value_uri,
                            "predicate": label,
                            "object": category_label,
                            "optional": True if attribute["optional"] else False
                        })

                    if attribute["visible"]:
                        self.selects.append(category_label)
                # filters
                if attribute["filterSelectedValues"] != [] and not attribute["optional"] and not attribute["linked"]:
                    filter_substrings_list = []
                    for value in attribute["filterSelectedValues"]:
                        if attribute["faldo"] and attribute["faldo"].endswith("faldoStrand"):
                            faldo_strand_filter = self.format_sparql_variable("{}{}_{}_faldoStrand_filter".format(attribute["entityLabel"], attribute["nodeId"], Utils.get_random_string(5)))
                            filter_substrings_list.append("({} = {})".format(category_value_uri, faldo_strand_filter))
                            triples_attributes.append({
                                "subject": "<{}>".append(value),
                                "predicate": "a",
                                "object": faldo_strand_filter,
                                "optional": True if attribute["optional"] else False
                            })
                            values.append("VALUES {} {{ faldo:ReverseStrandPosition faldo:ForwardStrandPosition }} ".format(faldo_strand_filter))
                        else:
                            filter_substrings_list.append("({} = <{}>)".format(category_value_uri, value))
                    filter_substring = ' || '.join(filter_substrings_list)
                    filter_string = "FILTER ({})".format(filter_substring)
                    filters.append(filter_string)
                if attribute["linked"]:
                    var_2 = self.format_sparql_variable("{}{}_{}Category".format(
                        attributes[attribute["linkedWith"]]["entity_label"],
                        attributes[attribute["linkedWith"]]["entity_id"],
                        attributes[attribute["linkedWith"]]["label"]
                    ))
                    var_to_replace.append((category_value_uri, var_2))

        from_string = self.get_froms_from_graphs(self.graphs)

        # Replace variables (linked attributes)
        for tpl_var in var_to_replace:
            var_1 = tpl_var[0]
            var_2 = tpl_var[1]
            common_var = "{}_{}".format(var_1, var_2.replace("?", ""))
            for i, triple_dict in enumerate(triples_relations):
                for key, value in triple_dict.items():
                    if key != "optional":
                        triples_relations[i][key] = value.replace(var_1, common_var).replace(var_2, common_var)
            for i, triple_dict in enumerate(triples_attributes):
                for key, value in triple_dict.items():
                    if key != "optional":
                        triples_attributes[i][key] = value.replace(var_1, common_var).replace(var_2, common_var)
            for i, select in enumerate(self.selects):
                self.selects[i] = select.replace(var_1, common_var)
                self.selects[i] = self.selects[i].replace(var_2, common_var)
            for i, filtr in enumerate(filters):
                filters[i] = filtr.replace(var_1, common_var)
                filters[i] = filters[i].replace(var_2, common_var)

        # Write the query
        if for_editor:
            query = """
SELECT DISTINCT {}
WHERE {{
    {}
    {}
    {}
    {}
}}
            """.format(
                ' '.join(self.selects),
                '\n    '.join([self.triple_dict_to_string(triple_dict) for triple_dict in triples_relations]),
                '\n    '.join([self.triple_dict_to_string(triple_dict) for triple_dict in triples_attributes]),
                '\n    '.join(filters),
                '\n    '.join(values))
        else:

            query = """
SELECT DISTINCT {}
{}
WHERE {{
    {}
    {}
    {}
    {}
}}
            """.format(
                ' '.join(self.selects), from_string,
                '\n    '.join([self.triple_dict_to_string(triple_dict) for triple_dict in triples_relations]),
                '\n    '.join([self.triple_dict_to_string(triple_dict) for triple_dict in triples_attributes]),
                '\n    '.join(filters),
                '\n    '.join(values))

        if preview:
            query += "\nLIMIT {}".format(self.settings.getint('triplestore', 'preview_limit'))

        return self.prefix_query(textwrap.dedent(query))
