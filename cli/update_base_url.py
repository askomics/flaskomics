"""CLI to update base_url for all graphs"""
import argparse
import sys

from askomics.app import create_app, create_celery
from askomics.libaskomics.LocalAuth import LocalAuth
from askomics.libaskomics.Start import Start


class UpdateUrl(object):
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
        parser.add_argument("-o", "--old_url", type=str, help="Old base url", required=True)
        parser.add_argument("-n", "--new_url", type=str, help="New base url", required=True)

        self.args = parser.parse_args()

        if not (self.args.old_url and self.args.new_url):
            print("Error: old_url and new_url must not be empty")
            sys.exit(1)

        self.check_urls(self.args.old_url, self.args.new_url)

        self.application = create_app(config=self.args.config_file)
        self.celery = create_celery(self.application)
        self.session = {}
        starter = Start(self.application, self.session)
        starter.start()

    def check_urls(self, old_url, new_url):
        # Some checks
        if not (old_url.startswith("http://") or old_url.startswith("https://")):
            print("Error: old_url must starts with either http:// or https://")
            sys.exit(1)
        if not (new_url.startswith("http://") or new_url.startswith("https://")):
            print("Error: new_url must starts with either http:// or https://")
            sys.exit(1)

        if not (old_url.endswith("/") and new_url.endswith("/")):
            print("Error: Both urls must have a trailing /")
            sys.exit(1)

        if old_url.endswith("/data/") and not new_url.endswith("/data/"):
            print("Error: Make sure the new url ends with /data/ too")
            sys.exit(1)

        if old_url.endswith("/internal/") and not new_url.endswith("/internal/"):
            print("Error: Make sure the new url ends with /internal/ too")
            sys.exit(1)

    def main(self):
        """Update graphs"""

        local_auth = LocalAuth(self.application, self.session)
        self.application.logger.info("Update base url from {} to {}".format(self.args.old_url, self.args.new_url))
        local_auth.update_base_url(self.args.old_url, self.args.new_url)


if __name__ == '__main__':
    """main"""
    UpdateUrl().main()
