import datetime
import os
import time
from urllib.parse import quote

from askomics.libaskomics.Params import Params
from askomics.libaskomics.SparqlQueryLauncher import SparqlQueryLauncher
from askomics.libaskomics.Utils import Utils
from askomics.libaskomics.RdfGraph import RdfGraph

from pkg_resources import get_distribution

import rdflib
from rdflib.namespace import Namespace


class File(Params):
    """Summary

    Attributes
    ----------
    askomics_namespace : Namespace
        AskOmics namespace askomics:
    askomics_prefix : Namespace
        AskOmics prefix :
    default_graph : string
        Default rdf graph
    file_graph : string
        File graph containing the file
    host_url : string
        AskOmics url
    id : int
        database file id
    max_chunk_size : int
        Max number of triple to insert in one Load or insert
    method : int
        Load or insert
    name : string
        Name of the file
    now : datetime
        timestamp of the current time
    ntriples : int
        Description
    path : string
        Path of the file
    public : bool
        True if the file is public
    size : int
        file size
    timestamp : TYPE
        Description
    ttl_dir : string
        path to the ttl directory
    type : string
        file type
    user_graph : string
        User graph
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
            File info
        host_url : None, optional
            AskOmics url
        """
        Params.__init__(self, app, session)

        self.host_url = host_url

        self.name = file_info['name']
        self.path = file_info['path']
        self.type = file_info['type']
        self.size = file_info['size']
        self.id = file_info['id']
        self.public = False
        self.ntriples = 0
        self.timestamp = int(time.time())

        self.default_graph = "{}".format(self.settings.get('triplestore', 'default_graph'))
        self.user_graph = "{}:{}_{}".format(
            self.settings.get('triplestore', 'default_graph'),
            self.session['user']['id'],
            self.session['user']['username']
        )
        self.file_graph = "{}:{}_{}:{}_{}".format(
            self.settings.get('triplestore', 'default_graph'),
            self.session['user']['id'],
            self.session['user']['username'],
            self.name,
            self.timestamp
        )

        self.ttl_dir = '{}/{}_{}/ttl'.format(
            self.settings.get('askomics', 'data_directory'),
            self.session['user']['id'],
            self.session['user']['username']
        )

        self.now = datetime.datetime.now().isoformat()

        self.askomics_namespace = Namespace(self.settings.get('triplestore', 'namespace'))
        self.askomics_prefix = Namespace(self.settings.get('triplestore', 'prefix'))

        self.method = self.settings.get('triplestore', 'upload_method')
        self.max_chunk_size = self.settings.getint('triplestore', 'chunk_size')

    def format_uri(self, string, remove_space=False):
        """remove space and quote"""
        if remove_space:
            return quote(string.replace(' ', ''))
        return quote(string)

    def get_metadata(self):
        """Get a rdflib graph of the metadata

        Returns
        -------
        Graph
            graph containing metadata of the file
        """
        # FIXME: find another way and don't hardcode this urls
        prov_uri = 'http://www.w3.org/ns/prov#'
        dc_uri = 'http://purl.org/dc/elements/1.1/'

        rdf_graph = RdfGraph(self.app, self.session)
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
            rdf_graph.add((rdflib.Literal(self.file_graph), self.askomics_prefix['public'], rdflib.Literal(True)))
        else:
            rdf_graph.add((rdflib.Literal(self.file_graph), self.askomics_prefix['public'], rdflib.Literal(False)))

        return rdf_graph

    def load_graph(self, rdf_graph, tmp_file_name):
        """Load a rdflib graph into the triplestore

        Write rdf to a tmp file, and send the url to this file
        to the triplestore with a LOAD request

        Parameters
        ----------
        rdf_graph : Graph
            rdf graph to load
        tmp_file_name : string
            Path to a tmp file
        """
        sparql = SparqlQueryLauncher(self.app, self.session)

        temp_file_path = '{}/{}'.format(self.ttl_dir, tmp_file_name)
        rdf_graph.serialize(format='turtle', encoding='utf-8', destination=temp_file_path)

        # Load the chunk
        sparql.load_data(tmp_file_name, self.file_graph, self.host_url)

        # Remove tmp file
        if not self.settings.getboolean('askomics', 'debug_ttl'):
            os.remove(temp_file_path)

    def rollback(self):
        """Drop the dataset from the triplestore in case of error"""
        sparql = SparqlQueryLauncher(self.app, self.session)
        sparql.drop_dataset(self.file_graph)

    def set_triples_number(self):
        """Set graph triples number by requesting the triplestore"""
        query = """
        SELECT count(*) AS ?count
        FROM <{}>
        WHERE {{
            ?s ?p ?o .
        }}
        """.format(self.file_graph)

        sparql = SparqlQueryLauncher(self.app, self.session)
        result = sparql.process_query(query)
        self.ntriples = result[1][0]["count"]

    def integrate(self):
        """Integrate the file into the triplestore"""
        sparql = SparqlQueryLauncher(self.app, self.session)

        # insert metadata
        sparql.insert_data(self.get_metadata(), self.user_graph, metadata=True)

        content_generator = self.generate_rdf_content()

        # Insert content
        chunk_number = 0
        graph_chunk = RdfGraph(self.app, self.session)

        for rdf_data in content_generator:

            graph_chunk.merge(rdf_data)

            if graph_chunk.ntriple >= self.max_chunk_size:

                if self.method == 'load':

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

                chunk_number += 1
                graph_chunk = RdfGraph(self.app, self.session)

        # Load the last chunk
        if self.method == 'load':
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
        abstraction_domain_knowledge = self.get_rdf_abstraction_domain_knowledge()

        if self.method == 'load':

            temp_file_name = 'tmp_{}_{}_abstraction_domain_knowledge.ttl'.format(
                Utils.get_random_string(5),
                self.name,
            )

            self.load_graph(abstraction_domain_knowledge, temp_file_name)
        else:
            # Insert
            sparql.insert_data(abstraction_domain_knowledge, self.file_graph)

        self.set_triples_number()

    def get_rdf_type(self, value):
        """get xsd type of a value

        Parameters
        ----------
        value :
            The value to get type

        Returns
        -------
        TYPE
            rdflib.XSD.string or rdflib.XSD.decimal
        """
        try:
            int(value)
            return rdflib.XSD.decimal
        except ValueError:
            try:
                float(value)
                return rdflib.XSD.decimal
            except ValueError:
                return rdflib.XSD.string

        return rdflib.XSD.string

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
