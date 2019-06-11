import unittest
import json

from . import AskomicsTestCase


class TestApiResults(AskomicsTestCase):
    """Test AskOmics API /api/results/<something>"""

    def test_get_results(self, client_logged_as_jdoe_with_data_and_result):
        """test /api/results route"""
        case = unittest.TestCase()

        response = client_logged_as_jdoe_with_data_and_result.get('/api/results')
        result_info = client_logged_as_jdoe_with_data_and_result.result_info

        assert response.status_code == 200
        case.assertCountEqual(response.json, {
            'error': False,
            'errorMessage': '',
            'files': [{
                'end': result_info["end"],
                'errorMessage': '',
                'graphState': 'null',
                'id': 1,
                'path': result_info["path"],
                'start': result_info["start"],
                'status': 'success'
            }],
            'triplestoreMaxRows': 10000
        })

    def test_get_preview(self, client_logged_as_jdoe_with_data_and_result):
        """test /api/results/preview route"""
        case = unittest.TestCase()

        result_info = client_logged_as_jdoe_with_data_and_result.result_info

        data = {
            "fileId": result_info["id"]
        }

        response = client_logged_as_jdoe_with_data_and_result.post('/api/results/preview', json=data)

        assert response.status_code == 200
        case.assertCountEqual(response.json, {
            'error': False,
            'errorMessage': '',
            'header': ['Gene1_Label'],
            'id': 1,
            'preview': [{
                'Gene1_Label': 'AT001'
            }, {
                'Gene1_Label': 'AT001'
            }, {
                'Gene1_Label': 'AT002'
            }, {
                'Gene1_Label': 'AT002'
            }, {
                'Gene1_Label': 'AT003'
            }, {
                'Gene1_Label': 'AT003'
            }, {
                'Gene1_Label': 'AT004'
            }, {
                'Gene1_Label': 'AT004'
            }, {
                'Gene1_Label': 'AT005'
            }, {
                'Gene1_Label': 'AT005'
            }, {
                'Gene1_Label': 'BN001'
            }, {
                'Gene1_Label': 'BN001'
            }, {
                'Gene1_Label': 'BN002'
            }, {
                'Gene1_Label': 'BN002'
            }, {
                'Gene1_Label': 'BN003'
            }, {
                'Gene1_Label': 'BN003'
            }]
        })

    def test_get_graph_state(self, client_logged_as_jdoe_with_data_and_result):
        """test /api/results/graphstate"""
        case = unittest.TestCase()

        result_info = client_logged_as_jdoe_with_data_and_result.result_info

        data = {
            "fileId": result_info["id"]
        }

        response = client_logged_as_jdoe_with_data_and_result.post('/api/results/graphstate', json=data)

        with open('tests/data/graphstate.json') as file:
            expected_json = json.loads(file.read())

        assert response.status_code == 200
        case.assertCountEqual(response.json, expected_json)

    def test_download_result(self, client_logged_as_jdoe_with_data_and_result):
        """test /api/results/download route"""
        result_info = client_logged_as_jdoe_with_data_and_result.result_info

        data = {
            "fileId": result_info["id"]
        }

        response = client_logged_as_jdoe_with_data_and_result.post('/api/results/download', json=data)

        assert response.status_code == 200

    def test_delete_result(self, client_logged_as_jdoe_with_data_and_result):
        """test .api/results/delete route"""
        result_info = client_logged_as_jdoe_with_data_and_result.result_info

        data = {
            "filesIdToDelete": [result_info["id"], ]
        }

        response = client_logged_as_jdoe_with_data_and_result.post('/api/results/delete', json=data)

        assert response.status_code == 200
        assert response.json == {
            "error": False,
            "errorMessage": "",
            "remainingFiles": []
        }

    def test_get_sparql_query(self, client_logged_as_jdoe_with_data_and_result):
        """test /api/results/sparqlquery route"""
        result_info = client_logged_as_jdoe_with_data_and_result.result_info

        data = {
            "fileId": result_info["id"]
        }

        response = client_logged_as_jdoe_with_data_and_result.post("/api/results/sparqlquery", json=data)

        with open('tests/results/query.sparql') as file:
            content = file.read()

        assert response.status_code == 200
        assert response.json == {
            'error': False,
            'errorMessage': '',
            'query': content
        }
