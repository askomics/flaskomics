from askomics.libaskomics.Params import Params

import rdflib
from rdflib.namespace import Namespace


class RdfGraph(Params):
    """rdflib.graph wrapper

    Attributes
    ----------
    namespace_internal : Namespace
        AskOmics napespace
    namespace_data : Namespace
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

        self.namespace_data = Namespace(self.settings.get('triplestore', 'namespace_data'))
        self.namespace_internal = Namespace(self.settings.get('triplestore', 'namespace_internal'))

        self.graph = rdflib.Graph()
        self.graph.bind('', self.namespace_data)
        self.graph.bind('askomics', self.namespace_internal)
        self.graph.bind('faldo', "http://biohackathon.org/resource/faldo/")
        self.graph.bind('dc', 'http://purl.org/dc/elements/1.1/')
        self.graph.bind('prov', 'http://www.w3.org/ns/prov#')
        self.ntriple = 0
        self.percent = None

    def parse(self, source=None, publicID=None, format=None, location=None, file=None, data=None, **args):
        """Parse a RDF file"""
        self.graph.parse(source=source, publicID=publicID, format=format, location=location, file=file, data=data, **args)

    def add(self, triple):
        """Add a triple into the rdf graph

        Parameters
        ----------
        triple : tuple
            triple to add
        """
        self.graph.add(triple)
        self.ntriple += 1

    def remove(self, triple):
        """Remove a triple into the rdf graph

        Parameters
        ----------
        triple : tuple
            triple to remove
        """
        self.graph.remove(triple)
        self.ntriple -= 1

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
        # self.percent = self.maxi(self.percent, other_graph.percent)

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

    @staticmethod
    def maxi(a, b):
        """Get the max between two valuesthat can be int or None

        Parameters
        ----------
        a : Int or None
            first value
        b : Int or None
            2nd value

        Returns
        -------
        Int or None
            Max of the two values
        """
        try:
            return max(a, b)
        except Exception:
            if a is None:
                return b
            if b is None:
                return a
            return None
