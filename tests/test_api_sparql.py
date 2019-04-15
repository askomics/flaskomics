import json
import unittest
from . import AskomicsTestCase


class TestApiSparql(AskomicsTestCase):
    """Test AskOmics API /api/sparql/<someting>"""

    def test_prefix(self, client_logged_as_jdoe_with_data):
        """Test /api/sparql/getquery route"""
        response = client_logged_as_jdoe_with_data.get("/api/sparql/getquery")
        assert response.status_code == 200
        assert response.json == {
            'error': False,
            'errorMessage': '',
            'query': 'PREFIX : <http://www.semanticweb.org/user/ontologies/2018/1#>\nPREFIX askomics: <http://www.semanticweb.org/askomics/ontologies/2018/1#>\nPREFIX prov: <http://www.w3.org/ns/prov#>\nPREFIX dc: <http://purl.org/dc/elements/1.1/>\nPREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\nPREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\nPREFIX owl: <http://www.w3.org/2002/07/owl#>\nPREFIX xsd: <http://www.w3.org/2001/XMLSchema#>\n\nSELECT DISTINCT ?s ?p ?o\nWHERE {\n    ?s ?p ?o\n}\nLIMIT 25\n'
        }

    def test_query(self, client_logged_as_jdoe_with_data):
        """Test /api/sparql/query route"""
        case = unittest.TestCase()
        ok_data = {
            'query': 'PREFIX : <http://www.semanticweb.org/user/ontologies/2018/1#>\nPREFIX askomics: <http://www.semanticweb.org/askomics/ontologies/2018/1#>\nPREFIX prov: <http://www.w3.org/ns/prov#>\nPREFIX dc: <http://purl.org/dc/elements/1.1/>\nPREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\nPREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\nPREFIX owl: <http://www.w3.org/2002/07/owl#>\nPREFIX xsd: <http://www.w3.org/2001/XMLSchema#>\n\nSELECT DISTINCT ?s ?p ?o\nWHERE {\n    ?s ?p ?o\n}\nLIMIT 25\n'
        }
        with open('tests/results/test_query.json') as f:
            expected = json.load(f)
        response = client_logged_as_jdoe_with_data.post("/api/sparql/query", json=ok_data)
        assert response.status_code == 200
        case.assertCountEqual(response.json, expected)
