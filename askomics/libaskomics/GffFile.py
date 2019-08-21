import rdflib

from BCBio.GFF import GFFExaminer
from BCBio import GFF

from askomics.libaskomics.File import File


class GffFile(File):
    """RDF (turtle) File

    Attributes
    ----------
    public : bool
        Public or private dataset
    """

    def __init__(self, app, session, file_info, host_url=None):
        """init

        Parameters
        ----------
        app : Flask
            Flask app
        session :
            AskOmics session
        file_info : dict
            file info
        host_url : None, optional
            AskOmics url
        """
        File.__init__(self, app, session, file_info, host_url)

        self.entities = []
        self.entities_to_integrate = []

        self.category_values = {}

        self.attributes = {}

        self.attribute_abstraction = []

    def set_preview(self):
        """Summary"""
        exam = GFFExaminer()
        handle = open(self.path, encoding="utf-8", errors="ignore")
        gff_type = exam.available_limits(handle)['gff_type']
        for entity in gff_type:
            self.entities.append(entity[0])

        handle.close()

    def get_preview(self):
        """Get gff file preview (list of entities)

        Returns
        -------
        dict
            Return info about the file
        """
        return {
            'type': self.type,
            'id': self.id,
            'name': self.name,
            'data': {
                'entities': self.entities
            }
        }

    def integrate(self, entities, public=True):
        """Integrate GFF file

        Parameters
        ----------
        entities : List
            Entities to integrate
        public : bool, optional
            Insert in public dataset
        """
        self.public = public
        self.entities_to_integrate = entities

        File.integrate(self)

    def get_rdf_abstraction_domain_knowledge(self):
        """Get the abstraction and domain knowledge

        Returns
        -------
        Graph
            Abstraction and domain knowledge
        """
        rdf_graph = self.rdf_graph()

        # Abstraction
        for entity in self.entities_to_integrate:
            rdf_graph.add((self.askomics_prefix[self.format_uri(entity, remove_space=True)], rdflib.RDF.type, self.askomics_prefix[self.format_uri("entity")]))
            rdf_graph.add((self.askomics_prefix[self.format_uri(entity, remove_space=True)], rdflib.RDF.type, self.askomics_prefix[self.format_uri("startPoint")]))
            rdf_graph.add((self.askomics_prefix[self.format_uri(entity, remove_space=True)], rdflib.RDF.type, rdflib.OWL["Class"]))
            rdf_graph.add((self.askomics_prefix[self.format_uri(entity, remove_space=True)], rdflib.RDFS.label, rdflib.Literal(entity)))

        for attribute in self.attribute_abstraction:
            for attr_type in attribute["type"]:
                rdf_graph.add((attribute["uri"], rdflib.RDF.type, attr_type))
            rdf_graph.add((attribute["uri"], rdflib.RDFS.label, attribute["label"]))
            rdf_graph.add((attribute["uri"], rdflib.RDFS.domain, attribute["domain"]))
            rdf_graph.add((attribute["uri"], rdflib.RDFS.range, attribute["range"]))

            # Domain Knowledge
            if "values" in attribute.keys():
                for value in attribute["values"]:
                    rdf_graph.add((self.askomics_prefix[self.format_uri(value)], rdflib.RDF.type, self.askomics_prefix[self.format_uri("{}CategoryValue".format(attribute["label"]))]))
                    rdf_graph.add((self.askomics_prefix[self.format_uri(value)], rdflib.RDFS.label, rdflib.Literal(value)))
                    rdf_graph.add((self.askomics_prefix[self.format_uri("{}Category".format(attribute["label"]))], self.askomics_namespace[self.format_uri("category")], self.askomics_prefix[self.format_uri(value)]))

        return rdf_graph

    def generate_rdf_content(self):
        """Generator of the rdf content

        Yields
        ------
        Graph
            Rdf content
        """
        handle = open(self.path, 'r', encoding='utf-8')
        limit = dict(gff_type=self.entities_to_integrate)

        indexes = {}
        attribute_list = []

        for rec in GFF.parse(handle, limit_info=limit, target_lines=1):
            # Loop on entities
            for feature in rec.features:

                # Entity type
                entity_type = self.askomics_prefix[self.format_uri(feature.type, remove_space=True)]

                # TODO: faldo??

                rdf_graph = self.rdf_graph()

                # Entity
                if not feature.id:
                    if "ID" not in feature.qualifiers.keys():
                        # index
                        if feature.type in indexes:
                            indexes[feature.type] += 1
                            index = indexes[feature.type]
                        else:
                            indexes[feature.type] = 1
                            index = 1
                        entity = self.askomics_prefix[self.format_uri("{}_{}".format(str(feature.type), str(index)))]
                        entity_label = "{}_{}".format(str(feature.type), str(index))
                    else:
                        entity = self.askomics_prefix[self.format_uri(feature.qualifiers["ID"][0])]
                        entity_label = feature.qualifiers["ID"][0]
                else:
                    entity = self.askomics_prefix[self.format_uri(feature.id)]
                    entity_label = feature.id

                rdf_graph.add((entity, rdflib.RDF.type, entity_type))
                rdf_graph.add((entity, rdflib.RDFS.label, rdflib.Literal(entity_label)))

                # Chrom
                self.category_values["chromosome"] = {rec.id, }
                relation = self.askomics_prefix[self.format_uri("chromosome")]
                attribute = self.askomics_prefix[self.format_uri(rec.id)]
                rdf_graph.add((entity, relation, attribute))

                if (feature.type, "chromosome") not in attribute_list:
                    attribute_list.append((feature.type, "chromosome"))
                    self.attribute_abstraction.append({
                        "uri": self.askomics_prefix[self.format_uri("chromosome")],
                        "label": rdflib.Literal("chromosome"),
                        "type": [self.askomics_prefix[self.format_uri("AskomicsCategory")], rdflib.OWL.ObjectProperty],
                        "domain": entity_type,
                        "range": self.askomics_prefix[self.format_uri("{}Category".format("chromosome"))],
                        "values": [rec.id]
                    })
                else:
                    # add the value
                    for at in self.attribute_abstraction:
                        if at["uri"] == self.askomics_prefix[self.format_uri("chromosome")] and at["domain"] == entity_type and rec.id not in at["values"]:
                            at["values"].append(rec.id)

                # Start
                relation = self.askomics_prefix[self.format_uri("start")]
                attribute = rdflib.Literal(self.convert_type(feature.location.start))
                rdf_graph.add((entity, relation, attribute))

                if (feature.type, "start") not in attribute_list:
                    attribute_list.append((feature.type, "start"))
                    self.attribute_abstraction.append({
                        "uri": self.askomics_prefix[self.format_uri("start")],
                        "label": rdflib.Literal("start"),
                        "type": [rdflib.OWL.DatatypeProperty],
                        "domain": entity_type,
                        "range": rdflib.XSD.decimal
                    })

                # End
                relation = self.askomics_prefix[self.format_uri("end")]
                attribute = rdflib.Literal(self.convert_type(feature.location.end))
                rdf_graph.add((entity, relation, attribute))

                if (feature.type, "end") not in attribute_list:
                    attribute_list.append((feature.type, "end"))
                    self.attribute_abstraction.append({
                        "uri": self.askomics_prefix[self.format_uri("end")],
                        "label": rdflib.Literal("end"),
                        "type": [rdflib.OWL.DatatypeProperty],
                        "domain": entity_type,
                        "range": rdflib.XSD.decimal
                    })

                # Strand
                if feature.location.strand == 1:
                    self.category_values["strand"] = {"+", }
                    relation = self.askomics_prefix[self.format_uri("strand")]
                    attribute = self.askomics_prefix[self.format_uri("+")]
                    rdf_graph.add((entity, relation, attribute))
                elif feature.location.strand == -1:
                    self.category_values["strand"] = {"-", }
                    relation = self.askomics_prefix[self.format_uri("strand")]
                    attribute = self.askomics_prefix[self.format_uri("-")]
                    rdf_graph.add((entity, relation, attribute))

                if (feature.type, "strand") not in attribute_list:
                    attribute_list.append((feature.type, "chromosome"))
                    self.attribute_abstraction.append({
                        "uri": self.askomics_prefix[self.format_uri("strand")],
                        "label": rdflib.Literal("strand"),
                        "type": [self.askomics_prefix[self.format_uri("AskomicsCategory")], rdflib.OWL.ObjectProperty],
                        "domain": entity_type,
                        "range": self.askomics_prefix[self.format_uri("{}Category".format("strand"))],
                        "values": ["+", "-"]
                    })

                # Qualifiers (9th columns)
                for qualifier_key, qualifier_value in feature.qualifiers.items():

                    for value in qualifier_value:

                        if qualifier_key in ("Parent", "Derives_from"):
                            relation = self.askomics_prefix[self.format_uri(qualifier_key)]
                            attribute = self.askomics_prefix[self.format_uri(value)]

                            if (feature.type, qualifier_key) not in attribute_list:
                                attribute_list.append((feature.type, qualifier_key))
                                self.attribute_abstraction.append({
                                    "uri": self.askomics_prefix[self.format_uri(qualifier_key)],
                                    "label": rdflib.Literal(qualifier_key),
                                    "type": [rdflib.OWL.ObjectProperty, self.askomics_prefix[self.format_uri("AskomicsRelation")]],
                                    "domain": entity_type,
                                    "range": self.askomics_prefix[self.format_uri(value.split(":")[0])]
                                })

                        else:
                            relation = self.askomics_prefix[self.format_uri(qualifier_key)]
                            attribute = rdflib.Literal(self.convert_type(value))

                            if (feature.type, qualifier_key) not in attribute_list:
                                attribute_list.append((feature.type, qualifier_key))
                                self.attribute_abstraction.append({
                                    "uri": self.askomics_prefix[self.format_uri(qualifier_key)],
                                    "label": rdflib.Literal(qualifier_key),
                                    "type": [rdflib.OWL.DatatypeProperty],
                                    "domain": entity_type,
                                    "range": self.get_rdf_type(value)
                                })

                        rdf_graph.add((entity, relation, attribute))

            yield rdf_graph
