import datetime
''
from askomics.libaskomics.ResultsHandler import ResultsHandler
from . import AskomicsTestCase


class TestCleanup(AskomicsTestCase):
    """Test correct URI interpretation"""

    def test_cleanup_failed(self, client):
        """Test that users failed jobs are NOT deleted"""
        client.create_two_users()
        client.log_user("jdoe")
        client.upload_and_integrate()

        # Add an old job
        start = int((datetime.date.today() - datetime.timedelta(1)).strftime("%s"))
        client.create_result(status="error", start=start)

        rh = ResultsHandler(client.app, client.session)
        results = rh.get_files_info()

        assert len(results) == 1
        rh.delete_older_results(1, "hour", "0", "error")
        results = rh.get_files_info()

        assert len(results) == 1

    def test_cleanup_success(self, client):
        """Test that users jobs are NOT deleted"""
        client.create_two_users()
        client.log_user("jdoe")
        client.upload_and_integrate()

        # Add an old job
        start = int((datetime.date.today() - datetime.timedelta(1)).strftime("%s"))
        client.create_result(start=start)

        rh = ResultsHandler(client.app, client.session)
        results = rh.get_files_info()

        assert len(results) == 1
        rh.delete_older_results(1, "hour", "0")
        results = rh.get_files_info()

        assert len(results) == 1

    def test_anon_cleanup_failed(self, client):
        """Test that anon failed jobs are deleted"""
        client.create_two_users()
        client.log_user("jdoe")
        client.upload_and_integrate(public=True)
        client.logout()

        client.log_anon()
        # Add an old job
        start = int((datetime.date.today() - datetime.timedelta(1)).strftime("%s"))
        client.create_result(status="error", start=start)

        rh = ResultsHandler(client.app, client.session)
        results = rh.get_files_info()

        assert len(results) == 1
        rh.delete_older_results(1, "hour", "0", "error")
        results = rh.get_files_info()

        assert len(results) == 0

    def test_anon_cleanup_success(self, client):
        """Test that anon jobs are  deleted"""
        client.create_two_users()
        client.log_user("jdoe")
        client.upload_and_integrate(public=True)
        client.logout()

        client.log_anon()
        # Add an old job
        start = int((datetime.date.today() - datetime.timedelta(1)).strftime("%s"))
        client.create_result(start=start)

        rh = ResultsHandler(client.app, client.session)
        results = rh.get_files_info()

        assert len(results) == 1
        rh.delete_older_results(1, "hour", "0")
        results = rh.get_files_info()

        assert len(results) == 0
