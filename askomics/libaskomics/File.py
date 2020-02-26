import datetime
import os
import time
from urllib.parse import quote

from askomics.libaskomics.Params import Params
from askomics.libaskomics.Database import Database
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
    namespace_internal : Namespace
        AskOmics namespace askomics:
    namespace_data : Namespace
        AskOmics prefix :
    dc : Namespace
        dc namespace
    default_graph : string
        Default rdf graph
    faldo : Namespace
        faldo namespace
    faldo_entity : bool
        True if entity is a faldo entity
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
        Number of triples
    path : string
        Path of the file
    prov : Namespace
        prov namespace
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

    def __init__(self, app, session, file_info, host_url=None, external_endpoint=None, custom_uri=None):
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

        self.human_name = file_info["name"]
        self.name = self.format_uri(file_info['name'], remove_space=True)
        self.path = file_info['path']
        self.type = file_info['type']
        self.size = file_info['size']
        self.id = file_info['id']
        self.public = False
        self.ntriples = 0
        self.timestamp = int(time.time())
        self.external_endpoint = external_endpoint

        self.default_graph = "{}".format(self.settings.get('triplestore', 'default_graph'))
        self.user_graph = "{}:{}_{}".format(
            self.settings.get('triplestore', 'default_graph'),
            self.session['user']['id'],
            self.session['user']['username']
        )
        if "graph_name" not in file_info:
            self.file_graph = "{}:{}_{}:{}_{}".format(
                self.settings.get('triplestore', 'default_graph'),
                self.session['user']['id'],
                self.session['user']['username'],
                self.name,
                self.timestamp
            )
        else:
            self.file_graph = file_info["graph_name"]

        self.ttl_dir = '{}/{}_{}/ttl'.format(
            self.settings.get('askomics', 'data_directory'),
            self.session['user']['id'],
            self.session['user']['username']
        )

        self.now = datetime.datetime.now().isoformat()

        self.namespace_internal = Namespace(self.settings.get('triplestore', 'namespace_internal'))
        self.namespace_data = Namespace(self.settings.get('triplestore', 'namespace_data'))
        self.namespace_entity = Namespace(custom_uri) if custom_uri else self.namespace_data

        self.faldo = Namespace('http://biohackathon.org/resource/faldo/')
        self.prov = Namespace('http://www.w3.org/ns/prov#')
        self.dc = Namespace('http://purl.org/dc/elements/1.1/')

        self.faldo_entity = False
        self.faldo_abstraction = {
            "start": None,
            "end": None,
            "strand": None,
            "reference": None
        }
        self.faldo_abstraction_eq = {
            "start": self.namespace_internal["faldoStart"],
            "end": self.namespace_internal["faldoEnd"],
            "strand": self.namespace_internal["faldoStrand"],
            "reference": self.namespace_internal["faldoReference"]
        }

        self.method = self.settings.get('triplestore', 'upload_method')
        self.max_chunk_size = self.settings.getint('triplestore', 'chunk_size')
        self.serialization_format = self.settings.get('triplestore', 'serialization_format')
        self.rdf_extention = 'ttl' if self.serialization_format == 'turtle' else self.serialization_format

        self.graph_chunk = RdfGraph(self.app, self.session)
        self.graph_abstraction_dk = RdfGraph(self.app, self.session)
        self.graph_metadata = RdfGraph(self.app, self.session)

        self.error = False
        self.error_message = ""

    def edit_name_in_db(self, new_name):
        """Edit file name

        Parameters
        ----------
        new_name : str
            New name
        """
        query = '''
        UPDATE files SET
        name=?
        WHERE id = ? and user_id = ?
        '''

        database = Database(self.app, self.session)
        database.execute_sql_query(query, (new_name, self.id, self.session["user"]["id"]))

    def update_percent_in_db(self, percent, dataset_id):
        """Update dataset percent

        Parameters
        ----------
        percent : float
            The new percent
        dataset_id : int
            the corresponding dataset id
        """
        query = '''
        UPDATE datasets SET
        percent = ?
        WHERE id = ? and user_id = ?
        '''

        database = Database(self.app, self.session)
        database.execute_sql_query(query, (percent, dataset_id, self.session["user"]["id"]))

    def format_uri(self, string, remove_space=False):
        """remove space and quote"""
        if remove_space:
            return quote(string.replace(' ', ''))
        return quote(string)

    def rdfize(self, string):
        """Rdfize a string

        Return the literal is string is an url, else,
        prefix it with askomics prefix

        Parameters
        ----------
        string : string
            Term to rdfize

        Returns
        -------
        rdflib.???
            Rdfized term
        """
        if Utils.is_valid_url(string):
            return rdflib.URIRef(string)
        else:
            return self.namespace_data[self.format_uri(string)]

    def set_metadata(self):
        """Get a rdflib graph of the metadata

        Returns
        -------
        Graph
            graph containing metadata of the file
        """
        location_endpoint = rdflib.Literal(self.external_endpoint) if self.external_endpoint else rdflib.Literal(self.settings.get('triplestore', 'endpoint'))

        self.graph_metadata.add((rdflib.Literal(self.file_graph), self.prov.atLocation, location_endpoint))
        self.graph_metadata.add((rdflib.Literal(self.file_graph), self.prov.generatedAtTime, rdflib.Literal(self.now)))
        self.graph_metadata.add((rdflib.Literal(self.file_graph), self.dc.creator, rdflib.Literal(self.session['user']['username'])))
        self.graph_metadata.add((rdflib.Literal(self.file_graph), self.prov.wasDerivedFrom, rdflib.Literal(self.name)))
        self.graph_metadata.add((rdflib.Literal(self.file_graph), self.dc.hasVersion, rdflib.Literal(get_distribution('askomics').version)))
        self.graph_metadata.add((rdflib.Literal(self.file_graph), self.prov.describesService, rdflib.Literal(os.uname()[1])))

        if self.public:
            self.graph_metadata.add((rdflib.Literal(self.file_graph), self.namespace_internal['public'], rdflib.Literal(True)))
        else:
            self.graph_metadata.add((rdflib.Literal(self.file_graph), self.namespace_internal['public'], rdflib.Literal(False)))

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

        encoding = 'utf-8' if self.serialization_format != 'nt' else None
        rdf_graph.serialize(format=self.serialization_format, encoding=encoding, destination=temp_file_path)

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

    def integrate(self, dataset_id=None):
        """Integrate the file into the triplestore"""
        sparql = SparqlQueryLauncher(self.app, self.session)

        # insert metadata
        self.set_metadata()
        sparql.insert_data(self.graph_metadata, self.file_graph, metadata=True)

        content_generator = self.generate_rdf_content()

        # Insert content
        chunk_number = 0

        for _ in content_generator:

            if self.graph_chunk.ntriple >= self.max_chunk_size:

                if self.graph_chunk.percent and dataset_id:
                    self.update_percent_in_db(self.graph_chunk.percent, dataset_id)

                if self.method == 'load':

                    # write rdf into a tmpfile and load it
                    temp_file_name = 'tmp_{}_{}_chunk_{}.{}'.format(
                        Utils.get_random_string(5),
                        self.name,
                        chunk_number,
                        self.rdf_extention
                    )

                    # Try to load data. if failure, wait 5 sec and retry 5 time
                    Utils.redo_if_failure(self.log, 5, 5, self.load_graph, self.graph_chunk, temp_file_name)
                else:
                    # Insert
                    # Try to insert data. if failure, wait 5 sec and retry 5 time
                    Utils.redo_if_failure(self.log, 5, 5, sparql.insert_data, self.graph_chunk, self.file_graph)

                chunk_number += 1
                self.graph_chunk = RdfGraph(self.app, self.session)

        # Load the last chunk
        if self.graph_chunk.percent and dataset_id:
            self.update_percent_in_db(100, dataset_id)

        if self.method == 'load':
            temp_file_name = 'tmp_{}_{}_chunk_{}.{}'.format(
                Utils.get_random_string(5),
                self.name,
                chunk_number,
                self.rdf_extention
            )

            # Try to load data. if failure, wait 5 sec and retry 5 time
            Utils.redo_if_failure(self.log, 5, 5, self.load_graph, self.graph_chunk, temp_file_name)
        else:
            # Insert
            # Try to insert data. if failure, wait 5 sec and retry 5 time
            Utils.redo_if_failure(self.log, 5, 5, sparql.insert_data, self.graph_chunk, self.file_graph)

        # Content is inserted, now insert abstraction and domain_knowledge
        self.set_rdf_abstraction_domain_knowledge()

        if self.method == 'load':

            temp_file_name = 'tmp_{}_{}_abstraction_domain_knowledge.{}'.format(
                Utils.get_random_string(5),
                self.name,
                self.rdf_extention
            )

            self.load_graph(self.graph_abstraction_dk, temp_file_name)
        else:
            # Insert
            sparql.insert_data(self.graph_abstraction_dk, self.file_graph)

        self.set_triples_number()

    def get_faldo_strand(self, raw_strand):
        """Get faldo strand

        Parameters
        ----------
        raw_strand : string
            raw value of strand

        Returns
        -------
        rdf term
            Faldo "Foward", "Reverse" or "Both" uri
        """
        if raw_strand in ("+", "plus", "1"):
            return self.faldo.ForwardStrandPosition

        if raw_strand in ("-", "minus", "moins", "-1"):
            return self.faldo.ReverseStrandPosition

        return self.faldo.BothStrandPosition

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
