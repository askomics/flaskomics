import os
import unittest
from . import AskomicsTestCase


class TestApiFile(AskomicsTestCase):
    """Test AskOmics API /api/file/<someting>"""

    def test_get_files(self, client_logged_as_jdoe_with_data):
        """test the /api/files route"""
        case = unittest.TestCase()
        response = client_logged_as_jdoe_with_data.get('/api/files')
        assert response.status_code == 200
        assert response.json == {
            'error': False,
            'errorMessage': '',
            'files': [{
                'id': 1,
                'size': 394,
                'name': 'gene',
                'type': 'csv/tsv'
            }]
        }

        # post request
        data = {
            "filesId": [1, ]
        }

        wrong_data = {
            "filesId": [2, ]
        }

        response = client_logged_as_jdoe_with_data.post('/api/files', json=data)
        assert response.status_code == 200
        print(response.json)
        assert response.json == {
            'error': False,
            'errorMessage': '',
            'files': [{
                'id': 1,
                'size': 394,
                'name': 'gene',
                'type': 'csv/tsv'
            }]
        }

        response = client_logged_as_jdoe_with_data.post('/api/files', json=wrong_data)
        assert response.status_code == 200
        print(response.json)
        assert response.json == {
            'error': False,
            'errorMessage': '',
            'files': []
        }

    def test_upload_chunk(self, client_logged_as_jdoe):
        """Test /api/files/upload_chunk route"""
        filepath = 'test-data/gene.tsv'
        with open(filepath, 'r') as content:
            chunk0 = content.read()

        # Load a one chunk file (first and last are True)
        chunk0_data = {
            "first": True,
            "last": True,
            "chunk": chunk0,
            "name": "gene",
            "type": "csv/tsv",
            "size": os.path.getsize(filepath)
        }

        response = client_logged_as_jdoe.post("/api/files/upload_chunk", json=chunk0_data)
        assert response.status_code == 200
        print(response.json)
        assert len(response.json) == 3
        assert not response.json["error"]
        assert response.json["errorMessage"] == ''
        assert len(response.json["path"]) == 10

        # Load a 3 chunk file
        with open('test-data/gene_chunk1.tsv', 'r') as content:
            chunk1 = content.read()
        with open('test-data/gene_chunk2.tsv', 'r') as content:
            chunk2 = content.read()
        with open('test-data/gene_chunk3.tsv', 'r') as content:
            chunk3 = content.read()

        chunk1_data = {
            "first": True,
            "last": False,
            "chunk": chunk1,
            "name": "gene",
            "type": "csv/tsv",
            "size": os.path.getsize(filepath)
        }

        response = client_logged_as_jdoe.post("/api/files/upload_chunk", json=chunk1_data)
        assert response.status_code == 200
        print(response.json)
        assert len(response.json) == 3
        assert not response.json["error"]
        assert response.json["errorMessage"] == ''
        assert len(response.json["path"]) == 10

        chunk2_data = {
            "first": False,
            "last": False,
            "chunk": chunk2,
            "name": "gene",
            "type": "csv/tsv",
            "size": os.path.getsize(filepath),
            "path": response.json["path"]
        }

        response = client_logged_as_jdoe.post("/api/files/upload_chunk", json=chunk2_data)
        assert response.status_code == 200
        print(response.json)
        assert len(response.json) == 3
        assert not response.json["error"]
        assert response.json["errorMessage"] == ''
        assert len(response.json["path"]) == 10

        chunk3_data = {
            "first": False,
            "last": True,
            "chunk": chunk3,
            "name": "gene",
            "type": "csv/tsv",
            "size": os.path.getsize(filepath),
            "path": response.json["path"]
        }

        response = client_logged_as_jdoe.post("/api/files/upload_chunk", json=chunk3_data)
        assert response.status_code == 200
        print(response.json)
        assert len(response.json) == 3
        assert not response.json["error"]
        assert response.json["errorMessage"] == ''
        assert len(response.json["path"]) == 10
