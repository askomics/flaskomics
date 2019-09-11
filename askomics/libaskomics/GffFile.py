import rdflib

from rdflib import BNode
from BCBio.GFF import GFFExaminer
from BCBio import GFF

from askomics.libaskomics.File import File


class GffFile(File):
    """GFF File

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

        self.faldo_entity = True

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

    def set_rdf_abstraction_domain_knowledge(self):
        """Set the abstraction and domain knowledge"""
        # Abstraction
        for entity in self.entities_to_integrate:
            self.graph_abstraction_dk.add((self.askomics_prefix[self.format_uri(entity, remove_space=True)], rdflib.RDF.type, self.askomics_prefix[self.format_uri("entity")]))
            self.graph_abstraction_dk.add((self.askomics_prefix[self.format_uri(entity, remove_space=True)], rdflib.RDF.type, self.askomics_prefix[self.format_uri("startPoint")]))
            self.graph_abstraction_dk.add((self.askomics_prefix[self.format_uri(entity, remove_space=True)], rdflib.RDF.type, self.askomics_prefix[self.format_uri("faldo")]))
            self.graph_abstraction_dk.add((self.askomics_prefix[self.format_uri(entity, remove_space=True)], rdflib.RDF.type, rdflib.OWL["Class"]))
            self.graph_abstraction_dk.add((self.askomics_prefix[self.format_uri(entity, remove_space=True)], rdflib.RDFS.label, rdflib.Literal(entity)))

        for attribute in self.attribute_abstraction:
            for attr_type in attribute["type"]:
                self.graph_abstraction_dk.add((attribute["uri"], rdflib.RDF.type, attr_type))
            self.graph_abstraction_dk.add((attribute["uri"], rdflib.RDFS.label, attribute["label"]))
            self.graph_abstraction_dk.add((attribute["uri"], rdflib.RDFS.domain, attribute["domain"]))
            self.graph_abstraction_dk.add((attribute["uri"], rdflib.RDFS.range, attribute["range"]))

            # Domain Knowledge
            if "values" in attribute.keys():
                for value in attribute["values"]:
                    self.graph_abstraction_dk.add((self.askomics_prefix[self.format_uri(value)], rdflib.RDF.type, self.askomics_prefix[self.format_uri("{}CategoryValue".format(attribute["label"]))]))
                    self.graph_abstraction_dk.add((self.askomics_prefix[self.format_uri(value)], rdflib.RDFS.label, rdflib.Literal(value)))
                    self.graph_abstraction_dk.add((self.askomics_prefix[self.format_uri("{}Category".format(attribute["label"]))], self.askomics_namespace[self.format_uri("category")], self.askomics_prefix[self.format_uri(value)]))

        # Faldo:
        if self.faldo_entity:
            for key, value in self.faldo_abstraction.items():
                if value:
                    self.graph_abstraction_dk.add((value, rdflib.RDF.type, self.faldo_abstraction_eq[key]))

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

                # Faldo
                faldo_reference = None
                faldo_strand = None
                faldo_start = None
                faldo_end = None

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

                self.graph_chunk.add((entity, rdflib.RDF.type, entity_type))
                self.graph_chunk.add((entity, rdflib.RDFS.label, rdflib.Literal(entity_label)))

                # Chrom
                self.category_values["reference"] = {rec.id, }
                relation = self.askomics_prefix[self.format_uri("reference")]
                attribute = self.askomics_prefix[self.format_uri(rec.id)]
                faldo_reference = attribute
                self.faldo_abstraction["reference"] = relation
                self.graph_chunk.add((entity, relation, attribute))

                if (feature.type, "reference") not in attribute_list:
                    attribute_list.append((feature.type, "reference"))
                    self.attribute_abstraction.append({
                        "uri": self.askomics_prefix[self.format_uri("reference")],
                        "label": rdflib.Literal("reference"),
                        "type": [self.askomics_prefix[self.format_uri("AskomicsCategory")], rdflib.OWL.ObjectProperty],
                        "domain": entity_type,
                        "range": self.askomics_prefix[self.format_uri("{}Category".format("reference"))],
                        "values": [rec.id]
                    })
                else:
                    # add the value
                    for at in self.attribute_abstraction:
                        if at["uri"] == self.askomics_prefix[self.format_uri("reference")] and at["domain"] == entity_type and rec.id not in at["values"]:
                            at["values"].append(rec.id)

                # Start
                relation = self.askomics_prefix[self.format_uri("start")]
                attribute = rdflib.Literal(self.convert_type(feature.location.start))
                faldo_start = attribute
                self.faldo_abstraction["start"] = relation
                self.graph_chunk.add((entity, relation, attribute))

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
                faldo_end = attribute
                self.faldo_abstraction["end"] = relation
                self.graph_chunk.add((entity, relation, attribute))

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
                    faldo_strand = self.get_faldo_strand("+")
                    self.faldo_abstraction["strand"] = relation
                    self.graph_chunk.add((entity, relation, attribute))
                elif feature.location.strand == -1:
                    self.category_values["strand"] = {"-", }
                    relation = self.askomics_prefix[self.format_uri("strand")]
                    attribute = self.askomics_prefix[self.format_uri("-")]
                    faldo_strand = self.get_faldo_strand("-")
                    self.faldo_abstraction["strand"] = relation
                    self.graph_chunk.add((entity, relation, attribute))

                if (feature.type, "strand") not in attribute_list:
                    attribute_list.append((feature.type, "strand"))
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

                        self.graph_chunk.add((entity, relation, attribute))

                location = BNode()
                begin = BNode()
                end = BNode()

                self.graph_chunk.add((entity, self.faldo.location, location))

                self.graph_chunk.add((location, rdflib.RDF.type, self.faldo.region))
                self.graph_chunk.add((location, self.faldo.begin, begin))
                self.graph_chunk.add((location, self.faldo.end, end))

                self.graph_chunk.add((begin, rdflib.RDF.type, self.faldo.ExactPosition))
                self.graph_chunk.add((begin, self.faldo.position, faldo_start))

                self.graph_chunk.add((end, rdflib.RDF.type, self.faldo.ExactPosition))
                self.graph_chunk.add((end, self.faldo.position, faldo_end))

                self.graph_chunk.add((begin, self.faldo.reference, faldo_reference))
                self.graph_chunk.add((end, self.faldo.reference, faldo_reference))

                if faldo_strand:
                    self.graph_chunk.add((begin, rdflib.RDF.type, faldo_strand))
                    self.graph_chunk.add((end, rdflib.RDF.type, faldo_strand))

                yield
