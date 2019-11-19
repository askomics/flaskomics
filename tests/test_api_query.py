import json

from . import AskomicsTestCase


class TestApiStartpoints(AskomicsTestCase):
    """Test AskOmics API /api/startpoints/<someting>"""

    def test_startpoints(self, client):
        """Test /api/startpoints route"""
        client.create_two_users()
        client.log_user("jdoe")
        info = client.upload_and_integrate()

        response = client.client.get('/api/query/startpoints')

        sp1 = {
            'entity': 'http://www.semanticweb.org/user/ontologies/2018/1#transcript',
            'entity_label': 'transcript',
            'graphs': [{
                'creator': 'jdoe',
                'public': 'false',
                'uri': 'urn:sparql:askomics_test:1_jdoe:transcripts.tsv_{}'.format(info["transcripts"]["timestamp"])
            }],
            'private': True,
            'public': False
        }

        sp2 = {
            'entity': 'http://www.semanticweb.org/user/ontologies/2018/1#DifferentialExpression',
            'entity_label': 'DifferentialExpression',
            'graphs': [{
                'creator': 'jdoe',
                'public': 'false',
                'uri': 'urn:sparql:askomics_test:1_jdoe:de.tsv_{}'.format(info["de"]["timestamp"])
            }],
            'private': True,
            'public': False
        }

        sp3 = {
            'entity': 'http://www.semanticweb.org/user/ontologies/2018/1#QTL',
            'entity_label': 'QTL',
            'graphs': [{
                'creator': 'jdoe',
                'public': 'false',
                'uri': 'urn:sparql:askomics_test:1_jdoe:qtl.tsv_{}'.format(info["qtl"]["timestamp"])
            }],
            'private': True,
            'public': False
        }

        assert response.status_code == 200
        assert len(response.json) == 4

        assert not response.json["error"]
        assert response.json["errorMessage"] == ''
        assert response.json["publicQueries"] == []
        assert len(response.json["startpoints"]) == 3

        assert sp1 in response.json["startpoints"]
        assert sp2 in response.json["startpoints"]
        assert sp3 in response.json["startpoints"]

    def test_get_abstraction(self, client):
        """Test /api/startpoints/abstraction route"""
        client.create_two_users()
        client.log_user("jdoe")
        info = client.upload_and_integrate()

        with open("tests/results/abstraction.json") as file:
            file_content = file.read()
        raw_abstraction = file_content.replace("###TRANSCRIPTS_TIMESTAMP###", str(info["transcripts"]["timestamp"]))
        raw_abstraction = raw_abstraction.replace("###QTL_TIMESTAMP###", str(info["qtl"]["timestamp"]))
        raw_abstraction = raw_abstraction.replace("###DE_TIMESTAMP###", str(info["de"]["timestamp"]))
        raw_abstraction = raw_abstraction.replace("###SIZE###", str(client.get_size_occupied_by_user()))
        expected = json.loads(raw_abstraction)

        response = client.client.get('/api/query/abstraction')

        print(json.dumps(response.json))

        assert response.status_code == 200
        assert len(response.json) == 4
        assert not response.json["error"]
        assert response.json["errorMessage"] == ""
        assert type(response.json["diskSpace"]) == int

        assert len(response.json["abstraction"]) == 3
        assert len(response.json["abstraction"]["attributes"]) == 21

        assert self.equal_objects(response.json, expected)

    def test_get_preview(self, client):
        """Test /api/query/preview route"""
        client.create_two_users()
        client.log_user("jdoe")
        client.upload_and_integrate()

        with open("tests/data/graphState_simple_query.json") as file:
            file_content = file.read()

        json_query = json.loads(file_content)
        data = {
            "graphState": json_query,
        }

        response = client.client.post('/api/query/preview', json=data)
        expected = {"error": False, "errorMessage": "", "headerPreview": ["transcript1_Label"], "resultsPreview": [{"transcript1_Label": "AT5G41905"}, {"transcript1_Label": "AT1G57800"}, {"transcript1_Label": "AT3G13660"}, {"transcript1_Label": "AT3G51470"}, {"transcript1_Label": "AT1G33615"}, {"transcript1_Label": "AT3G10490"}, {"transcript1_Label": "AT1G49500"}, {"transcript1_Label": "AT3G22640"}, {"transcript1_Label": "AT3G10460"}, {"transcript1_Label": "AT5G35334"}]}

        assert response.status_code == 200
        assert self.equal_objects(response.json, expected)

    def test_save_result(self, client):
        """Test /api/query/save_result route"""
        client.create_two_users()
        client.log_user("jdoe")
        client.upload_and_integrate()

        with open("tests/data/graphState_simple_query.json", "r") as file:
            file_content = file.read()

        json_query = json.loads(file_content)

        data = {
            "graphState": json_query,
        }

        response = client.client.post('/api/query/save_result', json=data)
        assert response.status_code == 200
        assert not response.json["error"]
        assert response.json["errorMessage"] == ''
