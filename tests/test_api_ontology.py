import json

from . import AskomicsTestCase


class TestApiOntology(AskomicsTestCase):
    """Test AskOmics API /api/ontology/<someting>"""

    def test_local_autocompletion(self, client):
        """test /api/ontology/AGRO/autocomplete route"""
        client.create_two_users()
        client.log_user("jdoe")

        client.create_ontology()

        query = ""
        response = client.client.get('/api/ontology/AGRO/autocomplete?q={}'.format(query))

        print(response.json)
        assert response.status_code == 200
        assert len(response.json["results"]) == 10
