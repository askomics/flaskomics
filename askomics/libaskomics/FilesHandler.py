from askomics.libaskomics.Params import Params
from askomics.libaskomics.CsvFile import CsvFile

class FilesHandler(Params):

    def __init__(self, app, session, files_infos):
        
        Params.__init__(self, app, session)
        self.files_infos = files_infos
        self.files = []
        self.get_files()

    def get_files(self):

        for file in self.files_infos:
            self.files.append(CsvFile(self.app, self.session, file))
            # if file['type'] in ('csv', 'tsv'):
                # files.append(CsvFile(self.app, self.session, file))
            # elif file['type'] in ('gff', 'gff3'):
            #     files.append(GffFiles(self.app, self.session, file))
            # elif file['type'] in ('bed', ):
            #     files.append(BedFiles(self.app, self.session, file))
            # elif file['type'] in ('ttl', 'owl', 'rdf', 'n3'):
            #     files.append(RdfFiles(self.app, self.session, file))       
            # else:
            #     pass      

