from . import AskomicsTestCase


class TestApiOntology(AskomicsTestCase):
    """Test AskOmics API /api/ontology/<someting>"""

    def test_local_autocompletion(self, client):
        """test /api/ontology/AGRO/autocomplete route"""
        client.create_two_users()
        client.log_user("jdoe")

        client.create_ontology()

        query = "blabla"
        response = client.client.get('/api/ontology/AGRO/autocomplete?q={}'.format(query))

        assert response.status_code == 200
        assert len(response.json["results"]) == 0
        assert response.json["results"] == []

        query = ""
        response = client.client.get('/api/ontology/AGRO/autocomplete?q={}'.format(query))

        expected = [
            "desuckering",
            "irrigation water source role",
            "irrigation water quantity",
            "reduced tillage process",
            "laser land levelling process",
            "chemical pest control process",
            "no-till",
            "puddling process",
            "mulch-till",
            "ridge-till",
            "strip-till",
            "aerial application"
        ]

        assert response.status_code == 200
        assert len(response.json["results"]) == 12

        # SPARQL order is not reliable, so we make sure to return everything
        # If it fails, skip this
        assert self.equal_objects(response.json["results"], expected)

        query = "irrigation"
        response = client.client.get('/api/ontology/AGRO/autocomplete?q={}'.format(query))

        expected = [
            "irrigation water source role",
            "irrigation water quantity"
        ]

        assert response.status_code == 200
        assert len(response.json["results"]) == 2
        assert self.equal_objects(response.json["results"], expected)
