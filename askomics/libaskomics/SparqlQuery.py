import re
import textwrap

from askomics.libaskomics.Params import Params
from askomics.libaskomics.PrefixManager import PrefixManager
from askomics.libaskomics.SparqlQueryLauncher import SparqlQueryLauncher
from askomics.libaskomics.Utils import Utils


class SparqlQuery(Params):
    """Format a sparql query

    Attributes
    ----------
    private_graphs : list
        all user private graph
    public_graphs : list
        all public graph
    """

    def __init__(self, app, session, json_query=None, get_graphs=True):
        """init

        Parameters
        ----------
        app : Flask
            Flask app
        session :
            AskOmics session
        """
        Params.__init__(self, app, session)

        self.json = json_query
        self.sparql = None

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
        # No need to call this twice if we need it later (sparql queries)
        if get_graphs:
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
        regexp = r"{}:.*:".format(
            self.settings.get("triplestore", "default_graph"),
        )

        return "_".join(re.sub(regexp, "", graph).split("_")[:-1])

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

    def get_graphs_and_endpoints(self, selected_graphs=[], selected_endpoints=[], all_selected=False):
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
                "selected": True if all_selected else True if graph in selected_graphs else False
            }
        for endpoint in self.endpoints:
            endpoints[endpoint] = {
                "uri": endpoint,
                "name": self.format_endpoint_name(endpoint),
                "selected": True if all_selected else True if endpoint in selected_endpoints else False
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
            <{graph}> askomics:public ?public .
        }}
        INSERT {{
            <{graph}> askomics:public <{public}> .
        }}
        WHERE {{
            <{graph}> askomics:public ?public .
        }}
        '''.format(graph=graph, public=public)

        query_launcher = SparqlQueryLauncher(self.app, self.session)
        query_launcher.execute_query(self.prefix_query(query))

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
          ?graph_abstraction askomics:public ?public .
          ?graph_abstraction dc:creator ?creator .
          ?graph askomics:public ?public .
          ?graph dc:creator ?creator .
          GRAPH ?graph_abstraction {{
            ?graph_abstraction prov:atLocation ?endpoint .
            ?entity_uri a ?askomics_type .
            VALUES ?askomics_type {{askomics:entity askomics:ontology}}
          }}
          GRAPH ?graph {{
            [] a ?entity_uri .
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

            # If local triplestore url is not accessible by federated query engine
            if res["endpoint"] == self.settings.get('triplestore', 'endpoint') and self.local_endpoint_f is not None:
                endpoint = self.local_endpoint_f
            else:
                endpoint = res["endpoint"]

            if not endpoints or endpoint in endpoints:
                self.endpoints.append(endpoint)

        self.endpoints = Utils.unique(self.endpoints)
        self.federated = len(self.endpoints) > 1

    def get_uri_parameters(self, uri, endpoints):
        """Get parameters for a specific data URI

        Parameters
        ----------
        uri : string
            URI to search

        Returns
        -------
        dict
            The corresponding parameters
        """
        raw_query = '''
        SELECT DISTINCT ?predicate ?object ?faldo_value ?faldo_uri
        WHERE {{
          ?URI ?predicate ?object .
          ?URI a ?entitytype .

          FILTER(! STRSTARTS(STR(?predicate), STR(askomics:)))
          OPTIONAL {{

            ?faldo_uri rdfs:domain ?entitytype .
            ?faldo_uri rdfs:label ?attribute_label .

            OPTIONAL {{
            ?object faldo:begin/faldo:position ?faldo_value .
            ?faldo_uri rdf:type askomics:faldoStart
            }}

            OPTIONAL {{
            ?object faldo:end/faldo:position ?faldo_value .
            ?faldo_uri rdf:type askomics:faldoEnd
            }}

            OPTIONAL {{
            ?object faldo:begin/faldo:reference/rdfs:label ?faldo_value .
            ?faldo_uri rdf:type askomics:faldoReference
            }}

            OPTIONAL {{
            ?object faldo:begin/rdf:type ?Gene1_strandCategory .
            ?Gene1_strand_faldoStrand a ?Gene1_strandCategory .
            ?Gene1_strand_faldoStrand rdfs:label ?faldo_value .
            ?faldo_uri rdf:type askomics:faldoStrand .
            }}

            VALUES ?predicate {{faldo:location}}
          }}
          VALUES ?URI {{{}}}
        }}
        '''.format(uri)

        federated = self.is_federated()
        replace_froms = self.replace_froms()

        raw_query = self.prefix_query(raw_query)

        sparql = self.format_query(raw_query, replace_froms=replace_froms, federated=federated)

        query_launcher = SparqlQueryLauncher(self.app, self.session, get_result_query=True, federated=federated, endpoints=endpoints)
        _, data = query_launcher.process_query(sparql)

        formated_data = []
        for row in data:
            formated_data.append({
                'predicate': row['faldo_uri'] if row.get('faldo_uri') else row['predicate'],
                'object': row['faldo_value'] if row.get('faldo_value') else row['object'],
            })

        return formated_data

    def autocomplete_local_ontology(self, uri, query, endpoints):
        """Get results for a specific query

        Parameters
        ----------
        uri : string
            ontology uri
        query : string
            query to search

        Returns
        -------
        dict
            The corresponding parameters
        """
        raw_query = '''
        SELECT DISTINCT ?label ?uri
        WHERE {{
          ?uri rdf:type <{}> .
          ?uri rdfs:label ?label .
          FILTER(contains(?label, "{}"))
        }}
        '''.format(uri, query)

        raw_query = self.prefix_query(raw_query)

        sparql = self.format_query(raw_query, limit=5, replace_froms=True, federated=False)

        query_launcher = SparqlQueryLauncher(self.app, self.session, get_result_query=True, federated=False, endpoints=endpoints)
        _, data = query_launcher.process_query(sparql)

        formated_data = []
        for row in data:
            formated_data.append({
                'uri': row['uri'],
                'label': row['label']
            })

        return formated_data

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

    def get_block_ids(self, node_id):
        """Get blockid and sblockid of a node with its id

        Parameters
        ----------
        node_id : int
            Node id

        Returns
        -------
        int, int
            blockid and sblockid
        """
        for node in self.json["nodes"]:
            if node["id"] == node_id:
                return node["specialNodeId"], node["specialNodeGroupId"], node["specialPreviousIds"]

        return None, None, (None, None)

    def triple_block_to_string(self, triple_block):
        """Convert a triple block to a SPARQL string

        Parameters
        ----------
        triple_block : dict
            A triple block

        Returns
        -------
        str
            Corresponding SPARQL
        """
        if triple_block["type"] in ("UNION", "MINUS"):

            block_string = "{\n"
            i = 0
            current_spacing = "    "

            for sblock in triple_block["sblocks"]:
                sblock_string = "{"
                triples_string = '\n{}'.format(current_spacing * 2).join([self.triple_dict_to_string(triple_dict) for triple_dict in sblock["triples"]])
                triples_string += '\n{}'.format(current_spacing * 2)
                triples_string += '\n{}'.format(current_spacing * 2).join([filtr for filtr in sblock["filters"]])
                triples_string += '\n{}'.format(current_spacing * 2)
                triples_string += '\n{}'.format(current_spacing * 2).join([value for value in sblock["values"]])
                sblock_string += "\n{}{}\n{}}}".format(current_spacing * 2, triples_string, current_spacing * 2)

                block_string += "{}{} ".format(current_spacing * 2, triple_block["type"]) if (triple_block["type"] == "MINUS" or i > 0) else current_spacing * 2
                block_string += sblock_string + "\n"
                i += 1

            block_string += current_spacing + "}\n"

        return block_string

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
            if triple_dict.get("nested_start"):
                triple = "OPTIONAL {{{}".format(triple)
            else:
                triple = "OPTIONAL {{{}}}".format(triple)
        # Close the }} if end of the nest
        if triple_dict.get("nested_end"):
            triple = "    " + triple + "}"
        elif triple_dict.get("nested"):
            triple = "    " + triple

        return triple

    def get_uri_filter_value(self, value):
        """Get full uri from a filter value (curie or uri)

        :xxx                     -->  :xxx
        uniprot:xxx              -->  <http://purl.uniprot.org/core/xxx>
        http://example.org/xxx   -->  <http://example.org/xxx>

        xxx                      -->  xxx is not a valid URI or CURIE
        bla:xxx                  -->  bla: is not a known prefix

        Parameters
        ----------
        value : string
            Input filter

        Returns
        -------
        string
            corresponding uri

        Raises
        ------
        ValueError
            Invalid URI or CURIE return a value error
        """
        if Utils().is_url(value):
            return "<{}>".format(value)
        elif ":" in value:
            prefix, val = value.split(":")
            if prefix:
                prefix_manager = PrefixManager(self.app, self.session)
                namespace = prefix_manager.get_namespace(prefix)
                if namespace:
                    return "<{}{}>".format(namespace, val)
                else:
                    raise ValueError("{}: is not a known prefix".format(prefix))
            else:
                return value

        raise ValueError("{} is not a valid URI or CURIE".format(value))

    def get_block_type(self, blockid):
        """Summary

        Parameters
        ----------
        blockid : TYPE
            Description

        Returns
        -------
        TYPE
            Description
        """
        types_dict = {
            "unionNode": "UNION",
            "minusNode": "MINUS"
        }

        for node in self.json["nodes"]:
            if node["type"] in ("unionNode", "minusNode"):
                if node["specialNodeId"] == blockid:
                    return types_dict[node["type"]]
        return None

    def store_triple(self, triple, blockid, sblockid, pblock_ids):
        """Store a triple inthe right list

        Parameters
        ----------
        triple : dict
            triple dict
        typ : str
            relatin or attribute
        block_info : None, optional
            block info if triple is part of a block
        """
        if blockid:
            self.store_block(triple, blockid, sblockid, pblock_ids)
        else:
            self.triples.append(triple)

    def store_filter(self, filtr, blockid, sblockid, pblock_ids):
        """Store a FILTER in the right list

        Parameters
        ----------
        triple : dict
            triple dict
        typ : str
            relatin or attribute
        block_info : None, optional
            block info if triple is part of a block
        """
        if blockid:
            self.store_filter_block(filtr, blockid, sblockid)
        else:
            self.filters.append(filtr)

    def store_value(self, value, blockid, sblockid, pblock_ids):
        """Store a VALUES inthe right list

        Parameters
        ----------
        triple : dict
            triple dict
        typ : str
            relatin or attribute
        block_info : None, optional
            block info if triple is part of a block
        """
        if blockid:
            self.store_values_block(value, blockid, sblockid)
        else:
            self.values.append(value)

    def store_values_block(self, value, blockid, sblockid):
        """Add a VALUES in a block. If block exist, add the triples, else, create a new block.

        Same for the sub block

        Parameters
        ----------
        triple : dict
            The triple dict to add
        blockid : int
            Block id
        sblockid : int
            Sub block id
        """
        for block in self.triples_blocks:
            if block["id"] == blockid:
                for sblock in block["sblocks"]:
                    if sblock["id"] == sblockid:
                        sblock["values"].append(value)
                        return
                block["sblocks"].append({
                    "id": sblockid,
                    "triples": [],
                    "filters": [],
                    "values": [value, ]
                })
                return
        self.triples_blocks.append({
            "id": blockid,
            "type": self.get_block_type(blockid),
            "sblocks": [{
                "id": sblockid,
                "triples": [],
                "filters": [],
                "values": [value, ]
            }, ]
        })

    def store_filter_block(self, filtr, blockid, sblockid):
        """Add a FILTER in a block. If block exist, add the triples, else, create a new block.

        Same for the sub block

        Parameters
        ----------
        triple : dict
            The triple dict to add
        blockid : int
            Block id
        sblockid : int
            Sub block id
        """
        for block in self.triples_blocks:
            if block["id"] == blockid:
                for sblock in block["sblocks"]:
                    if sblock["id"] == sblockid:
                        sblock["filters"].append(filtr)
                        return
                block["sblocks"].append({
                    "id": sblockid,
                    "triples": [],
                    "filters": [filtr, ],
                    "values": []
                })
                return
        self.triples_blocks.append({
            "id": blockid,
            "type": self.get_block_type(blockid),
            "sblocks": [{
                "id": sblockid,
                "triples": [],
                "filters": [filtr, ],
                "values": []
            }, ]
        })

    def store_block(self, triple, blockid, sblockid, pblock_ids):
        """Add a triple in a block. If block exist, add the triples, else, create a new block.

        Same for the sub block

        Parameters
        ----------
        triple : dict
            The triple dict to add
        blockid : int
            Block id
        sblockid : int
            Sub block id
        """
        for block in self.triples_blocks:
            if block["id"] == blockid:
                for sblock in block["sblocks"]:
                    if sblock["id"] == sblockid:
                        sblock["triples"].append(triple)
                        return
                block["sblocks"].append({
                    "id": sblockid,
                    "triples": [triple, ],
                    "filters": [],
                    "values": []
                })
                return
        self.triples_blocks.append({
            "id": blockid,
            "type": self.get_block_type(blockid),
            "sblocks": [{
                "id": sblockid,
                "triples": [triple, ],
                "filters": [],
                "values": []
            }, ]
        })

    def replace_variables_in_triples(self, var_to_replace):
        """Replace variables in triples

        Parameters
        ----------
        var_to_replace : list of tuples
            var to replace in triples
        """
        for tpl_var in var_to_replace:
            var_source = tpl_var[0]
            var_target = tpl_var[1]
            for i, triple_dict in enumerate(self.triples):
                for key, value in triple_dict.items():
                    if key not in ["optional", "nested", "nested_start", "nested_end", "form"]:
                        self.triples[i][key] = value.replace(var_source, var_target)
            for i, select in enumerate(self.selects):
                self.selects[i] = select.replace(var_source, var_target)
            for i, filtr in enumerate(self.filters):
                self.filters[i] = filtr.replace(var_source, var_target)

        # uniq lists
        self.triples = Utils.unique(self.triples)
        self.selects = Utils.unique(self.selects)

    def replace_variables_in_blocks(self, var_to_replace):
        """Replace variables in blocks

        Parameters
        ----------
        var_to_replace : list of tuples
            var to replace in block
        """
        for var_source, var_target in var_to_replace:
            # Interate throught blocks
            for nblock, block in enumerate(self.triples_blocks):
                # Iterate over sub-blocks
                for nsblock, sblock in enumerate(block["sblocks"]):
                    # Iterate over triples
                    for ntriple, triple_dict in enumerate(sblock["triples"]):
                        for key, value in triple_dict.items():
                            if key not in ["optional", "nested", "nested_start", "nested_end", "form"]:
                                self.triples_blocks[nblock]["sblocks"][nsblock]["triples"][ntriple][key] = value.replace(var_source, var_target)

                    for i, filtr in enumerate(sblock["filters"]):
                        self.triples_blocks[nblock]["sblocks"][nsblock]["filters"][i] = filtr.replace(var_source, var_target)

                    for i, value in enumerate(sblock["values"]):
                        self.triples_blocks[nblock]["sblocks"][nsblock]["values"][i] = value.replace(var_source, var_target)

                self.triples_blocks[nblock]["sblocks"][nsblock]["triples"] = Utils.unique(self.triples_blocks[nblock]["sblocks"][nsblock]["triples"])

    def get_source_of_special_node(self, special_node_id):
        """Get if of original node of a special one

        Parameters
        ----------
        special_node_id : int
            Special node id

        Returns
        -------
        int or None
            Original node id
        """
        for link in self.json["links"]:
            if link["type"] == "specialLink":
                if link["source"]["id"] == special_node_id:
                    return link["target"]["id"]
                if link["target"]["id"] == special_node_id:
                    return link["source"]["id"]
        return None

    def build_query_from_json(self, preview=False, for_editor=False):
        """Build a sparql query for the json dict of the query builder

        Parameters
        ----------
        preview : bool, optional
            Build a preview query (with LIMIT)
        for_editor : bool, optional
            Remove FROMS and @federate
        """
        entities = []
        attributes = {}
        linked_attributes = []

        self.selects = []

        self.triples = []
        self.triples_blocks = []

        self.values = []
        self.filters = []

        start_end = []
        strands = []

        var_to_replace = []

        # Browse attributes to get entities
        for attr in self.json["attr"]:
            entities = entities + attr["entityUris"]

        entities = list(set(entities))  # uniq list

        # Set graphs in function of entities needed
        self.set_graphs_and_endpoints(entities=entities)

        # self.log.debug(self.json)

        # Browse links (relations)
        for link in self.json["links"]:
            if not link["suggested"]:

                # if link is special, replace the special node variable with its real node
                if link["type"] == "specialLink":
                    special_node = link["source"] if link["source"]["type"] in ("unionNode", "minusNode") else link["target"]
                    real_node = link["target"] if link["source"]["type"] in ("unionNode", "minusNode") else link["source"]

                    var_to_replace.append((
                        self.format_sparql_variable("{}{}_uri".format(special_node["label"], special_node["id"])),
                        self.format_sparql_variable("{}{}_uri".format(real_node["label"], real_node["id"]))
                    ))

                    continue

                source = self.format_sparql_variable("{}{}_uri".format(link["source"]["label"], link["source"]["id"]))
                target = self.format_sparql_variable("{}{}_uri".format(link["target"]["label"], link["target"]["id"]))

                # Check if relation is in a block
                block_id = None
                sblock_id = None
                pblock_ids = (None, None)
                if link["source"]["specialNodeId"] or link["target"]["specialNodeId"]:
                    block_id = link["source"]["specialNodeId"]
                    sblock_id = link["source"]["specialNodeGroupId"] if link["source"]["specialNodeGroupId"] else link["target"]["specialNodeGroupId"]
                    pblock_ids = link["source"]["specialPreviousIds"]

                # Position
                if link["uri"] in ('included_in', 'overlap_with'):

                    # If source of target is a special node, replace the id with the id of the concerned node
                    source_id = link["source"]["id"]
                    target_id = link["target"]["id"]
                    if link["source"]["type"] in ("unionNode", "minusNode"):
                        source_id = self.get_source_of_special_node(link["source"]["id"])
                    if link["target"]["type"] in ("unionNode", "minusNode"):
                        target_id = self.get_source_of_special_node(link["target"]["id"])

                    common_block = self.format_sparql_variable("block_{}_{}".format(link["source"]["id"], link["target"]["id"]))
                    # Get start & end sparql variables
                    for attr in self.json["attr"]:
                        if not attr["faldo"]:
                            continue
                        if attr["nodeId"] == source_id:
                            if attr["faldo"].endswith("faldoStart"):
                                start_end.append(attr["id"])
                                start_1 = self.format_sparql_variable("{}{}_{}".format(attr["entityLabel"], attr["nodeId"], attr["label"]))
                            if attr["faldo"].endswith("faldoEnd"):
                                start_end.append(attr["id"])
                                end_1 = self.format_sparql_variable("{}{}_{}".format(attr["entityLabel"], attr["nodeId"], attr["label"]))
                            if attr["faldo"].endswith("faldoStrand"):
                                strand_1 = self.format_sparql_variable("{}{}_{}_faldoStrand".format(attr["entityLabel"], attr["nodeId"], attr["label"]))
                                strands.append(attr["id"])
                        if attr["nodeId"] == target_id:
                            if attr["faldo"].endswith("faldoStart"):
                                start_end.append(attr["id"])
                                start_2 = self.format_sparql_variable("{}{}_{}".format(attr["entityLabel"], attr["nodeId"], attr["label"]))
                            if attr["faldo"].endswith("faldoEnd"):
                                start_end.append(attr["id"])
                                end_2 = self.format_sparql_variable("{}{}_{}".format(attr["entityLabel"], attr["nodeId"], attr["label"]))
                            if attr["faldo"].endswith("faldoStrand"):
                                strand_2 = self.format_sparql_variable("{}{}_{}_faldoStrand".format(attr["entityLabel"], attr["nodeId"], attr["label"]))
                                strands.append(attr["id"])

                    self.store_triple({
                        "subject": source,
                        "predicate": "askomics:{}".format("includeInReference" if link["sameRef"] else "includeIn"),
                        "object": common_block,
                        "optional": False

                    }, block_id, sblock_id, pblock_ids)

                    self.store_triple({
                        "subject": target,
                        "predicate": "askomics:{}".format("includeInReference" if link["sameRef"] else "includeIn"),
                        "object": common_block,
                        "optional": False

                    }, block_id, sblock_id, pblock_ids)

                    if link["sameStrand"]:
                        var_to_replace.append((strand_1, strand_2))
                    else:
                        strands = []

                    equal_sign = "" if link["strict"] else "="

                    if link["uri"] == "included_in":
                        self.store_filter("FILTER ({start1} >{equalsign} {start2} && {end1} <{equalsign} {end2}) .".format(
                            start1=start_1,
                            start2=start_2,
                            end1=end_1,
                            end2=end_2,
                            equalsign=equal_sign
                        ), block_id, sblock_id, pblock_ids)

                    elif link["uri"] == "overlap_with":
                        self.store_filter("FILTER (({start2} >{equalsign} {start1} && {start2} <{equalsign} {end1}) || ({end2} >{equalsign} {start1} && {end2} <{equalsign} {end1}))".format(
                            start1=start_1,
                            start2=start_2,
                            end1=end_1,
                            end2=end_2,
                            equalsign=equal_sign
                        ), block_id, sblock_id, pblock_ids)

                # Classic relation
                else:
                    # Manage ontology stuff
                    inverse = ""
                    recurrence = ""
                    relation = link["uri"]

                    if relation.startswith("^"):
                        inverse = "^"
                        relation = relation.lstrip("^")

                    if relation.endswith("*"):
                        recurrence = "*"
                        relation = relation.rstrip("*")

                    relation = inverse + "<{}>".format(relation) + recurrence
                    triple = {
                        "subject": source,
                        "predicate": relation,
                        "object": target,
                        "optional": False
                    }

                    self.store_triple(triple, block_id, sblock_id, pblock_ids)

        # Store linked attributes
        for attribute in self.json["attr"]:
            attributes[attribute["id"]] = {
                "label": attribute["label"],
                "entity_label": attribute["entityLabel"],
                "entity_id": attribute["nodeId"]
            }
            if attribute["linked"]:
                linked_attributes.extend((attribute["id"], attribute["linkedWith"]))

        # Browse attributes
        for attribute in self.json["attr"]:
            # Get blockid and sblockid of the attribute node
            block_id, sblock_id, pblock_ids = self.get_block_ids(attribute["nodeId"])

            # URI ---
            if attribute["type"] == "uri":
                subject = self.format_sparql_variable("{}{}_uri".format(attribute["entityLabel"], attribute["nodeId"]))
                predicate = attribute["uri"]
                obj = "<{}>".format(attribute["entityUris"][0])
                if not self.is_bnode(attribute["entityUris"][0], self.json["nodes"]):
                    self.store_triple({
                        "subject": subject,
                        "predicate": predicate,
                        "object": obj,
                        "optional": False
                    }, block_id, sblock_id, pblock_ids)

                if attribute["visible"]:
                    self.selects.append(subject)
                # filters/values
                if attribute["filterValue"] != "" and not attribute["linked"]:
                    filter_value = self.get_uri_filter_value(attribute["filterValue"])
                    if attribute["filterType"] == "regexp":
                        negative_sign = ""
                        if attribute["negative"]:
                            negative_sign = "!"
                            self.store_filter("FILTER ({}regex({}, {}, 'i'))".format(negative_sign, subject, filter_value), block_id, sblock_id, pblock_ids)
                    elif attribute["filterType"] == "exact":
                        if attribute["negative"]:
                            self.store_filter("FILTER (str({}) != {}) .".format(subject, filter_value), block_id, sblock_id, pblock_ids)
                        else:
                            self.store_value("VALUES {} {{ {} }} .".format(subject, filter_value), block_id, sblock_id, pblock_ids)

                if attribute["linked"]:
                    var_2 = self.format_sparql_variable("{}{}_uri".format(
                        attributes[attribute["linkedWith"]]["entity_label"],
                        attributes[attribute["linkedWith"]]["entity_id"]
                    ))
                    var_to_replace.append((subject, var_2))

            if attribute["type"] == "boolean":
                if attribute["visible"] or attribute["filterSelectedValues"] != [] or attribute["id"] in linked_attributes:
                    subject = self.format_sparql_variable("{}{}_uri".format(attribute["entityLabel"], attribute["nodeId"]))
                    predicate = "<{}>".format(attribute["uri"])
                    obj = self.format_sparql_variable("{}{}_{}".format(attribute["entityLabel"], attribute["humanNodeId"], attribute["label"]))

                    self.store_triple({
                        "subject": subject,
                        "predicate": predicate,
                        "object": obj,
                        "optional": True if attribute["optional"] else False
                    }, block_id, sblock_id, pblock_ids)

                    if attribute["visible"]:
                        self.selects.append(obj)

                # values
                if attribute["filterSelectedValues"] != [] and not attribute["optional"] and not attribute["linked"]:
                    uri_val_list = []
                    for value in attribute["filterSelectedValues"]:
                        if value == "true":
                            bool_value = "'true'^^xsd:boolean"
                        else:
                            bool_value = "'false'^^xsd:boolean"
                        value_var = obj
                        uri_val_list.append(bool_value)

                    if uri_val_list:
                        self.store_value("VALUES {} {{ {} }}".format(value_var, ' '.join(uri_val_list)), block_id, sblock_id, pblock_ids)
                if attribute["linked"]:
                    var_2 = self.format_sparql_variable("{}{}_{}".format(
                        attributes[attribute["linkedWith"]]["entity_label"],
                        attributes[attribute["linkedWith"]]["entity_id"],
                        attributes[attribute["linkedWith"]]["label"]
                    ))
                    var_to_replace.append((obj, var_2))

            # Text
            if attribute["type"] == "text":
                if attribute["visible"] or attribute["filterValue"] != "" or attribute["id"] in linked_attributes:
                    subject = self.format_sparql_variable("{}{}_uri".format(attribute["entityLabel"], attribute["nodeId"]))
                    if attribute["uri"] == "rdfs:label":
                        predicate = attribute["uri"]
                    else:
                        predicate = "<{}>".format(attribute["uri"])

                    obj = self.format_sparql_variable("{}{}_{}".format(attribute["entityLabel"], attribute["humanNodeId"], attribute["label"]))

                    self.store_triple({
                        "subject": subject,
                        "predicate": predicate,
                        "object": obj,
                        "optional": True if attribute["optional"] else False
                    }, block_id, sblock_id, pblock_ids)
                    if attribute["visible"]:
                        self.selects.append(obj)
                # filters/values
                if attribute["filterValue"] != "" and not attribute["optional"] and not attribute["linked"]:
                    if attribute["filterType"] == "regexp":
                        negative_sign = ""
                        if attribute["negative"]:
                            negative_sign = "!"
                        self.store_filter("FILTER ({}regex({}, '{}', 'i'))".format(negative_sign, obj, attribute["filterValue"]), block_id, sblock_id, pblock_ids)
                    elif attribute["filterType"] == "exact":
                        if attribute["negative"]:
                            self.store_filter("FILTER (str({}) != '{}') .".format(obj, attribute["filterValue"]), block_id, sblock_id, pblock_ids)
                        else:
                            self.store_value("VALUES {} {{ '{}' }} .".format(obj, attribute["filterValue"]), block_id, sblock_id, pblock_ids)
                if attribute["linked"]:
                    var_2 = self.format_sparql_variable("{}{}_{}".format(
                        attributes[attribute["linkedWith"]]["entity_label"],
                        attributes[attribute["linkedWith"]]["entity_id"],
                        attributes[attribute["linkedWith"]]["label"]
                    ))
                    var_to_replace.append((obj, var_2))

            # Numeric
            if attribute["type"] == "decimal":
                if attribute["visible"] or Utils.check_key_in_list_of_dict(attribute["filters"], "filterValue") or attribute["id"] in start_end or attribute["id"] in linked_attributes:
                    subject = self.format_sparql_variable("{}{}_uri".format(attribute["entityLabel"], attribute["nodeId"]))
                    if attribute["faldo"]:
                        predicate = "faldo:location/faldo:{}/faldo:position".format("begin" if attribute["faldo"].endswith("faldoStart") else "end")
                    else:
                        predicate = "<{}>".format(attribute["uri"])
                    obj = self.format_sparql_variable("{}{}_{}".format(attribute["entityLabel"], attribute["nodeId"], attribute["label"]))
                    self.store_triple({
                        "subject": subject,
                        "predicate": predicate,
                        "object": obj,
                        "optional": True if attribute["optional"] else False
                    }, block_id, sblock_id, pblock_ids)
                    if attribute["visible"]:
                        self.selects.append(obj)
                # filters
                for filtr in attribute["filters"]:
                    if filtr["filterValue"] != "" and not attribute["optional"] and not attribute["linked"]:
                        if filtr['filterSign'] == "=":
                            self.store_value("VALUES {} {{ {} }} .".format(obj, filtr["filterValue"]), block_id, sblock_id, pblock_ids)
                        else:
                            filter_string = "FILTER ( {} {} {} ) .".format(obj, filtr["filterSign"], filtr["filterValue"])
                            self.store_filter(filter_string, block_id, sblock_id, pblock_ids)
                if attribute["linked"]:
                    var_2 = self.format_sparql_variable("{}{}_{}".format(
                        attributes[attribute["linkedWith"]]["entity_label"],
                        attributes[attribute["linkedWith"]]["entity_id"],
                        attributes[attribute["linkedWith"]]["label"]
                    ))
                    var_to_replace.append((obj, var_2))

            if attribute["type"] == "date":
                if attribute["visible"] or Utils.check_key_in_list_of_dict(attribute["filters"], "filterValue") or attribute["id"] in linked_attributes:
                    subject = self.format_sparql_variable("{}{}_uri".format(attribute["entityLabel"], attribute["nodeId"]))
                    predicate = "<{}>".format(attribute["uri"])
                    obj = self.format_sparql_variable("{}{}_{}".format(attribute["entityLabel"], attribute["nodeId"], attribute["label"]))
                    self.store_triple({
                        "subject": subject,
                        "predicate": predicate,
                        "object": obj,
                        "optional": True if attribute["optional"] else False
                    }, block_id, sblock_id, pblock_ids)
                    if attribute["visible"]:
                        self.selects.append(obj)
                # filters
                for filtr in attribute["filters"]:
                    if filtr["filterValue"] and not attribute["optional"] and not attribute["linked"]:
                        # COnvert datetime to date
                        val = filtr["filterValue"].split("T")[0]
                        if filtr['filterSign'] == "=":
                            self.store_value("VALUES {} {{ '{}'^^xsd:date }} .".format(obj, val), block_id, sblock_id, pblock_ids)
                        else:
                            filter_string = "FILTER ( {} {} '{}'^^xsd:date ) .".format(obj, filtr["filterSign"], val)
                            self.store_filter(filter_string, block_id, sblock_id, pblock_ids)
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
                    category_label = self.format_sparql_variable("{}{}_{}".format(attribute["entityLabel"], attribute["humanNodeId"], attribute["label"]))
                    faldo_strand = self.format_sparql_variable("{}{}_{}_faldoStrand".format(attribute["entityLabel"], attribute["nodeId"], attribute["label"]))
                    if attribute["faldo"] and attribute["faldo"].endswith("faldoReference"):
                        category_name = 'faldo:location/faldo:begin/faldo:reference'
                        self.store_triple({
                            "subject": node_uri,
                            "predicate": category_name,
                            "object": category_value_uri,
                            "optional": True if attribute["optional"] else False,
                            "nested_start": True if (attribute["optional"] and attribute["visible"]) else False
                        }, block_id, sblock_id, pblock_ids)
                        if attribute["visible"]:
                            self.store_triple({
                                "subject": category_value_uri,
                                "predicate": "rdfs:label",
                                "object": category_label,
                                "optional": True if attribute["optional"] else False,
                                "nested_end": True if attribute["optional"] else False
                            }, block_id, sblock_id, pblock_ids)
                    elif attribute["faldo"] and attribute["faldo"].endswith("faldoStrand"):
                        category_name = 'faldo:location/faldo:begin/rdf:type'
                        self.store_triple({
                            "subject": node_uri,
                            "predicate": category_name,
                            "object": category_value_uri,
                            "optional": True if attribute["optional"] else False
                        }, block_id, sblock_id, pblock_ids)
                        self.store_triple({
                            "subject": faldo_strand,
                            "predicate": "a",
                            "object": category_value_uri,
                            "optional": True if attribute["optional"] else False
                        }, block_id, sblock_id, pblock_ids)
                        if attribute["visible"]:
                            self.store_triple({
                                "subject": faldo_strand,
                                "predicate": "rdfs:label",
                                "object": category_label,
                                "optional": False
                            }, block_id, sblock_id, pblock_ids)
                        self.store_value("VALUES {} {{ faldo:ReverseStrandPosition faldo:ForwardStrandPosition faldo:BothStrandPosition}} .".format(category_value_uri), block_id, sblock_id, pblock_ids)
                    else:
                        category_name = "<{}>".format(attribute["uri"])
                        self.store_triple({
                            "subject": node_uri,
                            "predicate": category_name,
                            "object": category_value_uri,
                            "optional": True if attribute["optional"] else False,
                            "nested_start": True if (attribute["optional"] and attribute["visible"]) else False
                        }, block_id, sblock_id, pblock_ids)
                        if attribute["visible"]:
                            self.store_triple({
                                "subject": category_value_uri,
                                "predicate": "rdfs:label",
                                "object": category_label,
                                "optional": True if attribute["optional"] else False,
                                "nested_end": True if attribute["optional"] else False
                            }, block_id, sblock_id, pblock_ids)

                    if attribute["visible"]:
                        self.selects.append(category_label)
                # values
                if attribute["filterSelectedValues"] != [] and not attribute["optional"] and not attribute["linked"]:
                    uri_val_list = []
                    if attribute["faldo"] and attribute["faldo"].endswith("faldoStrand"):
                        value_var = faldo_strand
                    else:
                        value_var = category_value_uri
                    uri_val_list = ["<{}>".format(value) for value in attribute["filterSelectedValues"]]
                    if uri_val_list:
                        if attribute["exclude"]:
                            filter_string = "FILTER ( {} NOT IN ( {} ) ) .".format(value_var, " ,".join(uri_val_list))
                            self.store_filter(filter_string, block_id, sblock_id, pblock_ids)
                        else:
                            self.store_value("VALUES {} {{ {} }}".format(value_var, ' '.join(uri_val_list)), block_id, sblock_id, pblock_ids)

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
        self.replace_variables_in_blocks(var_to_replace)
        self.replace_variables_in_triples(var_to_replace)

        # Write the query

        # query is for editor (no froms, no federated)
        if for_editor:
            query = """
SELECT DISTINCT {selects}
WHERE {{
    {triples}
    {blocks}
    {filters}
    {values}
}}
            """.format(
                selects=' '.join(self.selects),
                triples='\n    '.join([self.triple_dict_to_string(triple_dict) for triple_dict in self.triples]),
                blocks='\n    '.join([self.triple_block_to_string(triple_block) for triple_block in self.triples_blocks]),
                filters='\n    '.join(self.filters),
                values='\n    '.join(self.values))

        # Query is federated, add federated lines @federate & @from)
        elif self.federated:
            query = """
{endpoints}
{federated}

SELECT DISTINCT {selects}
WHERE {{
    {triples}
    {blocks}
    {filters}
    {values}
}}
            """.format(
                endpoints=endpoints_string,
                federated=federated_from_string,
                selects=' '.join(self.selects),
                triples='\n    '.join([self.triple_dict_to_string(triple_dict) for triple_dict in self.triples]),
                blocks='\n    '.join([self.triple_block_to_string(triple_block) for triple_block in self.triples_blocks]),
                filters='\n    '.join(self.filters),
                values='\n    '.join(self.values)
            )

        # Query on the local endpoint (add froms)
        elif self.endpoints == [self.local_endpoint_f]:
            query = """
SELECT DISTINCT {selects}
{froms}
WHERE {{
    {triples}
    {blocks}
    {filters}
    {values}
}}
            """.format(
                selects=' '.join(self.selects),
                froms=from_string,
                triples='\n    '.join([self.triple_dict_to_string(triple_dict) for triple_dict in self.triples]),
                blocks='\n    '.join([self.triple_block_to_string(triple_block) for triple_block in self.triples_blocks]),
                filters='\n    '.join(self.filters),
                values='\n    '.join(self.values))

        # Query an external endpoint (no froms)
        else:
            query = """
SELECT DISTINCT {selects}
WHERE {{
    {triples}
    {blocks}
    {filters}
    {values}
}}
            """.format(
                selects=' '.join(self.selects),
                triples='\n    '.join([self.triple_dict_to_string(triple_dict) for triple_dict in self.triples]),
                blocks='\n    '.join([self.triple_block_to_string(triple_block) for triple_block in self.triples_blocks]),
                filters='\n    '.join(self.filters),
                values='\n    '.join(self.values))

        if preview:
            query += "\nLIMIT {}".format(self.settings.getint('triplestore', 'preview_limit'))

        self.sparql = self.prefix_query(textwrap.dedent(query))
