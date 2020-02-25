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

        self.type_dict = {
            "rdf/ttl": "turtle",
            "rdf/xml": "xml",
            "rdf/nt": "nt"
        }

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
            'name': self.human_name,
            'error': self.error,
            'error_message': self.error_message,
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

        # Load file into a RDF graph
        self.graph_chunk.parse(self.path, format=self.type_dict[self.type])

        # insert metadata
        sparql.insert_data(self.get_metadata(), self.file_graph, metadata=True)

        if method == "load":
            # write rdf into a tmpfile and load it
            temp_file_name = 'tmp_{}_{}.{}'.format(
                Utils.get_random_string(5),
                self.name,
                self.rdf_extention
            )

            # Try to load data. if failure, wait 5 sec and retry 5 time
            Utils.redo_if_failure(self.log, 5, 5, self.load_graph, self.graph_chunk, temp_file_name)

        else:
            # Insert
            # Try to insert data. if failure, wait 5 sec and retry 5 time
            Utils.redo_if_failure(self.log, 5, 5, sparql.insert_data, self.graph_chunk, self.file_graph)

        self.set_triples_number()
