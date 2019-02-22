import os
import time
import rdflib
import requests

from SPARQLWrapper import SPARQLWrapper, JSON

from askomics.libaskomics.Params import Params

class SparqlQuery(Params):

    def __init__(self, app, session):
        Params.__init__(self, app, session)

        self.query_time = None

        url_endpoint = self.settings.get('triplestore', 'endpoint')
        url_updatepoint = self.settings.get('triplestore', 'updatepoint')
        self.endpoint = SPARQLWrapper(url_endpoint, url_updatepoint)

        try:
            self.endpoint.setCredentials(
                self.settings.get('triplestore', 'username'),
                self.settings.get('triplestore', 'password')
            )
        except Exception as e:
            pass

        self.triplestore = self.settings.get('triplestore', 'triplestore')

    def load_data(self, file_name, graph, host_url):

        if self.triplestore == 'fuseki':
            self.load_data_fuseki(file_name, graph)
        else:
            self.load_data_virtuoso(file_name, graph, host_url)

    def load_data_fuseki(self, file_name, graph):

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

        try:
            load_url = self.settings.get('askomics', 'load_url')
        except Exception as e:
            load_url = host_url

        file_url = '{}files/ttl/{}/{}/{}'.format(
            load_url,
            self.session['user']['id'],
            self.session['user']['username'],
            file_name
        )

        query = "LOAD <{}> INTO GRAPH <{}>".format(file_url, graph)
        return self.execute_query(query)

    def get_triples_from_graph(self, graph):

        ttl = ""
        for s, p, o in graph:
            ttl += "<{}> <{}> <{}> .\n".format(s, p, o)
        return ttl


    def insert_data(self, ttl, graph, metadata=False):

        triples = self.get_triples_from_graph(ttl) if metadata else ttl.serialize(format='nt').decode("utf-8")

        query = '''
        INSERT DATA {{
            GRAPH <{}> {{
                {}
            }}
        }}
        '''.format(graph, triples)

        with open('/home/xgarnier/Desktop/query.sparql', 'w') as f:
            f.write(query) 

        return self.execute_query(query)


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

        start_time = time.time()
        self.endpoint.setQuery(query)

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

    def parse_results(self, json_results):

        try:
            return [{
                sparql_variable: entry[sparql_variable]["value"] for sparql_variable in entry.keys()
            } for entry in json_results["results"]["bindings"]]
        except Exception as e:
            return []