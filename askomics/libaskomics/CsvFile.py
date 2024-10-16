import csv
import re
import rdflib
import sys
import traceback
from dateutil import parser

from rdflib import BNode

from askomics.libaskomics.File import File
from askomics.libaskomics.OntologyManager import OntologyManager
from askomics.libaskomics.Utils import cached_property


class CsvFile(File):
    """CSV file

    Attributes
    ----------
    category_values : dict
        Category values
    columns_type : list
        Columns type
    header : list
        Header
    preview : list
        Previex
    public : bool
        Public
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
        self.preview_limit = 30
        try:
            self.preview_limit = self.settings.getint("askomics", "npreview")
        except Exception:
            pass
        self.header = []
        self.preview = []
        self.columns_type = []
        self.category_values = {}

    def set_preview(self):
        """Set previex, header and columns type by sniffing the file"""
        self.set_preview_and_header()
        self.set_columns_type()

    def save_preview(self):
        """Save location and endpoint in preview"""
        data = None
        error = None
        self.save_preview_in_db(data, error)

    def get_preview(self):
        """Get a preview of the file

        Returns
        -------
        dict
            File preview
        """
        return {
            'type': self.type,
            'id': self.id,
            'name': self.human_name,
            'error': self.error,
            'error_message': self.error_message,
            'data': {
                'header': self.header,
                'content_preview': self.preview,
                'columns_type': self.columns_type
            }
        }

    def force_columns_type(self, forced_columns_type):
        """Set the columns type without detecting them

        Parameters
        ----------
        forced_columns_type : list
            columns type
        """
        self.columns_type = forced_columns_type

    def force_header_names(self, forced_header_names):
        """Set the columns type without detecting them

        Parameters
        ----------
        forced_columns_type : list
            columns type
        """
        self.header = forced_header_names

    def set_preview_and_header(self):
        """Set the preview and header by looking in the fists lines of the file"""
        try:
            with open(self.path, 'r', encoding='utf-8') as csv_file:
                reader = csv.reader(csv_file, dialect=self.dialect)
                count = 0
                # Store header
                header = next(reader)
                self.header = [h.strip() for h in header]
                if not all(self.header):
                    raise Exception("Empty column in header")

                # Loop on lines
                preview = []
                for row in reader:
                    res_row = {}
                    res_row = dict.fromkeys(self.header, "")
                    for i, cell in enumerate(row):
                        res_row[self.header[i]] = cell
                    preview.append(res_row)

                    # Stop after x lines
                    if self.preview_limit:
                        count += 1
                        if count > self.preview_limit:
                            break
            self.preview = preview

        except Exception as e:
            self.error = True
            self.error_message = "Malformated CSV/TSV ({})".format(str(e))
            traceback.print_exc(file=sys.stdout)

    def set_columns_type(self):
        """Set the columns type by guessing them"""
        index = 0
        for col in self.transposed_preview:
            self.columns_type.append(self.guess_column_type(col, index))
            index += 1
        # check coltypes
        self.check_columns_types()

    def check_columns_types(self):
        """Check all columns type after detection and correct them"""
        # Change start and end into numeric if here is not only one start and one end
        if not (self.columns_type.count("start") == 1 and self.columns_type.count("end") == 1):
            self.columns_type = ["numeric" if ctype in ("start", "end") else ctype for ctype in self.columns_type]
        # Change ref into text if their is more than one
        if not self.columns_type.count("reference") == 1:
            self.columns_type = ["text" if ctype == "reference" else ctype for ctype in self.columns_type]
        # Change strand into text if their is more than one
        if not self.columns_type.count("strand") == 1:
            self.columns_type = ["text" if ctype == "strand" else ctype for ctype in self.columns_type]

    def is_category(self, values):
        """Check if a list af values are categories

        Parameters
        ----------
        values : list
            List of values

        Returns
        -------
        bool
            True if values are categories
        """
        return len(set(list(filter(None, values)))) <= int(len(list(filter(None, values))) / 3)

    def guess_column_type(self, values, header_index):
        """Guess the columns type

        Parameters
        ----------
        values : list
            columns preview
        header_index : int
            Header index

        Returns
        -------
        string
            The guessed type
        """
        # First col is entity start
        if header_index == 0:
            return "start_entity"

        # if name contain @, this is a relation
        if self.header[header_index].find("@") > 0:
            return "general_relation"

        # If it matches "label"
        if header_index == 1 and re.match(r".*label.*", self.header[header_index].lower(), re.IGNORECASE) is not None:
            return "label"

        special_types = {
            'reference': ('chr', 'ref', 'scaff'),
            'strand': ('strand', ),
            'start': ('start', 'begin'),
            'end': ('end', 'stop'),
            'date': ('date', 'time', 'birthday', 'day')
        }

        # First, detect boolean values
        if self.are_boolean(values):
            return "boolean"

        # Then, detect special type with header
        for stype, expressions in special_types.items():
            # Need to check once if it matches any subtype
            expression_regexp = "|".join([".*{}.*".format(expression.lower()) for expression in expressions])
            if re.match(expression_regexp, self.header[header_index].lower(), re.IGNORECASE) is not None:
                # Test if start and end are numerical
                if stype in ('start', 'end') and not all(self.is_decimal(val) for val in values):
                    break
                # test if strand is a category with 3 elements max
                if stype == 'strand' and len(set(list(filter(None, values)))) > 3:
                    break
                # Test if date respects a date format
                if stype == 'date' and not all(self.is_date(val) for val in values):
                    break
                return stype

        # Then, check goterm
        # if all((val.startswith("GO:") and val[3:].isdigit()) for val in values):
        #     return "goterm"

        # If header contain ID, it is text
        if re.match(r".*ID.*", self.header[header_index]) is not None:
            return "text"

        # Finaly, check numerical/text
        if all(self.is_decimal(val) for val in values):
            if all(val == "" for val in values):
                return "text"
            return "numeric"

        return "text"  # default

    @staticmethod
    def are_boolean(values):
        """Check if a list of values are boolean strings

        Parameters
        ----------
        values : list
            List of strings

        Returns
        -------
        boolean
            True if values are boolean strings (true false or 0 1)
        """
        return set(list(filter(None, [value.lower() for value in values]))) in ({'false', 'true'}, {'0', '1'})

    @staticmethod
    def is_decimal(value):
        """Guess if a variable if a number

        Parameters
        ----------
        value :
            The var to test

        Returns
        -------
        boolean
            True if it's decimal
        """
        if value == "":
            return True
        if value.isdigit():
            return True
        else:
            try:
                float(value)
                return True
            except ValueError:
                return False

    @staticmethod
    def is_date(value):
        """Guess if a variable is a date

        Parameters
        ----------
        value :
            The var to test

        Returns
        -------
        boolean
            True if it's a date
        """
        if value == "":
            return True
        try:
            parser.parse(value, dayfirst=True).date()
            return True
        except Exception:
            return False

    @property
    def transposed_preview(self):
        """Transpose the preview

        Returns
        -------
        list
            Transposed preview
        """
        data = [[] for x in range(len(self.header))]
        for row in self.preview:
            for key, value in row.items():
                data[self.header.index(key)].append(value)
        return data

    @cached_property
    def dialect(self):
        """Csv dialect

        Returns
        -------
        TYPE
            dialect
        """
        with open(self.path, 'r', encoding="utf-8", errors="ignore") as tabfile:
            # The sniffer needs to have enough data to guess,
            # and we restrict to a list of allowed delimiters to avoid strange results
            contents = tabfile.readline()
            dialect = csv.Sniffer().sniff(contents, delimiters=';,\t ')
            return dialect

    def integrate(self, dataset_id, forced_columns_type=None, forced_header_names=None, public=False):
        """Integrate the file

        Parameters
        ----------
        forced_columns_type : list
            columns type
        public : bool, optional
            True if dataset will be public
        """
        self.public = public
        self.set_preview_and_header()
        if forced_columns_type:
            self.force_columns_type(forced_columns_type)
        else:
            self.set_columns_type()
        if forced_header_names:
            self.force_header_names(forced_header_names)
        File.integrate(self, dataset_id=dataset_id)

    def set_rdf_abstraction_domain_knowledge(self):
        """Set intersection of abstraction and domain knowledge"""
        self.set_rdf_abstraction()
        self.set_rdf_domain_knowledge()

    def set_rdf_domain_knowledge(self):
        """Set the domain knowledge"""
        for index, attribute in enumerate(self.header):
            if self.columns_type[index] in ('category', 'reference', 'strand') and self.header[index] in self.category_values:
                s = self.namespace_data["{}Category".format(self.format_uri(attribute, remove_space=True))]
                p = self.namespace_internal["category"]
                for value in self.category_values[self.header[index]]:
                    o = self.rdfize(value)
                    if self.columns_type[index] == "strand":
                        o = self.get_faldo_strand(value)
                    self.graph_abstraction_dk.add((s, p, o))
                    self.graph_abstraction_dk.add((o, rdflib.RDF.type, self.namespace_data["{}CategoryValue".format(self.format_uri(self.header[index]))]))
                    self.graph_abstraction_dk.add((o, rdflib.RDFS.label, rdflib.Literal(value)))

    def set_rdf_abstraction(self):
        """Set the abstraction"""
        # Entity
        # Check subclass syntax (<)
        if self.header[0].find('<') > 0:
            splitted = self.header[0].split('<')
            entity = self.rdfize(splitted[0])
            entity_label = rdflib.Literal(splitted[0])
            mother_class = self.rdfize(splitted[1])
            # subClassOf
            self.graph_abstraction_dk.add((entity, rdflib.RDFS.subClassOf, mother_class))
        else:
            entity = self.rdfize(self.header[0])
            entity_label = rdflib.Literal(self.header[0])

        self.graph_abstraction_dk.add((entity, rdflib.RDF.type, rdflib.OWL.Class))
        self.graph_abstraction_dk.add((entity, rdflib.RDF.type, self.namespace_internal['entity']))
        if self.faldo_entity:
            self.graph_abstraction_dk.add((entity, rdflib.RDF.type, self.namespace_internal["faldo"]))
        self.graph_abstraction_dk.add((entity, rdflib.RDFS.label, entity_label))
        if self.columns_type[0] == 'start_entity':
            self.graph_abstraction_dk.add((entity, rdflib.RDF.type, self.namespace_internal['startPoint']))

        available_ontologies = {}
        for ontology in OntologyManager(self.app, self.session).list_ontologies():
            available_ontologies[ontology['short_name']] = ontology['uri']
        attribute_blanks = {}

        # Attributes and relations
        for index, attribute_name in enumerate(self.header):

            symetric_relation = False

            # Skip entity
            if index == 0:
                continue

            # Skip label for second column
            if self.columns_type[index] == "label" and index == 1:
                continue

            blank = BNode()
            # Relation
            if self.columns_type[index] in ('general_relation', 'symetric_relation', 'indirect_relation'):
                symetric_relation = True if self.columns_type[index] == 'symetric_relation' else False
                indirect_relation = True if self.columns_type[index] == 'indirect_relation' else False
                splitted = attribute_name.split('@')

                attribute = self.rdfize(splitted[0])
                label = rdflib.Literal(splitted[0])
                rdf_range = self.rdfize(splitted[1])
                rdf_type = rdflib.OWL.ObjectProperty

                # New way of storing relations (starting from 4.4.0)

                endpoint = rdflib.Literal(self.external_endpoint) if self.external_endpoint else rdflib.Literal(self.settings.get('triplestore', 'endpoint'))
                self.graph_abstraction_dk.add((blank, rdflib.RDF.type, rdflib.OWL.ObjectProperty))
                self.graph_abstraction_dk.add((blank, rdflib.RDF.type, self.namespace_internal["AskomicsRelation"]))
                self.graph_abstraction_dk.add((blank, self.namespace_internal["uri"], attribute))
                self.graph_abstraction_dk.add((blank, rdflib.RDFS.label, label))
                self.graph_abstraction_dk.add((blank, rdflib.RDFS.domain, entity))
                self.graph_abstraction_dk.add((blank, rdflib.RDFS.range, rdf_range))
                self.graph_abstraction_dk.add((blank, rdflib.DCAT.endpointURL, endpoint))
                self.graph_abstraction_dk.add((blank, rdflib.DCAT.dataset, rdflib.Literal(self.name)))
                if symetric_relation:
                    # Add reverted relation
                    sym_blank = BNode()
                    self.graph_abstraction_dk.add((sym_blank, rdflib.RDF.type, rdflib.OWL.ObjectProperty))
                    self.graph_abstraction_dk.add((sym_blank, rdflib.RDF.type, self.namespace_internal["AskomicsRelation"]))
                    self.graph_abstraction_dk.add((sym_blank, self.namespace_internal["uri"], attribute))
                    self.graph_abstraction_dk.add((sym_blank, rdflib.RDFS.label, label))
                    self.graph_abstraction_dk.add((sym_blank, rdflib.DCAT.endpointURL, endpoint))
                    self.graph_abstraction_dk.add((sym_blank, rdflib.DCAT.dataset, rdflib.Literal(self.name)))
                    self.graph_abstraction_dk.add((sym_blank, rdflib.RDFS.domain, rdf_range))
                    self.graph_abstraction_dk.add((sym_blank, rdflib.RDFS.range, entity))

                if indirect_relation:
                    self.graph_abstraction_dk.add((blank, self.namespace_internal["isIndirectRelation"], rdflib.Literal("true", datatype=rdflib.XSD.boolean)))

                continue

            # Manage ontologies
            if self.columns_type[index] in available_ontologies:

                attribute = self.rdfize(attribute_name)
                label = rdflib.Literal(attribute_name)
                rdf_range = self.rdfize(available_ontologies[self.columns_type[index]])
                rdf_type = rdflib.OWL.ObjectProperty

                # New way of storing relations (starting from 4.4.0)
                blank = BNode()
                endpoint = rdflib.Literal(self.external_endpoint) if self.external_endpoint else rdflib.Literal(self.settings.get('triplestore', 'endpoint'))
                self.graph_abstraction_dk.add((blank, rdflib.RDF.type, rdflib.OWL.ObjectProperty))
                self.graph_abstraction_dk.add((blank, rdflib.RDF.type, self.namespace_internal["AskomicsRelation"]))
                self.graph_abstraction_dk.add((blank, self.namespace_internal["uri"], attribute))
                self.graph_abstraction_dk.add((blank, rdflib.RDFS.label, label))
                self.graph_abstraction_dk.add((blank, rdflib.RDFS.domain, entity))
                self.graph_abstraction_dk.add((blank, rdflib.RDFS.range, rdf_range))
                self.graph_abstraction_dk.add((blank, rdflib.DCAT.endpointURL, endpoint))
                self.graph_abstraction_dk.add((blank, rdflib.DCAT.dataset, rdflib.Literal(self.name)))

                continue

            # Category
            elif self.columns_type[index] in ('category', 'reference', 'strand'):
                attribute = self.rdfize(attribute_name)
                label = rdflib.Literal(attribute_name)
                rdf_range = self.namespace_data["{}Category".format(self.format_uri(attribute_name, remove_space=True))]
                rdf_type = rdflib.OWL.ObjectProperty
                self.graph_abstraction_dk.add((blank, rdflib.RDF.type, self.namespace_internal["AskomicsCategory"]))

            # Numeric
            elif self.columns_type[index] in ('numeric', 'start', 'end'):
                attribute = self.rdfize(attribute_name)
                label = rdflib.Literal(attribute_name)
                rdf_range = rdflib.XSD.decimal
                rdf_type = rdflib.OWL.DatatypeProperty

            # Boolean
            elif self.columns_type[index] == "boolean":
                attribute = self.rdfize(attribute_name)
                label = rdflib.Literal(attribute_name)
                rdf_range = rdflib.XSD.boolean
                rdf_type = rdflib.OWL.DatatypeProperty

            # Date
            elif self.columns_type[index] == "date":
                attribute = self.rdfize(attribute_name)
                label = rdflib.Literal(attribute_name)
                rdf_range = rdflib.XSD.date
                rdf_type = rdflib.OWL.DatatypeProperty

            # Text (default)
            else:
                attribute = self.rdfize(attribute_name)
                label = rdflib.Literal(attribute_name)
                rdf_range = rdflib.XSD.string
                rdf_type = rdflib.OWL.DatatypeProperty

            attribute_blanks[attribute] = blank

            # New way of storing attributes (starting from 4.4.0)
            self.graph_abstraction_dk.add((blank, rdflib.RDF.type, rdf_type))
            self.graph_abstraction_dk.add((blank, self.namespace_internal["uri"], attribute))
            self.graph_abstraction_dk.add((blank, rdflib.RDFS.label, label))
            self.graph_abstraction_dk.add((blank, rdflib.RDFS.domain, entity))
            self.graph_abstraction_dk.add((blank, rdflib.RDFS.range, rdf_range))

        # Faldo:
        if self.faldo_entity:
            for key, value in self.faldo_abstraction.items():
                if value:
                    blank = attribute_blanks[value]
                    self.graph_abstraction_dk.add((blank, rdflib.RDF.type, self.faldo_abstraction_eq[key]))
                    self.graph_abstraction_dk.add((blank, self.namespace_internal["uri"], value))

    def generate_rdf_content(self):
        """Generator of the rdf content

        Yields
        ------
        Graph
            Rdf content
        """
        total_lines = sum(1 for line in open(self.path))

        available_ontologies = {}
        for ontology in OntologyManager(self.app, self.session).list_ontologies():
            available_ontologies[ontology['short_name']] = ontology['uri']

        with open(self.path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file, dialect=self.dialect)

            # Skip header
            next(reader)

            # Entity
            # Check subclass syntax (<)
            if self.header[0].find('<') > 0:
                splitted = self.header[0].split('<')
                entity_type = self.rdfize(splitted[0])
            else:
                entity_type = self.rdfize(self.header[0])

            # Faldo
            self.faldo_entity = True if 'start' in self.columns_type and 'end' in self.columns_type else False

            has_label = None
            # Get first value, ignore others
            if "label" in self.columns_type and self.columns_type.index("label") == 1:
                has_label = True

            # Loop on lines
            for row_number, row in enumerate(reader):

                # Percent
                self.graph_chunk.percent = row_number * 100 / total_lines

                # skip blank lines
                if not row:
                    continue

                # Entity
                entity = self.rdfize(row[0], custom_namespace=self.namespace_entity)
                if has_label and row[1]:
                    label = row[1]
                else:
                    label = self.get_uri_label(row[0])
                self.graph_chunk.add((entity, rdflib.RDF.type, entity_type))
                self.graph_chunk.add((entity, rdflib.RDFS.label, rdflib.Literal(label)))

                # Faldo
                faldo_reference = None
                faldo_strand = None
                faldo_start = None
                faldo_end = None

                # Position
                start = None
                end = None
                reference = None

                # For attributes, loop on cell
                for column_number, cell in enumerate(row):
                    current_type = self.columns_type[column_number]
                    current_header = self.header[column_number]

                    attribute = None
                    relation = None
                    symetric_relation = False

                    # Skip label type for second column
                    # if type is label but not second column, default to string
                    if current_type == "label" and column_number == 1:
                        continue

                    # We ignore all data for indirect relations
                    if current_type == "indirect_relation":
                        continue

                    # Skip entity and blank cells
                    if column_number == 0 or (not cell and not current_type == "strand"):
                        continue

                    # Relation
                    if current_type in ('general_relation', 'symetric_relation'):
                        symetric_relation = True if current_type == 'symetric_relation' else False
                        splitted = current_header.split('@')
                        relation = self.rdfize(splitted[0])
                        attribute = self.rdfize(cell)

                    # Ontology
                    elif current_type in available_ontologies:
                        symetric_relation = False
                        relation = self.rdfize(current_header)
                        attribute = self.rdfize(cell)

                    # Category
                    elif current_type in ('category', 'reference', 'strand'):
                        potential_relation = self.rdfize(current_header)
                        if current_type == "strand":
                            # Override csv value, use "proper" values
                            cell = self.get_faldo_strand_label(cell)
                        if current_header not in self.category_values.keys():
                            # Add the category in dict, and the first value in a set
                            self.category_values[current_header] = {cell, }
                        else:
                            # add the cell in the set
                            self.category_values[current_header].add(cell)
                        if current_type == 'reference':
                            faldo_reference = self.rdfize(cell)
                            reference = cell
                            self.faldo_abstraction["reference"] = potential_relation
                        elif current_type == 'strand':
                            faldo_strand = self.get_faldo_strand(cell)
                            self.faldo_abstraction["strand"] = potential_relation
                        else:
                            relation = potential_relation
                            attribute = self.rdfize(cell)

                    # Numeric
                    elif current_type in ('numeric', 'start', 'end'):
                        potential_relation = self.rdfize(current_header)
                        if current_type == "start":
                            faldo_start = rdflib.Literal(self.convert_type(cell))
                            start = cell
                            self.faldo_abstraction["start"] = potential_relation
                        elif current_type == "end":
                            faldo_end = rdflib.Literal(self.convert_type(cell))
                            end = cell
                            self.faldo_abstraction["end"] = potential_relation
                        else:
                            relation = potential_relation
                            attribute = rdflib.Literal(self.convert_type(cell))

                    # Boolean
                    elif current_type == "boolean":
                        relation = self.rdfize(current_header)
                        if cell.lower() in ("1", "true"):
                            attribute = rdflib.Literal("true", datatype=rdflib.XSD.boolean)
                        else:
                            attribute = rdflib.Literal("false", datatype=rdflib.XSD.boolean)

                    elif current_type == "date":
                        relation = self.rdfize(current_header)
                        attribute = rdflib.Literal(self.convert_type(cell, try_date=True))

                    # default is text
                    else:
                        relation = self.rdfize(current_header)
                        attribute = rdflib.Literal(self.convert_type(cell))

                    if entity and relation is not None and attribute is not None:
                        self.graph_chunk.add((entity, relation, attribute))
                        if symetric_relation:
                            self.graph_chunk.add((attribute, relation, entity))

                if self.faldo_entity and faldo_start and faldo_end:

                    # Triples respecting faldo ontology

                    location = BNode()
                    begin_node = BNode()
                    end_node = BNode()

                    self.graph_chunk.add((entity, self.faldo.location, location))

                    self.graph_chunk.add((location, rdflib.RDF.type, self.faldo.region))
                    self.graph_chunk.add((location, self.faldo.begin, begin_node))
                    self.graph_chunk.add((location, self.faldo.end, end_node))

                    self.graph_chunk.add((begin_node, rdflib.RDF.type, self.faldo.ExactPosition))
                    self.graph_chunk.add((begin_node, self.faldo.position, faldo_start))

                    self.graph_chunk.add((end_node, rdflib.RDF.type, self.faldo.ExactPosition))
                    self.graph_chunk.add((end_node, self.faldo.position, faldo_end))

                    if faldo_reference:
                        self.graph_chunk.add((begin_node, self.faldo.reference, faldo_reference))
                        self.graph_chunk.add((end_node, self.faldo.reference, faldo_reference))

                    if faldo_strand:
                        self.graph_chunk.add((begin_node, rdflib.RDF.type, faldo_strand))
                        self.graph_chunk.add((end_node, rdflib.RDF.type, faldo_strand))

                    # Shortcut triple for faldo queries
                    self.graph_chunk.add((entity, self.namespace_internal["faldoBegin"], faldo_start))
                    self.graph_chunk.add((entity, self.namespace_internal["faldoEnd"], faldo_end))
                    if faldo_reference:
                        self.graph_chunk.add((entity, self.namespace_internal["faldoReference"], faldo_reference))
                        if faldo_strand:
                            strand_ref = self.get_reference_strand_uri(reference, faldo_strand, None)
                            for sref in strand_ref:
                                self.graph_chunk.add((entity, self.namespace_internal["referenceStrand"], sref))

                    if faldo_strand:
                        self.graph_chunk.add((entity, self.namespace_internal["faldoStrand"], faldo_strand))

                    # blocks
                    block_base = self.settings.getint("triplestore", "block_size")
                    block_start = int(start) // block_base
                    block_end = int(end) // block_base

                    for slice_block in range(block_start, block_end + 1):
                        self.graph_chunk.add((entity, self.namespace_internal['includeIn'], rdflib.Literal(int(slice_block))))
                        if reference:
                            block_reference = self.rdfize(self.format_uri("{}_{}".format(reference, slice_block)))
                            self.graph_chunk.add((entity, self.namespace_internal["includeInReference"], block_reference))
                            if faldo_strand:
                                strand_ref = self.get_reference_strand_uri(reference, faldo_strand, slice_block)
                                for sref in strand_ref:
                                    self.graph_chunk.add((entity, self.namespace_internal["includeInReferenceStrand"], sref))
                        if faldo_strand:
                            strand_ref = self.get_reference_strand_uri(None, faldo_strand, slice_block)
                            for sref in strand_ref:
                                self.graph_chunk.add((entity, self.namespace_internal["includeInStrand"], sref))

                yield
