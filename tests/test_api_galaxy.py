import json

from . import AskomicsTestCase


class TestApiGalaxy(AskomicsTestCase):
    """Test AskOmics API /api/galaxy/<someting>"""

    def test_get_datasets(self, client):
        """test the /api/datasets route"""
        client.create_two_users()
        client.log_user("jdoe")
        dataset_info = client.upload_dataset_into_galaxy()

        response = client.client.get("/api/galaxy/datasets")

        expected_dataset = {
            'create_time': dataset_info["outputs"][0]["create_time"],
            'extension': 'tabular',
            'id': dataset_info["outputs"][0]["id"],
            'name': 'transcripts.tsv',
        }

        expected_history = {
            'id': client.galaxy_history["id"],
            'name': client.galaxy_history["name"],
            'selected': True
        }

        assert response.status_code == 200
        assert not response.json["error"]
        assert response.json["errorMessage"] == ""
        assert expected_dataset in response.json["datasets"]
        assert expected_history in response.json["histories"]

        data = {"history_id": client.galaxy_history["id"]}
        response = client.client.post("/api/galaxy/datasets", json=data)

        assert response.status_code == 200
        assert not response.json["error"]
        assert response.json["errorMessage"] == ""
        assert expected_dataset in response.json["datasets"]
        assert expected_history in response.json["histories"]

    def test_get_queries(self, client):
        """test the /api/datasets route"""
        client.create_two_users()
        client.log_user("jdoe")
        query_info = client.upload_query_into_galaxy()

        expected_dataset = {
            'create_time': query_info["outputs"][0]["create_time"],
            'extension': 'json',
            'id': query_info["outputs"][0]["id"],
            'name': 'graphstate.json',
        }

        expected_history = {
            'id': client.galaxy_history["id"],
            'name': client.galaxy_history["name"],
            'selected': True
        }

        response = client.client.get("/api/galaxy/queries")

        assert response.status_code == 200
        assert not response.json["error"]
        assert response.json["errorMessage"] == ""
        assert expected_dataset in response.json["datasets"]
        assert expected_history in response.json["histories"]

    def test_upload_datasets(self, client):
        """test the /api/galaxy/upload_datasets route"""
        client.create_two_users()
        client.log_user("jdoe")
        dataset_info = client.upload_dataset_into_galaxy()

        data = {
            "datasets_id": [dataset_info["outputs"][0]["id"], ]
        }

        response = client.client.post("/api/galaxy/upload_datasets", json=data)

        assert response.status_code == 200
        assert response.json == {
            'error': False,
            'errorMessage': ''
        }

        response = client.client.get('/api/files')

        assert response.status_code == 200
        assert not response.json['error']
        assert response.json['errorMessage'] == ''
        assert response.json['diskSpace'] == client.get_size_occupied_by_user()
        assert len(response.json['files']) == 1

    def test_get_dataset_content(self, client):
        """test the /api/galaxy/getdatasetcontent route"""
        client.create_two_users()
        client.log_user("jdoe")
        query_info = client.upload_query_into_galaxy()

        data = {
            "dataset_id": query_info["outputs"][0]["id"]
        }

        response = client.client.post("/api/galaxy/getdatasetcontent", json=data)

        with open("tests/data/graphState_simple_query.json") as file:
            file_content = file.read()
        expected = json.loads(file_content)

        assert response.status_code == 200
        assert len(response.json) == 3
        assert not response.json['error']
        assert response.json['errorMessage'] == ''
        assert self.equal_objects(expected, response.json["dataset_content"])
