from . import AskomicsTestCase


class TestApiStartpoints(AskomicsTestCase):
    """Test AskOmics API /api/startpoints/<someting>"""

    def test_startpoints(self, client_logged_as_jdoe_with_data):
        """Test /api/startpoints route"""
        gene_timestamp = client_logged_as_jdoe_with_data.gene_timestamp
        print(gene_timestamp)
        response = client_logged_as_jdoe_with_data.get('/api/startpoints')
        assert response.status_code == 200
        print(response.json)
        assert response.json == {
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
