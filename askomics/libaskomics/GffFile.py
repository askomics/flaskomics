import rdflib
import sys
import traceback

from rdflib import BNode
from BCBio import GFF

from askomics.libaskomics.File import File


class GffFile(File):
    """GFF File

    Attributes
    ----------
    public : bool
        Public or private dataset
    """

    def __init__(self, app, session, file_info, host_url=None, external_endpoint=None, custom_uri=None, external_graph=None):
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
        File.__init__(self, app, session, file_info, host_url, external_endpoint=external_endpoint, custom_uri=custom_uri, external_graph=external_graph)

        self.entities = []
        self.preview_attributes = {}

        self.entities_to_integrate = []
        self.attributes_to_integrate = {}

        self.category_values = {}

        self.attributes = {}

        self.attribute_abstraction = []

        self.faldo_entity = True

        self.faldo_abstraction = {
            "start": [],
            "end": [],
            "strand": [],
            "reference": []
        }

    def set_preview(self):
        """Summary"""

        if self.preview:
            self.entities = self.preview['entities']
            self.preview_attributes = self.preview.get("attributes", {})
            return

        try:
            entities = []
            attributes = {}

            with open(self.path, encoding="utf-8", errors="ignore") as f:
                for line in f:
                    if line.startswith("#"):
                        continue
                    content = line.strip().split("\t")
                    if not len(content) == 9:
                        raise Exception("Error parsing GFF file: number of columns is not 9")
                    entity = content[2].strip()
                    entities.append(entity)
                    if entity not in attributes:
                        attributes[entity] = set()

                    for attr in content[8].split(";"):
                        key = attr.split("=")[0]
                        # We need to integrate it in all cases (relations, not attributes)
                        if key in ["Parent", "Derives_from"]:
                            continue
                        attributes[entity].add(key)

            self.entities = list(dict.fromkeys(entities))
            for key, value in attributes.items():
                attributes[key] = list(value)
            self.preview_attributes = attributes

        except Exception as e:
            self.error = True
            self.error_message = "Malformated GFF ({})".format(str(e))
            traceback.print_exc(file=sys.stdout)

    def save_preview(self):
        """Save location and endpoint in preview"""
        data = None
        error = None
        self.set_preview()

        if self.error:
            error = self.error_message
        else:
            data = {'entities': self.entities, "attributes": self.preview_attributes}
        self.save_preview_in_db(data, error)

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
                'entities': self.entities,
                'attributes': self.preview_attributes
            }
        }

    def integrate(self, dataset_id, entities=[], attributes={}, public=True):
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

        if attributes:
            self.attributes_to_integrate = attributes

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

        attribute_blanks = {}

        for attribute in self.attribute_abstraction:
            blank = BNode()
            # New way of storing relations (starting from 4.4.0)
            if attribute.get("relation"):
                endpoint = rdflib.Literal(self.external_endpoint) if self.external_endpoint else rdflib.Literal(self.settings.get('triplestore', 'endpoint'))
                for attr_type in attribute["type"]:
                    self.graph_abstraction_dk.add((blank, rdflib.RDF.type, attr_type))
                self.graph_abstraction_dk.add((blank, self.namespace_internal["uri"], attribute["uri"]))
                self.graph_abstraction_dk.add((blank, rdflib.RDFS.label, attribute["label"]))
                self.graph_abstraction_dk.add((blank, rdflib.RDFS.domain, attribute["domain"]))
                self.graph_abstraction_dk.add((blank, rdflib.RDFS.range, attribute["range"]))
                self.graph_abstraction_dk.add((blank, rdflib.DCAT.endpointURL, endpoint))
                self.graph_abstraction_dk.add((blank, rdflib.DCAT.dataset, rdflib.Literal(self.name)))

            else:
                # New way of storing attributes (starting from 4.4.0)
                for attr_type in attribute["type"]:
                    self.graph_abstraction_dk.add((blank, rdflib.RDF.type, attr_type))
                self.graph_abstraction_dk.add((blank, self.namespace_internal["uri"], attribute["uri"]))
                self.graph_abstraction_dk.add((blank, rdflib.RDFS.label, attribute["label"]))
                self.graph_abstraction_dk.add((blank, rdflib.RDFS.domain, attribute["domain"]))
                self.graph_abstraction_dk.add((blank, rdflib.RDFS.range, attribute["range"]))

            attribute_blanks[(attribute['domain'], attribute["uri"])] = blank
            # Domain Knowledge
            if "values" in attribute.keys():
                for value in attribute["values"]:
                    o = self.namespace_data[self.format_uri(value)]
                    if attribute["label"] == rdflib.Literal("strand"):
                        o = self.get_faldo_strand(value)
                    self.graph_abstraction_dk.add((o, rdflib.RDF.type, self.namespace_data[self.format_uri("{}CategoryValue".format(attribute["label"]))]))
                    self.graph_abstraction_dk.add((o, rdflib.RDFS.label, rdflib.Literal(value)))
                    self.graph_abstraction_dk.add((self.namespace_data[self.format_uri("{}Category".format(attribute["label"]))], self.namespace_internal[self.format_uri("category")], o))
        # Faldo:
        if self.faldo_entity:
            for key, values in self.faldo_abstraction.items():
                if values:
                    for val in values:
                        blank = attribute_blanks[val]
                        self.graph_abstraction_dk.add((blank, rdflib.RDF.type, self.faldo_abstraction_eq[key]))
                        self.graph_abstraction_dk.add((blank, self.namespace_internal["uri"], val[1]))

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
                strand_type = None
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
                self.faldo_abstraction["reference"].append((entity_type, relation))
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
                self.faldo_abstraction["start"].append((entity_type, relation))
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
                self.faldo_abstraction["end"].append((entity_type, relation))
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
                    self.faldo_abstraction["strand"].append((entity_type, relation))
                    strand_type = "+"
                    # self.graph_chunk.add((entity, relation, attribute))
                elif feature.location.strand == -1:
                    self.category_values["strand"] = {"-", }
                    relation = self.namespace_data[self.format_uri("strand")]
                    attribute = self.namespace_data[self.format_uri("-")]
                    faldo_strand = self.get_faldo_strand("-")
                    self.faldo_abstraction["strand"].append((entity_type, relation))
                    strand_type = "-"
                    # self.graph_chunk.add((entity, relation, attribute))
                else:
                    self.category_values["strand"] = {".", }
                    relation = self.namespace_data[self.format_uri("strand")]
                    attribute = self.namespace_data[self.format_uri(".")]
                    faldo_strand = self.get_faldo_strand(".")
                    self.faldo_abstraction["strand"].append((entity_type, relation))
                    strand_type = "."

                if (feature.type, "strand", strand_type) not in attribute_list:
                    attribute_list.append((feature.type, "strand", strand_type))
                    self.attribute_abstraction.append({
                        "uri": self.namespace_data[self.format_uri("strand")],
                        "label": rdflib.Literal("strand"),
                        "type": [self.namespace_internal[self.format_uri("AskomicsCategory")], rdflib.OWL.ObjectProperty],
                        "domain": entity_type,
                        "range": self.namespace_data[self.format_uri("{}Category".format("strand"))],
                        "values": [strand_type]
                    })

                # Qualifiers (9th columns)
                for qualifier_key, qualifier_value in feature.qualifiers.items():

                    if self.attributes_to_integrate and (qualifier_key not in ("Parent", "Derives_from") and qualifier_key not in self.attributes_to_integrate.get(feature.type, [])):
                        continue

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
                                        "feature_type": feature.type,
                                        "relation": True
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
                                    "range": self.namespace_data[self.format_uri(related_type)],
                                    "relation": True
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

                # Triples respecting faldo ontology

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

                # Shortcut triple for faldo queries
                self.graph_chunk.add((entity, self.namespace_internal["faldoBegin"], faldo_start))
                self.graph_chunk.add((entity, self.namespace_internal["faldoEnd"], faldo_end))
                self.graph_chunk.add((entity, self.namespace_internal["faldoReference"], faldo_reference))

                if faldo_strand:
                    self.graph_chunk.add((entity, self.namespace_internal["faldoStrand"], faldo_strand))
                    strand_ref = self.get_reference_strand_uri(rec.id, faldo_strand, None)
                    for sref in strand_ref:
                        self.graph_chunk.add((entity, self.namespace_internal["referenceStrand"], sref))

                # blocks
                block_base = self.settings.getint("triplestore", "block_size")
                block_start = int(self.convert_type(feature.location.start)) // block_base
                block_end = int(self.convert_type(feature.location.end)) // block_base

                for slice_block in range(block_start, block_end + 1):
                    self.graph_chunk.add((entity, self.namespace_internal['includeIn'], rdflib.Literal(int(slice_block))))
                    block_reference = self.rdfize(self.format_uri("{}_{}".format(rec.id, slice_block)))
                    self.graph_chunk.add((entity, self.namespace_internal["includeInReference"], block_reference))
                    if faldo_strand:
                        strand_ref = self.get_reference_strand_uri(rec.id, faldo_strand, slice_block)
                        for sref in strand_ref:
                            self.graph_chunk.add((entity, self.namespace_internal["includeInReferenceStrand"], sref))
                        strand_ref = self.get_reference_strand_uri(None, faldo_strand, slice_block)
                        for sref in strand_ref:
                            self.graph_chunk.add((entity, self.namespace_internal["includeInStrand"], sref))

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
