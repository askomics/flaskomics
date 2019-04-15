import unittest
from . import AskomicsTestCase


class TestApiAdmin(AskomicsTestCase):
    """Test AskOmics API /api/admin/<someting>"""

    def test_get_users(self, client_logged_as_jdoe):
        """test the /api/admin/getusers route"""
        case = unittest.TestCase()
        response = client_logged_as_jdoe.get('/api/admin/getusers')
        expected = {
            'error': False,
            'errorMessage': '',
            'users': [{
                'admin': 1,
                'blocked': 0,
                'email': 'jdoe@askomics.org',
                'fname': 'John',
                'ldap': 0,
                'lname': 'Doe',
                'username': 'jdoe'
            }, {
                'admin': 0,
                'blocked': 0,
                'email': 'jsmith@askomics.org',
                'fname': 'Jane',
                'ldap': 0,
                'lname': 'Smith',
                'username': 'jsmith'
            }]
        }

        assert response.status_code == 200
        case.assertCountEqual(response.json, expected)

    def test_setadmin(self, client_logged_as_jdoe):
        """test the /api/admin/setadmin route"""
        set_jsmith_admin = {
            "username": "jsmith",
            "newAdmin": 1
        }

        response = client_logged_as_jdoe.post('/api/admin/setadmin', json=set_jsmith_admin)
        assert response.status_code == 200
        assert response.json == {'error': False, 'errorMessage': ''}

    def test_setblocked(self, client_logged_as_jdoe):
        """test the /api/admin/setblocked route"""
        set_jsmith_admin = {
            "username": "jsmith",
            "newBlocked": 1
        }

        response = client_logged_as_jdoe.post('/api/admin/setblocked', json=set_jsmith_admin)
        assert response.status_code == 200
        assert response.json == {'error': False, 'errorMessage': ''}
