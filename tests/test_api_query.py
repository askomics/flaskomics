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

        with open("tests/results/startpoints.json") as file:
            file_content = file.read()
        raw_startpoints = file_content.replace("###TRANSCRIPTS_TIMESTAMP###", str(info["transcripts"]["timestamp"]))
        raw_startpoints = raw_startpoints.replace("###QTL_TIMESTAMP###", str(info["qtl"]["timestamp"]))
        raw_startpoints = raw_startpoints.replace("###DE_TIMESTAMP###", str(info["de"]["timestamp"]))
        raw_startpoints = raw_startpoints.replace("###GFF_TIMESTAMP###", str(info["gff"]["timestamp"]))
        raw_startpoints = raw_startpoints.replace("###BED_TIMESTAMP###", str(info["bed"]["timestamp"]))
        expected = json.loads(raw_startpoints)

        assert response.status_code == 200
        assert self.equal_objects(response.json, expected)

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
        raw_abstraction = raw_abstraction.replace("###GFF_TIMESTAMP###", str(info["gff"]["timestamp"]))
        raw_abstraction = raw_abstraction.replace("###BED_TIMESTAMP###", str(info["bed"]["timestamp"]))
        raw_abstraction = raw_abstraction.replace("###SIZE###", str(client.get_size_occupied_by_user()))
        expected = json.loads(raw_abstraction)

        response = client.client.get('/api/query/abstraction')

        assert response.status_code == 200
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
        expected = {'error': False, 'errorMessage': '', 'headerPreview': ['transcript1_Label'], 'resultsPreview': [{'transcript1_Label': 'AT1G57800'}, {'transcript1_Label': 'AT5G35334'}, {'transcript1_Label': 'AT3G10460'}, {'transcript1_Label': 'AT1G49500'}, {'transcript1_Label': 'AT3G10490'}, {'transcript1_Label': 'AT3G51470'}, {'transcript1_Label': 'AT5G41905'}, {'transcript1_Label': 'AT1G33615'}, {'transcript1_Label': 'AT3G22640'}, {'transcript1_Label': 'AT3G13660'}, {'transcript1_Label': 'AT1G01010.1'}]}

        print(response.json)

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
