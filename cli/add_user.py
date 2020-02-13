"""CLI to add a user into the Askomics database"""
import argparse

from askomics.app import create_app, create_celery
from askomics.libaskomics.LocalAuth import LocalAuth
from askomics.libaskomics.Start import Start


class AddUser(object):
    """Add a user into AskOmics Database

    Attributes
    ----------
    application : Flask app
        Flask App
    args : args
        User arguments
    celery : Celery
        Celery
    session : dict
        Empty session
    user : dict
        The New user
    """

    def __init__(self):
        """Get Args"""
        parser = argparse.ArgumentParser(description="Add a new user into AskOmics database")

        parser.add_argument("-c", "--config-file", type=str, help="AskOmics config file", required=True)

        parser.add_argument("-f", "--first-name", type=str, help="User first name", default="Ad")
        parser.add_argument("-l", "--last-name", type=str, help="User last name", default="Min")
        parser.add_argument("-u", "--username", type=str, help="User username", default="admin")
        parser.add_argument("-p", "--password", type=str, help="User password", default="admin")
        parser.add_argument("-e", "--email", type=str, help="User email", default="admin@example.org")
        parser.add_argument("-k", "--api-key", type=str, help="User API key", default="admin")

        parser.add_argument("-g", "--galaxy-url", type=str, help="Galaxy URL")
        parser.add_argument("-gk", "--galaxy-apikey", type=str, help="Galaxy API key")

        self.args = parser.parse_args()

        self.application = create_app(config=self.args.config_file)
        self.celery = create_celery(self.application)
        self.session = {}
        self.user = None

        starter = Start(self.application, self.session)
        starter.start()

    def main(self):
        """Insert the user and the eventualy galaxy account"""
        # Inseret user in database
        inputs = {
            "fname": self.args.first_name,
            "lname": self.args.last_name,
            "username": self.args.username,
            "email": self.args.email,
            "password": self.args.password,
            "apikey": self.args.api_key
        }

        local_auth = LocalAuth(self.application, self.session)
        if local_auth.get_number_of_users() > 0:
            self.application.logger.error("Database is not empty, user {} will not be created".format(self.args.username))
            return
        self.application.logger.info("Create user {}".format(self.args.username))
        self.user = local_auth.persist_user(inputs)
        self.session["user"] = self.user
        local_auth.create_user_directories(self.user["id"], self.user["username"])

        # insert Galaxy account if set
        if self.args.galaxy_url and self.args.galaxy_apikey:
            result = local_auth.add_galaxy_account(self.user, self.args.galaxy_url, self.args.galaxy_apikey)
            self.user = result["user"]

if __name__ == '__main__':
    """main"""
    AddUser().main()
