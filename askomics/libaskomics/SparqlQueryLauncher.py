import time

from SPARQLWrapper import JSON, SPARQLWrapper

from askomics.libaskomics.Params import Params

import requests


class SparqlQueryLauncher(Params):
    """SparqlQueryLauncher

    Attributes
    ----------
    endpoint : SPARQLWrapper
        The triplestore endpoint
    query_time : time
        Query execution time
    triplestore : string
        triplesotre (virtuoso, fuseki ...)
    """

    def __init__(self, app, session, get_result_query=False):
        """init

        Parameters
        ----------
        app : Flask
            Flask app
        session :
            AskOmics session
        """
        Params.__init__(self, app, session)

        self.query_time = None

        self.external_endpoint = None

        try:
            self.external_endpoint = self.settings.get('triplestore', 'external_endpoint')
        except Exception:
            pass

        if get_result_query and self.external_endpoint is not None:
            url_endpoint = self.external_endpoint
            url_updatepoint = self.external_endpoint
        else:
            url_endpoint = self.settings.get('triplestore', 'endpoint')
            url_updatepoint = self.settings.get('triplestore', 'updatepoint')

        self.endpoint = SPARQLWrapper(url_endpoint, url_updatepoint)

        try:
            self.endpoint.setCredentials(
                self.settings.get('triplestore', 'username'),
                self.settings.get('triplestore', 'password')
            )
        except Exception:
            pass

        self.triplestore = self.settings.get('triplestore', 'triplestore')

    def load_data(self, file_name, graph, host_url):
        """Load data in function of the triplestore

        Parameters
        ----------
        file_name : string
            File name to load
        graph : string
            graph name
        host_url : string
            AskOmics url
        """
        if self.triplestore == 'fuseki':
            self.load_data_fuseki(file_name, graph)
        else:
            self.load_data_virtuoso(file_name, graph, host_url)

    def load_data_fuseki(self, file_name, graph):
        """Load data using fuseki load request

        Parameters
        ----------
        file_name : string
            File name to load
        graph : string
            graph name

        Returns
        -------
        response
            Response of request
        """
        file_path = "{}/{}_{}/ttl/{}".format(
            self.settings.get("askomics", "data_directory"),
            self.session["user"]["id"],
            self.session["user"]["username"],
            file_name
        )

        data = {'graph': graph}
        files = [('file', (file_name, open(file_path), 'text/turtle'))]

        start_time = time.time()

        response = requests.post(self.settings.get('triplestore', 'fuseki_upload_url'), data=data, files=files)

        self.query_time = time.time() - start_time

        return response

    def load_data_virtuoso(self, file_name, graph, host_url):
        """Load data using virtuoso load query

        Parameters
        ----------
        file_name : string
            File name to load
        graph : string
            graph name
        host_url : string
            AskOmics url

        Returns
        -------
        TYPE
            result of query
        """
        try:
            load_url = self.settings.get('triplestore', 'load_url')
        except Exception:
            load_url = host_url

        file_url = '{}api/files/ttl/{}/{}/{}'.format(
            load_url,
            self.session['user']['id'],
            self.session['user']['username'],
            file_name
        )

        query = "LOAD <{}> INTO GRAPH <{}>".format(file_url, graph)
        return self.execute_query(query)

    def get_triples_from_graph(self, graph):
        """Get triples from a rdflib graph

        Parameters
        ----------
        graph : Graph
            rdf graph

        Returns
        -------
        string
            ttl string
        """
        ttl = ""
        for s, p, o in graph:
            ttl += "<{}> <{}> <{}> .\n".format(s, p, o)
        return ttl

    def insert_data(self, ttl, graph, metadata=False):
        """Insert data into the triplesotre using INSERT

        Parameters
        ----------
        ttl : Graph
            rdflib graph
        graph : string
            graph name
        metadata : bool, optional
            metadatas?

        Returns
        -------
        TYPE
            query result
        """
        triples = self.get_triples_from_graph(ttl) if metadata else ttl.serialize(format='nt').decode("utf-8")

        query = '''
        INSERT DATA {{
            GRAPH <{}> {{
                {}
            }}
        }}
        '''.format(graph, triples)

        return self.execute_query(query)

    def drop_dataset(self, graph):
        """Drop the datasets of the triplestore and its metadata

        Parameters
        ----------
        graph : string
            graph name to remove
        """
        # Remove metadata
        query = '''
        DELETE WHERE {{
            GRAPH <{}> {{
                <{}> ?p ?o
            }}
        }}
        '''.format(graph, graph)
        self.execute_query(query)

        # Drop graph
        query = '''
        DROP SILENT GRAPH <{}>
        '''.format(graph)
        self.execute_query(query)

    def process_query(self, query):
        """Execute a query and return parsed results

        Parameters
        ----------
        query : string
            The query to execute

        Returns
        -------
        list
            Parsed results
        """
        return self.parse_results(self.execute_query(query))

    def execute_query(self, query):
        """Execute a sparql query

        Parameters
        ----------
        query : string
            Query to perform

        Returns
        -------
        TYPE
            result
        """
        start_time = time.time()
        self.endpoint.setQuery(query)

        # Debug
        if self.settings.getboolean('askomics', 'debug'):
            self.log.debug(query)

        # Update
        if self.endpoint.isSparqlUpdateRequest():
            self.endpoint.setMethod('POST')
            # Virtuoso hack
            if self.triplestore == 'virtuoso':
                self.endpoint.queryType = "SELECT"

            results = self.endpoint.query()
            self.query_time = time.time() - start_time
        # Select
        else:
            self.endpoint.setReturnFormat(JSON)
            results = self.endpoint.query().convert()
            self.query_time = time.time() - start_time

        return results

    def parse_results_old(self, json_results):
        """Parse result of sparql query

        Parameters
        ----------
        json_results :
            Result of the query

        Returns
        -------
        list
            parsed results
        """
        try:
            return [{
                sparql_variable: entry[sparql_variable]["value"] for sparql_variable in entry.keys()
            } for entry in json_results["results"]["bindings"]]
        except Exception:
            return []

    def parse_results(self, json_results):
        """Parse result of sparql query

        Parameters
        ----------
        json_results : dict
            Query result

        Returns
        -------
        list, list
            Header and data
        """
        try:
            header = json_results['head']['vars']
            data = []
            for row in json_results["results"]["bindings"]:
                row_dict = {}
                for key, value in row.items():
                    row_dict[key] = value['value']
                data.append(row_dict)

        except Exception as e:
            self.log.error(str(e))
            return [], []

        return header, data
