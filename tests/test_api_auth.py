from . import AskomicsTestCase


class TestApiAuth(AskomicsTestCase):
    """Test AskOmics API /api/auth/<someting>"""

    def test_signup(self, client_empty_db, client_filled_db):
        """Test /api/auth/signup route"""
        ok_data = {
            "fname": "John",
            "lname": "Wick",
            "username": "jwick",
            "password": "dontkillmydog",
            "passwordconf": "dontkillmydog",
            "email": "jwick@askomics.org",
            'apikey': "0000000000",
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
        response = client_empty_db.post('/api/auth/signup', json=empty_fname_data)
        assert response.status_code == 200
        assert response.json == {
            'error': True,
            'errorMessage': ['First name empty'],
            'user': {}
        }

        # lname empty
        response = client_empty_db.post('/api/auth/signup', json=empty_lname_data)
        assert response.status_code == 200
        assert response.json == {
            'error': True,
            'errorMessage': ['Last name empty'],
            'user': {}
        }

        # username empty
        response = client_empty_db.post('/api/auth/signup', json=empty_username_data)
        assert response.status_code == 200
        assert response.json == {
            'error': True,
            'errorMessage': ['Username name empty'],
            'user': {}
        }

        # non valid email
        response = client_empty_db.post('/api/auth/signup', json=unvalid_email_data)
        assert response.status_code == 200
        assert response.json == {
            'error': True,
            'errorMessage': ['Not a valid email'],
            'user': {}
        }

        # non valid email
        response = client_empty_db.post('/api/auth/signup', json=diff_password_data)
        assert response.status_code == 200
        assert response.json == {
            'error': True,
            'errorMessage': ["Passwords doesn't match"],
            'user': {}
        }

        # ok inputs
        response = client_empty_db.post('/api/auth/signup', json=ok_data)
        assert response.status_code == 200
        assert response.json == {
            'error': False,
            'errorMessage': [],
            'user': {
                'id': 1,
                'ldap': False,
                'fname': "John",
                'lname': "Wick",
                'username': "jwick",
                'email': "jwick@askomics.org",
                'admin': True,
                'blocked': False,
                'quota': 0,
                'apikey': "0000000000",
                'galaxy': None
            }
        }

        # Test logged
        with client_empty_db.session_transaction() as sess:
            assert 'user' in sess
            assert sess["user"] == {
                'id': 1,
                'ldap': False,
                'fname': "John",
                'lname': "Wick",
                'username': "jwick",
                'email': "jwick@askomics.org",
                'admin': True,
                'blocked': False,
                'quota': 0,
                'apikey': "0000000000",
                'galaxy': None
            }

        # Re-insert same user
        response = client_empty_db.post('/api/auth/signup', json=ok_data)
        assert response.status_code == 200
        assert response.json == {
            'error': True,
            'errorMessage': ["Username already registered", "Email already registered"],
            'user': {}
        }

    def test_wrong_login(self, client_filled_db):
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

        response = client_filled_db.post('/api/auth/login', json=inputs_wrong_username)

        assert response.status_code == 200
        assert response.json == {
            'error': True,
            'errorMessage': ["Wrong username"],
            'user': {}
        }

        response = client_filled_db.post('/api/auth/login', json=inputs_wrong_email)

        assert response.status_code == 200
        assert response.json == {
            'error': True,
            'errorMessage': ["Wrong username"],
            'user': {}
        }

        response = client_filled_db.post('/api/auth/login', json=inputs_wrong_password)

        assert response.status_code == 200
        assert response.json == {
            'error': True,
            'errorMessage': ["Wrong password"],
            'user': {}
        }

        # Test logged
        with client_filled_db.session_transaction() as sess:
            assert 'user' not in sess

    def test_ok_login(self, client_filled_db):
        """Test /api/auth/login route with good credentials"""
        ok_inputs_email = {
            "login": "jdoe@askomics.org",
            "password": "iamjohndoe"
        }

        ok_inputs_username = {
            "login": "jdoe",
            "password": "iamjohndoe"
        }

        response = client_filled_db.post('/api/auth/login', json=ok_inputs_username)

        assert response.status_code == 200
        assert response.json == {
            'error': False,
            'errorMessage': [],
            'user': {
                'id': 1,
                'ldap': False,
                'fname': "John",
                'lname': "Doe",
                'username': "jdoe",
                'email': "jdoe@askomics.org",
                'admin': True,
                'blocked': False,
                'quota': 0,
                'apikey': "0000000000",
                'galaxy': None
            }
        }

        response = client_filled_db.post('/api/auth/login', json=ok_inputs_email)

        assert response.status_code == 200
        assert response.json == {
            'error': False,
            'errorMessage': [],
            'user': {
                'id': 1,
                'ldap': False,
                'fname': "John",
                'lname': "Doe",
                'username': "jdoe",
                'email': "jdoe@askomics.org",
                'admin': True,
                'blocked': False,
                'quota': 0,
                'apikey': "0000000000",
                'galaxy': None
            }
        }

        # Test logged
        with client_filled_db.session_transaction() as sess:
            assert 'user' in sess
            assert sess["user"] == {
                'id': 1,
                'ldap': False,
                'fname': "John",
                'lname': "Doe",
                'username': "jdoe",
                'email': "jdoe@askomics.org",
                'admin': True,
                'blocked': False,
                'quota': 0,
                'apikey': "0000000000",
                'galaxy': None
            }

    def test_update_profile(self, client_logged_as_jdoe):
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

        response = client_logged_as_jdoe.post("/api/auth/profile", json=update_empty_data)
        assert response.status_code == 200
        assert response.json == {
            "error": False,
            "errorMessage": '',
            "user": {
                'id': 1,
                'ldap': False,
                'fname': "John",
                'lname': "Doe",
                'username': "jdoe",
                'email': "jdoe@askomics.org",
                'admin': True,
                'blocked': False,
                'quota': 0,
                'apikey': "0000000000",
                'galaxy': None
            }
        }
        # Assert database is untouched
        # TODO:

        # Assert session is untouched
        with client_logged_as_jdoe.session_transaction() as sess:
            assert 'user' in sess
            assert sess["user"] == {
                'id': 1,
                'ldap': False,
                'fname': "John",
                'lname': "Doe",
                'username': "jdoe",
                'email': "jdoe@askomics.org",
                'admin': True,
                'blocked': False,
                'quota': 0,
                'apikey': "0000000000",
                'galaxy': None
            }

        response = client_logged_as_jdoe.post("/api/auth/profile", json=update_lname_data)
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
                'admin': True,
                'blocked': False,
                'quota': 0,
                'apikey': "0000000000",
                'galaxy': None
            }
        }
        # Assert database is updated
        # TODO:

        # Assert session is updated
        with client_logged_as_jdoe.session_transaction() as sess:
            assert 'user' in sess
            assert sess["user"] == {
                'id': 1,
                'ldap': False,
                'fname': "John",
                'lname': "Dodo",
                'username': "jdoe",
                'email': "jdoe@askomics.org",
                'admin': True,
                'blocked': False,
                'quota': 0,
                'apikey': "0000000000",
                'galaxy': None
            }

        response = client_logged_as_jdoe.post("/api/auth/profile", json=update_email_data)
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
                'email': "jdodo@askomics.org",
                'admin': True,
                'blocked': False,
                'quota': 0,
                'apikey': "0000000000",
                'galaxy': None
            }
        }
        # Assert database is updated
        # TODO:

        # Assert session is updated
        with client_logged_as_jdoe.session_transaction() as sess:
            assert 'user' in sess
            assert sess["user"] == {
                'id': 1,
                'ldap': False,
                'fname': "John",
                'lname': "Dodo",
                'username': "jdoe",
                'email': "jdodo@askomics.org",
                'admin': True,
                'blocked': False,
                'quota': 0,
                'apikey': "0000000000",
                'galaxy': None
            }

        response = client_logged_as_jdoe.post("/api/auth/profile", json=update_all_data)
        assert response.status_code == 200
        assert response.json == {
            "error": False,
            "errorMessage": '',
            "user": {
                'id': 1,
                'ldap': False,
                'fname': "Johnny",
                'lname': "Dododo",
                'username': "jdoe",
                'email': "jdododo@askomics.org",
                'admin': True,
                'blocked': False,
                'quota': 0,
                'apikey': "0000000000",
                'galaxy': None
            }
        }
        # Assert database is updated
        # TODO:

        # Assert session is updated
        with client_logged_as_jdoe.session_transaction() as sess:
            assert 'user' in sess
            assert sess["user"] == {
                'id': 1,
                'ldap': False,
                'fname': "Johnny",
                'lname': "Dododo",
                'username': "jdoe",
                'email': "jdododo@askomics.org",
                'admin': True,
                'blocked': False,
                'quota': 0,
                'apikey': "0000000000",
                'galaxy': None
            }

    def test_update_password(self, client_logged_as_jdoe):
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

        response = client_logged_as_jdoe.post('/api/auth/password', json=empty_data)
        assert response.status_code == 200
        assert response.json == {
            "error": True,
            "errorMessage": 'Empty password',
            "user": {
                'id': 1,
                'ldap': False,
                'fname': "John",
                'lname': "Doe",
                'username': "jdoe",
                'email': "jdoe@askomics.org",
                'admin': True,
                'blocked': False,
                'quota': 0,
                'apikey': "0000000000",
                'galaxy': None
            }
        }

        response = client_logged_as_jdoe.post('/api/auth/password', json=unidentical_passwords_data)
        assert response.status_code == 200
        assert response.json == {
            "error": True,
            "errorMessage": 'New passwords are not identical',
            "user": {
                'id': 1,
                'ldap': False,
                'fname': "John",
                'lname': "Doe",
                'username': "jdoe",
                'email': "jdoe@askomics.org",
                'admin': True,
                'blocked': False,
                'quota': 0,
                'apikey': "0000000000",
                'galaxy': None
            }
        }

        response = client_logged_as_jdoe.post('/api/auth/password', json=wrong_old_passwords_data)
        assert response.status_code == 200
        assert response.json == {
            "error": True,
            "errorMessage": 'Incorrect old password',
            "user": {
                'id': 1,
                'ldap': False,
                'fname': "John",
                'lname': "Doe",
                'username': "jdoe",
                'email': "jdoe@askomics.org",
                'admin': True,
                'blocked': False,
                'quota': 0,
                'apikey': "0000000000",
                'galaxy': None
            }
        }

        response = client_logged_as_jdoe.post('/api/auth/password', json=ok_data)
        assert response.status_code == 200
        assert response.json == {
            "error": False,
            "errorMessage": '',
            "user": {
                'id': 1,
                'ldap': False,
                'fname': "John",
                'lname': "Doe",
                'username': "jdoe",
                'email': "jdoe@askomics.org",
                'admin': True,
                'blocked': False,
                'quota': 0,
                'apikey': "0000000000",
                'galaxy': None
            }
        }

    def test_update_apikey(self, client_logged_as_jdoe):
        """test /api/auth/logout route"""
        response = client_logged_as_jdoe.get('/api/auth/apikey')

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
        assert not response.json["user"]["apikey"] == "0000000000"
        assert response.json["user"]["galaxy"] is None

    def test_logout(self, client_logged_as_jdoe):
        """test /api/auth/logout route"""
        response = client_logged_as_jdoe.get('/api/auth/logout')

        assert response.status_code == 200
        assert response.json == {
            "user": {},
            "logged": False
        }
