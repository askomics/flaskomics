import csv
import re
import rdflib

from urllib.parse import quote
from rdflib import BNode

from askomics.libaskomics.File import File
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
            'name': self.name,
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

    def set_preview_and_header(self):
        """Set the preview and header by looking in the fists lines of the file"""
        with open(self.path, 'r', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file, dialect=self.dialect)
            count = 0
            # Store header
            header = next(reader)
            self.header = [h.strip() for h in header]

            # Loop on lines
            preview = []
            for row in reader:
                res_row = {}
                for i, cell in enumerate(row):
                    if len(cell) >= 25:
                        res_row[self.header[i]] = "{}...".format(cell[:25])
                    else:
                        res_row[self.header[i]] = cell
                preview.append(res_row)

                # Stop after x lines
                if self.preview_limit:
                    count += 1
                    if count > self.preview_limit:
                        break

        self.preview = preview

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

        special_types = {
            'reference': ('chrom', 'ref'),
            'strand': ('strand', ),
            'start': ('start', 'begin'),
            'end': ('end', 'stop'),
            'datetime': ('date', 'time', 'birthday', 'day')
        }

        date_regex = re.compile(r'^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}')

        # First, detect special type with header
        for stype, expressions in special_types.items():
            for expression in expressions:
                epression_regexp = ".*{}.*".format(expression.lower())
                if re.match(epression_regexp, self.header[header_index], re.IGNORECASE) is not None:
                    # Test if reference is a category
                    if stype == "reference" and not self.is_category(values):
                        break
                    # Test if start and end are numerical
                    if stype in ('start', 'end') and not all(self.is_decimal(val) for val in values):
                        break
                    # test if strand is a category with 2 elements
                    if stype == 'strand' and len(set(list(filter(None, values)))) != 2:
                        break
                    # Test if date respect a date format
                    if stype == 'datetime' and all(date_regex.match(val) for val in values):
                        break
                    return stype

        # Then, check goterm
        if all((val.startswith("GO:") and val[3:].isdigit()) for val in values):
            return "goterm"

        # Finaly, check numerical/text/category
        if all(self.is_decimal(val) for val in values):
            if all(val == "" for val in values):
                return "text"
            return "numeric"
        elif self.is_category(values):
            return "category"

        return "text"  # default

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

    def integrate(self, forced_columns_type, public=False):
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
        self.force_columns_type(forced_columns_type)
        File.integrate(self)

    def set_rdf_abstraction_domain_knowledge(self):
        """Set intersection of abstraction and domain knowledge"""
        self.set_rdf_abstraction()
        self.set_rdf_domain_knowledge()

    def set_rdf_domain_knowledge(self):
        """Set the domain knowledge"""
        for index, attribute in enumerate(self.header):

            if self.columns_type[index] in ('category', 'reference', 'strand'):
                s = self.askomics_prefix["{}Category".format(self.format_uri(attribute, remove_space=True))]
                p = self.askomics_namespace["category"]
                for value in self.category_values[self.header[index]]:
                    o = self.askomics_prefix[self.format_uri(value)]
                    self.graph_abstraction_dk.add((s, p, o))
                    self.graph_abstraction_dk.add((o, rdflib.RDF.type, self.askomics_prefix["{}CategoryValue".format(self.format_uri(self.header[index]))]))
                    self.graph_abstraction_dk.add((o, rdflib.RDFS.label, rdflib.Literal(value)))
                    if self.columns_type[index] == "strand":
                        self.graph_abstraction_dk.add((o, rdflib.RDF.type, self.get_faldo_strand(value)))

    def set_rdf_abstraction(self):
        """Set the abstraction"""
        # Entity
        # Check subclass syntax (<)
        if self.header[0].find('<') > 0:
            splitted = self.header[0].split('<')
            entity = self.askomics_prefix[self.format_uri(splitted[0], remove_space=True)]
            entity_label = rdflib.Literal(splitted[0])
            mother_class = self.askomics_prefix[self.format_uri(splitted[1], remove_space=True)]
            # subClassOf
            self.graph_abstraction_dk.add((entity, rdflib.RDFS.subClassOf, mother_class))
        else:
            entity = self.askomics_prefix[self.format_uri(self.header[0], remove_space=True)]
            entity_label = rdflib.Literal(self.header[0])

        self.graph_abstraction_dk.add((entity, rdflib.RDF.type, rdflib.OWL.Class))
        self.graph_abstraction_dk.add((entity, rdflib.RDF.type, self.askomics_prefix['entity']))
        if self.faldo_entity:
            self.graph_abstraction_dk.add((entity, rdflib.RDF.type, self.askomics_prefix["faldo"]))
        self.graph_abstraction_dk.add((entity, rdflib.RDFS.label, entity_label))
        if self.columns_type[0] == 'start_entity':
            self.graph_abstraction_dk.add((entity, rdflib.RDF.type, self.askomics_prefix['startPoint']))

        # Attributes and relations
        for index, attribute_name in enumerate(self.header):

            symetric_relation = False

            # Skip entity
            if index == 0:
                continue

            # Relation
            if self.columns_type[index] in ('general_relation', 'symetric_relation'):
                symetric_relation = True if self.columns_type[index] == 'symetric_relation' else False
                splitted = attribute_name.split('@')

                attribute = self.askomics_prefix[quote(splitted[0])]
                label = rdflib.Literal(splitted[0])
                rdf_range = self.askomics_prefix[quote(splitted[1])]
                rdf_type = rdflib.OWL.ObjectProperty
                self.graph_abstraction_dk.add((attribute, rdflib.RDF.type, self.askomics_prefix["AskomicsRelation"]))

            # Category
            elif self.columns_type[index] in ('category', 'reference', 'strand'):
                attribute = self.askomics_prefix[self.format_uri(attribute_name, remove_space=True)]
                label = rdflib.Literal(attribute_name)
                rdf_range = self.askomics_prefix["{}Category".format(self.format_uri(attribute_name, remove_space=True))]
                rdf_type = rdflib.OWL.ObjectProperty
                self.graph_abstraction_dk.add((attribute, rdflib.RDF.type, self.askomics_prefix["AskomicsCategory"]))

            # Numeric
            elif self.columns_type[index] in ('numeric', 'start', 'end'):
                attribute = self.askomics_prefix[self.format_uri(attribute_name, remove_space=True)]
                label = rdflib.Literal(attribute_name)
                rdf_range = rdflib.XSD.decimal
                rdf_type = rdflib.OWL.DatatypeProperty

            # TODO: datetime

            # Text (default)
            else:
                attribute = self.askomics_prefix[self.format_uri(attribute_name, remove_space=True)]
                label = rdflib.Literal(attribute_name)
                rdf_range = rdflib.XSD.string
                rdf_type = rdflib.OWL.DatatypeProperty

            self.graph_abstraction_dk.add((attribute, rdflib.RDF.type, rdf_type))
            self.graph_abstraction_dk.add((attribute, rdflib.RDFS.label, label))
            self.graph_abstraction_dk.add((attribute, rdflib.RDFS.domain, entity))
            self.graph_abstraction_dk.add((attribute, rdflib.RDFS.range, rdf_range))
            if symetric_relation:
                self.graph_abstraction_dk.add((attribute, rdflib.RDFS.domain, rdf_range))
                self.graph_abstraction_dk.add((attribute, rdflib.RDFS.range, entity))

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
        with open(self.path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file, dialect=self.dialect)

            # Skip header
            next(reader)

            # Entity
            # Check subclass syntax (<)
            if self.header[0].find('<') > 0:
                splitted = self.header[0].split('<')
                entity_type = self.askomics_prefix[self.format_uri(splitted[0], remove_space=True)]
            else:
                entity_type = self.askomics_prefix[self.format_uri(self.header[0], remove_space=True)]

            # Faldo
            self.faldo_entity = True if 'start' in self.columns_type and 'end' in self.columns_type else False

            # Loop on lines
            for row_number, row in enumerate(reader):

                # skip blank lines
                if not row:
                    continue

                # Entity
                entity = self.askomics_prefix[self.format_uri(row[0])]
                self.graph_chunk.add((entity, rdflib.RDF.type, entity_type))
                self.graph_chunk.add((entity, rdflib.RDFS.label, rdflib.Literal(row[0])))

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

                    # Skip entity and blank cells
                    if column_number == 0 or not cell:
                        continue

                    # Relation
                    if current_type in ('general_relation', 'symetric_relation'):
                        symetric_relation = True if current_type == 'symetric_relation' else False
                        splitted = current_header.split('@')
                        relation = self.askomics_prefix[self.format_uri(splitted[0])]
                        attribute = self.askomics_prefix[self.format_uri(cell)]

                    # Category
                    elif current_type in ('category', 'reference', 'strand'):
                        potential_relation = self.askomics_prefix[self.format_uri(current_header, remove_space=True)]
                        if current_header not in self.category_values.keys():
                            # Add the category in dict, and the first value in a set
                            self.category_values[current_header] = {cell, }
                        else:
                            # add the cell in the set
                            self.category_values[current_header].add(cell)
                        if current_type == 'reference':
                            faldo_reference = self.askomics_prefix[self.format_uri(cell)]
                            reference = cell
                            self.faldo_abstraction["reference"] = potential_relation
                        elif current_type == 'strand':
                            faldo_strand = self.get_faldo_strand(cell)
                            self.faldo_abstraction["strand"] = potential_relation
                        else:
                            relation = potential_relation
                            attribute = self.askomics_prefix[self.format_uri(cell)]

                    # Numeric
                    elif current_type in ('numeric', 'start', 'end'):
                        potential_relation = self.askomics_prefix[self.format_uri(current_header, remove_space=True)]
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

                    # TODO: datetime

                    # default is text
                    else:
                        relation = self.askomics_prefix[self.format_uri(current_header, remove_space=True)]
                        attribute = rdflib.Literal(self.convert_type(cell))

                    if entity and relation is not None and attribute is not None:
                        self.graph_chunk.add((entity, relation, attribute))
                        if symetric_relation:
                            self.graph_chunk.add((attribute, relation, entity))

                if self.faldo_entity and faldo_start and faldo_end:
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

                    # blocks
                    block_base = self.settings.getint("triplestore", "block_size")
                    block_start = int(start) // block_base
                    block_end = int(end) // block_base

                    for slice_block in range(block_start, block_end + 1):
                        self.graph_chunk.add((entity, self.askomics_namespace['includeIn'], rdflib.Literal(int(slice_block))))
                        if reference:
                            block_reference = self.askomics_prefix[self.format_uri("{}_{}".format(reference, slice_block))]
                            self.graph_chunk.add((entity, self.askomics_namespace["includeInReference"], block_reference))

                yield
