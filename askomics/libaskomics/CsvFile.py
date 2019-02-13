from askomics.libaskomics.File import File
from askomics.libaskomics.Utils import cached_property
import csv
import re

class CsvFile(File):

    def __init__(self, app, session, file_info):
        File.__init__(self, app, session, file_info)
        self.header = []
        self.preview = []
        self.columns_type = []


    def set_preview_and_header(self, preview_limit=30):

        with open(self.path, 'r', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file, dialect=self.dialect)
            count = 0
            # Store header
            header = next(reader)
            self.header = [h.strip() for h in header]

            # Loop on lines 
            data = [[] for x in range(len(header))]
            for row in reader:
                for i, val in enumerate(row):
                    data[i].append(val)

                    # Stop after x lines
                    if preview_limit:
                        count += 1
                        if count > preview_limit:
                            break

        self.preview = data

    def set_columns_type(self):

        index = 0
        for col in self.preview:
            self.columns_type.append(self.guess_column_type(col, index))
            index += 1


    def guess_column_type(self, values, header_index):

        # First col is entity start
        if header_index == 0:
            return "entity_start"

        # if name contain @, this is a relation
        if self.header[header_index].find("@") > 0:
            return "general_relation"

        special_types = {
            'organism': ('organism', 'taxon', 'species'),
            'chromosom': ('chrom', ),
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
                    if stype == 'date' and not all(date_regex.match(val) for val in values):
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


    @cached_property
    def dialect(self):

        with open(self.path, 'r', encoding="utf-8", errors="ignore") as tabfile:
            # The sniffer needs to have enough data to guess,
            # and we restrict to a list of allowed delimiters to avoid strange results
            contents = tabfile.readline()
            dialect = csv.Sniffer().sniff(contents, delimiters=';,\t ')
            return dialect