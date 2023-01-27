"""Contain the Database class"""

import hashlib
import os
import glob
import shutil
import textwrap
import time

from askomics.libaskomics.Database import Database
from askomics.libaskomics.Galaxy import Galaxy
from askomics.libaskomics.LdapAuth import LdapAuth
from askomics.libaskomics.Mailer import Mailer
from askomics.libaskomics.Params import Params
from askomics.libaskomics.SparqlQueryLauncher import SparqlQueryLauncher
from askomics.libaskomics.TriplestoreExplorer import TriplestoreExplorer
from askomics.libaskomics.Utils import Utils

from validate_email import validate_email


class LocalAuth(Params):
    """Manage user authentication"""

    def __init__(self, app, session):
        """init

        Parameters
        ----------
        app : Flask
            flask app
        session :
            AskOmics session, contain the user
        """
        Params.__init__(self, app, session)

    def check_inputs(self, inputs, admin_add=False):
        """Check user inputs

        Check if inputs are not empty, if passwords are identical, and if
        username and email are not already in the database

        Parameters
        ----------
        inputs : dict
            User inputs

        """
        if not inputs.get('fname'):
            self.error = True
            self.error_message.append('First name empty')

        if not inputs.get('lname'):
            self.error = True
            self.error_message.append('Last name empty')

        if not inputs.get('username'):
            self.error = True
            self.error_message.append('Username name empty')

        if not validate_email(inputs.get('email')):
            self.error = True
            self.error_message.append('Not a valid email')

        if not admin_add:
            if not inputs.get('password'):
                self.error = True
                self.error_message.append('Password empty')

            if inputs.get('password') != inputs.get('passwordconf'):
                self.error = True
                self.error_message.append("Passwords doesn't match")

        if self.is_username_in_db(inputs.get('username')):
            self.error = True
            self.error_message.append('Username already registered')

        if self.is_email_in_db(inputs.get('email')):
            self.error = True
            self.error_message.append('Email already registered')

    def is_username_in_db(self, username):
        """
        Check if the username is present in the database

        Parameters
        ----------
        username : str
            Username

        Returns
        -------
        bool
            True if the user exist
        """
        database = Database(self.app, self.session)
        query = '''
        SELECT username, password FROM users
        WHERE username=?
        '''

        rows = database.execute_sql_query(query, (username, ))

        if len(rows) <= 0:
            return False
        return True

    def is_email_in_db(self, email):
        """
        Check if the email is present in the database

        Parameters
        ----------
        email : str
            Email

        Returns
        -------
        bool
            True if the email exist
        """
        database = Database(self.app, self.session)
        query = '''
        SELECT email FROM users
        WHERE email=?
        '''

        rows = database.execute_sql_query(query, (email, ))

        if len(rows) <= 0:
            return False
        return True

    def persist_user_admin(self, inputs):
        """Persist a new user (admin action)

        Parameters
        ----------
        inputs : User input
            The new user info

        Returns
        -------
        dict
            The new user
        """
        inputs["password"] = Utils.get_random_string(8)
        return self.persist_user(inputs, return_password=True)

    def persist_user(self, inputs, ldap_login=False, return_password=False):
        """
        Persist user in the TS

        Parameters
        ----------
        inputs : dict
            User infos
        ldap_login : bool, optional
            If True, user is ldap

        Returns
        -------
        dict
            The user
        """
        database = Database(self.app, self.session)

        # Check if user is the first. if yes, set him admin
        if self.get_number_of_users() == 0:
            admin = True
            blocked = False

        else:
            admin = False
            blocked = self.settings.getboolean('askomics', 'default_locked_account')

        api_key = Utils.get_random_string(20) if "apikey" not in inputs else inputs["apikey"]

        query = '''
        INSERT INTO users VALUES(
            NULL,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            NULL
        )
        '''

        salt = None
        sha512_pw = None
        email = None
        fname = None
        lname = None

        if not ldap_login:
            # Create a salt
            salt = Utils.get_random_string(20) if "salt" not in inputs else inputs["salt"]
            # Concat askomics_salt + user_password + salt
            salted_pw = self.settings.get('askomics', 'password_salt') + inputs['password'] + salt
            # hash
            sha512_pw = hashlib.sha512(salted_pw.encode('utf8')).hexdigest()

            email = inputs["email"]
            fname = inputs["fname"]
            lname = inputs["lname"]

        # Store user in db
        user_id = database.execute_sql_query(
            query, (ldap_login, fname, lname, inputs['username'],
                    email, sha512_pw, salt, api_key, admin, blocked, Utils.humansize_to_bytes(self.settings.get("askomics", "quota")), int(time.time())), True)

        user = {
            'id': user_id,
            'ldap': ldap_login,
            'fname': fname,
            'lname': lname,
            'username': inputs['username'],
            'email': email,
            'admin': admin,
            'blocked': blocked,
            'quota': Utils.humansize_to_bytes(self.settings.get("askomics", "quota")),
            'apikey': api_key,
            'galaxy': None
        }

        if return_password and not ldap_login:
            user["password"] = inputs["password"]

        # Return user infos
        return user

    def create_user_directories(self, user_id, username):
        """Create the User directory

        Parameters
        ----------
        user_id : int
            User id
        username : string
            username
        """
        userdir_path = "{}/{}_{}".format(
            self.settings.get("askomics", "data_directory"),
            user_id,
            username
        )

        upload_path = "{}/{}".format(userdir_path, "upload")
        ttl_path = "{}/{}".format(userdir_path, "ttl")
        results_path = "{}/{}".format(userdir_path, "results")

        self.create_directory(userdir_path)
        self.create_directory(upload_path)
        self.create_directory(ttl_path)
        self.create_directory(results_path)

    def create_directory(self, directory_path):
        """Create a directory

        Parameters
        ----------
        directory_path : string
            Path
        """
        try:
            os.makedirs(directory_path)
        except FileExistsError:
            self.log.debug("{} already exist").format(directory_path)
        except PermissionError:
            self.error = True
            self.error_message.append(
                "Impossible to create directory {}, permission denied.").format(
                    directory_path)

    def get_number_of_users(self):
        """get the number of users in the DB

        Returns
        -------
        int
            Number of user in the Database
        """
        database = Database(self.app, self.session)
        query = '''
        SELECT COUNT(*)
        FROM users
        '''

        rows = database.execute_sql_query(query)

        return rows[0][0]

    def authenticate_user_with_apikey(self, apikey):
        """
        Return the user associated with the API key

        Parameters
        ----------
        inputs : string
            API key

        Returns
        -------
        dict
            user info if authentication success
        """
        database = Database(self.app, self.session)
        ldap_auth = LdapAuth(self.app, self.session)

        query = '''
        SELECT u.user_id, u.ldap, u.fname, u.lname, u.username, u.email, u.apikey, u.admin, u.blocked, u.quota, u.last_action, g.url, g.apikey
        FROM users u
        LEFT JOIN galaxy_accounts g ON u.user_id=g.user_id
        WHERE u.apikey = ?
        GROUP BY u.user_id
        '''

        error = False
        error_messages = []
        user = {}

        rows = database.execute_sql_query(query, (apikey, ))

        if len(rows) > 0:

            user = {
                'id': rows[0][0],
                'ldap': rows[0][1],
                'fname': rows[0][2],
                'lname': rows[0][3],
                'username': rows[0][4],
                'email': rows[0][5],
                'apikey': rows[0][6],
                'admin': rows[0][7],
                'blocked': rows[0][8],
                'quota': rows[0][9],
                'last_action': rows[0][10],
                'galaxy': None
            }

            if user["ldap"] == 1 and ldap_auth.ldap:
                ldap_user = ldap_auth.get_user(user["username"])
                user["fname"] = ldap_user["fname"]
                user["lname"] = ldap_user["lname"]
                user["email"] = ldap_user["email"]

            if rows[0][11] is not None and rows[0][12] is not None:
                user['galaxy'] = {
                    'url': rows[0][11],
                    'apikey': rows[0][12]
                }

        else:
            error = True
            error_messages.append('No user with this API key')

        return {'error': error, 'error_messages': error_messages, 'user': user}

    def authenticate_user(self, login, password):
        """Authenticate a user

        Parameters
        ----------
        login : str
            User login (username or email)
        password : str
            User password

        Returns
        -------
        dict
            user: User if authentication succed
            error: True if auth fail
            error_message: a message if auth fail
        """
        ldap_auth = LdapAuth(self.app, self.session)

        error = False
        error_messages = []
        user = {}

        # Try to auth user with db
        user = self.get_user_from_db(login)
        password_match = False

        if user:
            # If user is ldap and ldap is configured, get user from ldap and check password
            if user["ldap"] == 1 and ldap_auth.ldap:
                ldap_user = ldap_auth.get_user(login)
                if ldap_user:
                    user["username"] = ldap_user["username"]
                    user["fname"] = ldap_user["fname"]
                    user["lname"] = ldap_user["lname"]
                    user["email"] = ldap_user["email"]
                    password_match = ldap_auth.check_password(ldap_user["dn"], password)
            # If user is local, check the password
            else:
                password_match = self.check_password(user["username"], password, user["password"], user["salt"])
        else:
            # No user in database, try to get it from ldap
            if ldap_auth.ldap:
                ldap_user = ldap_auth.get_user(login)

                # we have a ldap user authenticated with email, redo auth with username (because email is not stored in db)
                if self.get_login_type(login) == "email":
                    return self.authenticate_user(ldap_user["username"], password)

                # If user in ldap and not in db, create it in db
                if ldap_user:
                    password_match = ldap_auth.check_password(ldap_user["dn"], password)
                    if password_match:
                        inputs = {
                            "username": ldap_user["username"]
                        }
                        # Create user in db
                        user = self.persist_user(inputs, ldap_login=True)
                        user["fname"] = ldap_user["fname"]
                        user["lname"] = ldap_user["lname"]
                        user["email"] = ldap_user["email"]
                        # Create user directories
                        self.create_user_directories(user["id"], user["username"])

        if not password_match or not user:
            error_messages.append("Bad login or password")
            user = {}
            error = True
        else:
            self.update_last_action(user["username"])

        # Don't return password and salt
        if "password" in user:
            user.pop("password")
        if "salt" in user:
            user.pop("salt")

        return {
            "user": user,
            "error": error,
            "error_messages": error_messages
        }

    def update_last_action(self, username):
        """Update last login time into user database

        Parameters
        ----------
        username : str
            Username

        Returns
        -------
        int
            timestamp
        """
        database = Database(self.app, self.session)

        now = int(time.time())

        query = '''
        UPDATE users SET
        last_action=?
        WHERE username=?
        '''

        database.execute_sql_query(query, (now, username))
        return now

    @staticmethod
    def get_login_type(login, ldap_login=False):
        """Get login type from a login

        Parameters
        ----------
        login : str
            Login

        Returns
        -------
        str
            email or username/uid
        """
        if validate_email(login):
            return 'email'
        return 'username' if not ldap_login else 'uid'

    def check_password(self, username, password_input, pasword_db, salt_db):
        """Check password

        Parameters
        ----------
        username : string
            User username
        password_input : string
            Input password (clear)
        pasword_db : string
            Database password (hashed)
        salt_db : string
            Database salt

        Returns
        -------
        bool
            True if password match
        """
        concat = self.settings.get('askomics', 'password_salt') + password_input + salt_db
        if len(pasword_db) == 64:
            # Use sha256 (old askomics database use sha256)
            shapw = hashlib.sha256(concat.encode('utf8')).hexdigest()
        else:
            # Use sha512
            shapw = hashlib.sha512(concat.encode('utf8')).hexdigest()

        return shapw == pasword_db

    def get_user_from_db(self, login):
        """Get a user from database

        Parameters
        ----------
        login : str
            email or username

        Returns
        -------
        dict
            User
        """
        database = Database(self.app, self.session)

        query = '''
        SELECT u.user_id, u.ldap, u.fname, u.lname, u.username, u.email, u.password, u.salt, u.apikey, u.admin, u.blocked, u.quota, u.last_action, g.url, g.apikey
        FROM users u
        LEFT JOIN galaxy_accounts g ON u.user_id=g.user_id
        WHERE {} = ?
        GROUP BY u.user_id
        '''.format(self.get_login_type(login))

        rows = database.execute_sql_query(query, (login, ))

        user = {}

        if len(rows) > 0:
            user = {
                'id': rows[0][0],
                'ldap': rows[0][1],
                'fname': rows[0][2],
                'lname': rows[0][3],
                'username': rows[0][4],
                'email': rows[0][5],
                'password': rows[0][6],
                'salt': rows[0][7],
                'apikey': rows[0][8],
                'admin': rows[0][9],
                'blocked': rows[0][10],
                'quota': rows[0][11],
                'last_action': rows[0][12],
                'galaxy': None
            }

            if rows[0][13] is not None and rows[0][14] is not None:
                user['galaxy'] = {
                    'url': rows[0][13],
                    'apikey': rows[0][14]
                }

        return user

    def update_profile(self, inputs, user):
        """Update the profile of a user

        Parameters
        ----------
        inputs : dict
            fields to update
        user : dict
            The current user

        Returns
        -------
        dict
            error, error message and updated user
        """
        error = False
        error_message = ''

        database = Database(self.app, self.session)

        update = []
        values = []

        new_fname = user['fname']
        new_lname = user['lname']
        new_email = user['email']

        # update only if one value are provided
        if not list(inputs.values()) == ['', '', '']:

            if inputs['newFname']:
                update.append('fname=?')
                values.append(inputs['newFname'])
                new_fname = inputs['newFname']
            if inputs['newLname']:
                update.append('lname=?')
                values.append(inputs['newLname'])
                new_lname = inputs['newLname']
            if inputs['newEmail']:
                update.append('email=?')
                values.append(inputs['newEmail'])
                new_email = inputs['newEmail']

            update_str = ', '.join(update)

            query = '''
            UPDATE users SET
            {}
            WHERE username=?
            '''.format(update_str)

            database.execute_sql_query(query, tuple(values) + (user['username'], ))

            user['fname'] = new_fname
            user['lname'] = new_lname
            user['email'] = new_email

        return {'error': error, 'error_message': error_message, 'user': user}

    def update_pw_db(self, username, password):
        """Update a password in database

        Parameters
        ----------
        username : str
            User username
        password : str
            New password
        """
        database = Database(self.app, self.session)

        salt = Utils.get_random_string(20)
        salted_pw = self.settings.get('askomics', 'password_salt') + password + salt
        sha512_pw = hashlib.sha512(salted_pw.encode('utf-8')).hexdigest()

        query = '''
        UPDATE users SET
        password=?, salt=?
        WHERE username=?
        '''

        database.execute_sql_query(query, (sha512_pw, salt, username))

    def update_password(self, inputs, user):
        """Update the password of a user

        Parameters
        ----------
        inputs : dict
            Curent password and the new one (and confirmation)
        user : dict
            The current user

        Returns
        -------
        dict
            error, error message and updated user
        """
        error = False
        error_message = ''

        # check if new passwords are identicals
        password_identical = (inputs['newPassword'] == inputs['confPassword'])

        if not inputs["newPassword"] == '':
            if password_identical:
                # Try to authenticate the user with his old password
                authentication = self.authenticate_user(user['username'], inputs['oldPassword'])
                if not authentication['error']:
                    self.update_pw_db(user['username'], inputs['newPassword'])
                else:
                    error = True
                    error_message = 'Incorrect old password'
            else:
                error = True
                error_message = 'New passwords are not identical'
        else:
            error = True
            error_message = 'Empty password'

        return {'error': error, 'error_message': error_message, 'user': user}

    def update_apikey(self, user):
        """Create a new api key and store in the database

        Parameters
        ----------
        user : dict
            The current user

        Returns
        -------
        dict
            error, error message and updated user
        """
        error = False
        error_message = ''

        database = Database(self.app, self.session)

        # get a new api key
        new_apikey = Utils.get_random_string(20)

        query = '''
        UPDATE users SET
        apikey=?
        WHERE username=?
        '''

        database.execute_sql_query(query, (new_apikey, user['username']))

        user['apikey'] = new_apikey

        return {'error': error, 'error_message': error_message, 'user': user}

    def update_galaxy_account(self, user, url, apikey):
        """Update a Galaxy account

        Parameters
        ----------
        user : dict
            Previous user info
        url : string
            Galaxy URL
        apikey : string
            Galaxy API key

        Returns
        -------
        dict
            Updated user
        """
        database = Database(self.app, self.session)
        galaxy = Galaxy(self.app, self.session, url, apikey)

        valid = galaxy.check_galaxy_instance()
        error_message = "Not a valid Galaxy"

        if valid:
            error_message = ""

            query = '''
            UPDATE galaxy_accounts SET
            url = ?,
            apikey = ?
            WHERE user_id = ?
            '''

            database.execute_sql_query(query, (url, apikey, self.session["user"]["id"]))

            user["galaxy"] = {
                "url": url,
                "apikey": apikey
            }

        return {"error": not valid, "error_message": error_message, "user": user}

    def add_galaxy_account(self, user, url, apikey):
        """Add a Galaxy account

        Parameters
        ----------
        user : dict
            Previous user info
        url : string
            Galaxy URL
        apikey : string
            Galaxy API key

        Returns
        -------
        dict
            Updated user
        """
        database = Database(self.app, self.session)
        galaxy = Galaxy(self.app, self.session, url, apikey)

        valid = galaxy.check_galaxy_instance()
        error_message = "Not a valid Galaxy"

        if valid:
            error_message = ""

            query = '''
            INSERT INTO galaxy_accounts VALUES(
                NULL,
                ?,
                ?,
                ?
            )
            '''

            database.execute_sql_query(query, (self.session["user"]["id"], url, apikey))

            user["galaxy"] = {
                "url": url,
                "apikey": apikey
            }

        return {"error": not valid, "error_message": error_message, "user": user}

    def get_user(self, username):
        """Get user form database and ldap (if ldap user)

        Parameters
        ----------
        username : str
            User username

        Returns
        -------
        dict
            User
        """
        user = self.get_user_from_db(username)
        if user:
            user.pop("password")
            user.pop("salt")
            ldap_auth = LdapAuth(self.app, self.session)

            if user["ldap"] == 1 and ldap_auth.ldap:
                ldap_user = ldap_auth.get_user(username)
                if ldap_user:
                    user["username"] = ldap_user["username"]
                    user["fname"] = ldap_user["fname"]
                    user["lname"] = ldap_user["lname"]
                    user["email"] = ldap_user["email"]

        return user

    def get_all_users(self):
        """Get all user info

        Returns
        -------
        list
            All user info
        """
        database = Database(self.app, self.session)
        ldap_auth = LdapAuth(self.app, self.session)

        query = '''
        SELECT u.user_id, u.ldap, u.fname, u.lname, u.username, u.email, u.admin, u.blocked, u.quota, u.last_action, g.url, g.apikey
        FROM users u
        LEFT JOIN galaxy_accounts g ON u.user_id=g.user_id
        GROUP BY u.user_id
        '''

        rows = database.execute_sql_query(query)

        users = []

        if rows:
            for row in rows:
                user = {}
                user['ldap'] = row[1]
                user['fname'] = row[2]
                user['lname'] = row[3]
                user['username'] = row[4]
                user['email'] = row[5]
                user['admin'] = row[6]
                user['blocked'] = row[7]
                user['quota'] = row[8]
                user['last_action'] = row[9]
                user['galaxy'] = None

                if row[10] is not None and row[11] is not None:
                    user['galaxy'] = {
                        'url': row[10],
                        'apikey': row[11]
                    }

                if user["ldap"] == 1:
                    ldap_user = ldap_auth.get_user(user["username"])
                    user["fname"] = ldap_user["fname"]
                    user["lname"] = ldap_user["lname"]
                    user["email"] = ldap_user["email"]

                users.append(user)

        return users

    def set_admin(self, new_status, username):
        """Set a new admin status to a user

        Parameters
        ----------
        new_status : boolean
            True for an admin
        username : string
            The concerned username
        """
        database = Database(self.app, self.session)

        query = '''
        UPDATE users
        SET admin=?
        WHERE username=?
        '''

        database.execute_sql_query(query, (new_status, username))

    def set_blocked(self, new_status, username):
        """Set a new blocked status to a user

        Parameters
        ----------
        new_status : boolean
            True for blocked
        username : string
            The concerned username
        """
        database = Database(self.app, self.session)

        query = '''
        UPDATE users
        SET blocked=?
        WHERE username=?
        '''

        database.execute_sql_query(query, (new_status, username))

    def set_quota(self, quota, username):
        """Set a new quota to a user

        Parameters
        ----------
        quota : int
            New quota
        username : string
            The concerned username
        """
        database = Database(self.app, self.session)

        query = '''
        UPDATE users
        SET quota=?
        WHERE username=?
        '''

        database.execute_sql_query(query, (Utils.humansize_to_bytes(quota), username))

    def get_email_with_username(self, username):
        """Get email from a username

        Parameters
        ----------
        username : str
            Username

        Returns
        -------
        str
            email
        """
        database = Database(self.app, self.session)

        query = """
        SELECT email
        FROM users
        WHERE username=?
        """

        return database.execute_sql_query(query, (username, ))[0][0]

    def get_username_with_email(self, email):
        """Get username from an email

        Parameters
        ----------
        email : str
            email

        Returns
        -------
        str
            username
        """
        database = Database(self.app, self.session)

        query = """
        SELECT username
        FROM users
        WHERE email=?
        """

        return database.execute_sql_query(query, (email, ))[0][0]

    def create_reset_token(self, login):
        """Insert a token into the db

        Parameters
        ----------
        login : str
            username or email

        Returns
        -------
        str
            The reset token
        """
        token = "{}:{}".format(int(time.time()), Utils.get_random_string(20))

        database_field = 'username'
        if validate_email(login):
            database_field = 'email'

        database = Database(self.app, self.session)
        query = """
        UPDATE users
        SET reset_token=?
        WHERE {}=?
        """.format(database_field)

        database.execute_sql_query(query, (token, login))

        return token

    def send_mail_to_new_user(self, user):
        """Send a reset password link for a newly created user

        Parameters
        ----------
        user : dict
            The new user
        """
        token = self.create_reset_token(user["username"])
        mailer = Mailer(self.app, self.session)
        if mailer.check_mailer():
            body = textwrap.dedent("""
            Dear {username}!

            An account with this email adress was created by the administrators of {url}.

            To use it, please use the following link to create your password. You will then be able to log in with your username ({username}).

            {url}/password_reset?token={token}

            This link will expire after 3 hours. To get a new password creation link, please visit {url}/password_reset

            Thanks,

            The AskOmics Team
            """.format(
                username=user["username"],
                url=self.settings.get('askomics', 'instance_url'),
                token=token
            ))

            asko_subtitle = ""
            try:
                asko_subtitle = " | {}".format(self.settings.get("askomics", "subtitle"))
            except Exception:
                pass

            mailer.send_mail(user["email"], "[AskOmics{}] New account".format(asko_subtitle), body)
        else:
            self.log.info("Account created for user {}".format(user["username"]))
            self.log.info("Link: {url}/password_reset?token={token}".format(url=self.settings.get('askomics', 'instance_url'), token=token))

    def send_reset_link(self, login):
        """Send a reset link to a user

        Parameters
        ----------
        login : str
            username or email
        """
        login_type = self.get_login_type(login)

        user = self.get_user(login)
        if user:
            if user["ldap"] == 1:
                return

            if login_type == 'username':
                valid_user = self.is_username_in_db(login)
                username = login
                email = self.get_email_with_username(login) if valid_user else None
            else:
                valid_user = self.is_email_in_db(login)
                username = self.get_username_with_email(login) if valid_user else None
                email = login

            if valid_user:
                token = self.create_reset_token(login)

                mailer = Mailer(self.app, self.session)
                if mailer.check_mailer():
                    body = textwrap.dedent("""
                    Dear {user},

                    A password reset request has been received for your {url} account.

                    If you did not initiate this request, feel free to ignore this message.

                    You can use the following link to reset your password:

                    {url}/password_reset?token={token}

                    This link will expire after 3 hours. To get a new password reset link, please visit {url}/password_reset

                    Best regards,
                    The AskOmics Team

                    """.format(
                        user=username,
                        url=self.settings.get('askomics', 'instance_url'),
                        token=token
                    ))

                    asko_subtitle = ""
                    try:
                        asko_subtitle = " | {}".format(self.settings.get("askomics", "subtitle"))
                    except Exception:
                        pass

                    mailer.send_mail(email, "[AskOmics{}] Password reset".format(asko_subtitle), body)
                else:
                    self.log.info("Password reset for user {}".format(username))
                    self.log.info("Link: {url}/password_reset?token={token}".format(url=self.settings.get('askomics', 'instance_url'), token=token))

    def check_token(self, token):
        """Get username corresponding to the token

        Parameters
        ----------
        token : str
            The reset token

        Returns
        -------
        dict
            Username and message
        """
        database = Database(self.app, self.session)

        query = """
        SELECT username, fname, lname
        FROM users
        WHERE reset_token=?
        """

        rows = database.execute_sql_query(query, (token, ))

        username = None
        fname = None
        lname = None
        message = "Invalid token"

        if len(rows) > 0:
            username = rows[0][0]
            fname = rows[0][1]
            lname = rows[0][2]

        if username:
            # check token validity
            token_timestamp = token.split(":")[0]
            time_elapsed = int(time.time()) - int(token_timestamp)

            if time_elapsed >= 10800:  # 3 hours
                username = None
                fname = None
                lname = None
                message = "{} (too old token)".format(message)

        return {
            "username": username,
            "fname": fname,
            "lname": lname,
            "message": "" if username else message
        }

    def remove_token(self, username):
        """Remove a user token from database

        Parameters
        ----------
        username : str
            User to remove token
        """
        database = Database(self.app, self.session)
        query = """
        UPDATE users
        SET reset_token=?
        WHERE username=?
        """

        database.execute_sql_query(query, (None, username))

    def reset_password_with_token(self, token, password, password_conf):
        """Reset password of user with his token

        Parameters
        ----------
        token : str
            User password reset token
        password : str
            new password
        password_conf : str
            new password confirmation

        Returns
        -------
        dict
            error and message
        """
        message = ""
        error = False

        if password != password_conf:
            message = "Password are not identical"
            error = True
        else:
            user = self.check_token(token)
            if user["username"]:
                self.update_pw_db(user["username"], password)
                self.remove_token(user["username"])
            else:
                error = True
                message = user["message"]

        return {
            "error": error,
            "message": message
        }

    def delete_user_database(self, username, delete_user=True):
        """Delete a user in database

        Parameters
        ----------
        username : string
            Username to delete
        """
        user = self.get_user(username)

        database = Database(self.app, self.session)
        queries = [
            "DELETE FROM datasets WHERE user_id = ?",
            "DELETE FROM files WHERE user_id = ?",
            "DELETE FROM galaxy_accounts WHERE user_id = ?",
            "DELETE FROM results WHERE user_id = ?"
        ]

        if delete_user:
            queries.append("DELETE FROM users WHERE user_id = ?")
            queries.append("DELETE FROM abstraction WHERE user_id = ?")
            queries.append("DELETE FROM galaxy_accounts WHERE user_id = ?")

        for query in queries:
            database.execute_sql_query(query, (user["id"], ))

    def delete_user_directory(self, user, delete_user=True):
        """Delete a user directory

        Delete in DB, TS and filesystem

        Parameters
        ----------
        username : dict
            User to delete
        """
        user_dir = "{}/{}_{}".format(self.app.iniconfig.get("askomics", "data_directory"), user["id"], user["username"])
        if delete_user:
            shutil.rmtree(user_dir)
        else:
            file_lists = [
                glob.glob("{}/results/*".format(user_dir), recursive=True),
                glob.glob("{}/ttl/*".format(user_dir), recursive=True),
                glob.glob("{}/upload/*".format(user_dir), recursive=True)
            ]

            for file_list in file_lists:
                for file in file_list:
                    try:
                        os.remove(file)
                    except OSError:
                        self.log.error("Error while deleting file")

    def delete_user_rdf(self, username):
        """Delete a user rdf graphs

        Delete in DB, TS and filesystem

        Parameters
        ----------
        username : string
            Username to delete
        """
        tse = TriplestoreExplorer(self.app, self.session)
        query_launcher = SparqlQueryLauncher(self.app, self.session)
        graphs = tse.get_graph_of_user(username)
        for graph in graphs:
            Utils.redo_if_failure(self.log, 3, 1, query_launcher.drop_dataset, graph)

    def update_base_url(self, old_url, new_url):
        """Update base url for all graphs

        Parameters
        ----------
        old_url : string
            Previous base url
        new_url : string
            New base url
        """
        tse = TriplestoreExplorer(self.app, self.session)
        graphs = tse.get_all_graphs()

        for graph in graphs:
            tse.update_base_url(graph, old_url, new_url)

    def clear_abstraction_cache(self):
        """Clear cache for all users"""

        tse = TriplestoreExplorer(self.app, self.session)
        tse.uncache_abstraction(public=True, force=True)
