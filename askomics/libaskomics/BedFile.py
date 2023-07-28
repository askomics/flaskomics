import rdflib
import sys
import traceback

from rdflib import BNode
from pybedtools import BedTool

from askomics.libaskomics.File import File


class BedFile(File):
    """Bed File

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

        self.entity_name = ''
        self.category_values = {}
        self.attributes = {}
        self.attribute_abstraction = []
        self.faldo_entity = True

    def set_preview(self):
        """Set entity name preview"""
        try:
            BedTool(self.path).count()
            self.entity_name = self.human_name
        except Exception as e:
            self.error = True
            self.error_message = "Malformated BED ({})".format(str(e))
            traceback.print_exc(file=sys.stdout)

    def get_preview(self):
        """Get file preview

        Returns
        -------
        dict
            bed file preview
        """
        return {
            'type': self.type,
            'id': self.id,
            'name': self.human_name,
            'error': self.error,
            'error_message': self.error_message,
            "entity_name": self.entity_name
        }

    def integrate(self, dataset_id, entity_name="", public=True):
        """Integrate BED file

        Parameters
        ----------
        entities : List
            Entities to integrate
        public : bool, optional
            Insert in public dataset
        """
        self.public = public
        if entity_name:
            self.entity_name = entity_name
        else:
            self.entity_name = self.human_name

        File.integrate(self, dataset_id=dataset_id)

    def set_rdf_abstraction_domain_knowledge(self):
        """Set the abstraction and domain knowledge"""
        # Abstraction
        self.graph_abstraction_dk.add((self.namespace_data[self.format_uri(self.entity_name, remove_space=True)], rdflib.RDF.type, self.namespace_internal[self.format_uri("entity")]))
        self.graph_abstraction_dk.add((self.namespace_data[self.format_uri(self.entity_name, remove_space=True)], rdflib.RDF.type, self.namespace_internal[self.format_uri("startPoint")]))
        self.graph_abstraction_dk.add((self.namespace_data[self.format_uri(self.entity_name, remove_space=True)], rdflib.RDF.type, self.namespace_internal[self.format_uri("faldo")]))

        self.graph_abstraction_dk.add((self.namespace_data[self.format_uri(self.entity_name, remove_space=True)], rdflib.RDF.type, rdflib.OWL["Class"]))
        self.graph_abstraction_dk.add((self.namespace_data[self.format_uri(self.entity_name, remove_space=True)], rdflib.RDFS.label, rdflib.Literal(self.entity_name)))

        attribute_blanks = {}

        for attribute in self.attribute_abstraction:
            blank = BNode()

            for attr_type in attribute["type"]:
                self.graph_abstraction_dk.add((blank, rdflib.RDF.type, attr_type))
            self.graph_abstraction_dk.add((blank, self.namespace_internal["uri"], attribute["uri"]))
            self.graph_abstraction_dk.add((blank, rdflib.RDFS.label, attribute["label"]))
            self.graph_abstraction_dk.add((blank, rdflib.RDFS.domain, attribute["domain"]))
            self.graph_abstraction_dk.add((blank, rdflib.RDFS.range, attribute["range"]))

            attribute_blanks[attribute["uri"]] = blank
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
            for key, value in self.faldo_abstraction.items():
                if value:
                    blank = attribute_blanks[value]
                    self.graph_abstraction_dk.add((blank, rdflib.RDF.type, self.faldo_abstraction_eq[key]))
                    self.graph_abstraction_dk.add((blank, self.namespace_internal["uri"], value))

    def generate_rdf_content(self):
        """Generate RDF content of the BED file

        Yields
        ------
        Graph
            RDF content
        """
        bedfile = BedTool(self.path)

        count = 0
        attribute_list = []

        total_lines = sum(1 for line in open(self.path))
        row_number = 0

        entity_type = self.namespace_data[self.format_uri(self.entity_name, remove_space=True)]

        for feature in bedfile:

            # Percent
            row_number += 1
            self.graph_chunk.percent = row_number * 100 / total_lines

            # Entity
            if feature.name != '.':
                entity_label = feature.name
            else:
                entity_label = "{}_{}".format(self.entity_name, str(count))
            count += 1
            entity = self.namespace_entity[self.format_uri(entity_label)]

            self.graph_chunk.add((entity, rdflib.RDF.type, entity_type))
            self.graph_chunk.add((entity, rdflib.RDFS.label, rdflib.Literal(entity_label)))

            # Faldo
            faldo_reference = None
            faldo_strand = None
            faldo_start = None
            faldo_end = None

            # Chromosome
            self.category_values["reference"] = {feature.chrom, }
            relation = self.namespace_data[self.format_uri("reference")]
            attribute = self.namespace_data[self.format_uri(feature.chrom)]
            faldo_reference = attribute
            self.faldo_abstraction["reference"] = relation
            self.graph_chunk.add((entity, relation, attribute))

            if "reference" not in attribute_list:
                attribute_list.append("reference")
                self.attribute_abstraction.append({
                    "uri": self.namespace_data[self.format_uri("reference")],
                    "label": rdflib.Literal("reference"),
                    "type": [self.namespace_internal[self.format_uri("AskomicsCategory")], rdflib.OWL.ObjectProperty],
                    "domain": entity_type,
                    "range": self.namespace_data[self.format_uri("{}Category".format("reference"))],
                    "values": [feature.chrom]
                })
            else:
                # add the value
                for at in self.attribute_abstraction:
                    if at["uri"] == self.namespace_data[self.format_uri("reference")] and at["domain"] == entity_type and feature.chrom not in at["values"]:
                        at["values"].append(feature.chrom)

            # Start
            relation = self.namespace_data[self.format_uri("start")]
            attribute = rdflib.Literal(self.convert_type(feature.start + 1))  # +1 because bed is 0 based
            faldo_start = attribute
            self.faldo_abstraction["start"] = relation
            self.graph_chunk.add((entity, relation, attribute))

            if "start" not in attribute_list:
                attribute_list.append("start")
                self.attribute_abstraction.append({
                    "uri": self.namespace_data[self.format_uri("start")],
                    "label": rdflib.Literal("start"),
                    "type": [rdflib.OWL.DatatypeProperty],
                    "domain": entity_type,
                    "range": rdflib.XSD.decimal
                })

            # End
            relation = self.namespace_data[self.format_uri("end")]
            attribute = rdflib.Literal(self.convert_type(feature.end))
            faldo_end = attribute
            self.faldo_abstraction["end"] = relation
            self.graph_chunk.add((entity, relation, attribute))

            if "end" not in attribute_list:
                attribute_list.append("end")
                self.attribute_abstraction.append({
                    "uri": self.namespace_data[self.format_uri("end")],
                    "label": rdflib.Literal("end"),
                    "type": [rdflib.OWL.DatatypeProperty],
                    "domain": entity_type,
                    "range": rdflib.XSD.decimal
                })

            # Strand
            strand = False
            strand_type = None
            if feature.strand == "+":
                self.category_values["strand"] = {"+", }
                relation = self.namespace_data[self.format_uri("strand")]
                attribute = self.namespace_data[self.format_uri("+")]
                faldo_strand = self.get_faldo_strand("+")
                self.faldo_abstraction["strand"] = relation
                self.graph_chunk.add((entity, relation, attribute))
                strand = True
                strand_type = "+"
            elif feature.strand == "-":
                self.category_values["strand"] = {"-", }
                relation = self.namespace_data[self.format_uri("strand")]
                attribute = self.namespace_data[self.format_uri("-")]
                faldo_strand = self.get_faldo_strand("-")
                self.faldo_abstraction["strand"] = relation
                self.graph_chunk.add((entity, relation, attribute))
                strand = True
                strand_type = "-"
            else:
                self.category_values["strand"] = {".", }
                relation = self.namespace_data[self.format_uri("strand")]
                attribute = self.namespace_data[self.format_uri(".")]
                faldo_strand = self.get_faldo_strand(".")
                self.faldo_abstraction["strand"] = relation
                self.graph_chunk.add((entity, relation, attribute))
                strand = True
                strand_type = "."

            if strand:
                if ("strand", strand_type) not in attribute_list:
                    attribute_list.append(("strand", strand_type))
                    self.attribute_abstraction.append({
                        "uri": self.namespace_data[self.format_uri("strand")],
                        "label": rdflib.Literal("strand"),
                        "type": [self.namespace_internal[self.format_uri("AskomicsCategory")], rdflib.OWL.ObjectProperty],
                        "domain": entity_type,
                        "range": self.namespace_data[self.format_uri("{}Category".format("strand"))],
                        "values": [strand_type]
                    })

            # Score
            if feature.score != '.':
                relation = self.namespace_data[self.format_uri("score")]
                attribute = rdflib.Literal(self.convert_type(feature.score))
                self.graph_chunk.add((entity, relation, attribute))

                if "score" not in attribute_list:
                    attribute_list.append("score")
                    self.attribute_abstraction.append({
                        "uri": self.namespace_data[self.format_uri("score")],
                        "label": rdflib.Literal("score"),
                        "type": [rdflib.OWL.DatatypeProperty],
                        "domain": entity_type,
                        "range": rdflib.XSD.decimal
                    })

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
            block_start = int(self.convert_type(feature.start + 1)) // block_base
            block_end = int(self.convert_type(feature.end)) // block_base

            for slice_block in range(block_start, block_end + 1):
                self.graph_chunk.add((entity, self.namespace_internal['includeIn'], rdflib.Literal(int(slice_block))))
                block_reference = self.rdfize(self.format_uri("{}_{}".format(feature.chrom, slice_block)))
                self.graph_chunk.add((entity, self.namespace_internal["includeInReference"], block_reference))
                if faldo_strand:
                    self.graph_chunk.add((entity, self.namespace_internal["includeInStrand"], faldo_strand))
                    strand_ref = self.get_reference_strand_uri(feature.chrom, faldo_strand, slice_block)
                    self.graph_chunk.add((entity, self.namespace_internal["includeInReferenceStrand"], strand_ref))

            yield
