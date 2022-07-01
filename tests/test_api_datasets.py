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
                'traceback': None,
                'percent': 100.0,
                'exec_time': info["transcripts"]["end"] - info["transcripts"]["start"],
                'ontology': False
            }, {
                'end': info["de"]["end"],
                'error_message': '',
                'id': 2,
                'name': 'de.tsv',
                'ntriples': 0,
                'public': False,
                'start': info["de"]["start"],
                'status': 'success',
                'traceback': None,
                'percent': 100.0,
                'exec_time': info["de"]["end"] - info["de"]["start"],
                'ontology': False
            }, {
                'end': info["qtl"]["end"],
                'error_message': '',
                'id': 3,
                'name': 'qtl.tsv',
                'ntriples': 0,
                'public': False,
                'start': info["qtl"]["start"],
                'status': 'success',
                'traceback': None,
                'percent': 100.0,
                'exec_time': info["qtl"]["end"] - info["qtl"]["start"],
                'ontology': False
            }, {
                'end': info["gff"]["end"],
                'error_message': '',
                'id': 4,
                'name': 'gene.gff3',
                'ntriples': 0,
                'public': False,
                'start': info["gff"]["start"],
                'status': 'success',
                'traceback': None,
                'percent': 100.0,
                'exec_time': info["gff"]["end"] - info["gff"]["start"],
                'ontology': False
            }, {
                'end': info["bed"]["end"],
                'error_message': '',
                'id': 5,
                'name': 'gene.bed',
                'ntriples': 0,
                'public': False,
                'start': info["bed"]["start"],
                'status': 'success',
                'traceback': None,
                'percent': 100.0,
                'exec_time': info["bed"]["end"] - info["bed"]["start"],
                'ontology': False
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

    def test_toggle_public(self, client):
        """Test the /api/datsets/delete route"""
        client.create_two_users()
        client.log_user("jdoe")
        info = client.upload_and_integrate()

        data = {"id": 1, "newStatus": True}

        expected = {
            'datasets': [{
                'end': info["transcripts"]["end"],
                'error_message': '',
                'id': 1,
                'name': 'transcripts.tsv',
                'ntriples': 0,
                'public': True,
                'start': info["transcripts"]["start"],
                'status': 'success',
                'traceback': None,
                'percent': 100.0,
                'exec_time': info["transcripts"]["end"] - info["transcripts"]["start"],
                'ontology': False
            }, {
                'end': info["de"]["end"],
                'error_message': '',
                'id': 2,
                'name': 'de.tsv',
                'ntriples': 0,
                'public': False,
                'start': info["de"]["start"],
                'status': 'success',
                'traceback': None,
                'percent': 100.0,
                'exec_time': info["de"]["end"] - info["de"]["start"],
                'ontology': False
            }, {
                'end': info["qtl"]["end"],
                'error_message': '',
                'id': 3,
                'name': 'qtl.tsv',
                'ntriples': 0,
                'public': False,
                'start': info["qtl"]["start"],
                'status': 'success',
                'traceback': None,
                'percent': 100.0,
                'exec_time': info["qtl"]["end"] - info["qtl"]["start"],
                'ontology': False
            }, {
                'end': info["gff"]["end"],
                'error_message': '',
                'id': 4,
                'name': 'gene.gff3',
                'ntriples': 0,
                'public': False,
                'start': info["gff"]["start"],
                'status': 'success',
                'traceback': None,
                'percent': 100.0,
                'exec_time': info["gff"]["end"] - info["gff"]["start"],
                'ontology': False
            }, {
                'end': info["bed"]["end"],
                'error_message': '',
                'id': 5,
                'name': 'gene.bed',
                'ntriples': 0,
                'public': False,
                'start': info["bed"]["start"],
                'status': 'success',
                'traceback': None,
                'percent': 100.0,
                'exec_time': info["bed"]["end"] - info["bed"]["start"],
                'ontology': False
            }],
            'error': False,
            'errorMessage': ''
        }

        response = client.client.post("/api/datasets/public", json=data)

        assert response.status_code == 200
        assert response.json == expected

        expected["datasets"][0]["public"] = False
        data["newStatus"] = False

        response = client.client.post("/api/datasets/public", json=data)

        assert response.status_code == 200
        assert response.json == expected
