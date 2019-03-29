"""Contain the Params class
"""


class Params(object):

    """Mother of all libaskomics classes

    Attributes
    ----------
    app :
        flask app
    log :
        flask logger
    session :
        flask session
    settings :
        askomics settings (from ini)
    """

    def __init__(self, app, session):
        """Store the logger, settings, session and app

        Parameters
        ----------
        app :
            flask app
        session :
            flask session
        """
        self.log = app.logger
        self.settings = app.iniconfig
        self.session = session
        self.app = app

        self.error = False
        self.error_message = []

    def get_error(self):

        return self.error

    def get_error_message(self):

        return self.error_message

    def str_to_bool(self, bool_str):
        """Convert a true/false string to a boolan value

        Parameters
        ----------
        bool_str : str
            boolean string

        Returns
        -------
        bool
            True or False
        """
        if bool_str.lower() == 'true':
            return True
        return False

    def logged_user(self):
        """Check if a user is logged

        Returns
        -------
        bool
            True if a user is logged
        """
        if "user" in self.session:
            return True
        return False
