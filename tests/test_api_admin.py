import json

from . import AskomicsTestCase


class TestApiAdmin(AskomicsTestCase):
    """Test AskOmics API /api/admin/<someting>"""

    def test_get_users(self, client):
        """test the /api/admin/getusers route"""
        client.create_two_users()

        client.log_user("jsmith")
        response = client.client.get('/api/admin/getusers')
        assert response.status_code == 401

        client.log_user("jdoe")
        client.upload()

        response = client.client.get('/api/admin/getusers')
        expected = {
            'error': False,
            'errorMessage': '',
            'users': [{
                'admin': 1,
                'blocked': 0,
                'email': 'jdoe@askomics.org',
                'fname': 'John',
                'galaxy': {"url": "http://localhost:8081", "apikey": "fakekey"},
                'last_action': None,
                'ldap': 0,
                'lname': 'Doe',
                'quota': 0,
                'username': 'jdoe'
            }, {
                'admin': 0,
                'blocked': 0,
                'email': 'jsmith@askomics.org',
                'fname': 'Jane',
                'galaxy': None,
                'last_action': None,
                'ldap': 0,
                'lname': 'Smith',
                'quota': 0,
                'username': 'jsmith'
            }]
        }

        assert response.status_code == 200
        assert response.json == expected

    def test_get_files(self, client):
        """test the /api/admin/getfiles route"""
        client.create_two_users()
        client.log_user("jsmith")

        response = client.client.get('/api/admin/getfiles')
        assert response.status_code == 401

        info = client.upload()
        client.log_user("jdoe")

        response = client.client.get('/api/admin/getfiles')
        expected = {
            'error': False,
            'errorMessage': '',
            'files': [{
                'date': info["transcripts"]["upload"]["file_date"],
                'id': 1,
                'name': 'transcripts.tsv',
                'size': 2264,
                'type': 'csv/tsv',
                'user': 'jsmith',
                'status': 'available'

            }, {
                'date': info["de"]["upload"]["file_date"],
                'id': 2,
                'name': 'de.tsv',
                'size': 819,
                'type': 'csv/tsv',
                'user': 'jsmith',
                'status': 'available'

            }, {
                'date': info["qtl"]["upload"]["file_date"],
                'id': 3,
                'name': 'qtl.tsv',
                'size': 99,
                'type': 'csv/tsv',
                'user': 'jsmith',
                'status': 'available'

            }, {
                'date': info["gene"]["upload"]["file_date"],
                'id': 4,
                'name': 'gene.gff3',
                'size': 2555,
                'type': 'gff/gff3',
                'user': 'jsmith',
                'status': 'available'

            }, {
                'date': info["bed"]["upload"]["file_date"],
                'id': 5,
                'name': 'gene.bed',
                'size': 689,
                'type': 'bed',
                'user': 'jsmith',
                'status': 'available'
            }]
        }

        assert response.status_code == 200
        assert response.json == expected

    def test_get_datasets(self, client):
        """test the /api/admin/getdatasets route"""
        client.create_two_users()
        client.log_user("jsmith")

        response = client.client.get('/api/admin/getdatasets')
        assert response.status_code == 401

        info = client.upload_and_integrate()
        client.log_user("jdoe")

        response = client.client.get('/api/admin/getdatasets')
        expected = {
            'datasets': [{
                'end': info["transcripts"]["end"],
                'error_message': '',
                'id': 1,
                'name': 'transcripts.tsv',
                'ntriples': 0,
                'public': False,
                'start': info["transcripts"]["start"],
                'status': 'success',
                'traceback': None,
                'percent': 100.0,
                'exec_time': info["transcripts"]["end"] - info["transcripts"]["start"],
                'user': 'jsmith',
                'ontology': False
            }, {
                'end': info["de"]["end"],
                'error_message': '',
                'id': 2,
                'name': 'de.tsv',
                'ntriples': 0,
                'public': False,
                'start': info["de"]["start"],
                'status': 'success',
                'traceback': None,
                'percent': 100.0,
                'exec_time': info["de"]["end"] - info["de"]["start"],
                'user': 'jsmith',
                'ontology': False
            }, {
                'end': info["qtl"]["end"],
                'error_message': '',
                'id': 3,
                'name': 'qtl.tsv',
                'ntriples': 0,
                'public': False,
                'start': info["qtl"]["start"],
                'status': 'success',
                'traceback': None,
                'percent': 100.0,
                'exec_time': info["qtl"]["end"] - info["qtl"]["start"],
                'user': 'jsmith',
                'ontology': False
            }, {
                'end': info["gff"]["end"],
                'error_message': '',
                'id': 4,
                'name': 'gene.gff3',
                'ntriples': 0,
                'public': False,
                'start': info["gff"]["start"],
                'status': 'success',
                'traceback': None,
                'percent': 100.0,
                'exec_time': info["gff"]["end"] - info["gff"]["start"],
                'user': 'jsmith',
                'ontology': False
            }, {
                'end': info["bed"]["end"],
                'error_message': '',
                'id': 5,
                'name': 'gene.bed',
                'ntriples': 0,
                'public': False,
                'start': info["bed"]["start"],
                'status': 'success',
                'traceback': None,
                'percent': 100.0,
                'exec_time': info["bed"]["end"] - info["bed"]["start"],
                'user': 'jsmith',
                'ontology': False
            }],
            'error': False,
            'errorMessage': ''
        }

        assert response.status_code == 200
        assert response.json == expected

    def test_get_queries(self, client):
        """test the /api/admin/getqueries route"""
        client.create_two_users()
        client.log_user("jsmith")

        response = client.client.get('/api/admin/getqueries')
        assert response.status_code == 401

        client.upload_and_integrate()
        result_info = client.create_result()
        client.publicize_result(result_info["id"], True)

        client.log_user("jdoe")

        with open("tests/results/results_admin.json", "r") as file:
            file_content = file.read()
        raw_results = file_content.replace("###START###", str(result_info["start"]))
        raw_results = raw_results.replace("###END###", str(result_info["end"]))
        raw_results = raw_results.replace("###EXECTIME###", str(int(result_info["end"] - result_info["start"])))
        raw_results = raw_results.replace("###ID###", str(result_info["id"]))
        raw_results = raw_results.replace("###SIZE###", str(result_info["size"]))
        raw_results = raw_results.replace("###PUBLIC###", str(1))
        raw_results = raw_results.replace("###DESC###", "Query")
        expected = json.loads(raw_results)

        response = client.client.get('/api/admin/getqueries')
        assert response.status_code == 200
        assert response.json == expected

    def test_setadmin(self, client):
        """test the /api/admin/setadmin route"""
        client.create_two_users()
        client.log_user("jdoe")
        client.upload()

        set_jsmith_admin = {
            "username": "jsmith",
            "newAdmin": 1
        }

        response = client.client.post('/api/admin/setadmin', json=set_jsmith_admin)
        assert response.status_code == 200
        assert response.json == {'error': False, 'errorMessage': ''}

    def test_set_dataset_public(self, client):
        """test the /api/admin/getdatasets route"""
        client.create_two_users()
        client.log_user("jsmith")

        response = client.client.post('/api/admin/publicize_dataset')
        assert response.status_code == 401

        client.upload_and_integrate()
        client.log_user("jdoe")

        data = {"datasetId": 1, "newStatus": True}

        response = client.client.post('/api/admin/publicize_dataset', json=data)

        assert response.status_code == 200
        assert not response.json["error"]
        assert response.json["errorMessage"] == ''
        assert response.json["datasets"][0]["public"] is True

    def test_set_query_private(self, client):
        """test the /api/admin/publicize_query route"""
        client.create_two_users()
        client.log_user("jsmith")

        response = client.client.post('/api/admin/publicize_query')
        assert response.status_code == 401

        client.upload_and_integrate()
        result_info = client.create_result()
        client.publicize_result(result_info["id"], True)

        client.log_user("jdoe")

        data = {"queryId": result_info["id"], "newStatus": False}
        response = client.client.post('/api/admin/publicize_query', json=data)

        expected = {
            'error': False,
            'errorMessage': '',
            'queries': [{
                'description': 'Query',
                'end': result_info["end"],
                'execTime': int(result_info["end"] - result_info["start"]),
                'id': result_info["id"],
                'nrows': 13,
                'public': 0,
                'size': result_info["size"],
                'start': result_info["start"],
                'status': 'success',
                'user': 'jsmith'}]
        }

        assert response.status_code == 200
        assert response.json == expected

    def test_update_query_description(self, client):
        """test the /api/admin/update_description route"""
        client.create_two_users()
        client.log_user("jsmith")

        response = client.client.post('/api/admin/update_description')
        assert response.status_code == 401

        client.upload_and_integrate()
        result_info = client.create_result()
        client.publicize_result(result_info["id"], True)

        client.log_user("jdoe")
        data = {"queryId": result_info["id"], "newDesc": "MyNewDesc"}
        response = client.client.post('/api/admin/update_description', json=data)

        expected = {
            'error': False,
            'errorMessage': '',
            'queries': [{
                'description': 'MyNewDesc',
                'end': result_info["end"],
                'execTime': int(result_info["end"] - result_info["start"]),
                'id': result_info["id"],
                'nrows': 13,
                'public': 0,
                'size': result_info["size"],
                'start': result_info["start"],
                'status': 'success',
                'user': 'jsmith'}]
        }

        assert response.status_code == 200
        assert response.json == expected

    def test_setquota(self, client):
        """test the /api/admin/setadmin route"""
        client.create_two_users()
        client.log_user("jdoe")
        client.upload()

        set_quota = {
            "username": "jsmith",
            "quota": "10mb"
        }

        response = client.client.post('/api/admin/setquota', json=set_quota)
        expected = {
            'error': False,
            'errorMessage': '',
            'users': [{
                'admin': 1,
                'blocked': 0,
                'email': 'jdoe@askomics.org',
                'fname': 'John',
                'galaxy': {"url": "http://localhost:8081", "apikey": "fakekey"},
                'last_action': None,
                'ldap': 0,
                'lname': 'Doe',
                'quota': 0,
                'username': 'jdoe'
            }, {
                'admin': 0,
                'blocked': 0,
                'email': 'jsmith@askomics.org',
                'fname': 'Jane',
                'galaxy': None,
                'last_action': None,
                'ldap': 0,
                'lname': 'Smith',
                'quota': 10000000,
                'username': 'jsmith'
            }]
        }

        assert response.status_code == 200
        assert response.json == expected

    def test_setblocked(self, client):
        """test the /api/admin/setblocked route"""
        client.create_two_users()
        client.log_user("jdoe")
        client.upload()

        set_jsmith_admin = {
            "username": "jsmith",
            "newBlocked": 1
        }

        response = client.client.post('/api/admin/setblocked', json=set_jsmith_admin)
        assert response.status_code == 200
        assert response.json == {'error': False, 'errorMessage': ''}

    def test_add_user(self, client):
        """test /api/admin/adduser route"""
        client.create_two_users()
        client.log_user("jdoe")

        data = {
            "fname": "John",
            "lname": "Wick",
            "username": "jwick",
            "email": "jwick@askomics.org"
        }

        response = client.client.post("/api/admin/adduser", json=data)
        password = response.json["user"]["password"]
        apikey = response.json["user"]["apikey"]

        assert response.status_code == 200
        assert response.json == {
            'displayPassword': True,
            'error': False,
            'errorMessage': [],
            'instanceUrl': 'http://localhost:5000',
            'user': {
                'admin': 0,
                'apikey': apikey,
                'blocked': 0,
                'email': 'jwick@askomics.org',
                'fname': 'John',
                'galaxy': None,
                'id': 3,
                'ldap': 0,
                'lname': 'Wick',
                'password': password,
                'quota': 0,
                'username': 'jwick'
            }
        }

    def test_delete_user(self, client):
        """test /api/admin/delete_users route"""
        client.create_two_users()
        client.log_user("jdoe")

        data = {
            "usersToDelete": ["jsmith", "jdoe"]  # jdoe will be removed from the list and no deleted from DB
        }

        response = client.client.post("/api/admin/delete_users", json=data)

        assert response.status_code == 200
        assert response.json == {
            'error': False,
            'errorMessage': [],
            'users': [{
                'admin': 1,
                'blocked': 0,
                'email': 'jdoe@askomics.org',
                'fname': 'John',
                'galaxy': {
                    'apikey': 'fakekey',
                    'url': 'http://localhost:8081'
                },
                'last_action': None,
                'ldap': 0,
                'lname': 'Doe',
                'quota': 0,
                'username': 'jdoe'
            }]
        }

    def test_delete_files(self, client):
        """test /api/admin/delete_files route"""
        client.create_two_users()
        client.log_user("jsmith")

        response = client.client.post('/api/admin/delete_files')
        assert response.status_code == 401
        info = client.upload()
        client.log_user("jdoe")

        data = {
            "filesIdToDelete": [1, 2]
        }

        response = client.client.post('/api/admin/delete_files', json=data)
        expected = {
            'error': False,
            'errorMessage': '',
            'files': [{
                'date': info["qtl"]["upload"]["file_date"],
                'id': 3,
                'name': 'qtl.tsv',
                'size': 99,
                'type': 'csv/tsv',
                'user': 'jsmith',
                'status': 'available'

            }, {
                'date': info["gene"]["upload"]["file_date"],
                'id': 4,
                'name': 'gene.gff3',
                'size': 2555,
                'type': 'gff/gff3',
                'user': 'jsmith',
                'status': 'available'

            }, {
                'date': info["bed"]["upload"]["file_date"],
                'id': 5,
                'name': 'gene.bed',
                'size': 689,
                'type': 'bed',
                'user': 'jsmith',
                'status': 'available'
            }]
        }

        assert response.status_code == 200
        assert response.json == expected

    def test_delete_datasets(self, client):
        """test /api/admin/delete_datasets route"""
        client.create_two_users()
        client.log_user("jsmith")

        response = client.client.post('/api/admin/delete_datasets')
        assert response.status_code == 401

        client.upload_and_integrate()
        client.log_user("jdoe")

        data = {
            "datasetsIdToDelete": [1, 2, 3]
        }

        response = client.client.post('/api/admin/delete_datasets', json=data)

        assert response.status_code == 200
        assert not response.json["error"]
        assert response.json["errorMessage"] == ''
        assert response.json["datasets"][0]["status"] == "queued"
        assert response.json["datasets"][1]["status"] == "queued"
        assert response.json["datasets"][2]["status"] == "queued"

    def test_delete_queries(self, client):
        """test /api/admin/delete_queries route"""
        client.create_two_users()
        client.log_user("jsmith")

        response = client.client.post('/api/admin/delete_queries')
        assert response.status_code == 401

        client.upload_and_integrate()
        result_info = client.create_result()

        client.log_user("jdoe")

        data = {"queriesIdToDelete": result_info["id"], "newStatus": False}

        response = client.client.post('/api/admin/delete_queries', json=data)

        assert response.status_code == 200
        assert not response.json["error"]
        assert response.json["errorMessage"] == ''
        assert len(response.json["queries"]) == 0

    def test_view_custom_prefixes(self, client):
        """test /api/admin/getprefixes route"""
        client.create_two_users()
        client.log_user("jsmith")

        response = client.client.get('/api/admin/getprefixes')
        assert response.status_code == 401

        client.log_user("jdoe")

        expected_empty = {
            "error": False,
            "errorMessage": "",
            "prefixes": []
        }

        response = client.client.get('/api/admin/getprefixes')
        assert response.status_code == 200
        assert response.json == expected_empty

        client.create_prefix()

        response = client.client.get('/api/admin/getprefixes')

        expected = {
            "error": False,
            "errorMessage": "",
            "prefixes": [{
                "id": 1,
                "namespace": "http://purl.obolibrary.org/obo/",
                "prefix": "OBO"
            }]
        }

        assert response.status_code == 200
        assert response.json == expected

    def test_add_custom_prefix(self, client):
        """test /api/admin/addprefix route"""
        client.create_two_users()
        client.log_user("jsmith")

        data = {"prefix": "OBO", "namespace": "http://purl.obolibrary.org/obo/"}

        response = client.client.post('/api/admin/addprefix', json=data)
        assert response.status_code == 401

        client.log_user("jdoe")

        response = client.client.post('/api/admin/addprefix', json=data)

        expected = {
            "error": False,
            "errorMessage": "",
            "prefixes": [{
                "id": 1,
                "namespace": "http://purl.obolibrary.org/obo/",
                "prefix": "OBO"
            }]
        }

        assert response.status_code == 200
        assert response.json == expected

    def test_delete_custom_prefix(self, client):
        """test /api/admin/delete_prefixes route"""
        client.create_two_users()
        client.log_user("jsmith")

        data = {"prefixesIdToDelete": [1]}

        response = client.client.post('/api/admin/delete_prefixes', json=data)
        assert response.status_code == 401

        client.log_user("jdoe")
        client.create_prefix()

        response = client.client.post('/api/admin/delete_prefixes', json=data)

        expected = {
            "error": False,
            "errorMessage": "",
            "prefixes": []
        }

        assert response.status_code == 200
        assert response.json == expected

    def test_view_ontologies(self, client):
        """test /api/admin/getontologies route"""
        client.create_two_users()
        client.log_user("jsmith")

        response = client.client.get('/api/admin/getontologies')
        assert response.status_code == 401

        client.log_user("jdoe")

        expected_empty = {
            "error": False,
            "errorMessage": "",
            "ontologies": []
        }

        response = client.client.get('/api/admin/getontologies')
        assert response.status_code == 200
        assert response.json == expected_empty

        graph, endpoint = client.create_ontology()

        response = client.client.get('/api/admin/getontologies')

        expected = {
            "error": False,
            "errorMessage": "",
            "ontologies": [{
                "id": 1,
                "name": "AgrO ontology",
                "uri": "http://purl.obolibrary.org/obo/agro.owl",
                "short_name": "AGRO",
                "type": "local",
                "dataset_id": 1,
                "dataset_name": "agro_min.ttl",
                "graph": graph,
                "endpoint": endpoint,
                "remote_graph": None,
                "label_uri": "rdfs:label"
            }]
        }

        assert response.status_code == 200
        assert response.json == expected

    def test_add_ontology(self, client):
        """test /api/admin/addontology route"""
        client.create_two_users()
        client.log_user("jsmith")

        data = {"shortName": "AGRO", "uri": "http://purl.obolibrary.org/obo/agro.owl", "name": "AgrO ontology", "type": "local", "datasetId": 1, "labelUri": "rdfs:label"}

        response = client.client.post('/api/admin/addontology', json=data)
        assert response.status_code == 401

        client.log_user("jdoe")
        graph_data = client.upload_and_integrate_ontology()
        graph = graph_data["graph"]
        endpoint = graph_data["endpoint"]

        response = client.client.post('/api/admin/addontology', json=data)

        # Dataset is not public
        assert response.status_code == 400
        assert response.json['errorMessage'] == "Invalid dataset id"

        client.publicize_dataset(1, True)
        response = client.client.post('/api/admin/addontology', json=data)

        expected = {
            "error": False,
            "errorMessage": "",
            "ontologies": [{
                "id": 1,
                "name": "AgrO ontology",
                "uri": "http://purl.obolibrary.org/obo/agro.owl",
                "short_name": "AGRO",
                "type": "local",
                "dataset_id": 1,
                "dataset_name": "agro_min.ttl",
                "label_uri": "rdfs:label",
                "graph": graph,
                "endpoint": endpoint,
                "remote_graph": None
            }]
        }

        assert response.status_code == 200
        assert response.json == expected

    def test_delete_ontologies(self, client):
        """test /api/admin/delete_ontologies route"""
        client.create_two_users()
        client.log_user("jsmith")

        data = {"ontologiesIdToDelete": [1]}

        response = client.client.post('/api/admin/delete_ontologies', json=data)
        assert response.status_code == 401

        client.log_user("jdoe")
        client.create_ontology()

        response = client.client.post('/api/admin/delete_ontologies', json=data)

        expected = {
            "error": False,
            "errorMessage": "",
            "ontologies": []
        }

        assert response.status_code == 200
        assert response.json == expected
