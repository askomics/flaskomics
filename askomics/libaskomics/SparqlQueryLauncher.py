import time
import traceback
import sys

from SPARQLWrapper import JSON, SPARQLWrapper

from askomics.libaskomics.Params import Params

import requests
from urllib3.exceptions import HTTPError


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

    def __init__(self, app, session, get_result_query=False, federated=False, endpoints=None):
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

        # local endpoint (for federated query engine)
        self.local_endpoint_f = self.settings.get('triplestore', 'endpoint')
        try:
            self.local_endpoint_f = self.settings.get('federation', 'local_endpoint')
        except Exception:
            pass

        local = False
        # Use the federated query engine
        if federated:
            self.federated = True
            self.local_query = False
            self.url_endpoint = self.settings.get('federation', 'endpoint')
            self.url_updatepoint = self.settings.get('federation', 'endpoint')
            self.triplestore = self.settings.get('federation', 'query_engine')
        # use the external endpoint
        elif endpoints is not None and endpoints != [self.local_endpoint_f]:
            self.federated = False
            self.local_query = False
            self.triplestore = "unknown"
            self.url_endpoint = endpoints[0]
            self.url_updatepoint = endpoints[0]
        # use the local endpoint
        else:
            self.federated = False
            self.local_query = True
            self.triplestore = self.settings.get('triplestore', 'triplestore')
            self.url_endpoint = self.settings.get('triplestore', 'endpoint')
            self.url_updatepoint = self.settings.get('triplestore', 'updatepoint')
            local = True

        self.endpoint = SPARQLWrapper(self.url_endpoint, self.url_updatepoint)

        if local:
            try:
                self.endpoint.setCredentials(
                    self.settings.get('triplestore', 'username'),
                    self.settings.get('triplestore', 'password')
                )
                self.endpoint.setHTTPAuth(self.settings.get('triplestore', 'http_auth', fallback="basic"))
            except Exception:
                pass

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

        if not load_url.endswith('/'):
            load_url = load_url + "/"

        file_url = '{}api/files/ttl/{}/{}/{}'.format(
            load_url,
            self.session['user']['id'],
            self.session['user']['username'],
            file_name
        )

        query = "LOAD <{}> INTO GRAPH <{}>".format(file_url, graph)
        return self.execute_query(query, is_update=True)

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
        for s, p, o in graph.get_triple():
            ttl += "<{}> <{}> <{}> .\n".format(s, p, o)
        return ttl

    def insert_ttl_string(self, ttl_string, graph):
        """Insert ttl into the triplestore

        Parameters
        ----------
        ttl_string : string
            ttl triples to insert
        graph : string
            Insert in the named graph

        Returns
        -------
        dict?
            query result
        """
        query = '''
        INSERT {{
            GRAPH <{}> {{
                {}
            }}
        }}
        '''.format(graph, ttl_string)

        return self.execute_query(query, is_update=True)

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
        triples = self.get_triples_from_graph(ttl) if metadata else ttl.serialize(format='nt')

        query = '''
        INSERT {{
            GRAPH <{}> {{
                {}
            }}
        }}
        '''.format(graph, triples)

        return self.execute_query(query, is_update=True)

    def drop_dataset(self, graph):
        """Drop the datasets of the triplestore and its metadata

        Parameters
        ----------
        graph : string
            graph name to remove
        """
        query = '''
        DROP SILENT GRAPH <{}>
        '''.format(graph)
        self.execute_query(query, disable_log=True, isql_api=True, is_update=True)

    def process_query(self, query, isql_api=False, is_update=False):
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
        return self.parse_results(self.execute_query(query, isql_api=isql_api, is_update=is_update))

    def execute_query(self, query, disable_log=False, isql_api=False, is_update=False):
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
        try:
            triplestore = self.settings.get("triplestore", "triplestore")

            # Use ISQL or SPARQL
            isql_api_url = None
            try:
                isql_api_url = self.settings.get("triplestore", "isqlapi")
            except Exception:
                pass
            use_isql = True if triplestore == "virtuoso" and isql_api_url and self.local_query and isql_api else False

            start_time = time.time()
            self.endpoint.setQuery(query)

            # Debug
            if self.settings.getboolean('askomics', 'debug'):
                self.log.debug("Launch {} query on {} ({})".format("ISQL" if use_isql else "SPARQL", self.triplestore, self.url_endpoint))
                self.log.debug(query)

            if use_isql:
                formatted_query = "SPARQL {}".format(query)
                json = {"command": formatted_query, "disable_log": disable_log, "sparql_select": not is_update}
                response = requests.post(url=isql_api_url, json=json)
                results = response.json()
                if results["status"] == 500:
                    raise HTTPError("isqlapi: {}".format(results["message"]))

            else:
                # Update
                if is_update:
                    self.endpoint.setMethod('POST')
                    # Force sending to secure endpoint
                    self.endpoint.queryType = "INSERT"
                    # Virtuoso hack
                    # if self.triplestore == 'virtuoso':
                    #    self.endpoint.queryType = "SELECT"

                    results = self.endpoint.query()
                # Select
                else:
                    self.endpoint.setReturnFormat(JSON)
                    # Force sending to public endpoint
                    self.endpoint.queryType = "SELECT"
                    results = self.endpoint.query().convert()

                self.query_time = time.time() - start_time

            return results

        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            raise type(e)("Triplestore error: {}".format(str(e))).with_traceback(sys.exc_info()[2])

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
            # If isql, results are allready parsed
            if "isql" in json_results:
                return json_results["vars"], json_results["rows"]

            header = json_results['head']['vars']
            data = []
            for row in json_results["results"]["bindings"]:
                row_dict = {}
                for key, value in row.items():
                    row_dict[key] = value['value']
                data.append(row_dict)

        except Exception:
            traceback.print_exc(file=sys.stdout)
            return [], []

        return header, data
