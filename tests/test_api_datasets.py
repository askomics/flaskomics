from . import AskomicsTestCase


class TestApiDatasets(AskomicsTestCase):
    """Test AskOmics API /api/datasets/<someting>"""

    def test_get_datasets(self, client_logged_as_jdoe_with_data):
        """test the /api/datasets route"""
        response = client_logged_as_jdoe_with_data.get('/api/datasets')
        assert response.status_code == 200
        assert len(response.json) == 3
        assert not response.json["error"]
        assert response.json["errorMessage"] == ''
        assert len(response.json["datasets"]) == 1
        assert len(response.json["datasets"][0]) == 7
        assert response.json["datasets"][0]["id"] == 1
        assert response.json["datasets"][0]["name"] == "gene"
        assert not response.json["datasets"][0]["public"]
        assert response.json["datasets"][0]["status"] == 'success'
        assert type(response.json["datasets"][0]["start"]) == int
        assert type(response.json["datasets"][0]["end"]) == int
        assert response.json["datasets"][0]["error_message"] == ''

    def test_delete_datasets(self, client_logged_as_jdoe_with_data):
        """Test the /api/datsets/delete route"""
        data = {
            "datasetsIdToDelete": [1, ]
        }

        response = client_logged_as_jdoe_with_data.post('/api/datasets/delete', json=data)
        assert response.status_code == 200
        assert not response.json["error"]
        assert response.json["errorMessage"] == ''
        assert response.json["datasets"][0]["status"] == "deleting"
