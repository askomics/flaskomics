import json

from . import AskomicsTestCase


class TestApiData(AskomicsTestCase):
    """Test AskOmics API /data/<uri>"""

    def test_get_uri(self, client):
        """test the /data/<uri> route"""
        client.create_two_users()
        client.log_user("jdoe")
        client.upload_and_integrate()

        with open("tests/results/data_full.json", "r") as file:
            file_content = file.read()
        expected = json.loads(file_content)

        response = client.client.get('/api/data/AT3G10490')

        assert response.status_code == 200
        assert self.equal_objects(response.json, expected)

    def test_get_empty_uri(self, client):
        """test the /data/<uri> route for an empty uri"""
        response = client.client.get('/api/data/random_uri')

        expected_empty_response = {
            'data': [],
            'error': False,
            'errorMessage': ""
        }

        assert response.status_code == 200
        assert response.json == expected_empty_response

    def test_uri_access(self, client):
        """test the /data/<uri> route for public and non public uris"""
        client.create_two_users()
        client.log_user("jdoe")
        client.upload_and_integrate()

        expected_empty_response = {
            'data': [],
            'error': False,
            'errorMessage': ""
        }

        client.log_user("jsmith")
        response = client.client.get('/api/data/AT3G10490')

        assert response.status_code == 200
        assert response.json == expected_empty_response

    def test_public_access(self, client):
        """test the /data/<uri> route for public and non public uris"""
        client.create_two_users()
        client.log_user("jdoe")
        client.upload_file("test-data/transcripts.tsv")

        client.integrate_file({
            "id": 1,
            "columns_type": ["start_entity", "label", "category", "text", "reference", "start", "end", "category", "strand", "text", "text", "date"]
        }, public=True)

        with open("tests/results/data_public.json", "r") as file:
            file_content = file.read()
        expected = json.loads(file_content)

        client.logout()
        response = client.client.get('/api/data/AT3G10490')

        assert response.status_code == 200
        assert self.equal_objects(response.json, expected)
