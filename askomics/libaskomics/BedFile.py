import os
import rdflib

from pybedtools import BedTool

from askomics.libaskomics.File import File
from askomics.libaskomics.RdfGraph import RdfGraph


class BedFile(File):
    """Bed File

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

        self.entity_name = ''
        self.category_values = {}
        self.attributes = {}
        self.attribute_abstraction = []

    def set_preview(self):
        """Set entity name preview"""
        self.entity_name = os.path.splitext(self.name)[0]

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
            'name': self.name,
            "entity_name": self.entity_name
        }

    def integrate(self, entity_name, public=True):
        """Integrate BeD file

        Parameters
        ----------
        entities : List
            Entities to integrate
        public : bool, optional
            Insert in public dataset
        """
        self.public = public
        self.entity_name = entity_name

        File.integrate(self)

    def get_rdf_abstraction_domain_knowledge(self):
        """Get the abstraction and domain knowledge

        Returns
        -------
        Graph
            Abstraction and domain knowledge
        """
        rdf_graph = RdfGraph(self.app, self.session)

        # Abstraction
        rdf_graph.add((self.askomics_prefix[self.format_uri(self.entity_name, remove_space=True)], rdflib.RDF.type, self.askomics_prefix[self.format_uri("entity")]))
        rdf_graph.add((self.askomics_prefix[self.format_uri(self.entity_name, remove_space=True)], rdflib.RDF.type, self.askomics_prefix[self.format_uri("startPoint")]))
        rdf_graph.add((self.askomics_prefix[self.format_uri(self.entity_name, remove_space=True)], rdflib.RDF.type, rdflib.OWL["Class"]))
        rdf_graph.add((self.askomics_prefix[self.format_uri(self.entity_name, remove_space=True)], rdflib.RDFS.label, rdflib.Literal(self.entity_name)))

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
        """Generate RDF content of the BED file

        Yields
        ------
        Graph
            RDF content
        """
        bedfile = BedTool(self.path)

        count = 0
        attribute_list = []

        entity_type = self.askomics_prefix[self.format_uri(self.entity_name, remove_space=True)]

        for feature in bedfile:

            rdf_graph = RdfGraph(self.app, self.session)

            # Entity
            if feature.name != '.':
                entity_label = feature.name
            else:
                entity_label = "{}_{}".format(self.entity_name, str(count))
            count += 1
            entity = self.askomics_prefix[self.format_uri(entity_label)]

            rdf_graph.add((entity, rdflib.RDF.type, entity_type))
            rdf_graph.add((entity, rdflib.RDFS.label, rdflib.Literal(entity_label)))

            # Chromosome
            self.category_values["chromosome"] = {feature.chrom, }
            relation = self.askomics_prefix[self.format_uri("chromosome")]
            attribute = self.askomics_prefix[self.format_uri(feature.chrom)]
            rdf_graph.add((entity, relation, attribute))

            if "chromosome" not in attribute_list:
                attribute_list.append("chromosome")
                self.attribute_abstraction.append({
                    "uri": self.askomics_prefix[self.format_uri("chromosome")],
                    "label": rdflib.Literal("chromosome"),
                    "type": [self.askomics_prefix[self.format_uri("AskomicsCategory")], rdflib.OWL.ObjectProperty],
                    "domain": entity_type,
                    "range": self.askomics_prefix[self.format_uri("{}Category".format("chromosome"))],
                    "values": [feature.chrom]
                })
            else:
                # add the value
                for at in self.attribute_abstraction:
                    if at["uri"] == self.askomics_prefix[self.format_uri("chromosome")] and at["domain"] == entity_type and feature.chrom not in at["values"]:
                        at["values"].append(feature.chrom)

            # Start
            relation = self.askomics_prefix[self.format_uri("start")]
            attribute = rdflib.Literal(self.convert_type(feature.start + 1))  # +1 because bed is 0 based
            rdf_graph.add((entity, relation, attribute))

            if "start" not in attribute_list:
                attribute_list.append("start")
                self.attribute_abstraction.append({
                    "uri": self.askomics_prefix[self.format_uri("start")],
                    "label": rdflib.Literal("start"),
                    "type": [rdflib.OWL.DatatypeProperty],
                    "domain": entity_type,
                    "range": rdflib.XSD.decimal
                })

            # End
            relation = self.askomics_prefix[self.format_uri("end")]
            attribute = rdflib.Literal(self.convert_type(feature.end))
            rdf_graph.add((entity, relation, attribute))

            if "end" not in attribute_list:
                attribute_list.append("end")
                self.attribute_abstraction.append({
                    "uri": self.askomics_prefix[self.format_uri("end")],
                    "label": rdflib.Literal("end"),
                    "type": [rdflib.OWL.DatatypeProperty],
                    "domain": entity_type,
                    "range": rdflib.XSD.decimal
                })

            # Strand
            strand = False
            if feature.strand == "+":
                self.category_values["strand"] = {"+", }
                relation = self.askomics_prefix[self.format_uri("strand")]
                attribute = self.askomics_prefix[self.format_uri("+")]
                rdf_graph.add((entity, relation, attribute))
                strand = True
            elif feature.strand == "-":
                self.category_values["strand"] = {"-", }
                relation = self.askomics_prefix[self.format_uri("strand")]
                attribute = self.askomics_prefix[self.format_uri("-")]
                rdf_graph.add((entity, relation, attribute))
                strand = True

            if strand:
                if "strand" not in attribute_list:
                    attribute_list.append("strand")
                    self.attribute_abstraction.append({
                        "uri": self.askomics_prefix[self.format_uri("strand")],
                        "label": rdflib.Literal("strand"),
                        "type": [self.askomics_prefix[self.format_uri("AskomicsCategory")], rdflib.OWL.ObjectProperty],
                        "domain": entity_type,
                        "range": self.askomics_prefix[self.format_uri("{}Category".format("strand"))],
                        "values": ["+", "-"]
                    })

            # Score
            if feature.score != '.':
                relation = self.askomics_prefix[self.format_uri("score")]
                attribute = rdflib.Literal(self.convert_type(feature.score))
                rdf_graph.add((entity, relation, attribute))

                if "score" not in attribute_list:
                    attribute_list.append("score")
                    self.attribute_abstraction.append({
                        "uri": self.askomics_prefix[self.format_uri("score")],
                        "label": rdflib.Literal("score"),
                        "type": [rdflib.OWL.DatatypeProperty],
                        "domain": entity_type,
                        "range": rdflib.XSD.decimal
                    })

            yield rdf_graph
