import os

from askomics.libaskomics.Params import Params
from askomics.libaskomics.Database import Database

class Start(Params):

    def __init__(self, app, session):

        Params.__init__(self, app, session)

        self.data_directory = self.settings.get('askomics', 'data_directory')
        self.database_path = self.settings.get('askomics', 'database_path')

    def start(self):

        self.create_data_directory()
        self.create_database()

    def create_data_directory(self):

        if not os.path.isdir(self.data_directory):
            os.makedirs(self.data_directory)

    def create_database(self):

        database = Database(self.app, self.session)
        database.init_database()
        
