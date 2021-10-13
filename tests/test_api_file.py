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
                'size': 2264,
                'type': 'csv/tsv',
                'status': 'available'
            }, {
                'date': info["de"]["upload"]["file_date"],
                'id': 2,
                'name': 'de.tsv',
                'size': 819,
                'type': 'csv/tsv',
                'status': 'available'
            }, {
                'date': info["qtl"]["upload"]["file_date"],
                'id': 3,
                'name': 'qtl.tsv',
                'size': 99,
                'type': 'csv/tsv',
                'status': 'available'
            }, {
                'date': info["gene"]["upload"]["file_date"],
                'id': 4,
                'name': 'gene.gff3',
                'size': 2555,
                'type': 'gff/gff3',
                'status': 'available'
            }, {
                'date': info["bed"]["upload"]["file_date"],
                'id': 5,
                'name': 'gene.bed',
                'size': 689,
                'type': 'bed',
                'status': 'available'
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
                'size': 2264,
                'type': 'csv/tsv',
                'status': 'available'
            }]
        }

        response = client.client.post("/api/files", json=wrong_data)
        assert response.status_code == 200
        assert response.json == {
            'diskSpace': client.get_size_occupied_by_user(),
            'error': False,
            'errorMessage': '',
            'files': [],
        }

    def test_get_files_upload(self, client):
        """test the /api/files route after an url upload"""
        client.create_two_users()
        client.log_user("jdoe")
        date = client.upload_file_url("https://raw.githubusercontent.com/askomics/demo-data/master/Example/gene.tsv")

        response = client.client.get('/api/files')

        assert response.status_code == 200
        assert response.json == {
            'diskSpace': client.get_size_occupied_by_user(),
            'error': False,
            'errorMessage': '',
            'files': [{
                'date': date,
                'id': 1,
                'name': 'gene.tsv',
                'size': 369,
                'type': 'csv/tsv',
                'status': 'available'
            }]
        }

    def test_edit_file(self, client):
        """Test /api/files/editname route"""
        client.create_two_users()
        client.log_user("jdoe")
        info = client.upload()

        data = {"id": 1, "newName": "new name.tsv"}

        response = client.client.post("/api/files/editname", json=data)
        assert response.status_code == 200
        assert response.json == {
            'diskSpace': client.get_size_occupied_by_user(),
            'error': False,
            'errorMessage': '',
            'files': [{
                'date': info["transcripts"]["upload"]["file_date"],
                'id': 1,
                'name': 'new name.tsv',
                'size': 2264,
                'type': 'csv/tsv',
                'status': 'available'
            }, {
                'date': info["de"]["upload"]["file_date"],
                'id': 2,
                'name': 'de.tsv',
                'size': 819,
                'type': 'csv/tsv',
                'status': 'available'
            }, {
                'date': info["qtl"]["upload"]["file_date"],
                'id': 3,
                'name': 'qtl.tsv',
                'size': 99,
                'type': 'csv/tsv',
                'status': 'available'
            }, {
                'date': info["gene"]["upload"]["file_date"],
                'id': 4,
                'name': 'gene.gff3',
                'size': 2555,
                'type': 'gff/gff3',
                'status': 'available'
            }, {
                'date': info["bed"]["upload"]["file_date"],
                'id': 5,
                'name': 'gene.bed',
                'size': 689,
                'type': 'bed',
                'status': 'available'
            }]
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

        # Load a one chunk GFF file
        filepath = 'test-data/gene.gff3'
        with open(filepath, 'r') as content:
            chunk0_gff = content.read()

        chunk0_gff = {
            "first": True,
            "last": True,
            "chunk": chunk0_gff,
            "name": "gene.gff3",
            "type": "",
            "size": os.path.getsize(filepath)
        }
        response = client.client.post("/api/files/upload_chunk", json=chunk0_gff)
        assert response.status_code == 200
        # print(response.json)
        assert len(response.json) == 3
        assert not response.json["error"]
        assert response.json["errorMessage"] == ''
        assert len(response.json["path"]) == 10

        # Load a one chunk ttl file
        filepath = 'test-data/abstraction.ttl'
        with open(filepath, 'r') as content:
            chunk0_ttl = content.read()

        chunk0_ttl = {
            "first": True,
            "last": True,
            "chunk": chunk0_ttl,
            "name": "abstraction.ttl",
            "type": "",
            "size": os.path.getsize(filepath)
        }
        response = client.client.post("/api/files/upload_chunk", json=chunk0_ttl)
        assert response.status_code == 200
        # print(response.json)
        assert len(response.json) == 3
        assert not response.json["error"]
        assert response.json["errorMessage"] == ''
        assert len(response.json["path"]) == 10

        # Load a one chunk xml file
        filepath = 'test-data/abstraction.xml'
        with open(filepath, 'r') as content:
            chunk0_xml = content.read()

        chunk0_xml = {
            "first": True,
            "last": True,
            "chunk": chunk0_xml,
            "name": "abstraction.xml",
            "type": "",
            "size": os.path.getsize(filepath)
        }
        response = client.client.post("/api/files/upload_chunk", json=chunk0_xml)
        assert response.status_code == 200
        # print(response.json)
        assert len(response.json) == 3
        assert not response.json["error"]
        assert response.json["errorMessage"] == ''
        assert len(response.json["path"]) == 10

        # Load a one chunk NT file
        filepath = 'test-data/abstraction.nt'
        with open(filepath, 'r') as content:
            chunk0_nt = content.read()

        chunk0_nt = {
            "first": True,
            "last": True,
            "chunk": chunk0_nt,
            "name": "abstraction.nt",
            "type": "",
            "size": os.path.getsize(filepath)
        }
        response = client.client.post("/api/files/upload_chunk", json=chunk0_nt)
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

    def test_get_preview(self, client):
        """Test /api/files/preview route"""
        client.create_two_users()
        client.log_user("jdoe")
        client.upload()

        client.upload_file("test-data/malformed.tsv")

        csv_data = {
            "filesId": [1, ]
        }

        gff_data = {
            "filesId": [4, ]
        }

        fake_data = {
            "filesId": [42, ]
        }

        malformed_data = {
            "filesId": [6, ]
        }

        with open("tests/results/preview_files.json") as file:
            csv_expected = json.loads(file.read())

        with open("tests/results/preview_malformed_files.json") as file:
            csv_malformed = json.loads(file.read())

        response = client.client.post('/api/files/preview', json=fake_data)
        assert response.status_code == 200
        assert response.json == {
            'error': False,
            'errorMessage': '',
            'previewFiles': []
        }

        response = client.client.post('/api/files/preview', json=malformed_data)
        assert response.status_code == 200
        assert response.json == csv_malformed

        response = client.client.post('/api/files/preview', json=csv_data)
        assert response.status_code == 200
        assert response.json == csv_expected

        response = client.client.post('/api/files/preview', json=gff_data)
        assert response.status_code == 200
        assert response.json == {
            'error': False,
            'errorMessage': '',
            'previewFiles': [{
                'data': {
                    'entities': [
                        'gene', 'transcript', 'five_prime_UTR', 'exon', 'CDS',
                        'three_prime_UTR'
                    ]
                },
                'id': 4,
                'name': 'gene.gff3',
                'type': 'gff/gff3',
                'error': False,
                'error_message': ''
            }]
        }

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
                'type': 'csv/tsv',
                'status': 'available'
            }, {
                'date': info["qtl"]["upload"]["file_date"],
                'id': 3,
                'name': 'qtl.tsv',
                'size': 99,
                'type': 'csv/tsv',
                'status': 'available'
            }, {
                'date': info["gene"]["upload"]["file_date"],
                'id': 4,
                'name': 'gene.gff3',
                'size': 2555,
                'type': 'gff/gff3',
                'status': 'available'
            }, {
                'date': info["bed"]["upload"]["file_date"],
                'id': 5,
                'name': 'gene.bed',
                'size': 689,
                'type': 'bed',
                'status': 'available'
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
                'type': 'csv/tsv',
                'status': 'available'
            }, {
                'date': info["gene"]["upload"]["file_date"],
                'id': 4,
                'name': 'gene.gff3',
                'size': 2555,
                'type': 'gff/gff3',
                'status': 'available'
            }, {
                'date': info["bed"]["upload"]["file_date"],
                'id': 5,
                'name': 'gene.bed',
                'size': 689,
                'type': 'bed',
                'status': 'available'
            }]
        }

    def test_integrate(self, client):
        """Test /api/files/integrate route"""
        client.create_two_users()
        client.log_user("jdoe")
        client.upload()

        tsv_data = {
            "fileId": 1,
            "public": False,
            "customUri": None,
            "externalEndpoint": None
        }

        gff_data = {
            "fileId": 4,
            "public": True,
            "customUri": None,
            "externalEndpoint": None
        }

        bed_data = {
            "fileId": 5,
            "public": True,
            "customUri": None,
            "externalEndpoint": None
        }

        wrong_data = {
            "fileId": 42,
            "public": False,
            "customUri": None,
            "externalEndpoint": None
        }

        response = client.client.post('/api/files/integrate', json=wrong_data)
        assert response.status_code == 200
        # print(response.json)
        assert len(response.json) == 3
        assert not response.json["error"]
        assert response.json["errorMessage"] == ''
        assert response.json["dataset_ids"] == []

        response = client.client.post('/api/files/integrate', json=tsv_data)
        assert response.status_code == 200
        assert len(response.json) == 3
        assert not response.json["error"]
        assert response.json["errorMessage"] == ''
        assert response.json["dataset_ids"]

        response = client.client.post('/api/files/integrate', json=gff_data)
        assert response.status_code == 200
        print(response.json)
        assert len(response.json) == 3
        assert not response.json["error"]
        assert response.json["errorMessage"] == ''
        assert response.json["dataset_ids"]

        response = client.client.post('/api/files/integrate', json=bed_data)
        assert response.status_code == 200
        print(response.json)
        assert len(response.json) == 3
        assert not response.json["error"]
        assert response.json["errorMessage"] == ''
        assert response.json["dataset_ids"]

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
        assert response.data == content
