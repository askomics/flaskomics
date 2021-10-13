import ldap

from askomics.libaskomics.Params import Params


class LdapAuth(Params):
    """Summary

    Attributes
    ----------
    bind_dn : str
    Description
    bind_password : str
    Description
    first_name_attribute : str
    Description
    host : str
    Description
    mail_attribute : str
    Description
    port : str
    Description
    search_base : str
    Description
    surname_attribute : str
    Description
    user_filter : str
    Description
    username_attribute : str
    Description
    """

    def __init__(self, app, session):
        """Get ldap config

        Parameters
        ----------
        app : Flask
            flask app
        session
            AskOmics session, contain the user
        """
        Params.__init__(self, app, session)

        self.ldap = self.app.iniconfig.getboolean("askomics", "ldap_auth")

        if self.ldap:
            self.host = self.app.iniconfig.get("askomics", "ldap_host")
            self.port = self.app.iniconfig.get("askomics", "ldap_port")
            self.bind_dn = self.app.iniconfig.get("askomics", "ldap_bind_dn")
            self.bind_password = self.app.iniconfig.get("askomics", "ldap_bind_password")
            self.search_base = self.app.iniconfig.get("askomics", "ldap_search_base")
            self.user_filter = self.app.iniconfig.get("askomics", "ldap_user_filter")
            self.username_attribute = self.app.iniconfig.get("askomics", "ldap_username_attribute")
            self.first_name_attribute = self.app.iniconfig.get("askomics", "ldap_first_name_attribute")
            self.surname_attribute = self.app.iniconfig.get("askomics", "ldap_surname_attribute")
            self.mail_attribute = self.app.iniconfig.get("askomics", "ldap_mail_attribute")

    def get_user(self, login):
        """Get user with a login

        Parameters
        ----------
        login : str
            user login (mail or uid)

        Returns
        -------
        dict
            ldap user
        """
        try:
            ldap_client = ldap.initialize('ldap://' + self.host + ':' + self.port)
            ldap_client.set_option(ldap.OPT_REFERRALS, 0)
            search_filter = self.user_filter.replace('%s', login)
            field_list = [
                self.username_attribute,
                self.mail_attribute,
                self.first_name_attribute,
                self.surname_attribute
            ]
            ldap_user = ldap_client.search_s(self.search_base, ldap.SCOPE_SUBTREE, search_filter, field_list)
        except ldap.INVALID_CREDENTIALS as e:
            self.log.error('Invalid ldap bind credentials')
            raise e
        except ldap.SERVER_DOWN as e:
            self.log.error("Ldap server not found")
            raise e

        if not ldap_user:
            return {}

        return {
            'dn': ldap_user[0][0],
            'email': ldap_user[0][1][self.mail_attribute][0],
            'username': ldap_user[0][1][self.username_attribute][0],
            'fname': ldap_user[0][1][self.first_name_attribute][0],
            'lname': ldap_user[0][1][self.surname_attribute][0]
        }

    def check_password(self, dn, password):
        """Check user ldap password

        Parameters
        ----------
        dn : str
            User dn
        password : str
            User password

        Returns
        -------
        bool
            True if password match
        """
        try:
            ldap_client = ldap.initialize('ldap://' + self.host + ':' + self.port)
            ldap_client.set_option(ldap.OPT_REFERRALS, 0)

            ldap_client.simple_bind_s(dn, password)
        except ldap.INVALID_CREDENTIALS:
            ldap_client.unbind()
            return False
        except ldap.SERVER_DOWN as e:
            raise e
        ldap_client.unbind()
        return True
