from pkg_resources import get_distribution

from . import AskomicsTestCase


class TestApi(AskomicsTestCase):
    """Test AskOmics API"""

    def test_hello(self, client_no_db, client_logged_as_jdoe):
        """Test /api/hello route"""
        response = client_no_db.get('/api/hello')

        assert response.status_code == 200
        assert response.json == {
            "error": False,
            "errorMessage": '',
            "message": "Welcome to AskOmics"
        }

        response = client_logged_as_jdoe.get('/api/hello')

        assert response.status_code == 200
        assert response.json == {
            "error": False,
            "errorMessage": '',
            "message": "Hello John Doe, Welcome to AskOmics!"
        }

    def test_start(self, app, client_no_db, client_logged_as_jdoe, client_logged_as_jsmith):
        """Test /api/start route"""
        # Non logged
        response = client_no_db.get('/api/start')

        expected_config = {
            'footerMessage': app.iniconfig.get('askomics', 'footer_message'),
            'version': get_distribution('askomics').version,
            "commit": None,
            "disableIntegration": app.iniconfig.getboolean('askomics', 'disable_integration'),
            "prefix": app.iniconfig.get('triplestore', 'prefix'),
            "namespace": app.iniconfig.get('triplestore', 'namespace')
        }

        assert response.status_code == 200
        assert response.json == {
            "error": False,
            "errorMessage": '',
            "user": None,
            "logged": False,
            "config": expected_config
        }

        # Jdoe (admin) logged
        response = client_logged_as_jdoe.get('/api/start')

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
                'apikey': "0000000000",
                'galaxy': None
            },
            "logged": True,
            "config": expected_config
        }

        # jsmith (non admin) logged
        response = client_logged_as_jsmith.get('/api/start')

        assert response.status_code == 200
        assert response.json == {
            "error": False,
            "errorMessage": '',
            "user": {
                'id': 2,
                'ldap': False,
                'fname': "Jane",
                'lname': "Smith",
                'username': "jsmith",
                'email': "jsmith@askomics.org",
                'admin': False,
                'blocked': False,
                'apikey': "0000000000",
                'galaxy': None
            },
            "logged": True,
            "config": expected_config
        }
