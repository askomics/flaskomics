"""Contain the Start classe
"""
import os

from askomics.libaskomics.Database import Database
from askomics.libaskomics.Params import Params


class Start(Params):

    """Initialize the data directory and the database

    Attributes
    ----------
    data_directory : str
        Path to the data directory
    database_path : str
        Path to the database file
    """

    def __init__(self, app, session):
        """Get data directory and database paths from the askomics settings

        Parameters
        ----------
        app :
            flask app
        session :
            flask session
        """
        Params.__init__(self, app, session)

        self.data_directory = self.settings.get('askomics', 'data_directory')
        self.database_path = self.settings.get('askomics', 'database_path')

    def start(self):
        """Create the data diretory and initialize the database file
        """
        self.create_data_directory()
        self.create_database()
        self.create_anonymous()

    def create_data_directory(self):
        """Create the data directory if it not exists
        """
        if not os.path.isdir(self.data_directory):
            os.makedirs(self.data_directory)

    def create_database(self):
        """Initialize the database file
        """
        database = Database(self.app, self.session)
        database.init_database()

    def create_anonymous(self):
        """Create anonymous data folder if required
        """
        if self.settings.get('askomics', 'anonymous_query', fallback=False):
            data_path = "{}/{}_{}/results".format(
                self.data_directory,
                "0",
                "anonymous"
            )
            if not os.path.isdir(self.data_directory):
                os.makedirs(self.data_directory)
