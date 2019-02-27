import csv
import re
import rdflib

from urllib.parse import quote

from askomics.libaskomics.File import File
from askomics.libaskomics.Utils import cached_property

class CsvFile(File):

    def __init__(self, app, session, file_info, host_url=None):
        File.__init__(self, app, session, file_info, host_url)
        self.header = []
        self.preview = []
        self.columns_type = []
        self.category_values = {}

    def set_preview(self):

        self.set_preview_and_header()
        self.set_columns_type()

    def get_preview(self):

        return {
            'type': self.type,
            'id': self.id,
            'name': self.name,
            'csv_data': {
                'header': self.header,
                'content_preview': self.preview,
                'columns_type': self.columns_type
            }
        }

    def force_columns_type(self, forced_columns_type):

        self.columns_type = forced_columns_type

    def set_preview_and_header(self, preview_limit=30):

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
                if preview_limit:
                    count += 1
                    if count > preview_limit:
                        break

        self.preview = preview

    def set_columns_type(self):

        index = 0
        for col in self.transposed_preview:
            self.columns_type.append(self.guess_column_type(col, index))
            index += 1


    def guess_column_type(self, values, header_index):

        # First col is entity start
        if header_index == 0:
            return "start_entity"

        # if name contain @, this is a relation
        if self.header[header_index].find("@") > 0:
            return "general_relation"

        special_types = {
            'organism': ('organism', 'taxon', 'species'),
            'chromosome': ('chrom', ),
            'strand': ('strand', ),
            'start': ('start', 'begin'),
            'end': ('end', 'stop'),
            'datetime': ('date', 'time', 'birthday')
        }

        date_regex = re.compile(r'^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}')

        # First, detect special type with header
        for stype, expressions in special_types.items():
            for expression in expressions:
                epression_regexp = ".*{}.*".format(expression)
                if re.match(epression_regexp, self.header[header_index], re.IGNORECASE) is not None:
                    # Test if start and end are numerical
                    if stype in ('start', 'end') and not all(self.is_decimal(val) for val in values):
                        break
                    # test if strand is a catégory with 2 elements
                    if stype == 'strand' and len(set(values)) != 2:
                        break
                    # Test if date respect a date format
                    if stype == 'datetime' and not all(date_regex.match(val) for val in values):
                        break
                    return stype

        # Then, check goterm
        if all((val.startswith("GO:") and val[3:].isdigit()) for val in values):
            return "goterm"

        threshold = 10
        if len(values) < 30:
            threshold = 5

        # Finaly, check numerical/text/category
        if all(self.is_decimal(val) for val in values):
            if all(val == "" for val in values):
                return "text"
            return "numeric"
        elif len(set(values)) < threshold:
            return "category"

        return "text" # default

    @staticmethod
    def is_decimal(value):

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

        data = [[] for x in range(len(self.header))]
        for row in self.preview:
            for key, value in row.items():
                data[self.header.index(key)].append(value)
        return data


    @cached_property
    def dialect(self):

        with open(self.path, 'r', encoding="utf-8", errors="ignore") as tabfile:
            # The sniffer needs to have enough data to guess,
            # and we restrict to a list of allowed delimiters to avoid strange results
            contents = tabfile.readline()
            dialect = csv.Sniffer().sniff(contents, delimiters=';,\t ')
            return dialect


    def integrate(self, forced_columns_type, public=False):

        self.public = public
        self.set_preview_and_header()
        self.force_columns_type(forced_columns_type)
        File.integrate(self)

    def get_rdf_domain_knowledge(self):

        rdf_graph = self.rdf_graph()


        for index, attribute in enumerate(self.header):

            if self.columns_type[index] in ('category', 'organism', 'chromosome', 'strand'):
                s = self.askomics_namespace["{}Category".format(quote(attribute))]
                p = self.askomics_namespace["category"]
                for value in self.category_values[self.header[index]]:
                    o = self.askomics_namespace[quote(value)]
                    rdf_graph.add((s, p, o))
                    rdf_graph.add((o, rdflib.RDF.type, self.askomics_namespace["{}CategoryValue".format(quote(self.header[index]))]))
                    rdf_graph.add((o, rdflib.RDFS.label, rdflib.Literal(value)))

        return rdf_graph

    def get_rdf_abstraction(self):

        rdf_graph = self.rdf_graph()

        # Entity
        entity = self.askomics_prefix[quote(self.header[0])]

        rdf_graph.add((entity, rdflib.RDF.type, rdflib.OWL.Class))
        rdf_graph.add((entity, rdflib.RDF.type, self.askomics_namespace['entity']))
        if self.columns_type[0] == 'start_entity':
            rdf_graph.add((entity, rdflib.RDF.type, self.askomics_namespace['startPoint']))

        # Attributes and relations
        for index, attribute_name in enumerate(self.header):

            # Skip entity
            if index == 0:
                continue

            # Relation
            if self.columns_type[index] in ('general_relation', ):
                splitted = attribute_name.split('@')

                attribute = self.askomics_namespace[quote(splitted[0])]
                label = rdflib.Literal(splitted[0])
                rdf_range = self.askomics_prefix[quote(splitted[1])]
                rdf_type = rdflib.OWL.ObjectProperty

            # Category
            elif self.columns_type[index] in ('category', 'organism', 'chromosome', 'strand'):
                attribute = self.askomics_namespace[quote(attribute_name)]
                label = rdflib.Literal(attribute_name)
                rdf_range = self.askomics_namespace["{}Category".format(quote(attribute_name))]
                rdf_type = rdflib.OWL.DatatypeProperty

            # Numeric
            elif self.columns_type[index] in ('numeric', 'start', 'end'):
                attribute = self.askomics_namespace[quote(attribute_name)]
                label = rdflib.Literal(attribute_name)
                rdf_range = rdflib.XSD.decimal
                rdf_type = rdflib.OWL.DatatypeProperty

            #TODO: datetime

            # Text (default)
            else:
                attribute = self.askomics_namespace[quote(attribute_name)]
                label = rdflib.Literal(attribute_name)
                rdf_range = rdflib.XSD.string
                rdf_type = rdflib.OWL.DatatypeProperty

            rdf_graph.add((attribute, rdflib.RDF.type, rdf_type))
            rdf_graph.add((attribute, rdflib.RDFS.label, label))
            rdf_graph.add((attribute, rdflib.RDFS.domain, entity))
            rdf_graph.add((attribute, rdflib.RDFS.range, rdf_range))

        return rdf_graph


    def generate_rdf_content(self):


        with open(self.path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file, dialect=self.dialect)

            # Skip header
            next(reader)

            # Entity
            entity_type = self.askomics_prefix[quote(self.header[0])]

            # Faldo?
            is_faldo_entity = True if 'start' in self.columns_type and 'end' in self.columns_type else False


            # Loop on lines
            for row_number, row in enumerate(reader):

                rdf_graph = self.rdf_graph()

                # skip blank lines
                if not row:
                    continue

                # Entity
                entity = self.askomics_prefix[quote(row[0])]
                rdf_graph.add((entity, rdflib.RDF.type, entity_type))

                # For attributes, loop on cell
                for column_number, cell in enumerate(row):
                    current_type = self.columns_type[column_number]
                    current_header = self.header[column_number]

                    # Skip entity and blank cells
                    if column_number == 0 or not cell:
                        continue

                    # Relation
                    if current_type == 'general_relation':
                        splitted = current_header.split('@')
                        relation = self.askomics_namespace[quote(splitted[0])]
                        attribute = self.askomics_prefix[quote(cell)]

                    # Category
                    elif current_type in ('category', 'organism', 'chromosome', 'strand'):
                        if current_header not in self.category_values.keys():
                            # Add the category in dict, and the first value in a set
                            self.category_values[current_header] = {cell, }
                        else:
                            # add the cell in the set
                            self.category_values[current_header].add(cell)
                        relation = self.askomics_namespace[quote(current_header)]
                        attribute = rdflib.Literal(self.convert_type(cell))

                    # Numeric
                    elif current_type in ('numeric', 'start', 'end'):
                        relation = self.askomics_namespace[quote(current_header)]
                        attribute = rdflib.Literal(self.convert_type(cell))


                    #TODO: datetime

                    # default is text
                    else:
                        relation = self.askomics_namespace[quote(current_header)]
                        attribute = rdflib.Literal(self.convert_type(cell))

                    rdf_graph.add((entity, relation, attribute))

                yield rdf_graph


    def convert_type(self, value):
        """Convert a value to a int or float or text

        Parameters
        ----------
        value : string
            The value to convert

        Returns
        -------
        string/float/int
            the converted value
        """
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return value

        return value
