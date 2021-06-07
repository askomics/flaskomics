import json

from . import AskomicsTestCase


class TestURIResults(AskomicsTestCase):
    """Test correct URI interpretation"""

    def test_uri(self, client):
        """Test entity uri interpretation"""
        client.create_two_users()
        client.log_user("jdoe")
        client.upload_file("test-data/uris.csv")

        client.integrate_file({
            "id": 1,
            "columns_type": ["start_entity", "text"]
        })

        with open("tests/data/uri_query.json") as file:
            file_content = file.read()

        json_query = json.loads(file_content)

        with open("tests/results/results_uri.json") as file:
            file_content = file.read()

        expected = json.loads(file_content)

        response = client.client.post('/api/query/preview', json=json_query)

        assert response.status_code == 200
        assert response.json == expected

    def test_linked_uri(self, client):
        """Test linked uri interpretation"""
        client.create_two_users()
        client.log_user("jdoe")
        client.upload_file("test-data/uris.csv")
        client.upload_file("test-data/linked_uris.csv")

        client.integrate_file({
            "id": 1,
            "columns_type": ["start_entity", "text"]
        })

        client.integrate_file({
            "id": 2,
            "columns_type": ["start_entity", "reference"]
        })

        with open("tests/data/linked_uri_query.json") as file:
            file_content = file.read()

        json_query = json.loads(file_content)

        with open("tests/results/results_linked_uri.json") as file:
            file_content = file.read()

        expected = json.loads(file_content)

        response = client.client.post('/api/query/preview', json=json_query)

        assert response.status_code == 200
        assert response.json == expected
