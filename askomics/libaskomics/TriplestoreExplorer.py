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
        filter_user = ""
        if self.logged_user():
            filter_user = " || ?creator = <{}>".format(self.session["user"]["username"])

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
                ?public = <true>{}
            )
        }}
        '''.format(filter_user)

        header, data = query_launcher.process_query(query_builder.prefix_query(query))

        startpoints = []
        entities = []

        for result in data:
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
                if self.str_to_bool(result["public"]):
                    startpoints[index]["public"] = True
                else:
                    startpoints[index]["private"] = True

        return startpoints

    def get_abstraction(self):

        return self.get_abstraction_new()
        # return self.get_abstraction_deprecated()

    def get_abstraction_new(self):
        """Get user abstraction from the triplestore

        Returns
        -------
        list
            AskOmics abstraction
        """
        filter_user = ""
        if self.logged_user():
            filter_user = " || ?creator = <{}>".format(self.session["user"]["username"])

        query_launcher = SparqlQueryLauncher(self.app, self.session)
        query_builder = SparqlQueryBuilder(self.app, self.session)

        query = '''
        SELECT DISTINCT ?graph ?entity_uri ?entity_label ?node_type ?attribute_uri ?attribute_label ?attribute_type ?property_uri ?property_type ?property_label ?range_uri ?category_value_uri ?category_value_label
        WHERE {{
            # Graphs
            ?graph :public ?public .
            ?graph dc:creator ?creator .
            GRAPH ?graph {{
                # Entities
                ?entity_uri a ?node_type .
                VALUES ?node_type {{ :entity :bnode }} .
                OPTIONAL {{
                    ?entity_uri rdfs:label ?entity_label .
                }}
                # Attributes
                OPTIONAL {{
                    ?attribute_uri a owl:DatatypeProperty .
                    ?attribute_uri rdfs:label ?attribute_label .
                    ?attribute_uri rdfs:domain ?entity_uri .
                    ?attribute_uri rdfs:range ?attribute_type .
                }}
                # Property (relations and categories)
                OPTIONAL {{
                    ?property_uri a owl:ObjectProperty .
                    ?property_uri rdfs:label ?property_label .
                    ?property_uri rdfs:domain ?entity_uri .
                    ?property_uri rdfs:range ?range_uri .
                    ?property_uri a ?property_type .
                }}
                # Categories (DK)
                OPTIONAL {{
                    ?range_uri askomics:category ?category_value_uri .
                    ?category_value_uri rdfs:label ?category_value_label .
                }}
            }}
            FILTER (
                ?public = <true>{}
            )
        }}
        '''.format(filter_user)

        header, data = query_launcher.process_query(query_builder.prefix_query(query))

        entities_list = []  # list of entity uri
        attributes_list = []
        relations_list = []

        entities = []  # list of entity dict
        attributes = []
        relations = []

        abstraction = []

        for result in data:
            if result["entity_uri"] not in entities_list:
                # New entity
                entities_list.append(result["entity_uri"])
                # Uri, graph and label
                label = "" if "entity_label" not in result else result["entity_label"]
                node_type = "bnode" if result["node_type"] == "{}bnode".format(self.settings.get("triplestore", "prefix")) else "node"
                entity = {
                    "uri": result["entity_uri"],
                    "type": node_type,
                    "label": label,
                    "graphs": [result["graph"]],
                }

                entities.append(entity)
            else:
                # if graph is different, store it
                index_entity = entities_list.index(result['entity_uri'])
                if result["graph"] not in entities[index_entity]["graphs"]:
                    entities[index_entity]["graphs"].append(result["graph"])

            # Get index of the current entity
            index_entity = entities_list.index(result['entity_uri'])

            # Attributes
            if "attribute_uri" in result and "attribute_label" in result:
                attr_tpl = (result["attribute_uri"], result["entity_uri"])
                if attr_tpl not in attributes_list:
                    attributes_list.append(attr_tpl)
                    attribute = {
                        "uri": result["attribute_uri"],
                        "label": result["attribute_label"],
                        "graphs": [result["graph"], ],
                        "entityUri": result["entity_uri"],
                        "type": result["attribute_type"]
                    }
                    attributes.append(attribute)
                else:
                    # if graph is different, store it
                    index_attribute = attributes_list.index(attr_tpl)
                    if result["graph"] not in attributes[index_attribute]["graphs"]:
                        attributes[index_attribute]["graphs"].append(result["graph"])

                index_attribute = attributes_list.index(attr_tpl)

            # Categories
            if "property_uri" in result and result["property_type"] == "{}AskomicsCategory".format(self.settings.get("triplestore", "prefix")):
                attr_tpl = (result["property_uri"], result["entity_uri"])
                if attr_tpl not in attributes_list:
                    attributes_list.append(attr_tpl)
                    attribute = {
                        "uri": result["property_uri"],
                        "label": result["property_label"],
                        "graphs": [result["graph"], ],
                        "entityUri": result["entity_uri"],
                        "type": result["property_type"],
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

            # Relation
            if "property_uri" in result and result["property_type"] == "{}AskomicsRelation".format(self.settings.get("triplestore", "prefix")):
                rel_tpl = (result["property_uri"], result["entity_uri"], result["range_uri"])
                if rel_tpl not in relations_list:
                    relations_list.append(rel_tpl)
                    relation = {
                        "uri": result["property_uri"],
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

        abstraction = {
            "entities": entities,
            "attributes": attributes,
            "relations": relations
        }

        return abstraction

    def get_abstraction_deprecated(self):
        """Get user abstraction from the triplestore

        Returns
        -------
        list
            AskOmics abstraction
        """
        filter_user = ""
        if self.logged_user():
            filter_user = " || ?creator = <{}>".format(self.session["user"]["username"])

        query_launcher = SparqlQueryLauncher(self.app, self.session)
        query_builder = SparqlQueryBuilder(self.app, self.session)

        query = '''
        SELECT DISTINCT ?graph ?entity_uri ?entity_label ?attribute_uri ?attribute_label ?attribute_type ?property_uri ?property_type ?property_label ?range_uri ?category_value_uri ?category_value_label
        WHERE {{
            # Graphs
            ?graph :public ?public .
            ?graph dc:creator ?creator .
            GRAPH ?graph {{
                # Entities
                ?entity_uri a :entity .
                ?entity_uri a :startPoint .
                ?entity_uri rdfs:label ?entity_label .
                # Attributes
                OPTIONAL {{
                    ?attribute_uri a owl:DatatypeProperty .
                    ?attribute_uri rdfs:label ?attribute_label .
                    ?attribute_uri rdfs:domain ?entity_uri .
                    ?attribute_uri rdfs:range ?attribute_type .
                }}
                # Property (relations and categories)
                OPTIONAL {{
                    ?property_uri a owl:ObjectProperty .
                    ?property_uri rdfs:label ?property_label .
                    ?property_uri rdfs:domain ?entity_uri .
                    ?property_uri rdfs:range ?range_uri .
                    ?property_uri a ?property_type .
                }}
                # Categories (DK)
                OPTIONAL {{
                    ?range_uri askomics:category ?category_value_uri .
                    ?category_value_uri rdfs:label ?category_value_label .
                }}
            }}
            FILTER (
                ?public = <true>{}
            )
        }}
        '''.format(filter_user)

        header, data = query_launcher.process_query(query_builder.prefix_query(query))

        abstraction = []
        entities = []

        for result in data:
            if result["entity_uri"] not in entities:
                # New entity
                entities.append(result["entity_uri"])
                # Uri, graph and label
                entity = {
                    "uri": result["entity_uri"],
                    "label": result["entity_label"],
                    "graphs": [result["graph"]],
                    "attributes": [],
                    "relations": []
                }

                abstraction.append(entity)

            # Get index of the current entity
            index = entities.index(result['entity_uri'])

            # DatatypeProperty (Attributes)
            if "attribute_uri" in result and "attribute_label" in result:
                # Create if not exist
                if not self.check_presence(result["attribute_uri"], abstraction[index]["attributes"]):
                    attribute = {
                        "uri": result["attribute_uri"],
                        "label": result["attribute_label"],
                        "type": result["attribute_type"]
                    }
                    abstraction[index]["attributes"].append(attribute)

            # Category
            if "property_uri" in result and result["property_type"] == "http://www.semanticweb.org/user/ontologies/2018/1#AskomicsCategory":
                # create if not exist
                if not self.check_presence(result["property_uri"], abstraction[index]["attributes"]):
                    category = {
                        "uri": result["property_uri"],
                        "label": result["property_label"],
                        "type": result["property_type"],
                        "values": [{
                            "uri": result["category_value_uri"],
                            "label": result["category_value_label"]
                        }]
                    }
                    abstraction[index]["attributes"].append(category)
                else:
                    # Add other category value
                    # Get index of attribute
                    index_attribute = self.get_attribute_index(result["property_uri"], abstraction[index]["attributes"])

                    if not self.check_presence(result["category_value_uri"], abstraction[index]["attributes"][index_attribute]["values"]):
                        # add the new value
                        value = {
                            "uri": result["category_value_uri"],
                            "label": result["category_value_label"]
                        }
                        abstraction[index]["attributes"][index_attribute]["values"].append(value)

            # Relation
            if "property_uri" in result and result["property_type"] == "http://www.semanticweb.org/user/ontologies/2018/1#AskomicsRelation":
                # create if not exist
                if not self.check_presence(result["property_uri"], abstraction[index]["relations"]):
                    object_property = {
                        "uri": result["property_uri"],
                        "label": result["property_label"],
                        "target": result["range_uri"]
                    }
                    abstraction[index]["relations"].append(object_property)

        return abstraction

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
