"""Contain the Database class
"""
import random
import hashlib
from validate_email import validate_email

from askomics.libaskomics.Params import Params
from askomics.libaskomics.Database import Database

class LocalAuth(Params):

    def __init__(self, app, session):

        Params.__init__(self, app, session)


    def check_inputs(self, inputs):
        """Check user inputs

        Check if inputs are not empty, if passwords are identical, and if
        username and email are not already in the database

        Parameters
        ----------
        inputs : dict
            User inputs

        Returns
        -------
        dict
            Errors of inputs
        """
        error = False
        error_messages = []

        if not inputs['fname']:
            error = True
            error_messages.append('First name empty')

        if not inputs['lname']:
            error = True
            error_messages.append('Last name empty')

        if not inputs['username']:
            error = True
            error_messages.append('Username name empty')

        if not validate_email(inputs['email']):
            error = True
            error_messages.append('Not a valid email')

        if not inputs['password']:
            error = True
            error_messages.append('Password empty')

        if inputs['password'] != inputs['passwordconf']:
            error = True
            error_messages.append("Passwords doesn't match")

        if self.is_username_in_db(inputs['username']):
            error = True
            error_messages.append('Username already registered')

        if self.is_email_in_db(inputs['email']):
            error = True
            error_messages.append('Email already registered')

        return error, error_messages

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
        Persist all user infos in the TS
        """

        database = Database(self.app, self.session)

        #check if user is the first. if yes, set him admin
        if self.get_number_of_users() == 0:
            admin = True
            blocked = False

        else:
            admin = False
            blocked = self.settings.get('askomics', 'default_locked_account')

        api_key = self.get_random_string(20)

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
            ?
        )
        '''

        salt = None
        sha512_pw = None

        if not ldap:
            # Create a salt
            salt = self.get_random_string(20)
            # Concat askomics_salt + user_password + salt
            salted_pw = self.settings.get('askomics', 'password_salt') + inputs['password'] + salt
            # hash
            sha512_pw = hashlib.sha512(salted_pw.encode('utf8')).hexdigest()

        # Store user in db
        user_id = database.execute_sql_query(
            query, (ldap, inputs['fname'], inputs['lname'], inputs['username'],
                    inputs['email'], sha512_pw, salt, api_key, admin, blocked), True)

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
            'apikey': api_key
        }


    def get_number_of_users(self):
        """
        get the number of users in the TS
        """

        database = Database(self.app, self.session)
        query = '''
        SELECT COUNT(*)
        FROM users
        '''

        rows = database.execute_sql_query(query)

        return rows[0][0]


    def authenticate_user(self, inputs):
        """
        check if the password is the good password associate with the email

        Parameters
        ----------
        inputs : dict
            username and password

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
        SELECT * FROM users
        WHERE {}=?
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

            user = {
                'id': rows[0][0],
                'ldap': rows[0][1],
                'fname': rows[0][2],
                'lname': rows[0][3],
                'username': rows[0][4],
                'email': rows[0][5],
                'admin': rows[0][9],
                'blocked': rows[0][10],
                'apikey': rows[0][8]
            }
        else:
            error = True
            error_messages.append('Wrong username')

        return {'error': error, 'error_messages': error_messages, 'user': user}


    @staticmethod
    def get_random_string(number):
        """return a random string of n character"""
        # self.log.debug('get_random_key')

        alpabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        return ''.join(random.choice(alpabet) for i in range(number))