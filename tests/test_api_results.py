import json
from deepdiff import DeepDiff

from . import AskomicsTestCase


class TestApiResults(AskomicsTestCase):
    """Test AskOmics API /api/results/<something>"""

    def test_get_results(self, client):
        """test /api/results route"""
        client.create_two_users()
        client.log_user("jdoe")
        client.upload_and_integrate()

        response = client.client.get('/api/results')

        assert response.status_code == 200
        assert response.json == {'error': False, 'errorMessage': '', 'files': [], 'triplestoreMaxRows': 10000}

        result_info = client.create_result()

        response = client.client.get('/api/results')

        with open("tests/results/results.json", "r") as file:
            file_content = file.read()
        raw_results = file_content.replace("###START###", str(result_info["start"]))
        raw_results = raw_results.replace("###END###", str(result_info["end"]))
        raw_results = raw_results.replace("###ID###", str(result_info["id"]))
        raw_results = raw_results.replace("###PATH###", str(result_info["path"]))

        expected = json.loads(raw_results)

        assert response.status_code == 200
        assert response.json == expected

    def test_get_preview(self, client):
        """test /api/results/preview route"""
        client.create_two_users()
        client.log_user("jdoe")
        client.upload_and_integrate()
        result_info = client.create_result()

        data = {
            "fileId": result_info["id"]
        }

        with open("tests/results/preview.json", "r") as file:
            file_content = file.read()
        expected = json.loads(file_content)

        response = client.client.post('/api/results/preview', json=data)
        ddiff = DeepDiff(response.json, expected, ignore_order=True)

        assert response.status_code == 200
        assert ddiff == {}

    def test_get_graph_state(self, client):
        """test /api/results/graphstate"""
        client.create_two_users()
        client.log_user("jdoe")
        client.upload_and_integrate()
        result_info = client.create_result()

        data = {
            "fileId": result_info["id"]
        }

        response = client.client.post('/api/results/graphstate', json=data)

        with open('tests/results/graphstate.json') as file:
            expected = json.loads(file.read())

        assert response.status_code == 200
        assert response.json == expected

    def test_download_result(self, client):
        """test /api/results/download route"""
        client.create_two_users()
        client.log_user("jdoe")
        client.upload_and_integrate()
        result_info = client.create_result()

        data = {
            "fileId": result_info["id"]
        }

        response = client.client.post('/api/results/download', json=data)

        assert response.status_code == 200

    def test_delete_result(self, client):
        """test .api/results/delete route"""
        client.create_two_users()
        client.log_user("jdoe")
        client.upload_and_integrate()
        result_info = client.create_result()

        data = {
            "filesIdToDelete": [result_info["id"], ]
        }

        response = client.client.post('/api/results/delete', json=data)

        assert response.status_code == 200
        assert response.json == {
            "error": False,
            "errorMessage": "",
            "remainingFiles": []
        }

    def test_get_sparql_query(self, client):
        """test /api/results/sparqlquery route"""
        client.create_two_users()
        client.log_user("jdoe")
        client.upload_and_integrate()
        result_info = client.create_result()

        data = {
            "fileId": result_info["id"]
        }

        response = client.client.post("/api/results/sparqlquery", json=data)

        with open('tests/results/query.sparql') as file:
            content = file.read()

        assert response.status_code == 200
        assert response.json == {
            'error': False,
            'diskSpace': client.get_size_occupied_by_user(),
            'errorMessage': '',
            'query': content
        }
