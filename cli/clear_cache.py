"""CLI to clear cache for all users"""
import argparse

from askomics.app import create_app, create_celery
from askomics.libaskomics.LocalAuth import LocalAuth
from askomics.libaskomics.Start import Start


class ClearCache(object):
    """Update base_url for all graphs

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
    """

    def __init__(self):
        """Get Args"""
        parser = argparse.ArgumentParser(description="Update base_url for all graphs")

        parser.add_argument("-c", "--config-file", type=str, help="AskOmics config file", required=True)

        self.args = parser.parse_args()

        self.application = create_app(config=self.args.config_file)
        self.celery = create_celery(self.application)
        self.session = {}
        starter = Start(self.application, self.session)
        starter.start()

    def main(self):
        """Update graphs"""

        local_auth = LocalAuth(self.application, self.session)
        self.application.logger.info("Clearing abstraction cache")
        local_auth.clear_abstraction_cache()


if __name__ == '__main__':
    """main"""
    ClearCache().main()
