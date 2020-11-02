from pkg_resources import get_distribution

from . import AskomicsTestCase


class TestApi(AskomicsTestCase):
    """Test AskOmics API"""

    def test_start(self, client):
        """Test /api/start route"""
        front_message = None
        try:
            front_message = client.get_config('askomics', 'front_message')
        except Exception:
            pass
        # Get ldap password reset link if set
        password_reset_link = None
        try:
            password_reset_link = client.get_config("askomics", "ldap_password_reset_link")
        except Exception:
            pass
        # Get ldap password reset link if set
        account_link = None
        try:
            account_link = client.get_config("askomics", "ldap_account_link")
        except Exception:
            pass

        # Non logged
        expected_config_nouser = {
            'footerMessage': client.get_config('askomics', 'footer_message'),
            'frontMessage': front_message,
            "version": get_distribution('askomics').version,
            "commit": None,
            "gitUrl": "https://github.com/askomics/flaskomics",
            "disableAccountCreation": client.get_config('askomics', 'disable_account_creation', boolean=True),
            "disableIntegration": client.get_config('askomics', 'disable_integration', boolean=True),
            "protectPublic": client.get_config('askomics', 'protect_public', boolean=True),
            "passwordResetLink": password_reset_link,
            "accountLink": account_link,
            "namespaceData": client.get_config('triplestore', 'namespace_data'),
            "namespaceInternal": client.get_config('triplestore', 'namespace_internal'),
            "proxyPath": "/",
            "user": {},
            "logged": False
        }
        response = client.client.get('/api/start')
        assert response.status_code == 200
        assert response.json == {
            "error": False,
            "errorMessage": '',
            "config": expected_config_nouser
        }

        # Create database and user
        client.create_two_users()

        # Jdoe (admin) logged
        client.log_user("jdoe")

        expected_config_jdoe = expected_config_nouser
        expected_config_jdoe["logged"] = True
        expected_config_jdoe["user"] = {
            'id': 1,
            'ldap': 0,
            'fname': "John",
            'lname': "Doe",
            'username': "jdoe",
            'email': "jdoe@askomics.org",
            'admin': 1,
            'blocked': 0,
            "quota": 0,
            'apikey': "0000000001",
            'galaxy': {"url": "http://localhost:8081", "apikey": "fakekey"},
            'last_action': None
        }
        response = client.client.get('/api/start')

        assert response.status_code == 200
        assert response.json == {
            "error": False,
            "errorMessage": '',
            "config": expected_config_jdoe
        }

        # jsmith (non admin) logged
        client.log_user("jsmith")

        expected_config_jsmith = expected_config_nouser
        expected_config_jsmith["logged"] = True
        expected_config_jsmith["user"] = {
            'id': 2,
            'ldap': 0,
            'fname': "Jane",
            'lname': "Smith",
            'username': "jsmith",
            'email': "jsmith@askomics.org",
            'admin': 0,
            'blocked': 0,
            "quota": 0,
            'apikey': "0000000002",
            'galaxy': None,
            'last_action': None
        }
        response = client.client.get('/api/start')

        assert response.status_code == 200
        assert response.json == {
            "error": False,
            "errorMessage": '',
            "config": expected_config_jsmith
        }
