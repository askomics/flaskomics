from . import AskomicsTestCase


class TestApiAuth(AskomicsTestCase):
    """Test AskOmics API /api/auth/<someting>"""

    def test_signup(self, client):
        """Test /api/auth/signup route"""
        ok_data = {
            "fname": "John",
            "lname": "Wick",
            "username": "jwick",
            "password": "dontkillmydog",
            "passwordconf": "dontkillmydog",
            "email": "jwick@askomics.org",
            'apikey': "0000000001",
            "galaxy": None
        }

        empty_fname_data = {
            "fname": "",
            "lname": "Wick",
            "username": "jwick",
            "password": "dontkillmydog",
            "passwordconf": "dontkillmydog",
            "email": "jwick@askomics.org",
            "galaxy": None
        }

        empty_lname_data = {
            "fname": "John",
            "lname": "",
            "username": "jwick",
            "password": "dontkillmydog",
            "passwordconf": "dontkillmydog",
            "email": "jwick@askomics.org",
            "galaxy": None
        }

        empty_password_data = {
            "fname": "John",
            "lname": "Doe",
            "username": "jwick",
            "password": "",
            "passwordconf": "",
            "email": "jwick@askomics.org",
            "galaxy": None
        }

        empty_username_data = {
            "fname": "John",
            "lname": "Wick",
            "username": "",
            "password": "dontkillmydog",
            "passwordconf": "dontkillmydog",
            "email": "jwick@askomics.org",
            "galaxy": None
        }

        unvalid_email_data = {
            "fname": "John",
            "lname": "Wick",
            "username": "jwick",
            "password": "dontkillmydog",
            "passwordconf": "dontkillmydog",
            "email": "xx",
            "galaxy": None
        }

        diff_password_data = {
            "fname": "John",
            "lname": "Wick",
            "username": "jwick",
            "password": "dontkillmydog",
            "passwordconf": "dontstillmycar",
            "email": "jwick@askomics.org",
            "galaxy": None
        }

        # fname empty
        response = client.client.post('/api/auth/signup', json=empty_fname_data)
        assert response.status_code == 200
        assert response.json == {
            'error': True,
            'errorMessage': ['First name empty'],
            'user': {}
        }

        # lname empty
        response = client.client.post('/api/auth/signup', json=empty_lname_data)
        assert response.status_code == 200
        assert response.json == {
            'error': True,
            'errorMessage': ['Last name empty'],
            'user': {}
        }

        # username empty
        response = client.client.post('/api/auth/signup', json=empty_username_data)
        assert response.status_code == 200
        assert response.json == {
            'error': True,
            'errorMessage': ['Username name empty'],
            'user': {}
        }

        # username password
        response = client.client.post('/api/auth/signup', json=empty_password_data)
        assert response.status_code == 200
        assert response.json == {
            'error': True,
            'errorMessage': ['Password empty'],
            'user': {}
        }

        # non valid email
        response = client.client.post('/api/auth/signup', json=unvalid_email_data)
        assert response.status_code == 200
        assert response.json == {
            'error': True,
            'errorMessage': ['Not a valid email'],
            'user': {}
        }

        # non valid email
        response = client.client.post('/api/auth/signup', json=diff_password_data)
        assert response.status_code == 200
        assert response.json == {
            'error': True,
            'errorMessage': ["Passwords doesn't match"],
            'user': {}
        }

        # Account creation disabled in config file
        client.set_config("askomics", "disable_account_creation", "true")
        response = client.client.post("/api/auth/signup", json=ok_data)
        assert response.status_code == 400
        assert response.json == {
            "error": True,
            "errorMessage": "Account creation is disabled",
            "user": {}
        }

        # ok inputs
        client.set_config("askomics", "disable_account_creation", "false")
        response = client.client.post('/api/auth/signup', json=ok_data)
        assert response.status_code == 200
        assert response.json == {
            'error': False,
            'errorMessage': [],
            'user': {
                'id': 1,
                'ldap': 0,
                'fname': "John",
                'lname': "Wick",
                'username': "jwick",
                'email': "jwick@askomics.org",
                'admin': 1,
                'blocked': 0,
                'quota': 0,
                'apikey': "0000000001",
                'galaxy': None
            }
        }

        # Test logged
        with client.client.session_transaction() as sess:
            assert 'user' in sess
            assert sess["user"] == {
                'id': 1,
                'ldap': 0,
                'fname': "John",
                'lname': "Wick",
                'username': "jwick",
                'email': "jwick@askomics.org",
                'admin': 1,
                'blocked': 0,
                'quota': 0,
                'apikey': "0000000001",
                'galaxy': None
            }

        # Re-insert same user
        response = client.client.post('/api/auth/signup', json=ok_data)
        assert response.status_code == 200
        assert response.json == {
            'error': True,
            'errorMessage': ["Username already registered", "Email already registered"],
            'user': {}
        }

    def test_wrong_login(self, client):
        """Test /api/auth/login route with wrong credentials"""
        inputs_wrong_username = {
            "login": "xx",
            "password": "iamjohndoe"
        }

        inputs_wrong_email = {
            "login": "xx@example.org",
            "password": "iamjohndoe"
        }

        inputs_wrong_password = {
            "login": "jdoe@askomics.org",
            "password": "xx"
        }

        client.create_two_users()

        response = client.client.post('/api/auth/login', json=inputs_wrong_username)

        assert response.status_code == 200
        assert response.json == {
            'error': True,
            'errorMessage': ["Bad login or password"],
            'user': {}
        }

        response = client.client.post('/api/auth/login', json=inputs_wrong_email)

        assert response.status_code == 200
        assert response.json == {
            'error': True,
            'errorMessage': ["Bad login or password"],
            'user': {}
        }

        response = client.client.post('/api/auth/login', json=inputs_wrong_password)

        assert response.status_code == 200
        assert response.json == {
            'error': True,
            'errorMessage': ["Bad login or password"],
            'user': {}
        }

        # Test logged
        with client.client.session_transaction() as sess:
            assert 'user' not in sess

    def test_ldap_login(self, client):
        """test /api/auth/login with ldap credentials"""
        client.set_config("askomics", "ldap_auth", "true")

        ok_inputs_email = {
            "login": "john.wick@askomics.org",
            "password": "jwick"
        }

        ok_inputs_username = {
            "login": "jwick",
            "password": "jwick"
        }

        # First login create user in DB with a new API key
        response = client.client.post('/api/auth/login', json=ok_inputs_email)
        api_key = response.json["user"]["apikey"]

        assert response.json == {
            'error': False,
            'errorMessage': [],
            'user': {
                'admin': 1,
                'apikey': api_key,
                'blocked': 0,
                'email': 'john.wick@askomics.org',
                'fname': 'John',
                'galaxy': None,
                'id': 1,
                'ldap': 1,
                'lname': 'Wick',
                'quota': 0,
                'username': 'jwick'
            }
        }

        # Second login get the user with the same API key
        client.logout()
        response = client.client.post('/api/auth/login', json=ok_inputs_email)

        resp = response.json
        assert resp['user']['last_action'] > 1000
        del resp['user']['last_action']
        assert resp == {
            'error': False,
            'errorMessage': [],
            'user': {
                'admin': 1,
                'apikey': api_key,
                'blocked': 0,
                'email': 'john.wick@askomics.org',
                'fname': 'John',
                'galaxy': None,
                'id': 1,
                'ldap': 1,
                'lname': 'Wick',
                'quota': 0,
                'username': 'jwick'
            }
        }

        # login with username
        client.session.pop("user", None)
        response = client.client.post('/api/auth/login', json=ok_inputs_username)

        resp = response.json
        assert resp['user']['last_action'] > 1000
        del resp['user']['last_action']
        assert resp == {
            'error': False,
            'errorMessage': [],
            'user': {
                'admin': 1,
                'apikey': api_key,
                'blocked': 0,
                'email': 'john.wick@askomics.org',
                'fname': 'John',
                'galaxy': None,
                'id': 1,
                'ldap': 1,
                'lname': 'Wick',
                'quota': 0,
                'username': 'jwick'
            }
        }

    def test_ok_login(self, client):
        """Test /api/auth/login route with good credentials"""
        ok_inputs_email = {
            "login": "jdoe@askomics.org",
            "password": "iamjohndoe"
        }

        ok_inputs_username = {
            "login": "jdoe",
            "password": "iamjohndoe"
        }

        client.create_two_users()

        response = client.client.post('/api/auth/login', json=ok_inputs_username)

        assert response.status_code == 200
        assert response.json == {
            'error': False,
            'errorMessage': [],
            'user': {
                'id': 1,
                'ldap': 0,
                'fname': "John",
                'lname': "Doe",
                'username': "jdoe",
                'email': "jdoe@askomics.org",
                'admin': 1,
                'blocked': 0,
                'quota': 0,
                'apikey': "0000000001",
                'galaxy': {"url": "http://localhost:8081", "apikey": "fakekey"},
                'last_action': None
            }
        }

        response = client.client.post('/api/auth/login', json=ok_inputs_email)

        assert response.status_code == 200
        resp = response.json
        assert resp['user']['last_action'] > 1000
        del resp['user']['last_action']
        assert resp == {
            'error': False,
            'errorMessage': [],
            'user': {
                'id': 1,
                'ldap': 0,
                'fname': "John",
                'lname': "Doe",
                'username': "jdoe",
                'email': "jdoe@askomics.org",
                'admin': 1,
                'blocked': 0,
                'quota': 0,
                'apikey': "0000000001",
                'galaxy': {"url": "http://localhost:8081", "apikey": "fakekey"}
            }
        }

        # Test logged
        with client.client.session_transaction() as sess:
            assert 'user' in sess
            assert sess['user']['last_action'] > 1000
            del sess['user']['last_action']
            assert sess["user"] == {
                'id': 1,
                'ldap': 0,
                'fname': "John",
                'lname': "Doe",
                'username': "jdoe",
                'email': "jdoe@askomics.org",
                'admin': 1,
                'blocked': 0,
                'quota': 0,
                'apikey': "0000000001",
                'galaxy': {"url": "http://localhost:8081", "apikey": "fakekey"}
            }

    def test_login_apikey(self, client):
        """Test /loginapikey route"""
        route_jdoe_apikey = "/loginapikey/0000000001"
        route_jsmith_apikey = "/loginapikey/0000000002"
        route_wrong_apikey = "/loginapikey/0000000000"

        client.create_two_users()

        response = client.client.get(route_jdoe_apikey)

        assert response.status_code == 200
        assert not response.json

        response = client.client.get(route_jsmith_apikey)

        assert response.status_code == 200
        assert not response.json

        response = client.client.get(route_wrong_apikey)

        assert response.status_code == 200
        assert response.json == {
            "error": True,
            "errorMessage": ["No user with this API key"],
            "user": {}
        }

    def test_update_profile(self, client):
        """Test /api/auth/profile route"""
        update_all_data = {
            "newFname": "Johnny",
            "newLname": "Dododo",
            "newEmail": "jdododo@askomics.org"
        }

        update_lname_data = {
            "newFname": "",
            "newLname": "Dodo",
            "newEmail": ""
        }

        update_email_data = {
            "newFname": "",
            "newLname": "",
            "newEmail": "jdodo@askomics.org"
        }

        update_empty_data = {
            "newFname": "",
            "newLname": "",
            "newEmail": ""
        }

        client.create_two_users()
        client.log_user("jdoe")

        response = client.client.post("/api/auth/profile", json=update_empty_data)
        assert response.status_code == 200
        assert response.json == {
            "error": False,
            "errorMessage": '',
            "user": {
                'id': 1,
                'ldap': 0,
                'fname': "John",
                'lname': "Doe",
                'username': "jdoe",
                'email': "jdoe@askomics.org",
                'admin': 1,
                'blocked': 0,
                'quota': 0,
                'apikey': "0000000001",
                'galaxy': {"url": "http://localhost:8081", "apikey": "fakekey"}
            }
        }
        # Assert database is untouched
        # TODO:

        # Assert session is untouched
        with client.client.session_transaction() as sess:
            assert 'user' in sess
            assert sess["user"] == {
                'id': 1,
                'ldap': 0,
                'fname': "John",
                'lname': "Doe",
                'username': "jdoe",
                'email': "jdoe@askomics.org",
                'admin': 1,
                'blocked': 0,
                'quota': 0,
                'apikey': "0000000001",
                'galaxy': {"url": "http://localhost:8081", "apikey": "fakekey"}
            }

        response = client.client.post("/api/auth/profile", json=update_lname_data)
        assert response.status_code == 200
        assert response.json == {
            "error": False,
            "errorMessage": '',
            "user": {
                'id': 1,
                'ldap': False,
                'fname': "John",
                'lname': "Dodo",
                'username': "jdoe",
                'email': "jdoe@askomics.org",
                'admin': 1,
                'blocked': 0,
                'quota': 0,
                'apikey': "0000000001",
                'galaxy': {"url": "http://localhost:8081", "apikey": "fakekey"}
            }
        }
        # Assert database is updated
        # TODO:

        # Assert session is updated
        with client.client.session_transaction() as sess:
            assert 'user' in sess
            assert sess["user"] == {
                'id': 1,
                'ldap': 0,
                'fname': "John",
                'lname': "Dodo",
                'username': "jdoe",
                'email': "jdoe@askomics.org",
                'admin': 1,
                'blocked': 0,
                'quota': 0,
                'apikey': "0000000001",
                'galaxy': {"url": "http://localhost:8081", "apikey": "fakekey"}
            }

        response = client.client.post("/api/auth/profile", json=update_email_data)
        assert response.status_code == 200
        assert response.json == {
            "error": False,
            "errorMessage": '',
            "user": {
                'id': 1,
                'ldap': 0,
                'fname': "John",
                'lname': "Dodo",
                'username': "jdoe",
                'email': "jdodo@askomics.org",
                'admin': 1,
                'blocked': 0,
                'quota': 0,
                'apikey': "0000000001",
                'galaxy': {"url": "http://localhost:8081", "apikey": "fakekey"}
            }
        }
        # Assert database is updated
        # TODO:

        # Assert session is updated
        with client.client.session_transaction() as sess:
            assert 'user' in sess
            assert sess["user"] == {
                'id': 1,
                'ldap': 0,
                'fname': "John",
                'lname': "Dodo",
                'username': "jdoe",
                'email': "jdodo@askomics.org",
                'admin': 1,
                'blocked': 0,
                'quota': 0,
                'apikey': "0000000001",
                'galaxy': {"url": "http://localhost:8081", "apikey": "fakekey"}
            }

        response = client.client.post("/api/auth/profile", json=update_all_data)
        assert response.status_code == 200
        assert response.json == {
            "error": False,
            "errorMessage": '',
            "user": {
                'id': 1,
                'ldap': 0,
                'fname': "Johnny",
                'lname': "Dododo",
                'username': "jdoe",
                'email': "jdododo@askomics.org",
                'admin': 1,
                'blocked': 0,
                'quota': 0,
                'apikey': "0000000001",
                'galaxy': {"url": "http://localhost:8081", "apikey": "fakekey"}
            }
        }
        # Assert database is updated
        # TODO:

        # Assert session is updated
        with client.client.session_transaction() as sess:
            assert 'user' in sess
            assert sess["user"] == {
                'id': 1,
                'ldap': 0,
                'fname': "Johnny",
                'lname': "Dododo",
                'username': "jdoe",
                'email': "jdododo@askomics.org",
                'admin': 1,
                'blocked': 0,
                'quota': 0,
                'apikey': "0000000001",
                'galaxy': {"url": "http://localhost:8081", "apikey": "fakekey"}
            }

    def test_update_password(self, client):
        """test /api/auth/password"""
        empty_data = {
            "newPassword": "",
            "confPassword": "",
            "oldPassword": ""
        }

        unidentical_passwords_data = {
            "newPassword": "helloworld",
            "confPassword": "holamundo",
            "oldPassword": "iamjohndoe"
        }

        wrong_old_passwords_data = {
            "newPassword": "helloworld",
            "confPassword": "helloworld",
            "oldPassword": "wrongpassword"
        }

        ok_data = {
            "newPassword": "helloworld",
            "confPassword": "helloworld",
            "oldPassword": "iamjohndoe"
        }

        client.create_two_users()
        client.log_user("jdoe")

        response = client.client.post('/api/auth/password', json=empty_data)
        assert response.status_code == 200
        assert response.json == {
            "error": True,
            "errorMessage": 'Empty password',
            "user": {
                'id': 1,
                'ldap': 0,
                'fname': "John",
                'lname': "Doe",
                'username': "jdoe",
                'email': "jdoe@askomics.org",
                'admin': 1,
                'blocked': 0,
                'quota': 0,
                'apikey': "0000000001",
                'galaxy': {"url": "http://localhost:8081", "apikey": "fakekey"}
            }
        }

        response = client.client.post('/api/auth/password', json=unidentical_passwords_data)
        assert response.status_code == 200
        assert response.json == {
            "error": True,
            "errorMessage": 'New passwords are not identical',
            "user": {
                'id': 1,
                'ldap': 0,
                'fname': "John",
                'lname': "Doe",
                'username': "jdoe",
                'email': "jdoe@askomics.org",
                'admin': 1,
                'blocked': 0,
                'quota': 0,
                'apikey': "0000000001",
                'galaxy': {"url": "http://localhost:8081", "apikey": "fakekey"}
            }
        }

        response = client.client.post('/api/auth/password', json=wrong_old_passwords_data)
        assert response.status_code == 200
        assert response.json == {
            "error": True,
            "errorMessage": 'Incorrect old password',
            "user": {
                'id': 1,
                'ldap': 0,
                'fname': "John",
                'lname': "Doe",
                'username': "jdoe",
                'email': "jdoe@askomics.org",
                'admin': 1,
                'blocked': 0,
                'quota': 0,
                'apikey': "0000000001",
                'galaxy': {"url": "http://localhost:8081", "apikey": "fakekey"}
            }
        }

        response = client.client.post('/api/auth/password', json=ok_data)
        assert response.status_code == 200
        assert response.json == {
            "error": False,
            "errorMessage": '',
            "user": {
                'id': 1,
                'ldap': 0,
                'fname': "John",
                'lname': "Doe",
                'username': "jdoe",
                'email': "jdoe@askomics.org",
                'admin': 1,
                'blocked': 0,
                'quota': 0,
                'apikey': "0000000001",
                'galaxy': {"url": "http://localhost:8081", "apikey": "fakekey"}
            }
        }

    def test_update_apikey(self, client):
        """test /api/auth/logout route"""
        client.create_two_users()
        client.log_user("jdoe")

        response = client.client.get('/api/auth/apikey')

        assert response.status_code == 200
        assert len(response.json) == 3
        assert not response.json["error"]
        assert response.json["errorMessage"] == ''
        assert len(response.json["user"]) == 11
        assert response.json["user"]["id"] == 1
        assert not response.json["user"]["ldap"]
        assert response.json["user"]["fname"] == "John"
        assert response.json["user"]["lname"] == "Doe"
        assert response.json["user"]["username"] == "jdoe"
        assert response.json["user"]["email"] == "jdoe@askomics.org"
        assert response.json["user"]["admin"]
        assert not response.json["user"]["blocked"]
        assert response.json["user"]["quota"] == 0
        assert not response.json["user"]["apikey"] == "0000000001"
        assert response.json["user"]["galaxy"] == {"url": "http://localhost:8081", "apikey": "fakekey"}

    def test_update_galaxy(self, client):
        """test /api/auth/galaxy route"""
        client.create_two_users()
        client.log_user("jsmith")  # jsmith don't gave galaxy account linked

        fake_data = {
            "gurl": "http://nogalaxy.org",
            "gkey": "nokey"
        }

        ok_data = {
            "gurl": "http://localhost:8081",
            "gkey": "fakekey"
        }

        response = client.client.post("/api/auth/galaxy", json=fake_data)

        assert response.status_code == 200
        assert response.json == {
            'error': True,
            'errorMessage': 'Not a valid Galaxy',
            'user': {
                'admin': 0,
                'apikey': '0000000002',
                'blocked': 0,
                'email': 'jsmith@askomics.org',
                'fname': 'Jane',
                'galaxy': None,
                'id': 2,
                'ldap': 0,
                'lname': 'Smith',
                'quota': 0,
                'username': 'jsmith'
            }
        }

        response = client.client.post("/api/auth/galaxy", json=ok_data)

        assert response.status_code == 200
        assert response.json == {
            'error': False,
            'errorMessage': '',
            'user': {
                'admin': 0,
                'apikey': '0000000002',
                'blocked': 0,
                'email': 'jsmith@askomics.org',
                'fname': 'Jane',
                'id': 2,
                'ldap': 0,
                'lname': 'Smith',
                'quota': 0,
                'username': 'jsmith',
                'galaxy': {
                    "url": "http://localhost:8081",
                    "apikey": "fakekey"
                }
            }
        }

        # Update jode galaxy account
        client.logout()
        client.log_user("jdoe")

        response = client.client.post("/api/auth/galaxy", json=fake_data)

        assert response.status_code == 200
        assert response.json == {
            'error': True,
            'errorMessage': 'Not a valid Galaxy',
            'user': {
                'admin': 1,
                'apikey': '0000000001',
                'blocked': 0,
                'email': 'jdoe@askomics.org',
                'fname': 'John',
                'id': 1,
                'ldap': 0,
                'lname': 'Doe',
                'quota': 0,
                'username': 'jdoe',
                'galaxy': {
                    "url": "http://localhost:8081",
                    "apikey": "fakekey"
                },
            }
        }

        response = client.client.post("/api/auth/galaxy", json=ok_data)

        assert response.status_code == 200
        assert response.json == {
            'error': False,
            'errorMessage': '',
            'user': {
                'admin': 1,
                'apikey': '0000000001',
                'blocked': 0,
                'email': 'jdoe@askomics.org',
                'fname': 'John',
                'id': 1,
                'ldap': 0,
                'lname': 'Doe',
                'quota': 0,
                'username': 'jdoe',
                'galaxy': {
                    "url": "http://localhost:8081",
                    "apikey": "fakekey"
                }
            }
        }

    def test_logout(self, client):
        """test /api/auth/logout route"""
        client.create_two_users()
        client.log_user("jdoe")

        response = client.client.get('/api/auth/logout')

        assert response.status_code == 200
        assert response.json == {
            "user": {},
            "logged": False
        }

    def test_reset_password(self, client):
        """test /api/auth/reset_password route"""
        client.create_two_users()

        # Test send link
        fake_data = {"login": "jean-michel-fake"}
        ok_data = {"login": "jdoe"}
        ok_data_email = {"login": "jdoe@askomics.org"}

        expected = {
            "error": False,
            "errorMessage": ""
        }

        response = client.client.post("/api/auth/reset_password", json=fake_data)
        assert response.status_code == 200
        assert response.json == expected

        response = client.client.post("/api/auth/reset_password", json=ok_data)
        assert response.status_code == 200
        assert response.json == expected

        response = client.client.post("/api/auth/reset_password", json=ok_data_email)
        assert response.status_code == 200
        assert response.json == expected

        # Test check token
        token = client.create_reset_token("jdoe")
        fake_data = {
            "token": "fake_token"
        }
        ok_data = {
            "token": token
        }

        response = client.client.post("/api/auth/reset_password", json=fake_data)
        assert response.status_code == 200
        assert response.json == {
            "token": "fake_token",
            "username": None,
            "fname": None,
            "lname": None,
            "error": True,
            "errorMessage": "Invalid token"
        }

        response = client.client.post("/api/auth/reset_password", json=ok_data)
        assert response.status_code == 200
        assert response.json == {
            "token": token,
            "username": "jdoe",
            "fname": "John",
            "lname": "Doe",
            "error": False,
            "errorMessage": ""
        }

        # Old token
        token = client.create_reset_token("jdoe", old_token=True)
        old_data = {
            "token": token
        }
        response = client.client.post("/api/auth/reset_password", json=old_data)
        assert response.status_code == 200
        assert response.json == {
            "token": token,
            "username": None,
            "fname": None,
            "lname": None,
            "error": True,
            "errorMessage": "Invalid token (too old token)"
        }

        # Test update password
        token = client.create_reset_token("jdoe")
        fake_data = {
            "token": token,
            "password": "coucou",
            "passwordConf": "niktarace",
        }

        response = client.client.post("/api/auth/reset_password", json=fake_data)
        assert response.status_code == 200
        assert response.json == {
            "error": True,
            "errorMessage": "Password are not identical"
        }

        token = client.create_reset_token("jdoe", old_token=True)
        old_data = {
            "token": token,
            "password": "coucou",
            "passwordConf": "coucou",
        }
        response = client.client.post("/api/auth/reset_password", json=old_data)
        assert response.status_code == 200
        assert response.json == {
            "error": True,
            "errorMessage": "Invalid token (too old token)"
        }

        token = client.create_reset_token("jdoe")
        old_data = {
            "token": token,
            "password": "coucou",
            "passwordConf": "coucou",
        }
        response = client.client.post("/api/auth/reset_password", json=old_data)
        assert response.status_code == 200
        assert response.json == {
            "error": False,
            "errorMessage": ""
        }

    def test_delete_account(self, client):
        """test /api/auth/delete_account route"""
        client.create_two_users()
        client.log_user("jdoe")

        response = client.client.get("/api/auth/delete_account")

        assert response.status_code == 200
        assert response.json == {
            "error": False,
            "errorMessage": ""
        }

    def test_reset_account(self, client):
        """test /api/auth/reset_account route"""
        client.create_two_users()
        client.log_user("jdoe")

        response = client.client.get("/api/auth/reset_account")

        assert response.status_code == 200
        assert response.json == {
            "error": False,
            "errorMessage": ""
        }

    def test_login_required(self, client):
        """test login_required decorator"""
        client.create_two_users()

        response = client.client.get("/api/auth/apikey")

        assert response.status_code == 401
        assert response.json == {
            "error": True,
            "errorMessage": "Login required"
        }

        client.log_user("jsmith", blocked=True)
        response = client.client.get("/api/auth/apikey")

        assert response.status_code == 401
        assert response.json == {
            "error": True,
            "errorMessage": "Blocked account"
        }

    def test_admin_required(self, client):
        """test admin_required decorator"""
        client.create_two_users()
        response = client.client.get("/api/admin/getusers")

        assert response.status_code == 401
        assert response.json == {
            "error": True,
            "errorMessage": "Login required"
        }

        client.log_user("jsmith")
        response = client.client.get("/api/admin/getusers")

        assert response.status_code == 401
        assert response.json == {
            "error": True,
            "errorMessage": "Admin required"
        }

    def test_local_required(self, client):
        """test local_required decorator"""
        client.create_two_users()
        response = client.client.post("/api/auth/profile", json={})

        assert response.status_code == 401
        assert response.json == {
            "error": True,
            "errorMessage": "Login required"
        }

        client.log_user("jsmith", ldap=True)
        response = client.client.post("/api/auth/profile", json={})

        assert response.status_code == 401
        assert response.json == {
            "error": True,
            "errorMessage": "Local user required"
        }
