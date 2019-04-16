import unittest

from . import AskomicsTestCase


class TestApiStartpoints(AskomicsTestCase):
    """Test AskOmics API /api/startpoints/<someting>"""

    def test_startpoints(self, client_logged_as_jdoe_with_data):
        """Test /api/startpoints route"""
        case = unittest.TestCase()
        gene_timestamp = client_logged_as_jdoe_with_data.gene_timestamp
        response = client_logged_as_jdoe_with_data.get('/api/startpoints')
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
            }]
        }
        case.assertCountEqual(response.json, expected)

    def test_get_abstraction(self, client_logged_as_jdoe_with_data):
        """Test /api/startpoints/abstraction route"""
        case = unittest.TestCase()
        gene_timestamp = client_logged_as_jdoe_with_data.gene_timestamp
        response = client_logged_as_jdoe_with_data.get('/api/startpoints/abstraction')
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
