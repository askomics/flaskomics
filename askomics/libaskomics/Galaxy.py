from bioblend import galaxy
from askomics.libaskomics.Params import Params


class Galaxy(Params):
    """Connection with a Galaxy account

    Attributes
    ----------
    apikey : string
        Galaxy API key
    url : string
        Galaxy url
    """

    def __init__(self, app, session, url, apikey):
        """init

        Parameters
        ----------
        app : Flask
            flask app
        session :
            AskOmics session, contain the user
        url : string
            Galaxy url
        apikey : string
            Galaxy API key
        """
        Params.__init__(self, app, session)

        self.url = url
        self.apikey = apikey

    def check_galaxy_instance(self):
        """Check the Galaxy credentials

        Returns
        -------
        Boolean
            True if URL and Key exists
        """
        try:
            galaxy_instance = galaxy.GalaxyInstance(self.url, self.apikey)
            galaxy_instance.config.get_config()
        except Exception:
            return False

        return True
