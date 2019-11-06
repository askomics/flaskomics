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
                'galaxy': None,
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
                'galaxy': None,
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
