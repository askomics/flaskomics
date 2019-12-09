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
        self.endpoints = []
        self.selects = []
        self.federated = False

        # local endpoint (for federated query engine)
        self.local_endpoint_f = self.settings.get('triplestore', 'endpoint')
        try:
            self.local_endpoint_f = self.settings.get('federation', 'local_endpoint')
        except Exception:
            pass

        self.set_graphs_and_endpoints()

    def set_graphs(self, graphs):
        """Set graphs

        Parameters
        ----------
        graphs : list
            graphs
        """
        self.graphs = graphs

    def set_endpoints(self, endpoints):
        """Set endpoints

        Parameters
        ----------
        endpoints : list
            Endpoints
        """
        self.endpoints = endpoints

    def is_federated(self):
        """Return True if there is more than 1 endpoint

        Returns
        -------
        bool
            True or False
        """
        if len(self.endpoints) > 1:
            return True
        return False

    def replace_froms(self):
        """True if not federated and endpoint is local

        Returns
        -------
        bool
            True or False
        """
        if not self.is_federated():
            if self.endpoints == [self.local_endpoint_f]:
                return True

        return False

    def get_federated_froms(self):
        """Get @from string fir the federated query engine

        Returns
        -------
        string
            The from string
        """
        from_string = "@from <{}>".format(self.local_endpoint_f)
        for graph in self.graphs:
            from_string += " <{}>".format(graph)

        return from_string

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

    def get_federated_line(self):
        """Get federtated line

        Returns
        -------
        string
            @federate <endpoint1> <endpoint1> ...
        """
        federated_string = '@federate '
        for endpoint in self.endpoints:
            federated_string += '<{}> '.format(endpoint)

        return federated_string

    def format_graph_name(self, graph):
        """Format graph name by removing base graph and timestamp

        Parameters
        ----------
        graph : string
            The graph name

        Returns
        -------
        string
            Formated graph name
        """
        to_remove = "{}:{}_{}:".format(
            self.settings.get("triplestore", "default_graph"),
            self.session["user"]["id"],
            self.session["user"]["username"]
        )

        return "_".join(graph.replace(to_remove, "").split("_")[:-1])

    def format_endpoint_name(self, endpoint):
        """Replace local url by "local triplestore"

        Parameters
        ----------
        endpoint : string
            The endpoint name

        Returns
        -------
        string
            Formated endpoint name
        """
        if endpoint in (self.settings.get("triplestore", "endpoint"), self.local_endpoint_f):
            return "local triplestore"
        return endpoint

    def get_graphs_and_endpoints(self, selected_graphs=None, selected_endpoints=None):
        """get graphs and endpoints (uri and names)

        Returns
        -------
        list
            List of dict uri name
        """
        graphs = {}
        endpoints = {}
        for graph in self.graphs:
            graphs[graph] = {
                "uri": graph,
                "name": self.format_graph_name(graph),
                "selected": True if graph in selected_graphs else False
            }
        for endpoint in self.endpoints:
            endpoints[endpoint] = {
                "uri": endpoint,
                "name": self.format_endpoint_name(endpoint),
                "selected": True if endpoint in selected_endpoints else False
            }

        return (graphs, endpoints)

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

    def format_query(self, query, limit=30, replace_froms=True, federated=False):
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

        if federated:
            federated_line = "{}\n{}".format(self.get_federated_line(), self.get_federated_froms())

        query_lines = query.split('\n')

        new_query = ''

        for line in query_lines:
            # Remove all FROM and LIMIT and @federated
            if not line.upper().lstrip().startswith('FROM') and not line.upper().lstrip().startswith('LIMIT') and not line.upper().lstrip().startswith('@FEDERATE'):
                if line.upper().lstrip().startswith('SELECT') and federated:
                    new_query += "\n{}\n".format(federated_line)
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

    def get_federated_froms_from_graphs(self, graphs):
        """Get @from string fir the federated query engine

        Returns
        -------
        string
            The from string
        """
        from_string = "@from <{}>".format(self.local_endpoint_f)
        for graph in graphs:
            from_string += " <{}>".format(graph)

        return from_string

    def get_endpoints_string(self):
        """get endpoint strngs for the federated query engine

        Returns
        -------
        string
            the endpoint string
        """
        endpoints_string = '@federate '
        for endpoint in self.endpoints:
            endpoints_string += "<{}> ".format(endpoint)

        return endpoints_string

    def set_graphs_and_endpoints(self, entities=None, graphs=None, endpoints=None):
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
        SELECT DISTINCT ?graph ?endpoint
        WHERE {{
          ?graph :public ?public .
          ?graph dc:creator ?creator .
          GRAPH ?graph {{
            ?graph prov:atLocation ?endpoint .
            ?entity_uri a :entity .
          }}
          {}
          {}
        }}
        '''.format(filter_public_string, filter_entity_string)

        query_launcher = SparqlQueryLauncher(self.app, self.session)
        header, results = query_launcher.process_query(self.prefix_query(query))
        self.graphs = []
        self.endpoints = []
        for res in results:
            if not graphs or res["graph"] in graphs:
                self.graphs.append(res["graph"])

            # If local triplestore url is not accessible by federetad query engine
            if res["endpoint"] == self.settings.get('triplestore', 'endpoint') and self.local_endpoint_f is not None:
                endpoint = self.local_endpoint_f
            else:
                endpoint = res["endpoint"]

            if not endpoints or endpoint in endpoints:
                self.endpoints.append(endpoint)

        self.endpoints = Utils.unique(self.endpoints)
        self.federated = len(self.endpoints) > 1

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

        self.set_graphs_and_endpoints(entities=entities)

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
                # filters/values
                if attribute["filterValue"] != "" and not attribute["linked"]:
                    filter_value = "<{}>".format(attribute["filterValue"]) if Utils.is_url(attribute["filterValue"]) else "{}".format(attribute["filterValue"])
                    if attribute["filterType"] == "regexp":
                        negative_sign = ""
                        if attribute["negative"]:
                            negative_sign = "!"
                        filters.append("FILTER ({}regex({}, {}, 'i'))".format(negative_sign, subject, filter_value))
                    elif attribute["filterType"] == "exact":
                        if attribute["negative"]:
                            filters.append("FILTER (str({}) != {}) .".format(subject, filter_value))
                        else:
                            values.append("VALUES {} {{ {} }} .".format(subject, filter_value))

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
                # filters/values
                if attribute["filterValue"] != "" and not attribute["optional"] and not attribute["linked"]:
                    if attribute["filterType"] == "regexp":
                        negative_sign = ""
                        if attribute["negative"]:
                            negative_sign = "!"
                        filters.append("FILTER ({}regex({}, '{}', 'i'))".format(negative_sign, obj, attribute["filterValue"]))
                    elif attribute["filterType"] == "exact":
                        if attribute["negative"]:
                            filters.append("FILTER (str({}) != '{}') .".format(obj, attribute["filterValue"]))
                        else:
                            values.append("VALUES {} {{ '{}' }} .".format(obj, attribute["filterValue"]))

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
                    if attribute['filterSign'] == "=":
                        values.append("VALUES {} {{ {} }} .".format(obj, attribute["filterValue"]))
                    else:
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
                    if attribute["faldo"] and attribute["faldo"].endswith("faldoReference"):
                        category_name = 'faldo:location/faldo:begin/faldo:reference'
                        triples_attributes.append({
                            "subject": node_uri,
                            "predicate": category_name,
                            "object": category_value_uri,
                            "optional": True if attribute["optional"] else False
                        })
                        if attribute["visible"]:
                            triples_attributes.append({
                                "subject": category_value_uri,
                                "predicate": "rdfs:label",
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
                        if attribute["visible"]:
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
                        if attribute["visible"]:
                            triples_attributes.append({
                                "subject": category_value_uri,
                                "predicate": "rdfs:label",
                                "object": category_label,
                                "optional": True if attribute["optional"] else False
                            })

                    if attribute["visible"]:
                        self.selects.append(category_label)
                # values
                if attribute["filterSelectedValues"] != [] and not attribute["optional"] and not attribute["linked"]:
                    uri_val_list = []
                    for value in attribute["filterSelectedValues"]:
                        if attribute["faldo"] and attribute["faldo"].endswith("faldoStrand"):
                            value_var = faldo_strand
                            uri_val_list.append("<{}>".format(value))
                        else:
                            value_var = category_value_uri
                            uri_val_list.append("<{}>".format(value))

                    if uri_val_list:
                        values.append("VALUES {} {{ {} }}".format(value_var, ' '.join(uri_val_list)))

                if attribute["linked"]:
                    var_2 = self.format_sparql_variable("{}{}_{}Category".format(
                        attributes[attribute["linkedWith"]]["entity_label"],
                        attributes[attribute["linkedWith"]]["entity_id"],
                        attributes[attribute["linkedWith"]]["label"]
                    ))
                    var_to_replace.append((category_value_uri, var_2))

        from_string = self.get_froms_from_graphs(self.graphs)
        federated_from_string = self.get_federated_froms_from_graphs(self.graphs)
        endpoints_string = self.get_endpoints_string()

        # Linked attributes: replace SPARQL variable target by source
        for tpl_var in var_to_replace:
            var_source = tpl_var[0]
            var_target = tpl_var[1]
            for i, triple_dict in enumerate(triples_relations):
                for key, value in triple_dict.items():
                    if key != "optional":
                        triples_relations[i][key] = value.replace(var_source, var_target)
            for i, triple_dict in enumerate(triples_attributes):
                for key, value in triple_dict.items():
                    if key != "optional":
                        triples_attributes[i][key] = value.replace(var_source, var_target)
            for i, select in enumerate(self.selects):
                self.selects[i] = select.replace(var_source, var_target)
            for i, filtr in enumerate(filters):
                filters[i] = filtr.replace(var_source, var_target)

        # uniq lists
        triples_relations = Utils.unique(triples_relations)
        triples_attributes = Utils.unique(triples_attributes)
        self.selects = Utils.unique(self.selects)

        # Write the query

        # query is for editor (no froms, no federated)
        if for_editor:
            query = """
SELECT DISTINCT {selects}
WHERE {{
    {relations}
    {attributes}
    {filters}
    {values}
}}
            """.format(
                selects=' '.join(self.selects),
                relations='\n    '.join([self.triple_dict_to_string(triple_dict) for triple_dict in triples_relations]),
                attributes='\n    '.join([self.triple_dict_to_string(triple_dict) for triple_dict in triples_attributes]),
                filters='\n    '.join(filters),
                values='\n    '.join(values))

        # Query is federated, add federated lines @federate & @from)
        elif self.federated:
            query = """
{endpoints}
{federated}

SELECT DISTINCT {selects}
WHERE {{
    {relations}
    {attributes}
    {filters}
    {values}
}}
            """.format(
                endpoints=endpoints_string,
                federated=federated_from_string,
                selects=' '.join(self.selects),
                relations='\n    '.join([self.triple_dict_to_string(triple_dict) for triple_dict in triples_relations]),
                attributes='\n    '.join([self.triple_dict_to_string(triple_dict) for triple_dict in triples_attributes]),
                filters='\n    '.join(filters),
                values='\n    '.join(values)
            )

        # Query on the local endpoint (add froms)
        elif self.endpoints == [self.local_endpoint_f]:
            query = """
SELECT DISTINCT {selects}
{froms}
WHERE {{
    {relations}
    {attributes}
    {filters}
    {values}
}}
            """.format(
                selects=' '.join(self.selects),
                froms=from_string,
                relations='\n    '.join([self.triple_dict_to_string(triple_dict) for triple_dict in triples_relations]),
                attributes='\n    '.join([self.triple_dict_to_string(triple_dict) for triple_dict in triples_attributes]),
                filters='\n    '.join(filters),
                values='\n    '.join(values))

        # Query an external endpoint (no froms)
        else:
            query = """
SELECT DISTINCT {selects}
WHERE {{
    {relations}
    {attributes}
    {filters}
    {values}
}}
            """.format(
                selects=' '.join(self.selects),
                relations='\n    '.join([self.triple_dict_to_string(triple_dict) for triple_dict in triples_relations]),
                attributes='\n    '.join([self.triple_dict_to_string(triple_dict) for triple_dict in triples_attributes]),
                filters='\n    '.join(filters),
                values='\n    '.join(values))

        if preview:
            query += "\nLIMIT {}".format(self.settings.getint('triplestore', 'preview_limit'))

        return self.prefix_query(textwrap.dedent(query))
