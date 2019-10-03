"""Contain the Database class"""

import hashlib
import os

from askomics.libaskomics.Database import Database
from askomics.libaskomics.Galaxy import Galaxy
from askomics.libaskomics.Params import Params
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

    def check_inputs(self, inputs):
        """Check user inputs

        Check if inputs are not empty, if passwords are identical, and if
        username and email are not already in the database

        Parameters
        ----------
        inputs : dict
            User inputs

        """
        if not inputs['fname']:
            self.error = True
            self.error_message.append('First name empty')

        if not inputs['lname']:
            self.error = True
            self.error_message.append('Last name empty')

        if not inputs['username']:
            self.error = True
            self.error_message.append('Username name empty')

        if not validate_email(inputs['email']):
            self.error = True
            self.error_message.append('Not a valid email')

        if not inputs['password']:
            self.error = True
            self.error_message.append('Password empty')

        if inputs['password'] != inputs['passwordconf']:
            self.error = True
            self.error_message.append("Passwords doesn't match")

        if self.is_username_in_db(inputs['username']):
            self.error = True
            self.error_message.append('Username already registered')

        if self.is_email_in_db(inputs['email']):
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

    def persist_user(self, inputs, ldap=False):
        """
        Persist user in the TS

        Parameters
        ----------
        inputs : dict
            User infos
        ldap : bool, optional
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
            ?
        )
        '''

        salt = None
        sha512_pw = None

        if not ldap:
            # Create a salt
            salt = Utils.get_random_string(20) if "salt" not in inputs else inputs["salt"]
            # Concat askomics_salt + user_password + salt
            salted_pw = self.settings.get('askomics', 'password_salt') + inputs['password'] + salt
            # hash
            sha512_pw = hashlib.sha512(salted_pw.encode('utf8')).hexdigest()

        # Store user in db
        user_id = database.execute_sql_query(
            query, (ldap, inputs['fname'], inputs['lname'], inputs['username'],
                    inputs['email'], sha512_pw, salt, api_key, admin, blocked, Utils.humansize_to_bytes(self.settings.get("askomics", "quota"))), True)

        # Return user infos
        return {
            'id': user_id,
            'ldap': ldap,
            'fname': inputs['fname'],
            'lname': inputs['lname'],
            'username': inputs['username'],
            'email': inputs['email'],
            'admin': admin,
            'blocked': blocked,
            'quota': Utils.humansize_to_bytes(self.settings.get("askomics", "quota")),
            'apikey': api_key,
            'galaxy': None
        }

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

        query = '''
        SELECT u.user_id, u.ldap, u.fname, u.lname, u.username, u.email, u.apikey, u.admin, u.blocked, u.quota, g.url, g.apikey
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
                'galaxy': None
            }

            if rows[0][10] is not None and rows[0][11] is not None:
                user['galaxy'] = {
                    'url': rows[0][10],
                    'apikey': rows[0][11]
                }

        else:
            error = True
            error_messages.append('No user with this API key')

        return {'error': error, 'error_messages': error_messages, 'user': user}

    def authenticate_user(self, inputs):
        """
        check if the password is the good password associate with the email

        Parameters
        ----------
        inputs : dict
            login and password

        Returns
        -------
        dict
            user info if authentication success
        """
        database_field = 'username'
        if validate_email(inputs['login']):
            database_field = 'email'

        error = False
        error_messages = []
        user = {}

        database = Database(self.app, self.session)

        query = '''
        SELECT u.user_id, u.ldap, u.fname, u.lname, u.username, u.email, u.password, u.salt, u.apikey, u.admin, u.blocked, u.quota, g.url, g.apikey
        FROM users u
        LEFT JOIN galaxy_accounts g ON u.user_id=g.user_id
        WHERE {} = ?
        GROUP BY u.user_id
        '''.format(database_field)

        rows = database.execute_sql_query(query, (inputs['login'], ))

        if len(rows) > 0:
            concat = self.settings.get('askomics', 'password_salt') + inputs['password'] + rows[0][7]
            if len(rows[0][6]) == 64:
                # Use sha256 (old askomics database use sha256)
                shapw = hashlib.sha256(concat.encode('utf8')).hexdigest()
            else:
                # Use sha512
                shapw = hashlib.sha512(concat.encode('utf8')).hexdigest()

            if rows[0][6] != shapw:
                error = True
                error_messages.append('Wrong password')
            else:
                user = {
                    'id': rows[0][0],
                    'ldap': rows[0][1],
                    'fname': rows[0][2],
                    'lname': rows[0][3],
                    'username': rows[0][4],
                    'email': rows[0][5],
                    'apikey': rows[0][8],
                    'admin': rows[0][9],
                    'blocked': rows[0][10],
                    'quota': rows[0][11],
                    'galaxy': None
                }

            if rows[0][12] is not None and rows[0][13] is not None:
                user['galaxy'] = {
                    'url': rows[0][12],
                    'apikey': rows[0][13]
                }

        else:
            error = True
            error_messages.append('Wrong username')

        return {'error': error, 'error_messages': error_messages, 'user': user}

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

        database = Database(self.app, self.session)

        # check if new passwords are identicals
        password_identical = (inputs['newPassword'] == inputs['confPassword'])

        if not inputs["newPassword"] == '':
            if password_identical:
                # Try to authenticate the user with his old password
                credentials = {'login': user['username'], 'password': inputs['oldPassword']}
                authentication = self.authenticate_user(credentials)
                if not authentication['error']:
                    # Update the password
                    salt = Utils.get_random_string(20)
                    salted_pw = self.settings.get('askomics', 'password_salt') + inputs['newPassword'] + salt
                    sha512_pw = hashlib.sha512(salted_pw.encode('utf-8')).hexdigest()

                    query = '''
                    UPDATE users SET
                    password=?, salt=?
                    WHERE username=?
                    '''

                    database.execute_sql_query(query, (sha512_pw, salt, user['username']))
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
        """Get a specific user by his username

        Parameters
        ----------
        username : string
            User username

        Returns
        -------
        dict
            The corresponding user
        """
        database = Database(self.app, self.session)

        query = '''
        SELECT u.user_id, u.ldap, u.fname, u.lname, u.username, u.email, u.apikey, u.admin, u.blocked, u.quota, g.url, g.apikey
        FROM users u
        LEFT JOIN galaxy_accounts g ON u.user_id=g.user_id
        WHERE username = ?
        GROUP BY u.user_id
        '''

        rows = database.execute_sql_query(query, (username, ))
        self.log.debug("rows")
        self.log.debug(rows)

        user = {}
        user['id'] = rows[0][0]
        user['ldap'] = rows[0][1]
        user['fname'] = rows[0][2]
        user['lname'] = rows[0][3]
        user['username'] = rows[0][4]
        user['email'] = rows[0][5]
        user['apikey'] = rows[0][6]
        user['admin'] = rows[0][7]
        user['blocked'] = rows[0][8]
        user['quota'] = rows[0][9]
        user['galaxy'] = None

        if rows[0][10] is not None and rows[0][11] is not None:
            user['galaxy'] = {
                'url': rows[0][10],
                'apikey': rows[0][11]
            }

        return user

    def get_all_users(self):
        """Get all user info

        Returns
        -------
        list
            All user info
        """
        database = Database(self.app, self.session)

        query = '''
        SELECT u.user_id, u.ldap, u.fname, u.lname, u.username, u.email, u.admin, u.blocked, u.quota, g.url, g.apikey
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
                user['galaxy'] = None

                if row[9] is not None and row[10] is not None:
                    user['galaxy'] = {
                        'url': row[9],
                        'apikey': row[10]
                    }

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
