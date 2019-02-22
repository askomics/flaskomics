import os
import rdflib
import datetime
import time
import tempfile
from pkg_resources import get_distribution

from rdflib.namespace import Namespace

from askomics.libaskomics.Utils import Utils
from askomics.libaskomics.Params import Params
from askomics.libaskomics.SparqlQuery import SparqlQuery

class File(Params):

    def __init__(self, app, session, file_info, host_url=None):
        Params.__init__(self, app, session)

        self.host_url = host_url

        self.name = file_info['name']
        self.path = file_info['path']
        self.type = file_info['type']
        self.size = file_info['size']
        self.id = file_info['id']
        self.public = False

        self.default_graph = "{}".format(self.settings.get('triplestore', 'default_graph'))
        self.user_graph = "{}:{}_{}".format(
            self.settings.get('triplestore', 'default_graph'),
            self.session['user']['id'],
            self.session['user']['username']
        )
        self.file_graph = "{}:{}_{}:{}".format(
            self.settings.get('triplestore', 'default_graph'),
            self.session['user']['id'],
            self.session['user']['username'],
            self.name
        )

        self.ttl_dir = '{}/{}_{}/ttl'.format(
            self.settings.get('askomics', 'data_directory'),
            self.session['user']['id'],
            self.session['user']['username']
        )

        self.now = datetime.datetime.now().isoformat()

        self.askomics_namespace = Namespace(self.settings.get('triplestore', 'namespace'))
        self.askomics_prefix = Namespace(self.settings.get('triplestore', 'prefix'))

    def rdf_graph(self):
        """Initialize a rdf graph with akomics prefixes

        Returns
        -------
        rdflib.graph.Graph
            The rdf graph
        """
        rdf_graph = rdflib.Graph()
        rdf_graph.bind('', self.askomics_prefix)
        rdf_graph.bind('askomics', self.askomics_namespace)

        return rdf_graph


    def get_metadata(self):

        #FIXME: find another way and don't hardcode this urls
        prov_uri = 'http://www.w3.org/ns/prov#'
        dc_uri = 'http://purl.org/dc/elements/1.1/'

        rdf_graph = self.rdf_graph()
        prov = Namespace(prov_uri)
        rdf_graph.bind('prov', prov_uri)
        dc = Namespace(dc_uri)
        rdf_graph.bind('dc', dc_uri)
        local_endpoint = rdflib.Literal(self.settings.get('triplestore', 'endpoint'))

        rdf_graph.add((rdflib.Literal(self.file_graph), prov.atLocation, local_endpoint))
        rdf_graph.add((rdflib.Literal(self.file_graph), prov.generatedAtTime, rdflib.Literal(self.now)))
        rdf_graph.add((rdflib.Literal(self.file_graph), dc.creator, rdflib.Literal(self.session['user']['username'])))
        rdf_graph.add((rdflib.Literal(self.file_graph), prov.wasDerivedFrom, rdflib.Literal(self.name)))
        rdf_graph.add((rdflib.Literal(self.file_graph), dc.hasVersion, rdflib.Literal(get_distribution('askomics').version)))
        rdf_graph.add((rdflib.Literal(self.file_graph), prov.describesService, rdflib.Literal(os.uname()[1])))

        if self.public:
            rdf_graph.add((rdflib.Literal(self.file_graph), rdflib.RDF.type, self.askomics_prefix['publicGraph']))

        return rdf_graph


    def load_graph(self, rdf_graph, tmp_file_name):

        sparql = SparqlQuery(self.app, self.session)

        temp_file_path = '{}/{}'.format(self.ttl_dir, tmp_file_name)
        rdf_graph.serialize(format='turtle', encoding='utf-8', destination=temp_file_path)

        # Load the chunk
        sparql.load_data(tmp_file_name, self.file_graph, self.host_url)

        # Remove tmp file
        os.remove(temp_file_path)

    def rollback(self):

        sparql = SparqlQuery(self.app, self.session)
        sparql.drop_dataset(self.file_graph)

    def integrate(self):

        sparql = SparqlQuery(self.app, self.session)

        method = self.settings.get('triplestore', 'upload_method')
        max_chunk_size = self.settings.getint('triplestore', 'chunk_size')

        # insert metadata
        try:
            sparql.insert_data(self.get_metadata(), self.user_graph, metadata=True)

            content_generator = self.generate_rdf_content()

            # Insert content
            chunk_size = 0
            chunk_number = 0
            graph_chunk = self.rdf_graph()

            for rdf_data in content_generator:

                graph_chunk += rdf_data
                chunk_size += 1

                if chunk_size >= max_chunk_size:

                    if method == 'load':

                        # write rdf into a tmpfile and load it
                        temp_file_name = 'tmp_{}_{}_chunk_{}.ttl'.format(
                            Utils.get_random_string(5),
                            self.name,
                            chunk_number
                        )

                        self.load_graph(graph_chunk, temp_file_name)

                    else:
                        # Insert
                        sparql.insert_data(graph_chunk, self.file_graph)

                    chunk_size = 0
                    chunk_number += 1
                    graph_chunk = self.rdf_graph()

            # Load the last chunk
            if method == 'load':
                temp_file_name = 'tmp_{}_{}_chunk_{}.ttl'.format(
                    Utils.get_random_string(5),
                    self.name,
                    chunk_number
                )

                self.load_graph(graph_chunk, temp_file_name)
            else:
                # Insert
                sparql.insert_data(graph_chunk, self.file_graph)

            # Content is inserted, now insert abstraction and domain_knowledge
            abstraction = self.get_rdf_abstraction()
            domain_knowledge = self.get_rdf_domain_knowledge()
            abstraction_domain_knowledge = abstraction + domain_knowledge

            if method == 'load':

                temp_file_name = 'tmp_{}_{}_abstraction_domain_knowledge.ttl'.format(
                    Utils.get_random_string(5),
                    self.name,
                )

                self.load_graph(abstraction_domain_knowledge, temp_file_name)
            else:
                # Insert
                sparql.insert_data(abstraction_domain_knowledge, self.file_graph)


        except Exception as e:
            # TODO: Rollback
            raise e

