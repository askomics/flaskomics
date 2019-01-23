class Params(object):

    def __init__(self, app, session):

        self.log = app.logger
        self.settings = app.iniconfig
        self.session = session
        self.app = app
