import json

from . import AskomicsTestCase


class TestApiResults(AskomicsTestCase):
    """Test AskOmics API /api/results/<something>"""

    def test_get_results_anon(self, client):
        """test /api/results route"""
        client.create_two_users()
        client.log_user("jdoe")
        client.upload_and_integrate(public=True)
        client.logout()

        response = client.client.get('/api/results')
        assert response.status_code == 401
        assert response.json == {
            "error": True,
            "errorMessage": "Login required",
        }

        client.set_config("askomics", "anonymous_query", "true")
        response = client.client.get('/api/results')

        assert response.status_code == 200
        assert response.json == {'error': False, 'errorMessage': '', 'files': [], 'triplestoreMaxRows': 10000}

        # Need to force a session to create a result
        client.log_anon()
        result_info = client.create_result()
        client.logout()

        response = client.client.get('/api/results')

        with open("tests/results/results.json", "r") as file:
            file_content = file.read()
        raw_results = file_content.replace("###START###", str(result_info["start"]))
        raw_results = raw_results.replace("###END###", str(result_info["end"]))
        raw_results = raw_results.replace("###EXECTIME###", str(int(result_info["end"] - result_info["start"])))
        raw_results = raw_results.replace("###ID###", str(result_info["id"]))
        raw_results = raw_results.replace("###PATH###", str(result_info["path"]))
        raw_results = raw_results.replace("###SIZE###", str(result_info["size"]))
        raw_results = raw_results.replace("###PUBLIC###", str(0))
        raw_results = raw_results.replace("###TEMPLATE###", str(0))
        raw_results = raw_results.replace("###FORM###", str(0))
        raw_results = raw_results.replace("###HAS_FORM_ATTR###", str(0))
        raw_results = raw_results.replace("###DESC###", "Query")

        expected = json.loads(raw_results)

        assert response.status_code == 200
        assert response.json == expected

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
        raw_results = raw_results.replace("###EXECTIME###", str(int(result_info["end"] - result_info["start"])))
        raw_results = raw_results.replace("###ID###", str(result_info["id"]))
        raw_results = raw_results.replace("###PATH###", str(result_info["path"]))
        raw_results = raw_results.replace("###SIZE###", str(result_info["size"]))
        raw_results = raw_results.replace("###PUBLIC###", str(0))
        raw_results = raw_results.replace("###TEMPLATE###", str(0))
        raw_results = raw_results.replace("###FORM###", str(0))
        raw_results = raw_results.replace("###HAS_FORM_ATTR###", str(0))
        raw_results = raw_results.replace("###DESC###", "Query")

        expected = json.loads(raw_results)

        assert response.status_code == 200
        assert response.json == expected

    def test_get_results_form(self, client):
        """test /api/results route"""
        client.create_two_users()
        client.log_user("jdoe")
        client.upload_and_integrate()

        response = client.client.get('/api/results')

        assert response.status_code == 200
        assert response.json == {'error': False, 'errorMessage': '', 'files': [], 'triplestoreMaxRows': 10000}

        result_info = client.create_result(has_form=True)

        response = client.client.get('/api/results')

        with open("tests/results/results_form.json", "r") as file:
            file_content = file.read()
        raw_results = file_content.replace("###START###", str(result_info["start"]))
        raw_results = raw_results.replace("###END###", str(result_info["end"]))
        raw_results = raw_results.replace("###EXECTIME###", str(int(result_info["end"] - result_info["start"])))
        raw_results = raw_results.replace("###ID###", str(result_info["id"]))
        raw_results = raw_results.replace("###PATH###", str(result_info["path"]))
        raw_results = raw_results.replace("###SIZE###", str(result_info["size"]))
        raw_results = raw_results.replace("###PUBLIC###", str(0))
        raw_results = raw_results.replace("###TEMPLATE###", str(0))
        raw_results = raw_results.replace("###FORM###", str(0))
        raw_results = raw_results.replace("###HAS_FORM_ATTR###", str(1))
        raw_results = raw_results.replace("###DESC###", "Query")

        expected = json.loads(raw_results)

        assert response.status_code == 200
        assert self.equal_objects(response.json, expected)

    def test_get_results_form_non_admin(self, client):
        """test /api/results route"""
        client.create_two_users()
        client.log_user("jsmith")
        client.upload_and_integrate()

        response = client.client.get('/api/results')

        assert response.status_code == 200
        assert response.json == {'error': False, 'errorMessage': '', 'files': [], 'triplestoreMaxRows': 10000}

        result_info = client.create_result(has_form=True)

        response = client.client.get('/api/results')

        with open("tests/results/results_form.json", "r") as file:
            file_content = file.read()
        raw_results = file_content.replace("###START###", str(result_info["start"]))
        raw_results = raw_results.replace("###END###", str(result_info["end"]))
        raw_results = raw_results.replace("###EXECTIME###", str(int(result_info["end"] - result_info["start"])))
        raw_results = raw_results.replace("###ID###", str(result_info["id"]))
        raw_results = raw_results.replace("###PATH###", str(result_info["path"]))
        raw_results = raw_results.replace("###SIZE###", str(result_info["size"]))
        raw_results = raw_results.replace("###PUBLIC###", str(0))
        raw_results = raw_results.replace("###TEMPLATE###", str(0))
        raw_results = raw_results.replace("###FORM###", str(0))
        raw_results = raw_results.replace("###HAS_FORM_ATTR###", str(0))
        raw_results = raw_results.replace("###DESC###", "Query")

        expected = json.loads(raw_results)

        assert response.status_code == 200
        assert self.equal_objects(response.json, expected)

    def test_get_preview_anon(self, client):
        """test /api/results/preview route"""
        client.create_two_users()
        client.log_user("jdoe")
        client.upload_and_integrate(public=True)

        client.logout()
        client.set_config("askomics", "anonymous_query", "true")

        # Need to force a session to create a result
        client.log_anon()
        result_info = client.create_result()
        client.logout()

        data = {
            "fileId": result_info["id"]
        }

        with open("tests/results/preview.json", "r") as file:
            file_content = file.read()
        expected = json.loads(file_content)

        response = client.client.post('/api/results/preview', json=data)

        assert response.status_code == 200
        assert self.equal_objects(response.json, expected)

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

        assert response.status_code == 200
        assert self.equal_objects(response.json, expected)

    def test_get_graph_and_sparql_query(self, client):
        """test /api/results/getquery route"""
        client.create_two_users()
        client.log_user("jdoe")
        info = client.upload_and_integrate()
        result_info = client.create_result()

        data = {"fileId": result_info["id"]}

        with open("tests/results/sparql_and_graph.json", "r") as file:
            content = file.read()
        content = content.replace("###TRANSCRIPTS_TIMESTAMP###", str(info["transcripts"]["timestamp"]))
        content = content.replace("###QTL_TIMESTAMP###", str(info["qtl"]["timestamp"]))
        content = content.replace("###DE_TIMESTAMP###", str(info["de"]["timestamp"]))
        content = content.replace("###GFF_TIMESTAMP###", str(info["gff"]["timestamp"]))
        content = content.replace("###BED_TIMESTAMP###", str(info["bed"]["timestamp"]))
        content = content.replace("###LOCAL_ENDPOINT###", str(client.get_config("federation", "local_endpoint")))
        content = content.replace("###SIZE###", str(client.get_size_occupied_by_user()))
        expected = json.loads(content)

        response = client.client.post("/api/results/getquery", json=data)
        print(json.dumps(response.json, indent=2))

        assert response.status_code == 200
        assert self.equal_objects(response.json, expected)

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

    def test_download_anon(self, client):
        """test /api/results/download route"""
        client.create_two_users()
        client.log_user("jdoe")
        client.upload_and_integrate()
        client.logout()
        client.set_config("askomics", "anonymous_query", "true")

        # Need to force a session to create a result
        client.log_anon()
        result_info = client.create_result()
        client.logout()

        data = {
            "fileId": result_info["id"]
        }

        response = client.client.post('/api/results/download', json=data)

        assert response.status_code == 200

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
        info = client.upload_and_integrate()
        result_info = client.create_result()

        data = {
            "fileId": result_info["id"]
        }

        response = client.client.post("/api/results/sparqlquery", json=data)

        with open('tests/results/sparql_query.json') as file:
            content = file.read()
        content = content.replace("###TRANSCRIPTS_TIMESTAMP###", str(info["transcripts"]["timestamp"]))
        content = content.replace("###QTL_TIMESTAMP###", str(info["qtl"]["timestamp"]))
        content = content.replace("###DE_TIMESTAMP###", str(info["de"]["timestamp"]))
        content = content.replace("###GFF_TIMESTAMP###", str(info["gff"]["timestamp"]))
        content = content.replace("###BED_TIMESTAMP###", str(info["bed"]["timestamp"]))
        content = content.replace("###LOCAL_ENDPOINT###", str(client.get_config("federation", "local_endpoint")))
        content = content.replace("###SIZE###", str(client.get_size_occupied_by_user()))

        expected = json.loads(content)

        assert response.status_code == 200
        assert self.equal_objects(response.json, expected)

    def test_set_description(self, client):
        """test /api/results/description route"""
        client.create_two_users()
        client.log_user("jdoe")
        client.upload_and_integrate()
        result_info = client.create_result()

        data = {"id": result_info["id"], "newDesc": "new description"}

        with open("tests/results/results.json", "r") as file:
            file_content = file.read()
        raw_results = file_content.replace("###START###", str(result_info["start"]))
        raw_results = raw_results.replace("###END###", str(result_info["end"]))
        raw_results = raw_results.replace("###EXECTIME###", str(int(result_info["end"] - result_info["start"])))
        raw_results = raw_results.replace("###ID###", str(result_info["id"]))
        raw_results = raw_results.replace("###PATH###", str(result_info["path"]))
        raw_results = raw_results.replace("###SIZE###", str(result_info["size"]))
        raw_results = raw_results.replace("###PUBLIC###", str(0))
        raw_results = raw_results.replace("###TEMPLATE###", str(0))
        raw_results = raw_results.replace("###FORM###", str(0))
        raw_results = raw_results.replace("###HAS_FORM_ATTR###", str(0))
        raw_results = raw_results.replace("###DESC###", "new description")

        expected = json.loads(raw_results)
        del expected["triplestoreMaxRows"]

        response = client.client.post("/api/results/description", json=data)

        assert response.status_code == 200
        assert response.json == expected

    def test_template(self, client):
        """test /api/results/template route"""
        client.create_two_users()
        client.log_user("jdoe")
        client.upload_and_integrate()
        result_info = client.create_result()

        data = {"id": result_info["id"], "template": True}

        with open("tests/results/results.json", "r") as file:
            file_content = file.read()
        raw_results = file_content.replace("###START###", str(result_info["start"]))
        raw_results = raw_results.replace("###END###", str(result_info["end"]))
        raw_results = raw_results.replace("###EXECTIME###", str(int(result_info["end"] - result_info["start"])))
        raw_results = raw_results.replace("###ID###", str(result_info["id"]))
        raw_results = raw_results.replace("###PATH###", str(result_info["path"]))
        raw_results = raw_results.replace("###SIZE###", str(result_info["size"]))
        raw_results = raw_results.replace("###PUBLIC###", str(0))
        raw_results = raw_results.replace("###TEMPLATE###", str(1))
        raw_results = raw_results.replace("###FORM###", str(0))
        raw_results = raw_results.replace("###HAS_FORM_ATTR###", str(0))
        raw_results = raw_results.replace("###DESC###", "Query")

        expected = json.loads(raw_results)
        del expected["triplestoreMaxRows"]

        response = client.client.post("/api/results/template", json=data)

        assert response.status_code == 200
        assert response.json == expected

        # untemplate a public result => unpublic it
        data_public = {"id": result_info["id"], "public": True}
        data_template = {"id": result_info["id"], "template": False}

        with open("tests/results/results.json", "r") as file:
            file_content = file.read()
        raw_results = file_content.replace("###START###", str(result_info["start"]))
        raw_results = raw_results.replace("###END###", str(result_info["end"]))
        raw_results = raw_results.replace("###EXECTIME###", str(int(result_info["end"] - result_info["start"])))
        raw_results = raw_results.replace("###ID###", str(result_info["id"]))
        raw_results = raw_results.replace("###PATH###", str(result_info["path"]))
        raw_results = raw_results.replace("###SIZE###", str(result_info["size"]))
        raw_results = raw_results.replace("###PUBLIC###", str(0))
        raw_results = raw_results.replace("###TEMPLATE###", str(0))
        raw_results = raw_results.replace("###FORM###", str(0))
        raw_results = raw_results.replace("###HAS_FORM_ATTR###", str(0))
        raw_results = raw_results.replace("###DESC###", "Query")

        expected = json.loads(raw_results)
        del expected["triplestoreMaxRows"]

        client.client.post("/api/results/public", json=data_public)
        response = client.client.post("/api/results/template", json=data_template)

        assert response.status_code == 200
        assert response.json == expected

    def test_form(self, client):
        """test /api/results/form route"""
        client.create_two_users()
        client.log_user("jdoe")
        client.upload_and_integrate()
        result_info = client.create_result(has_form=True)

        data = {"id": result_info["id"], "form": True}

        with open("tests/results/results_form.json", "r") as file:
            file_content = file.read()
        raw_results = file_content.replace("###START###", str(result_info["start"]))
        raw_results = raw_results.replace("###END###", str(result_info["end"]))
        raw_results = raw_results.replace("###EXECTIME###", str(int(result_info["end"] - result_info["start"])))
        raw_results = raw_results.replace("###ID###", str(result_info["id"]))
        raw_results = raw_results.replace("###PATH###", str(result_info["path"]))
        raw_results = raw_results.replace("###SIZE###", str(result_info["size"]))
        raw_results = raw_results.replace("###PUBLIC###", str(0))
        raw_results = raw_results.replace("###TEMPLATE###", str(0))
        raw_results = raw_results.replace("###FORM###", str(1))
        raw_results = raw_results.replace("###HAS_FORM_ATTR###", str(1))
        raw_results = raw_results.replace("###DESC###", "Query")

        expected = json.loads(raw_results)
        del expected["triplestoreMaxRows"]

        response = client.client.post("/api/results/form", json=data)

        assert response.status_code == 200
        assert self.equal_objects(response.json, expected)

        # unform a public result => unpublic it
        data_public = {"id": result_info["id"], "public": True}
        data_form = {"id": result_info["id"], "form": False}

        with open("tests/results/results_form.json", "r") as file:
            file_content = file.read()
        raw_results = file_content.replace("###START###", str(result_info["start"]))
        raw_results = raw_results.replace("###END###", str(result_info["end"]))
        raw_results = raw_results.replace("###EXECTIME###", str(int(result_info["end"] - result_info["start"])))
        raw_results = raw_results.replace("###ID###", str(result_info["id"]))
        raw_results = raw_results.replace("###PATH###", str(result_info["path"]))
        raw_results = raw_results.replace("###SIZE###", str(result_info["size"]))
        raw_results = raw_results.replace("###PUBLIC###", str(0))
        raw_results = raw_results.replace("###TEMPLATE###", str(0))
        raw_results = raw_results.replace("###FORM###", str(0))
        raw_results = raw_results.replace("###HAS_FORM_ATTR###", str(1))
        raw_results = raw_results.replace("###DESC###", "Query")

        expected = json.loads(raw_results)
        del expected["triplestoreMaxRows"]

        client.client.post("/api/results/public", json=data_public)
        response = client.client.post("/api/results/form", json=data_form)

        assert response.status_code == 200
        assert self.equal_objects(response.json, expected)

        # If template is on and form is toggled, un-toggle template
        data_template = {"id": result_info["id"], "template": True}
        client.client.post("/api/results/template", json=data_template)
        response = client.client.post("/api/results/form", json=data)

        with open("tests/results/results_form.json", "r") as file:
            file_content = file.read()
        raw_results = file_content.replace("###START###", str(result_info["start"]))
        raw_results = raw_results.replace("###END###", str(result_info["end"]))
        raw_results = raw_results.replace("###EXECTIME###", str(int(result_info["end"] - result_info["start"])))
        raw_results = raw_results.replace("###ID###", str(result_info["id"]))
        raw_results = raw_results.replace("###PATH###", str(result_info["path"]))
        raw_results = raw_results.replace("###SIZE###", str(result_info["size"]))
        raw_results = raw_results.replace("###PUBLIC###", str(0))
        raw_results = raw_results.replace("###TEMPLATE###", str(0))
        raw_results = raw_results.replace("###FORM###", str(1))
        raw_results = raw_results.replace("###HAS_FORM_ATTR###", str(1))
        raw_results = raw_results.replace("###DESC###", "Query")

        expected = json.loads(raw_results)
        del expected["triplestoreMaxRows"]

        assert response.status_code == 200
        assert self.equal_objects(response.json, expected)

    def test_form_no_attr(self, client):
        """test /api/results/form route"""
        client.create_two_users()
        client.log_user("jdoe")
        client.upload_and_integrate()
        result_info = client.create_result()

        data = {"id": result_info["id"], "form": True}
        response = client.client.post("/api/results/form", json=data)

        expected = {
            'files': [],
            'error': True,
            'errorMessage': 'Failed to create form template query: \nThis query does not has any form template attribute'
        }

        assert response.status_code == 500
        assert response.json == expected

    def test_form_non_admin(self, client):
        """test /api/results/form route"""
        client.create_two_users()
        client.log_user("jsmith")
        client.upload_and_integrate()
        result_info = client.create_result(has_form=True)

        data = {"id": result_info["id"], "form": True}

        response = client.client.post("/api/results/form", json=data)

        assert response.status_code == 401

    def test_publish(self, client):
        """test /api/results/publish route"""
        client.create_two_users()
        client.log_user("jdoe")
        client.upload_and_integrate()
        result_info = client.create_result()

        data = {"id": result_info["id"], "public": True}

        with open("tests/results/results.json", "r") as file:
            file_content = file.read()
        raw_results = file_content.replace("###START###", str(result_info["start"]))
        raw_results = raw_results.replace("###END###", str(result_info["end"]))
        raw_results = raw_results.replace("###EXECTIME###", str(int(result_info["end"] - result_info["start"])))
        raw_results = raw_results.replace("###ID###", str(result_info["id"]))
        raw_results = raw_results.replace("###PATH###", str(result_info["path"]))
        raw_results = raw_results.replace("###SIZE###", str(result_info["size"]))
        raw_results = raw_results.replace("###PUBLIC###", str(1))
        raw_results = raw_results.replace("###TEMPLATE###", str(1))
        raw_results = raw_results.replace("###FORM###", str(0))
        raw_results = raw_results.replace("###HAS_FORM_ATTR###", str(0))
        raw_results = raw_results.replace("###DESC###", "Query")

        expected = json.loads(raw_results)
        del expected["triplestoreMaxRows"]

        response = client.client.post("/api/results/publish", json=data)

        assert response.status_code == 200
        assert response.json == expected

        data = {"id": result_info["id"], "public": False}

        with open("tests/results/results.json", "r") as file:
            file_content = file.read()
        raw_results = file_content.replace("###START###", str(result_info["start"]))
        raw_results = raw_results.replace("###END###", str(result_info["end"]))
        raw_results = raw_results.replace("###EXECTIME###", str(int(result_info["end"] - result_info["start"])))
        raw_results = raw_results.replace("###ID###", str(result_info["id"]))
        raw_results = raw_results.replace("###PATH###", str(result_info["path"]))
        raw_results = raw_results.replace("###SIZE###", str(result_info["size"]))
        raw_results = raw_results.replace("###PUBLIC###", str(0))
        raw_results = raw_results.replace("###TEMPLATE###", str(1))
        raw_results = raw_results.replace("###FORM###", str(0))
        raw_results = raw_results.replace("###HAS_FORM_ATTR###", str(0))
        raw_results = raw_results.replace("###DESC###", "Query")

        expected = json.loads(raw_results)
        del expected["triplestoreMaxRows"]

        response = client.client.post("/api/results/publish", json=data)

        assert response.status_code == 200
        assert response.json == expected

    def test_update_form(self, client):
        """test /api/results/save_form route"""
        client.create_two_users()
        client.log_user("jdoe")
        client.upload_and_integrate()
        result_info = client.create_result(has_form=True)

        with open("tests/data/graphState_simple_query_form_modified.json", "r") as file:
            file_content = file.read()
        body = json.loads(file_content)
        data = {"formId": result_info["id"], "graphState": body}

        response = client.client.post("/api/results/save_form", json=data)

        assert response.status_code == 200

        response = client.client.get('/api/results')
        assert response.status_code == 200

        res = json.loads(response.json["files"][0]["graphState"])

        assert self.equal_objects(res, body)

        client.log_user("jsmith")
        response = client.client.post("/api/results/save_form", json=data)

        assert response.status_code == 401

    def test_send2galaxy(self, client):
        """test /api/results/send2galaxy route"""
        client.create_two_users()
        client.log_user("jdoe")
        client.upload_and_integrate()
        client.init_galaxy()
        result_info = client.create_result()

        data = {"fileId": result_info["id"], "fileToSend": "result"}

        response = client.client.post("/api/results/send2galaxy", json=data)

        assert response.status_code == 200
        assert response.json == {
            'error': False,
            'errorMessage': ''
        }
