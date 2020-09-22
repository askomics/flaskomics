from . import AskomicsTestCase


class TestApiAdmin(AskomicsTestCase):
    """Test AskOmics API /api/admin/<someting>"""

    def test_get_users(self, client):
        """test the /api/admin/getusers route"""
        client.create_two_users()
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
                'admin': False,
                'apikey': apikey,
                'blocked': False,
                'email': 'jwick@askomics.org',
                'fname': 'John',
                'galaxy': None,
                'id': 3,
                'ldap': False,
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
