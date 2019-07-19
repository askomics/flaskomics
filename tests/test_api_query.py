import unittest
import json

from . import AskomicsTestCase


class TestApiStartpoints(AskomicsTestCase):
    """Test AskOmics API /api/startpoints/<someting>"""

    def test_startpoints(self, client_logged_as_jdoe_with_data):
        """Test /api/startpoints route"""
        case = unittest.TestCase()
        gene_timestamp = client_logged_as_jdoe_with_data.gene_timestamp
        response = client_logged_as_jdoe_with_data.get('/api/query/startpoints')
        assert response.status_code == 200
        expected = {
            'error': False,
            'errorMessage': '',
            'startpoints': [{
                'entity':
                'http://www.semanticweb.org/user/ontologies/2018/1#Gene',
                'entity_label':
                'Gene',
                'graphs': [{
                    'creator': 'jdoe',
                    'public': 'false',
                    'uri': 'urn:sparql:askomics_test:1_jdoe:gene_{}'.format(gene_timestamp)
                }],
                'private': True,
                'public': False
            }],
            'publicQueries': []
        }
        case.assertCountEqual(response.json, expected)

    def test_get_abstraction(self, client_logged_as_jdoe_with_data):
        """Test /api/startpoints/abstraction route"""
        case = unittest.TestCase()
        gene_timestamp = client_logged_as_jdoe_with_data.gene_timestamp
        response = client_logged_as_jdoe_with_data.get('/api/query/abstraction')
        assert response.status_code == 200
        expected = {
            'abstraction': [{
                'attributes':
                [{
                    'label': 'end',
                    'type': 'http://www.w3.org/2001/XMLSchema#decimal',
                    'uri': 'http://www.semanticweb.org/user/ontologies/2018/1#end'
                }, {
                    'label': 'start',
                    'type': 'http://www.w3.org/2001/XMLSchema#decimal',
                    'uri': 'http://www.semanticweb.org/user/ontologies/2018/1#start'
                }, {
                    'label': 'chromosome',
                    'type': 'http://www.semanticweb.org/user/ontologies/2018/1#AskomicsCategory',
                    'uri': 'http://www.semanticweb.org/user/ontologies/2018/1#chromosome',
                    'values':
                    [{
                        'label': 'AT1',
                        'uri': 'http://www.semanticweb.org/user/ontologies/2018/1#AT1'
                    }, {
                        'label': 'AT2',
                        'uri': 'http://www.semanticweb.org/user/ontologies/2018/1#AT2'
                    }, {
                        'label': 'AT3',
                        'uri': 'http://www.semanticweb.org/user/ontologies/2018/1#AT3'
                    }, {
                        'label': 'BN1',
                        'uri': 'http://www.semanticweb.org/user/ontologies/2018/1#BN1'
                    }, {
                        'label': 'BN2',
                        'uri': 'http://www.semanticweb.org/user/ontologies/2018/1#BN2'
                    }]
                }, {
                    'label': 'organism',
                    'type': 'http://www.semanticweb.org/user/ontologies/2018/1#AskomicsCategory',
                    'uri': 'http://www.semanticweb.org/user/ontologies/2018/1#organism',
                    'values':
                        [{
                            'label': 'Arabidopsis thaliana',
                            'uri': 'http://www.semanticweb.org/user/ontologies/2018/1#Arabidopsis%20thaliana'
                        }, {
                            'label': 'Brassica napus',
                            'uri': 'http://www.semanticweb.org/user/ontologies/2018/1#Brassica%20napus'
                        }]
                }, {
                    'label': 'strand',
                    'type': 'http://www.semanticweb.org/user/ontologies/2018/1#AskomicsCategory',
                    'uri': 'http://www.semanticweb.org/user/ontologies/2018/1#strand',
                    'values':
                        [{
                            'label': 'plus',
                            'uri': 'http://www.semanticweb.org/user/ontologies/2018/1#plus'
                        }, {
                            'label': 'minus',
                            'uri': 'http://www.semanticweb.org/user/ontologies/2018/1#minus'
                        }]
                }],
                'graphs': ['urn:sparql:askomics_test:1_jdoe:gene_{}'.format(gene_timestamp)],
                'label': 'Gene',
                'relations': [],
                'uri': 'http://www.semanticweb.org/user/ontologies/2018/1#Gene'
            }],
            'error': False,
            'errorMessage': ''
        }
        case.assertCountEqual(response.json, expected)

    def test_get_preview(self, client_logged_as_jdoe_with_data):
        """Test /api/query/preview route"""
        case = unittest.TestCase()

        gene_timestamp = client_logged_as_jdoe_with_data.gene_timestamp

        with open("tests/data/query.json", "r") as file:
            file_content = file.read()

        raw_query = file_content.replace("##TIMESTAMP###", str(gene_timestamp))
        json_query = json.loads(raw_query)

        data = {
            "graphState": json_query,
        }

        expected = {
            'error': False,
            'errorMessage': '',
            'headerPreview': ['Gene1_Label'],
            'resultsPreview': [{
                'Gene1_Label': 'AT001'
            }, {
                'Gene1_Label': 'AT001'
            }, {
                'Gene1_Label': 'AT002'
            }, {
                'Gene1_Label': 'AT002'
            }, {
                'Gene1_Label': 'AT003'
            }, {
                'Gene1_Label': 'AT003'
            }, {
                'Gene1_Label': 'AT004'
            }, {
                'Gene1_Label': 'AT004'
            }, {
                'Gene1_Label': 'AT005'
            }, {
                'Gene1_Label': 'AT005'
            }, {
                'Gene1_Label': 'BN001'
            }, {
                'Gene1_Label': 'BN001'
            }, {
                'Gene1_Label': 'BN002'
            }, {
                'Gene1_Label': 'BN002'
            }, {
                'Gene1_Label': 'BN003'
            }, {
                'Gene1_Label': 'BN003'
            }]
        }

        response = client_logged_as_jdoe_with_data.post('/api/query/preview', json=data)
        assert response.status_code == 200
        case.assertCountEqual(response.json, expected)

    def test_save_result(self, client_logged_as_jdoe_with_data):
        """Test /api/query/save_result route"""
        gene_timestamp = client_logged_as_jdoe_with_data.gene_timestamp

        with open("tests/data/query.json", "r") as file:
            file_content = file.read()

        raw_query = file_content.replace("##TIMESTAMP###", str(gene_timestamp))
        json_query = json.loads(raw_query)

        data = {
            "graphState": json_query,
        }

        response = client_logged_as_jdoe_with_data.post('/api/query/save_result', json=data)
        assert response.status_code == 200
        assert not response.json["error"]
        assert response.json["errorMessage"] == ''
