import json
import os
import random

from . import AskomicsTestCase


class TestApiFile(AskomicsTestCase):
    """Test AskOmics API /api/file/<someting>"""

    def test_get_files(self, client):
        """test the /api/files route"""
        client.create_two_users()
        client.log_user("jdoe")
        info = client.upload()

        response = client.client.get('/api/files')

        assert response.status_code == 200
        assert response.json == {
            'diskSpace': client.get_size_occupied_by_user(),
            'error': False,
            'errorMessage': '',
            'files': [{
                'date': info["transcripts"]["upload"]["file_date"],
                'id': 1,
                'name': 'transcripts.tsv',
                'size': 1986,
                'type': 'csv/tsv'
            }, {
                'date': info["de"]["upload"]["file_date"],
                'id': 2,
                'name': 'de.tsv',
                'size': 819,
                'type': 'csv/tsv'
            }, {
                'date': info["qtl"]["upload"]["file_date"],
                'id': 3,
                'name': 'qtl.tsv',
                'size': 99,
                'type': 'csv/tsv'
            }]
        }

        # post request
        data = {
            "filesId": [1, ]
        }

        wrong_data = {
            "filesId": [42, ]
        }

        response = client.client.post("/api/files", json=data)
        assert response.status_code == 200
        assert response.json == {
            'diskSpace': client.get_size_occupied_by_user(),
            'error': False,
            'errorMessage': '',
            'files': [{
                'date': info["transcripts"]["upload"]["file_date"],
                'id': 1,
                'name': 'transcripts.tsv',
                'size': 1986,
                'type': 'csv/tsv'
            }]
        }

        response = client.client.post("/api/files", json=wrong_data)
        assert response.status_code == 200
        assert response.json == {
            'diskSpace': client.get_size_occupied_by_user(),
            'error': False,
            'errorMessage': '',
            'files': []
        }

    def test_upload_chunk(self, client):
        """Test /api/files/upload_chunk route"""
        client.create_two_users()
        client.log_user("jdoe")

        filepath = 'test-data/transcripts.tsv'
        with open(filepath, 'r') as content:
            chunk0 = content.read()

        # Load a one chunk file (first and last are True)
        chunk0_data = {
            "first": True,
            "last": True,
            "chunk": chunk0,
            "name": "transcripts.tsv",
            "type": "text/tab-separated-values",
            "size": os.path.getsize(filepath)
        }

        response = client.client.post("/api/files/upload_chunk", json=chunk0_data)
        assert response.status_code == 200
        # print(response.json)
        assert len(response.json) == 3
        assert not response.json["error"]
        assert response.json["errorMessage"] == ''
        assert len(response.json["path"]) == 10

        # Load a 3 chunk file
        with open('test-data/transcripts_chunk1.tsv', 'r') as content:
            chunk1 = content.read()
        with open('test-data/transcripts_chunk2.tsv', 'r') as content:
            chunk2 = content.read()
        with open('test-data/transcripts_chunk3.tsv', 'r') as content:
            chunk3 = content.read()

        chunk1_data = {
            "first": True,
            "last": False,
            "chunk": chunk1,
            "name": "transcripts.tsv",
            "type": "text/tab-separated-values",
            "size": os.path.getsize(filepath)
        }

        response = client.client.post("/api/files/upload_chunk", json=chunk1_data)
        assert response.status_code == 200
        # print(response.json)
        assert len(response.json) == 3
        assert not response.json["error"]
        assert response.json["errorMessage"] == ''
        assert len(response.json["path"]) == 10

        chunk2_data = {
            "first": False,
            "last": False,
            "chunk": chunk2,
            "name": "transcripts.tsv",
            "type": "text/tab-separated-values",
            "size": os.path.getsize(filepath),
            "path": response.json["path"]
        }

        response = client.client.post("/api/files/upload_chunk", json=chunk2_data)
        assert response.status_code == 200
        # print(response.json)
        assert len(response.json) == 3
        assert not response.json["error"]
        assert response.json["errorMessage"] == ''
        assert len(response.json["path"]) == 10

        chunk3_data = {
            "first": False,
            "last": True,
            "chunk": chunk3,
            "name": "transcripts.tsv",
            "type": "text/tab-separated-values",
            "size": os.path.getsize(filepath),
            "path": response.json["path"]
        }

        response = client.client.post("/api/files/upload_chunk", json=chunk3_data)
        assert response.status_code == 200
        # print(response.json)
        assert len(response.json) == 3
        assert not response.json["error"]
        assert response.json["errorMessage"] == ''
        assert len(response.json["path"]) == 10

    def test_upload_url(self, client):
        """Test /api/files/upload_url route"""
        client.create_two_users()
        client.log_user("jdoe")

        data = {"url": "https://raw.githubusercontent.com/askomics/demo-data/master/Example/gene.tsv"}  # FIXME: use a local url

        response = client.client.post("/api/files/upload_url", json=data)

        assert response.status_code == 200
        assert response.json == {
            "error": False,
            "errorMessage": ""
        }

        response = client.client.get("/api/files")
        assert response.status_code == 200
        assert len(response.json["files"]) == 1

    def test_get_preview(self, client):
        """Test /api/files/preview route"""
        client.create_two_users()
        client.log_user("jdoe")
        client.upload()

        data = {
            "filesId": [1, ]
        }

        fake_data = {
            "filesId": [42, ]
        }

        with open("tests/results/preview_files.json") as file:
            expected = json.loads(file.read())

        response = client.client.post('/api/files/preview', json=fake_data)
        assert response.status_code == 200
        assert response.json == {
            'error': False,
            'errorMessage': '',
            'previewFiles': []
        }

        response = client.client.post('/api/files/preview', json=data)
        assert response.status_code == 200
        print(json.dumps(response.json))
        assert response.json == expected

    def test_delete_files(self, client):
        """Test /api/files/delete route"""
        client.create_two_users()
        client.log_user("jdoe")
        info = client.upload()

        ok_data = {
            "filesIdToDelete": [1, ]
        }

        ok_data_2 = {
            "filesIdToDelete": [2, ]
        }

        fake_data = {
            "filesIdToDelete": [42, ]
        }

        response = client.client.post('/api/files/delete', json=fake_data)
        assert response.status_code == 500
        assert response.json == {
            'error': True,
            'errorMessage': 'list index out of range',
            'files': []
        }

        response = client.client.post('/api/files/delete', json=ok_data)
        assert response.status_code == 200
        assert response.json == {
            'error': False,
            'errorMessage': '',
            'files': [{
                'date': info["de"]["upload"]["file_date"],
                'id': 2,
                'name': 'de.tsv',
                'size': 819,
                'type': 'csv/tsv'
            }, {
                'date': info["qtl"]["upload"]["file_date"],
                'id': 3,
                'name': 'qtl.tsv',
                'size': 99,
                'type': 'csv/tsv'
            }]
        }

        response = client.client.post('/api/files/delete', json=ok_data_2)
        assert response.status_code == 200
        assert response.json == {
            'error': False,
            'errorMessage': '',
            'files': [{
                'date': info["qtl"]["upload"]["file_date"],
                'id': 3,
                'name': 'qtl.tsv',
                'size': 99,
                'type': 'csv/tsv'
            }]
        }

    def test_integrate(self, client):
        """Test /api/files/integrate route"""
        client.create_two_users()
        client.log_user("jdoe")
        client.upload()

        tsv_data = {
            "fileId": 1,
            "public": False
        }

        gff_data = {
            "fileId": 2,
            "public": True
        }

        wrong_data = {
            "fileId": 42,
            "public": False
        }

        response = client.client.post('/api/files/integrate', json=wrong_data)
        assert response.status_code == 200
        # print(response.json)
        assert len(response.json) == 3
        assert not response.json["error"]
        assert response.json["errorMessage"] == ''
        assert len(response.json["task_id"]) == 0

        response = client.client.post('/api/files/integrate', json=tsv_data)
        assert response.status_code == 200
        # print(response.json)
        assert len(response.json) == 3
        assert not response.json["error"]
        assert response.json["errorMessage"] == ''
        assert len(response.json["task_id"]) == 36

        response = client.client.post('/api/files/integrate', json=gff_data)
        assert response.status_code == 200
        print(response.json)
        assert len(response.json) == 3
        assert not response.json["error"]
        assert response.json["errorMessage"] == ''
        assert len(response.json["task_id"]) == 36

    def test_serve_file(self, client):
        """Test /api/files/ttl/<userid>/<username>/<filepath> route"""
        client.create_two_users()
        client.log_user("jdoe")
        client.upload()

        ttl_dir = "{}/1_jdoe/ttl".format(client.dir_path)

        # Generate random name and content
        alpabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        content = "{}\n".format(''.join(random.choice(alpabet) for i in range(100)))
        filename = ''.join(random.choice(alpabet) for i in range(10))

        # Write file
        with open("{}/{}".format(ttl_dir, filename), "w+") as f:
            f.write(content)

        response = client.client.get('/api/files/ttl/1/jdoe/{}'.format(filename))

        assert response.status_code == 200
        # print(response.data.decode("utf-8"))
        assert response.data.decode("utf-8") == content
