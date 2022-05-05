import tld
import json
from urllib.parse import urlparse

from askomics.libaskomics.Database import Database
from askomics.libaskomics.Params import Params
from askomics.libaskomics.SparqlQuery import SparqlQuery
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

    def get_graph_of_user(self, username):
        """get all graph of a user

        Parameters
        ----------
        username : string
            Username

        Returns
        -------
        list
            List of graphs
        """
        query_launcher = SparqlQueryLauncher(self.app, self.session)
        query_builder = SparqlQuery(self.app, self.session)

        query = """
        SELECT DISTINCT ?graph
        WHERE {{
            ?graph dc:creator <{}> .
        }}
        """.format(username)

        header, data = query_launcher.process_query(query_builder.prefix_query(query))

        graphs = []
        for result in data:
            graphs.append(result["graph"])
        return graphs

    def get_all_graphs(self):
        """get all graph of a user

        Returns
        -------
        list
            List of graphs
        """

        query_launcher = SparqlQueryLauncher(self.app, self.session)
        query_builder = SparqlQuery(self.app, self.session)

        query = """
        SELECT DISTINCT ?graph
        WHERE {{
            ?graph dc:creator ?user .
        }}
        """

        header, data = query_launcher.process_query(query_builder.prefix_query(query))

        graphs = []
        for result in data:
            graphs.append(result["graph"])
        return graphs

    def update_base_url(self, graph, old_url, new_url):
        """Update base url for a graph
        Parameters
        ----------
        graph : string
            Graph to update
        old_url : string
            Old base_url
        new_url : string
            New base_url

        Returns
        -------
        list
            List of graphs
        """

        query_launcher = SparqlQueryLauncher(self.app, self.session)
        query_builder = SparqlQuery(self.app, self.session)

        query = """
        WITH <{0}>
        DELETE{{
            ?s ?p ?o
        }}
        INSERT{{
            ?s2 ?p2 ?o2
        }}
        WHERE {{
            ?s ?p ?o
            FILTER(REGEX(?s, '{1}', 'i') || REGEX(?p, '{1}', 'i') || REGEX(?o, '{1}', 'i')) .
            BIND(IF (isURI(?o), URI(REPLACE(STR(?o), '{1}', '{2}')), ?o) AS ?o2) .
            BIND(IF (isURI(?s), URI(REPLACE(STR(?s), '{1}', '{2}')), ?s) AS ?s2) .
            BIND(IF (isURI(?p), URI(REPLACE(STR(?p), '{1}', '{2}')), ?p) AS ?p2) .
        }}
        """.format(graph, old_url, new_url)

        header, data = query_launcher.process_query(query_builder.prefix_query(query))

    def get_startpoints(self):
        """Get public and user startpoints

        Returns
        -------
        list
            Startpoints
        """
        filter_user = ""
        if not self.settings.get("askomics", "single_tenant", fallback=False):
            filter_user = '''
            FILTER (
                ?public = <true>{}
            )
            '''
            if self.logged_user():
                filter_user.format(" || ?creator = <{}>".format(self.session["user"]["username"]))

        query_launcher = SparqlQueryLauncher(self.app, self.session)
        query_builder = SparqlQuery(self.app, self.session)

        query = '''
        SELECT DISTINCT ?endpoint ?graph ?entity ?entity_label ?creator ?public
        WHERE {{
            ?graph askomics:public ?public .
            ?graph dc:creator ?creator .
            GRAPH ?graph {{
                ?graph prov:atLocation ?endpoint .
                ?entity a askomics:entity .
                ?entity a askomics:startPoint .
                ?entity rdfs:label ?entity_label .
            }}
            {}
        }}
        '''.format(filter_user)

        header, data = query_launcher.process_query(query_builder.prefix_query(query))

        startpoints = []
        entities = []

        for result in data:

            if result["endpoint"] == self.settings.get("triplestore", "endpoint"):
                endpoint_name = "local"
            else:
                try:
                    endpoint_name = tld.get_fld(result["endpoint"]).split('.')[0]
                except Exception:
                    endpoint_name = urlparse(result["endpoint"]).netloc

            if result["entity"] not in entities:
                # new entity
                entities.append(result['entity'])
                startpoint = {
                    "entity": result["entity"],
                    "entity_label": result["entity_label"],
                    "graphs": [{
                        "uri": result["graph"],
                        "public": result["public"],
                        "creator": result["creator"]
                    }],
                    "endpoints": [{"url": result["endpoint"], "name": endpoint_name}],
                    "public": self.str_to_bool(result["public"]),
                    "private": not self.str_to_bool(result["public"])
                }
                startpoints.append(startpoint)
            else:
                # update existing entity
                index = entities.index(result['entity'])
                graph = {
                    "uri": result["graph"],
                    "public": result["public"],
                    "creator": result["creator"]
                }
                startpoints[index]["graphs"].append(graph)
                startpoints[index]["endpoints"].append({"url": result["endpoint"], "name": endpoint_name})
                if self.str_to_bool(result["public"]):
                    startpoints[index]["public"] = True
                else:
                    startpoints[index]["private"] = True

        return startpoints

    def get_abstraction(self):
        """Get AskOmics Abstraction

        Returns
        -------
        dict
            AskOmics abstraction
        """
        insert, abstraction = self.get_cached_asbtraction()

        single_tenant = self.settings.get("askomics", "single_tenant", fallback=False)

        # No abstraction entry in database, create it
        if not abstraction:
            abstraction = {
                "entities": self.get_abstraction_entities(single_tenant),
                "attributes": self.get_abstraction_attributes(single_tenant),
                "relations": self.get_abstraction_relations(single_tenant)
            }

            # Cache abstraction in DB, only for logged users
            if "user" in self.session:
                self.cache_asbtraction(abstraction, insert)

        return abstraction

    def get_cached_asbtraction(self):
        """Get cached abstraction from database

        Returns
        -------
        (bool, dict):
            bool: True if no row exist, else False if row exist
            dict: {} if no abstraction, else, return abstraction

        """
        if "user" not in self.session:
            return True, {}

        database = Database(self.app, self.session)

        query = """
        SELECT abstraction
        FROM abstraction
        WHERE user_id=?
        """
        results = database.execute_sql_query(query, (self.session["user"]["id"], ))

        if results:
            if results[0][0]:
                return False, json.loads(results[0][0])
            else:
                return False, {}
        return True, {}

    def cache_asbtraction(self, abstraction, insert):
        """Summary

        Parameters
        ----------
        abstraction : TYPE
            Description
        insert : bool, optional
            Description
        """
        database = Database(self.app, self.session)

        if insert:
            query = """
            INSERT INTO abstraction VALUES (
                NULL,
                ?,
                ?
            )
            """
            database.execute_sql_query(query, (self.session["user"]["id"], json.dumps(abstraction)))
        else:
            query = """
            UPDATE abstraction SET
            abstraction=?
            WHERE user_id=?
            """
            database.execute_sql_query(query, (json.dumps(abstraction), self.session["user"]["id"]))

    def uncache_abstraction(self, public=True, force=False):
        """Remove cached abstraction from database

        Parameters
        ----------
        public : bool, optional
            Remove for all users if True, else, for logged user only
        """
        if force:
            public = True

        if "user" in self.session or force:
            database = Database(self.app, self.session)

            sub_query = "WHERE user_id=?" if not public else ""
            sql_var = (self.session["user"]["id"], ) if not public else ()

            query = """
            UPDATE abstraction SET
            abstraction=NULL
            {}
            """.format(sub_query)

            database.execute_sql_query(query, sql_var)

    def get_abstraction_entities(self, single_tenant=False):
        """Get abstraction entities

        Returns
        -------
        list
            List of entities available
        """

        filter_user = ""
        if not single_tenant:
            filter_user = '''
            FILTER (
                ?public = <true>{}
            )
            '''
            if self.logged_user():
                filter_user.format(" || ?creator = <{}>".format(self.session["user"]["username"]))

        query_launcher = SparqlQueryLauncher(self.app, self.session)
        query_builder = SparqlQuery(self.app, self.session)

        query = '''
        SELECT DISTINCT ?endpoint ?graph ?entity_uri ?entity_type ?entity_faldo ?entity_label ?have_no_label
        WHERE {{
            ?graph askomics:public ?public .
            ?graph dc:creator ?creator .
            GRAPH ?graph {{
                ?graph prov:atLocation ?endpoint .
                ?entity_uri a ?entity_type .
                VALUES ?entity_type {{ askomics:entity askomics:bnode }} .
                # Faldo
                OPTIONAL {{
                    ?entity_uri a ?entity_faldo .
                    VALUES ?entity_faldo {{ askomics:faldo }} .
                }}
                # Label
                OPTIONAL {{ ?entity_uri rdfs:label ?entity_label . }}
                OPTIONAL {{ ?entity_uri askomics:instancesHaveNoLabels ?have_no_label . }}
            }}
            {}
        }}
        '''.format(filter_user)

        header, data = query_launcher.process_query(query_builder.prefix_query(query))

        entities_list = []  # list of entity uri
        entities = []  # list of entity dict

        for result in data:
            if result["entity_uri"] not in entities_list:
                # New entity
                entities_list.append(result["entity_uri"])
                # Uri, graph and label
                label = "" if "entity_label" not in result else result["entity_label"]
                entity_type = "bnode" if result["entity_type"] == "{}bnode".format(self.settings.get("triplestore", "namespace_internal")) else "node"
                entity = {
                    "uri": result["entity_uri"],
                    "type": entity_type,
                    "label": label,
                    "instancesHaveLabels": True if "have_no_label" not in result else False if result["have_no_label"] == "1" else True,
                    "faldo": True if "entity_faldo" in result else False,
                    "endpoints": [result["endpoint"]],
                    "graphs": [result["graph"]],
                }

                entities.append(entity)
            else:
                # if graph is different, store it
                index_entity = entities_list.index(result['entity_uri'])
                if result["graph"] not in entities[index_entity]["graphs"]:
                    entities[index_entity]["graphs"].append(result["graph"])
                # If endpoint is different, store it
                if result["endpoint"] not in entities[index_entity]["endpoints"]:
                    entities[index_entity]["endpoints"].append(result["endpoint"])

        return entities

    def get_abstraction_attributes(self, single_tenant=False):
        """Get user abstraction attributes from the triplestore

        Returns
        -------
        list
            AskOmics attributes
        """
        filter_user = ""
        if not single_tenant:
            filter_user = '''
            FILTER (
                ?public = <true>{}
            )
            '''
            if self.logged_user():
                filter_user.format(" || ?creator = <{}>".format(self.session["user"]["username"]))

        litterals = (
            "http://www.w3.org/2001/XMLSchema#string",
            "http://www.w3.org/2001/XMLSchema#decimal",
            "http://www.w3.org/2001/XMLSchema#boolean",
            "http://www.w3.org/2001/XMLSchema#date"
        )

        query_launcher = SparqlQueryLauncher(self.app, self.session)
        query_builder = SparqlQuery(self.app, self.session)

        query = '''
        SELECT DISTINCT ?graph ?entity_uri ?attribute_uri ?attribute_type ?attribute_faldo ?attribute_label ?attribute_range ?category_value_uri ?category_value_label
        WHERE {{
            # Graphs
            ?graph askomics:public ?public .
            ?graph dc:creator ?creator .
            GRAPH ?graph {{
                ?attribute_uri a ?attribute_type .
                VALUES ?attribute_type {{ owl:DatatypeProperty askomics:AskomicsCategory }}
                ?attribute_uri rdfs:label ?attribute_label .
                ?attribute_uri rdfs:range ?attribute_range .
                # Faldo
                OPTIONAL {{
                    ?attribute_uri a ?attribute_faldo .
                    VALUES ?attribute_faldo {{ askomics:faldoStart askomics:faldoEnd askomics:faldoStrand askomics:faldoReference }}
                }}
                # Categories (DK)
                OPTIONAL {{
                    ?attribute_range askomics:category ?category_value_uri .
                    ?category_value_uri rdfs:label ?category_value_label .
                }}
            }}
            # Attribute of entity (or motherclass of entity)
            {{
                ?attribute_uri rdfs:domain ?mother .
                ?entity_uri rdfs:subClassOf ?mother .
            }} UNION {{
                ?attribute_uri rdfs:domain ?entity_uri .
            }}
            {}
        }}
        '''.format(filter_user)

        header, data = query_launcher.process_query(query_builder.prefix_query(query))
        attributes_list = []

        attributes = []

        for result in data:
            # Attributes
            if "attribute_uri" in result and "attribute_label" in result and result["attribute_type"] != "{}AskomicsCategory".format(self.settings.get("triplestore", "namespace_internal")) and result["attribute_range"] in litterals:
                attr_tpl = (result["attribute_uri"], result["entity_uri"])
                if attr_tpl not in attributes_list:
                    attributes_list.append(attr_tpl)
                    attribute = {
                        "uri": result["attribute_uri"],
                        "label": result["attribute_label"],
                        "graphs": [result["graph"], ],
                        "entityUri": result["entity_uri"],
                        "type": result["attribute_range"],
                        "faldo": result["attribute_faldo"] if "attribute_faldo" in result else None,
                        "categories": []
                    }
                    attributes.append(attribute)
                else:
                    # if graph is different, store it
                    index_attribute = attributes_list.index(attr_tpl)
                    if result["graph"] not in attributes[index_attribute]["graphs"]:
                        attributes[index_attribute]["graphs"].append(result["graph"])

                index_attribute = attributes_list.index(attr_tpl)

            # Categories
            if "attribute_uri" in result and result["attribute_type"] == "{}AskomicsCategory".format(self.settings.get("triplestore", "namespace_internal")) and "category_value_uri" in result:
                attr_tpl = (result["attribute_uri"], result["entity_uri"])
                if attr_tpl not in attributes_list:
                    attributes_list.append(attr_tpl)
                    attribute = {
                        "uri": result["attribute_uri"],
                        "label": result["attribute_label"],
                        "graphs": [result["graph"], ],
                        "entityUri": result["entity_uri"],
                        "type": result["attribute_type"],
                        "faldo": result["attribute_faldo"] if "attribute_faldo" in result else None,
                        "categories": [{
                            "uri": result["category_value_uri"],
                            "label": result["category_value_label"]
                        }]
                    }
                    attributes.append(attribute)
                else:
                    # if graph diff, store it
                    index_attribute = attributes_list.index(attr_tpl)
                    if result["graph"] not in attributes[index_attribute]["graphs"]:
                        attributes[index_attribute]["graphs"].append(result["graph"])
                    # Store value if new
                    value = {
                        "uri": result["category_value_uri"],
                        "label": result["category_value_label"]
                    }
                    if value not in attributes[index_attribute]["categories"]:
                        attributes[index_attribute]["categories"].append(value)

        return attributes

    def get_abstraction_relations(self, single_tenant=False):
        """Get user abstraction relations from the triplestore

        Returns
        -------
        list
            Relations
        """
        filter_user = ""
        if not single_tenant:
            filter_user = '''
            FILTER (
                ?public = <true>{}
            )
            '''
            if self.logged_user():
                filter_user.format(" || ?creator = <{}>".format(self.session["user"]["username"]))

        query_launcher = SparqlQueryLauncher(self.app, self.session)
        query_builder = SparqlQuery(self.app, self.session)

        query = '''
        SELECT DISTINCT ?graph ?entity_uri ?entity_faldo ?entity_label ?node ?node_type ?attribute_uri ?attribute_faldo ?attribute_label ?attribute_range ?property_uri ?property_faldo ?property_label ?range_uri ?category_value_uri ?category_value_label
        WHERE {{
            # Graphs
            ?graph askomics:public ?public .
            ?graph dc:creator ?creator .
            GRAPH ?graph {{
                # Property (relations and categories)
                ?node a owl:ObjectProperty .
                ?node a askomics:AskomicsRelation .
                ?node rdfs:label ?property_label .
                ?node rdfs:range ?range_uri .
                # Retrocompatibility
                OPTIONAL {{?node askomics:uri ?property_uri}}
            }}
            # Relation of entity (or motherclass of entity)
            {{
                ?node rdfs:domain ?mother .
                ?entity_uri rdfs:subClassOf ?mother .
            }} UNION {{
                ?node rdfs:domain ?entity_uri .
            }}
            {}
        }}
        '''.format(filter_user)

        header, data = query_launcher.process_query(query_builder.prefix_query(query))

        relations_list = []
        relations = []
        for result in data:
            # Relation
            if "node" in result:
                # Retrocompatibility
                property_uri = result.get("property_uri", result["node"])
                rel_tpl = (property_uri, result["entity_uri"], result["range_uri"])
                if rel_tpl not in relations_list:
                    relations_list.append(rel_tpl)
                    relation = {
                        "uri": property_uri,
                        "label": result["property_label"],
                        "graphs": [result["graph"], ],
                        "source": result["entity_uri"],
                        "target": result["range_uri"]
                    }
                    relations.append(relation)
                else:
                    # if graph is diff, append it
                    index_relation = relations_list.index(rel_tpl)
                    if result["graph"] not in relations[index_relation]["graphs"]:
                        relations[index_relation]["graphs"].append(result["graph"])

        return relations

    def get_attribute_index(self, uri, attribute_list):
        """Get attribute index

        Parameters
        ----------
        uri : string
            uri of the attribute
        attribute_list : list
            list of attributes

        Returns
        -------
        int
            Index of the given uri in the list
        """
        index = 0
        for attribute in attribute_list:
            if attribute["uri"] == uri:
                return index
            index += 1

    def check_presence(self, uri, list_of_things):
        """Check if an uri is present in a list of dict

        Parameters
        ----------
        uri : string
            the uri to test
        list_of_things : list
            the list of dict['uri']

        Returns
        -------
        bool
            True if the uri is present
        """
        for things in list_of_things:
            if things["uri"] == uri:
                return True
        return False
