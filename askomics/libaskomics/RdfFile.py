import os
from shutil import copyfile

from askomics.libaskomics.File import File
from askomics.libaskomics.SparqlQueryLauncher import SparqlQueryLauncher
from askomics.libaskomics.Utils import Utils


class RdfFile(File):
    """RDF (turtle) File

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

    def set_preview(self):
        """Summary"""
        pass

    def get_preview(self):
        """Get a preview of the frist 100 lines of a ttl file

        Returns
        -------
        TYPE
            Description
        """
        with open(self.path) as ttl_file:
            # Read 100 lines
            head = ''
            for x in range(1, 100):
                head += ttl_file.readline()

        return {
            'type': self.type,
            'id': self.id,
            'name': self.name,
            'data': {
                'preview': head
            }
        }

    def integrate(self, public=False):
        """Integrate the file into the triplestore

        Parameters
        ----------
        public : bool, optional
            Integrate in private or public graph
        """
        sparql = SparqlQueryLauncher(self.app, self.session)

        self.public = public

        method = self.settings.get('triplestore', 'upload_method')

        # insert metadata
        sparql.insert_data(self.get_metadata(), self.user_graph, metadata=True)

        if method == "load":
            # cp file into ttl dir
            tmp_file_name = 'tmp_{}_{}.ttl'.format(
                Utils.get_random_string(5),
                self.name,
            )
            temp_file_path = '{}/{}'.format(self.ttl_dir, tmp_file_name)
            copyfile(self.path, temp_file_path)
            # Load the chunk
            sparql.load_data(tmp_file_name, self.file_graph, self.host_url)

            # Remove tmp file
            if not self.settings.getboolean('askomics', 'debug_ttl'):
                os.remove(temp_file_path)
        else:

            with open(self.path) as ttl_file:
                ttl_content = ttl_file.read()
                sparql.insert_ttl_string(ttl_content, self.user_graph)

        self.set_triples_number()
