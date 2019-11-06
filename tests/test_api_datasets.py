from . import AskomicsTestCase


class TestApiDatasets(AskomicsTestCase):
    """Test AskOmics API /api/datasets/<someting>"""

    def test_get_datasets(self, client):
        """test the /api/datasets route"""
        client.create_two_users()
        client.log_user("jdoe")
        info = client.upload_and_integrate()

        response = client.client.get('/api/datasets')

        expected = {
            'datasets': [{
                'end': info["transcripts"]["end"],
                'error_message': '',
                'id': 1,
                'name': 'transcripts.tsv',
                'ntriples': 0,
                'public': False,
                'start': info["transcripts"]["start"],
                'status': 'success',
                'traceback': None
            }, {
                'end': info["de"]["end"],
                'error_message': '',
                'id': 2,
                'name': 'de.tsv',
                'ntriples': 0,
                'public': False,
                'start': info["de"]["start"],
                'status': 'success',
                'traceback': None
            }, {
                'end': info["qtl"]["end"],
                'error_message': '',
                'id': 3,
                'name': 'qtl.tsv',
                'ntriples': 0,
                'public': False,
                'start': info["qtl"]["start"],
                'status': 'success',
                'traceback': None
            }],
            'error': False,
            'errorMessage': ''
        }

        assert response.status_code == 200
        assert response.json == expected

    def test_delete_datasets(self, client):
        """Test the /api/datsets/delete route"""
        client.create_two_users()
        client.log_user("jdoe")
        client.upload_and_integrate()

        data = {
            "datasetsIdToDelete": [1, ]
        }

        response = client.client.post('/api/datasets/delete', json=data)

        assert response.status_code == 200
        assert not response.json["error"]
        assert response.json["errorMessage"] == ''
        assert response.json["datasets"][0]["status"] == "queued"
