import json

from . import AskomicsTestCase


class TestApiSparql(AskomicsTestCase):
    """Test AskOmics API /api/sparql/<someting>"""

    def test_init(self, client):
        """Test /api/sparql/init route"""
        client.create_two_users()
        client.log_user("jdoe")
        info = client.upload_and_integrate()

        response = client.client.get("/api/sparql/init")

        with open("tests/results/init.json", "r") as file:
            content = file.read()
        content = content.replace("###TRANSCRIPTS_TIMESTAMP###", str(info["transcripts"]["timestamp"]))
        content = content.replace("###QTL_TIMESTAMP###", str(info["qtl"]["timestamp"]))
        content = content.replace("###DE_TIMESTAMP###", str(info["de"]["timestamp"]))
        content = content.replace("###GFF_TIMESTAMP###", str(info["gff"]["timestamp"]))
        content = content.replace("###BED_TIMESTAMP###", str(info["bed"]["timestamp"]))
        content = content.replace("###LOCAL_ENDPOINT###", str(client.get_config("federation", "local_endpoint")))
        content = content.replace("###SIZE###", str(client.get_size_occupied_by_user()))
        expected = json.loads(content)

        assert response.status_code == 200
        assert self.equal_objects(response.json, expected)

    def test_preview(self, client):
        """Test /api/sparql/previewquery route"""
        client.create_two_users()
        client.log_user("jdoe")
        info = client.upload_and_integrate()

        no_endpoint_data = {
            'query': "PREFIX : <http://askomics.org/test/data/>\nPREFIX askomics: <http://askomics.org/test/internal/>\nPREFIX dc: <http://purl.org/dc/elements/1.1/>\nPREFIX faldo: <http://biohackathon.org/resource/faldo/>\nPREFIX owl: <http://www.w3.org/2002/07/owl#>\nPREFIX prov: <http://www.w3.org/ns/prov#>\nPREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\nPREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\nPREFIX xsd: <http://www.w3.org/2001/XMLSchema#>\nSELECT DISTINCT ?transcript1_Label\nWHERE {\n    ?transcript1_uri rdf:type <http://askomics.org/test/data/transcript> .\n    ?transcript1_uri rdfs:label ?transcript1_Label .\n}\n",
            'graphs': ["urn:sparql:askomics_test:1_jdoe:transcripts.tsv_{}".format(str(info["transcripts"]["timestamp"]))],
            'endpoints': []
        }

        no_graph_data = {
            'query': "PREFIX : <http://askomics.org/test/data/>\nPREFIX askomics: <http://askomics.org/test/internal/>\nPREFIX dc: <http://purl.org/dc/elements/1.1/>\nPREFIX faldo: <http://biohackathon.org/resource/faldo/>\nPREFIX owl: <http://www.w3.org/2002/07/owl#>\nPREFIX prov: <http://www.w3.org/ns/prov#>\nPREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\nPREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\nPREFIX xsd: <http://www.w3.org/2001/XMLSchema#>\nSELECT DISTINCT ?transcript1_Label\nWHERE {\n    ?transcript1_uri rdf:type <http://askomics.org/test/data/transcript> .\n    ?transcript1_uri rdfs:label ?transcript1_Label .\n}\n",
            'graphs': [],
            'endpoints': [client.get_config("federation", "local_endpoint")]
        }

        ok_data = {
            'query': "PREFIX : <http://askomics.org/test/data/>\nPREFIX askomics: <http://askomics.org/test/internal/>\nPREFIX dc: <http://purl.org/dc/elements/1.1/>\nPREFIX faldo: <http://biohackathon.org/resource/faldo/>\nPREFIX owl: <http://www.w3.org/2002/07/owl#>\nPREFIX prov: <http://www.w3.org/ns/prov#>\nPREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\nPREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\nPREFIX xsd: <http://www.w3.org/2001/XMLSchema#>\nSELECT DISTINCT ?transcript1_Label\nWHERE {\n    ?transcript1_uri rdf:type <http://askomics.org/test/data/transcript> .\n    ?transcript1_uri rdfs:label ?transcript1_Label .\n}\n",
            'graphs': ["urn:sparql:askomics_test:1_jdoe:transcripts.tsv_{}".format(str(info["transcripts"]["timestamp"]))],
            'endpoints': [client.get_config("federation", "local_endpoint")]
        }

        with open("tests/results/sparql_preview.json") as file:
            file_content = file.read()

        expected = json.loads(file_content)

        response = client.client.post("/api/sparql/previewquery", json=ok_data)

        assert response.status_code == 200
        assert self.equal_objects(response.json, expected)

        # 500
        response = client.client.post("/api/sparql/previewquery", json=no_endpoint_data)
        expected = {
            'error': True,
            'errorMessage': "No endpoint selected",
            'header': [],
            'data': []
        }
        assert response.status_code == 400
        assert self.equal_objects(response.json, expected)

        response = client.client.post("/api/sparql/previewquery", json=no_graph_data)
        expected = {
            'error': True,
            'errorMessage': "No graph selected in local triplestore",
            'header': [],
            'data': []
        }
        assert response.status_code == 400
        assert self.equal_objects(response.json, expected)

    def test_query(self, client):
        """Test /api/sparql/savequery route"""
        client.create_two_users()
        client.log_user("jdoe")
        info = client.upload_and_integrate()

        no_endpoint_data = {
            'query': "PREFIX : <http://askomics.org/test/data/>\nPREFIX askomics: <http://askomics.org/test/internal/>\nPREFIX dc: <http://purl.org/dc/elements/1.1/>\nPREFIX faldo: <http://biohackathon.org/resource/faldo/>\nPREFIX owl: <http://www.w3.org/2002/07/owl#>\nPREFIX prov: <http://www.w3.org/ns/prov#>\nPREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\nPREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\nPREFIX xsd: <http://www.w3.org/2001/XMLSchema#>\nSELECT DISTINCT ?transcript1_Label\nWHERE {\n    ?transcript1_uri rdf:type <http://askomics.org/test/data/transcript> .\n    ?transcript1_uri rdfs:label ?transcript1_Label .\n}\n",
            'graphs': ["urn:sparql:askomics_test:1_jdoe:transcripts.tsv_{}".format(str(info["transcripts"]["timestamp"]))],
            'endpoints': []
        }

        no_graph_data = {
            'query': "PREFIX : <http://askomics.org/test/data/>\nPREFIX askomics: <http://askomics.org/test/internal/>\nPREFIX dc: <http://purl.org/dc/elements/1.1/>\nPREFIX faldo: <http://biohackathon.org/resource/faldo/>\nPREFIX owl: <http://www.w3.org/2002/07/owl#>\nPREFIX prov: <http://www.w3.org/ns/prov#>\nPREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\nPREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\nPREFIX xsd: <http://www.w3.org/2001/XMLSchema#>\nSELECT DISTINCT ?transcript1_Label\nWHERE {\n    ?transcript1_uri rdf:type <http://askomics.org/test/data/transcript> .\n    ?transcript1_uri rdfs:label ?transcript1_Label .\n}\n",
            'graphs': [],
            'endpoints': [client.get_config("federation", "local_endpoint")]
        }

        ok_data = {
            'query': "PREFIX : <http://askomics.org/test/data/>\nPREFIX askomics: <http://askomics.org/test/internal/>\nPREFIX dc: <http://purl.org/dc/elements/1.1/>\nPREFIX faldo: <http://biohackathon.org/resource/faldo/>\nPREFIX owl: <http://www.w3.org/2002/07/owl#>\nPREFIX prov: <http://www.w3.org/ns/prov#>\nPREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\nPREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\nPREFIX xsd: <http://www.w3.org/2001/XMLSchema#>\nSELECT DISTINCT ?transcript1_Label\nWHERE {\n    ?transcript1_uri rdf:type <http://askomics.org/test/data/transcript> .\n    ?transcript1_uri rdfs:label ?transcript1_Label .\n}\n",
            'graphs': ["urn:sparql:askomics_test:1_jdoe:transcripts.tsv_{}".format(str(info["transcripts"]["timestamp"]))],
            'endpoints': [client.get_config("federation", "local_endpoint")]
        }
        response = client.client.post("/api/sparql/savequery", json=ok_data)
        assert response.status_code == 200
        assert not response.json["error"]
        assert response.json["errorMessage"] == ''
        assert 'result_id' in response.json

        # 500
        response = client.client.post("/api/sparql/previewquery", json=no_endpoint_data)
        expected = {
            'error': True,
            'errorMessage': "No endpoint selected",
            'header': [],
            'data': []
        }
        assert response.status_code == 400
        assert self.equal_objects(response.json, expected)

        response = client.client.post("/api/sparql/previewquery", json=no_graph_data)
        expected = {
            'error': True,
            'errorMessage': "No graph selected in local triplestore",
            'header': [],
            'data': []
        }
        assert response.status_code == 400
        assert self.equal_objects(response.json, expected)
