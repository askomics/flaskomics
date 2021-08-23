import rdflib
import sys
import traceback

from collections import defaultdict
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

    def __init__(self, app, session, file_info, host_url=None, external_endpoint=None, custom_uri=None):
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
        File.__init__(self, app, session, file_info, host_url, external_endpoint=external_endpoint, custom_uri=custom_uri)

        self.entities = {}
        self.entities_to_integrate = []

        self.category_values = {}

        self.attributes = {}

        self.attribute_abstraction = []

        self.faldo_entity = True

    def set_preview(self):
        """Summary"""
        try:
            # exam = GFFExaminer()
            handle = open(self.path, encoding="utf-8", errors="ignore")
            # gff_type = exam.available_limits(handle)['gff_type']
            # for entity in gff_type:
            #    self.entities.append(entity[0])

            data = defaultdict(lambda: set())

            for rec in GFF.parse(handle):
                for feature in rec.features:
                    data[feature.type] |= set(feature.qualifiers.keys())
            self.entities = data
            handle.close()
        except Exception as e:
            self.error = True
            self.error_message = "Malformated GFF ({})".format(str(e))
            traceback.print_exc(file=sys.stdout)

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
            'name': self.human_name,
            'error': self.error,
            'error_message': self.error_message,
            'data': {
                'entities': self.entities
            }
        }

    def integrate(self, dataset_id, entities=[], public=True):
        """Integrate GFF file

        Parameters
        ----------
        entities : List
            Entities to integrate
        public : bool, optional
            Insert in public dataset
        """
        self.public = public
        if entities:
            self.entities_to_integrate = entities
        else:
            self.set_preview()
            self.entities_to_integrate = self.entities

        File.integrate(self, dataset_id=dataset_id)

    def set_rdf_abstraction_domain_knowledge(self):
        """Set the abstraction and domain knowledge"""
        # Abstraction
        for entity in self.entities_to_integrate:
            self.graph_abstraction_dk.add((self.namespace_data[self.format_uri(entity, remove_space=True)], rdflib.RDF.type, self.namespace_internal[self.format_uri("entity")]))
            self.graph_abstraction_dk.add((self.namespace_data[self.format_uri(entity, remove_space=True)], rdflib.RDF.type, self.namespace_internal[self.format_uri("startPoint")]))
            self.graph_abstraction_dk.add((self.namespace_data[self.format_uri(entity, remove_space=True)], rdflib.RDF.type, self.namespace_internal[self.format_uri("faldo")]))
            self.graph_abstraction_dk.add((self.namespace_data[self.format_uri(entity, remove_space=True)], rdflib.RDF.type, rdflib.OWL["Class"]))
            self.graph_abstraction_dk.add((self.namespace_data[self.format_uri(entity, remove_space=True)], rdflib.RDFS.label, rdflib.Literal(entity)))

        for attribute in self.attribute_abstraction:
            for attr_type in attribute["type"]:
                self.graph_abstraction_dk.add((attribute["uri"], rdflib.RDF.type, attr_type))
            self.graph_abstraction_dk.add((attribute["uri"], rdflib.RDFS.label, attribute["label"]))
            self.graph_abstraction_dk.add((attribute["uri"], rdflib.RDFS.domain, attribute["domain"]))
            self.graph_abstraction_dk.add((attribute["uri"], rdflib.RDFS.range, attribute["range"]))

            # Domain Knowledge
            if "values" in attribute.keys():
                for value in attribute["values"]:
                    self.graph_abstraction_dk.add((self.namespace_data[self.format_uri(value)], rdflib.RDF.type, self.namespace_data[self.format_uri("{}CategoryValue".format(attribute["label"]))]))
                    self.graph_abstraction_dk.add((self.namespace_data[self.format_uri(value)], rdflib.RDFS.label, rdflib.Literal(value)))
                    self.graph_abstraction_dk.add((self.namespace_data[self.format_uri("{}Category".format(attribute["label"]))], self.namespace_internal[self.format_uri("category")], self.namespace_data[self.format_uri(value)]))

                    if attribute["label"] == rdflib.Literal("strand"):
                        self.graph_abstraction_dk.add((self.namespace_data[self.format_uri(value)], rdflib.RDF.type, self.get_faldo_strand(value)))

        # Faldo:
        if self.faldo_entity:
            for key, value in self.faldo_abstraction.items():
                if value:
                    self.graph_abstraction_dk.add((value, rdflib.RDF.type, self.faldo_abstraction_eq[key]))

    def format_gff_entity(self, entity):
        """Format a gff entity name by removing type (type:entity --> entity)

        Parameters
        ----------
        entity : string
            The GFF entity

        Returns
        -------
        string
            Entity without type
        """
        return ''.join(entity.split(":")[1:]) if ":" in entity else entity

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

        total_lines = sum(1 for line in open(self.path))
        row_number = 0
        feature_dict = {}
        delayed_link = []

        for rec in GFF.parse(handle, limit_info=limit, target_lines=1):

            # Percent
            row_number += 1
            self.graph_chunk.percent = row_number * 100 / total_lines

            # Loop on entities
            for feature in rec.features:

                # Entity type
                entity_type = self.namespace_data[self.format_uri(feature.type, remove_space=True)]

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
                        entity = self.namespace_entity[self.format_uri("{}_{}".format(str(feature.type), str(index)))]
                        entity_label = "{}_{}".format(str(feature.type), str(index))
                    else:
                        entity = self.namespace_entity[self.format_uri(self.format_gff_entity(feature.qualifiers["ID"][0]))]
                        entity_label = self.format_gff_entity(feature.qualifiers["ID"][0])
                        feature_dict[self.format_gff_entity(feature.qualifiers["ID"][0])] = feature.type
                else:
                    entity = self.namespace_entity[self.format_uri(self.format_gff_entity(feature.id))]
                    entity_label = self.format_gff_entity(feature.id)
                    feature_dict[self.format_gff_entity(feature.id)] = feature.type

                self.graph_chunk.add((entity, rdflib.RDF.type, entity_type))
                self.graph_chunk.add((entity, rdflib.RDFS.label, rdflib.Literal(entity_label)))

                # Chrom
                self.category_values["reference"] = {rec.id, }
                relation = self.namespace_data[self.format_uri("reference")]
                attribute = self.namespace_data[self.format_uri(rec.id)]
                faldo_reference = attribute
                self.faldo_abstraction["reference"] = relation
                # self.graph_chunk.add((entity, relation, attribute))

                if (feature.type, "reference") not in attribute_list:
                    attribute_list.append((feature.type, "reference"))
                    self.attribute_abstraction.append({
                        "uri": self.namespace_data[self.format_uri("reference")],
                        "label": rdflib.Literal("reference"),
                        "type": [self.namespace_internal[self.format_uri("AskomicsCategory")], rdflib.OWL.ObjectProperty],
                        "domain": entity_type,
                        "range": self.namespace_data[self.format_uri("{}Category".format("reference"))],
                        "values": [rec.id]
                    })
                else:
                    # add the value
                    for at in self.attribute_abstraction:
                        if at["uri"] == self.namespace_data[self.format_uri("reference")] and at["domain"] == entity_type and rec.id not in at["values"]:
                            at["values"].append(rec.id)

                # Start
                relation = self.namespace_data[self.format_uri("start")]
                attribute = rdflib.Literal(self.convert_type(feature.location.start))
                faldo_start = attribute
                self.faldo_abstraction["start"] = relation
                # self.graph_chunk.add((entity, relation, attribute))

                if (feature.type, "start") not in attribute_list:
                    attribute_list.append((feature.type, "start"))
                    self.attribute_abstraction.append({
                        "uri": self.namespace_data[self.format_uri("start")],
                        "label": rdflib.Literal("start"),
                        "type": [rdflib.OWL.DatatypeProperty],
                        "domain": entity_type,
                        "range": rdflib.XSD.decimal
                    })

                # End
                relation = self.namespace_data[self.format_uri("end")]
                attribute = rdflib.Literal(self.convert_type(feature.location.end))
                faldo_end = attribute
                self.faldo_abstraction["end"] = relation
                # self.graph_chunk.add((entity, relation, attribute))

                if (feature.type, "end") not in attribute_list:
                    attribute_list.append((feature.type, "end"))
                    self.attribute_abstraction.append({
                        "uri": self.namespace_data[self.format_uri("end")],
                        "label": rdflib.Literal("end"),
                        "type": [rdflib.OWL.DatatypeProperty],
                        "domain": entity_type,
                        "range": rdflib.XSD.decimal
                    })

                # Strand
                if feature.location.strand == 1:
                    self.category_values["strand"] = {"+", }
                    relation = self.namespace_data[self.format_uri("strand")]
                    attribute = self.namespace_data[self.format_uri("+")]
                    faldo_strand = self.get_faldo_strand("+")
                    self.faldo_abstraction["strand"] = relation
                    # self.graph_chunk.add((entity, relation, attribute))
                elif feature.location.strand == -1:
                    self.category_values["strand"] = {"-", }
                    relation = self.namespace_data[self.format_uri("strand")]
                    attribute = self.namespace_data[self.format_uri("-")]
                    faldo_strand = self.get_faldo_strand("-")
                    self.faldo_abstraction["strand"] = relation
                    # self.graph_chunk.add((entity, relation, attribute))
                else:
                    self.category_values["strand"] = {".", }
                    relation = self.namespace_data[self.format_uri("strand")]
                    attribute = self.namespace_data[self.format_uri(".")]
                    faldo_strand = self.get_faldo_strand(".")
                    self.faldo_abstraction["strand"] = relation

                if (feature.type, "strand") not in attribute_list:
                    attribute_list.append((feature.type, "strand"))
                    self.attribute_abstraction.append({
                        "uri": self.namespace_data[self.format_uri("strand")],
                        "label": rdflib.Literal("strand"),
                        "type": [self.namespace_internal[self.format_uri("AskomicsCategory")], rdflib.OWL.ObjectProperty],
                        "domain": entity_type,
                        "range": self.namespace_data[self.format_uri("{}Category".format("strand"))],
                        "values": ["+", "-", "."]
                    })

                # Qualifiers (9th columns)
                for qualifier_key, qualifier_value in feature.qualifiers.items():

                    for value in qualifier_value:
                        skip = False

                        if qualifier_key in ("Parent", "Derives_from"):
                            if len(value.split(":")) == 1:
                                # The entity is not in the value, try to detect it
                                if value in feature_dict:
                                    related_type = feature_dict[value]
                                    related_qualifier_key = qualifier_key + "_" + related_type
                                else:
                                    # Do this later
                                    delayed_link.append({
                                        "uri": self.namespace_data[self.format_uri(qualifier_key)],
                                        "label": rdflib.Literal(qualifier_key),
                                        "type": [rdflib.OWL.ObjectProperty, self.namespace_internal[self.format_uri("AskomicsRelation")]],
                                        "domain": entity_type,
                                        "range": value,
                                        "qualifier_key": qualifier_key,
                                        "feature_type": feature.type
                                    })
                                    skip = True
                            else:
                                related_type = value.split(":")[0]
                                related_qualifier_key = qualifier_key + "_" + related_type

                            relation = self.namespace_data[self.format_uri(qualifier_key)]
                            attribute = self.namespace_data[self.format_uri(self.format_gff_entity(value))]

                            if not skip and (feature.type, related_qualifier_key) not in attribute_list:
                                attribute_list.append((feature.type, related_qualifier_key))
                                self.attribute_abstraction.append({
                                    "uri": self.namespace_data[self.format_uri(qualifier_key)],
                                    "label": rdflib.Literal(qualifier_key),
                                    "type": [rdflib.OWL.ObjectProperty, self.namespace_internal[self.format_uri("AskomicsRelation")]],
                                    "domain": entity_type,
                                    "range": self.namespace_data[self.format_uri(related_type)]
                                })

                        else:
                            relation = self.namespace_data[self.format_uri(qualifier_key)]
                            attribute = rdflib.Literal(self.convert_type(value))

                            if (feature.type, qualifier_key) not in attribute_list:
                                attribute_list.append((feature.type, qualifier_key))
                                self.attribute_abstraction.append({
                                    "uri": self.namespace_data[self.format_uri(qualifier_key)],
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

                    # blocks
                    block_base = self.settings.getint("triplestore", "block_size")
                    block_start = int(self.convert_type(feature.location.start)) // block_base
                    block_end = int(self.convert_type(feature.location.end)) // block_base

                    for slice_block in range(block_start, block_end + 1):
                        self.graph_chunk.add((entity, self.namespace_internal['includeIn'], rdflib.Literal(int(slice_block))))
                        block_reference = self.rdfize(self.format_uri("{}_{}".format(rec.id, slice_block)))
                        self.graph_chunk.add((entity, self.namespace_internal["includeInReference"], block_reference))

                yield

        # Add missing abstractions
        for link in delayed_link:
            if link["range"] in feature_dict:
                entity_type = feature_dict[link['range']]
                related_qualifier_key = link.pop("qualifier_key") + "_" + entity_type
                feature_type = link.pop("feature_type")
                if (feature_type, related_qualifier_key) not in attribute_list:
                    link['range'] = self.namespace_data[self.format_uri(entity_type)]
                    self.attribute_abstraction.append(link)
