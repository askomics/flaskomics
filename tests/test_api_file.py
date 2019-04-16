import os
import random

from . import AskomicsTestCase


class TestApiFile(AskomicsTestCase):
    """Test AskOmics API /api/file/<someting>"""

    def test_get_files(self, client_logged_as_jdoe_with_data):
        """test the /api/files route"""
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

    def test_get_preview(self, client_logged_as_jdoe_with_data):
        """Test /api/files/preview route"""
        ok_data = {
            "filesId": [1, ]
        }

        fake_data = {
            "filesId": [42, ]
        }

        response = client_logged_as_jdoe_with_data.post('/api/files/preview', json=fake_data)
        assert response.status_code == 200
        assert response.json == {
            'error': False,
            'errorMessage': '',
            'previewFiles': []
        }

        response = client_logged_as_jdoe_with_data.post('/api/files/preview', json=ok_data)
        assert response.status_code == 200
        print(response.json)
        assert response.json == {
            'error': False,
            'errorMessage': '',
            'previewFiles': [{
                'csv_data': {
                    'columns_type': [
                        'start_entity',
                        'organism',
                        'chromosome',
                        'strand',
                        'start',
                        'end'
                    ],
                    'content_preview': [{
                        'Gene': 'AT001',
                        'chromosome': 'AT1',
                        'end': '40000',
                        'organism': 'Arabidopsis thaliana',
                        'start': '1',
                        'strand': 'plus'
                    }, {
                        'Gene': 'AT002',
                        'chromosome': 'AT1',
                        'end': '80000',
                        'organism': 'Arabidopsis thaliana',
                        'start': '50000',
                        'strand': 'plus'
                    }, {
                        'Gene': 'AT003',
                        'chromosome': 'AT2',
                        'end': '6000',
                        'organism': 'Arabidopsis thaliana',
                        'start': '200',
                        'strand': 'plus'
                    }, {
                        'Gene': 'AT004',
                        'chromosome': 'AT3',
                        'end': '60000',
                        'organism': 'Arabidopsis thaliana',
                        'start': '1000',
                        'strand': 'minus'
                    }, {
                        'Gene': 'AT005',
                        'chromosome': 'AT3',
                        'end': '110000',
                        'organism': 'Arabidopsis thaliana',
                        'start': '90000',
                        'strand': 'plus'
                    }, {
                        'Gene': 'BN001',
                        'chromosome': 'BN1',
                        'end': '90000',
                        'organism': 'Brassica napus',
                        'start': '700',
                        'strand': 'plus'
                    }, {
                        'Gene': 'BN002',
                        'chromosome': 'BN2',
                        'end': '4000',
                        'organism': 'Brassica napus',
                        'start': '60',
                        'strand': 'plus'
                    }, {
                        'Gene': 'BN003',
                        'chromosome': 'BN2',
                        'end': '10000',
                        'organism': 'Brassica napus',
                        'start': '7000',
                        'strand': 'plus'
                    }],
                    'header': ['Gene', 'organism', 'chromosome', 'strand', 'start', 'end']
                },
                'id': 1,
                'name': 'gene',
                'type': 'csv/tsv'
            }]}

    def test_delete_files(self, client_logged_as_jdoe_with_data):
        """Test /api/files/delete route"""
        ok_data = {
            "filesIdToDelete": [1, ]
        }

        fake_data = {
            "filesIdToDelete": [42, ]
        }

        response = client_logged_as_jdoe_with_data.post('/api/files/delete', json=fake_data)
        assert response.status_code == 500
        print(response.json)
        assert response.json == {
            'error': True,
            'errorMessage': 'list index out of range',
            'files': []
        }

        response = client_logged_as_jdoe_with_data.post('/api/files/delete', json=ok_data)
        assert response.status_code == 200
        print(response.json)
        assert response.json == {
            'error': False,
            'errorMessage': '',
            'files': []
        }

    def test_integrate(self, client_logged_as_jdoe_with_data):
        """Test /api/files/integrate route"""
        ok_data = {
            "fileId": 1
        }

        wrong_data = {
            "fileId": 42
        }

        response = client_logged_as_jdoe_with_data.post('/api/files/integrate', json=wrong_data)
        assert response.status_code == 200
        print(response.json)
        assert len(response.json) == 3
        assert not response.json["error"]
        assert response.json["errorMessage"] == ''
        assert len(response.json["task_id"]) == 36

        response = client_logged_as_jdoe_with_data.post('/api/files/integrate', json=ok_data)
        assert response.status_code == 200
        print(response.json)
        assert len(response.json) == 3
        assert not response.json["error"]
        assert response.json["errorMessage"] == ''
        assert len(response.json["task_id"]) == 36

    def test_serve_file(self, client_logged_as_jdoe_with_data):
        """Test /api/files/ttl/<userid>/<username>/<filepath> route"""
        ttl_dir = "{}/1_jdoe/ttl".format(client_logged_as_jdoe_with_data.dir_path)
        alpabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        content = "{}\n".format(''.join(random.choice(alpabet) for i in range(100)))
        filename = ''.join(random.choice(alpabet) for i in range(10))
        with open("{}/{}".format(ttl_dir, filename), "w+") as f:
            f.write(content)

        response = client_logged_as_jdoe_with_data.get('/api/files/ttl/1/jdoe/{}'.format(filename))

        assert response.status_code == 200
        print(response.data.decode("utf-8"))
        assert response.data.decode("utf-8") == content
