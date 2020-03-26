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
        # Non logged
        expected_config_nouser = {
            'footerMessage': client.get_config('askomics', 'footer_message'),
            'frontMessage': front_message,
            "version": get_distribution('askomics').version,
            "commit": None,
            "gitUrl": "https://github.com/askomics/flaskomics",
            "disableIntegration": client.get_config('askomics', 'disable_integration', boolean=True),
            "disableAccountCreation": client.get_config('askomics', 'disable_account_creation', boolean=True),
            "protectPublic": client.get_config('askomics', 'protect_public', boolean=True),
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
            'ldap': False,
            'fname': "John",
            'lname': "Doe",
            'username': "jdoe",
            'email': "jdoe@askomics.org",
            'admin': True,
            'blocked': False,
            "quota": 0,
            'apikey': "0000000001",
            'galaxy': {"url": "http://localhost:8081", "apikey": "admin"}
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
            'ldap': False,
            'fname': "Jane",
            'lname': "Smith",
            'username': "jsmith",
            'email': "jsmith@askomics.org",
            'admin': False,
            'blocked': False,
            "quota": 0,
            'apikey': "0000000002",
            'galaxy': None
        }
        response = client.client.get('/api/start')

        assert response.status_code == 200
        assert response.json == {
            "error": False,
            "errorMessage": '',
            "config": expected_config_jsmith
        }
