from askomics.libaskomics.Params import Params

import rdflib


class PrefixManager(Params):
    """Manage sparql prefixes

    Attributes
    ----------
    askomics_namespace : str
        askomics namespace, from config file
    askomics_prefix : str
        askomics prefix, from config file
    prefix : dict
        dict of all prefixes
    """

    def __init__(self, app, session):
        """init

        Parameters
        ----------
        app : Flask
            Flask app
        session :
            AskOmics session
        """
        Params.__init__(self, app, session)
        self.askomics_namespace = self.settings.get('triplestore', 'namespace')
        self.askomics_prefix = self.settings.get('triplestore', 'prefix')

        self.prefix = {
            ':': self.settings.get('triplestore', 'prefix'),
            'askomics:': self.settings.get('triplestore', 'namespace'),
            'prov:': 'http://www.w3.org/ns/prov#',
            'dc:': 'http://purl.org/dc/elements/1.1/',
            'rdf:': str(rdflib.RDF),
            'rdfs:': str(rdflib.RDFS),
            'owl:': str(rdflib.OWL),
            'xsd:': str(rdflib.XSD)
        }

    def get_prefix(self):
        """Get all prefixes

        Returns
        -------
        str
            prefixes
        """
        prefix_string = ''
        for prefix, url in self.prefix.items():
            prefix_string += 'PREFIX {} <{}>\n'.format(prefix, url)

        return prefix_string
