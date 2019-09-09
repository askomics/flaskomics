from askomics.libaskomics.Params import Params

import rdflib
from rdflib.namespace import Namespace


class RdfGraph(Params):
    """rdflib.graph wrapper

    Attributes
    ----------
    askomics_namespace : Namespace
        AskOmics napespace
    askomics_prefix : Namespace
        AskOmics prefix
    graph : Graph
        rdflib graph
    ntriple : int
        Number of triple in the graph
    """

    def __init__(self, app, session):
        """init

        Parameters
        ----------
        app : Flask
            Flask app
        session
            AskOmics session
        """
        Params.__init__(self, app, session)

        self.askomics_namespace = Namespace(self.settings.get('triplestore', 'namespace'))
        self.askomics_prefix = Namespace(self.settings.get('triplestore', 'prefix'))

        self.graph = rdflib.Graph()
        self.graph.bind('', self.askomics_prefix)
        self.graph.bind('askomics', self.askomics_namespace)
        self.graph.bind('faldo', "http://biohackathon.org/resource/faldo/")
        self.graph.bind('dc', 'http://purl.org/dc/elements/1.1/')
        self.graph.bind('prov', 'http://www.w3.org/ns/prov#')
        self.ntriple = 0

    def add(self, triple):
        """Add a triple into the rdf graph

        Parameters
        ----------
        triple : tuple
            triple to add
        """
        self.graph.add(triple)
        self.ntriple += 1

    def bind(self, a, b):
        """Bind a namespace

        Parameters
        ----------
        a : string
            prefix
        b : string
            namespace
        """
        self.graph.bind(a, b)

    def get_triple(self):
        """Get all triple"""
        for s, p, o in self.graph:
            yield s, p, o

    def merge(self, other_graph):
        """Merge a graph into this graph

        Parameters
        ----------
        other_graph : RdfGraph
            The graph to merge
        """
        self.graph += other_graph.graph
        self.ntriple += other_graph.ntriple

    def serialize(self, destination=None, format='xml', base=None, encoding=None, **args):
        """Serialize the graph into a file

        Parameters
        ----------
        format : string
            rdf syntaxe
        encoding : string
            Encoding
        destination : string
            File destination
        """
        result = self.graph.serialize(destination=destination, format=format, base=base, encoding=encoding, **args)

        if destination is None:
            return result
