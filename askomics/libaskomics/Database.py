"""Contain the Database class
"""
import sqlite3
import textwrap

from askomics.libaskomics.Params import Params


class Database(Params):
    """
    Manage Database connection
    Attributes
    ----------
    database_path : str
        Path to the database file
    """

    def __init__(self, app, session):
        """Store the database path

        Parameters
        ----------
        app :
            flask app
        session :
            flask session
        """
        Params.__init__(self, app, session)

        self.database_path = self.settings.get('askomics', 'database_path')

    def execute_sql_query(self, query, variables=[], get_id=False):
        """
        Execute an sql query to the database

        Parameters
        ----------
        query : str
            The sql query
        variables : List, optional
            Sql variables
        get_id : bool, optional
            Return the last row id

        Returns
        -------
        List
            Result of the query, or last row id
        """

        connection = sqlite3.connect("file:" + self.database_path, uri=True)
        connection.set_trace_callback(self.log.debug)
        cursor = connection.cursor()

        if variables:
            cursor.execute(textwrap.dedent(query), variables)
        else:
            cursor.execute(query)
        rows = cursor.fetchall()
        connection.commit()
        connection.close()

        if get_id:
            return cursor.lastrowid

        return rows

    def init_database(self):
        """Create all tables
        """
        self.create_user_table()
        self.create_galaxy_table()
        self.create_integration_table()
        self.create_query_table()
        self.create_endpoints_table()
        self.create_files_table()
        self.create_datasets_table()

    def create_user_table(self):
        """Create the user table
        """
        query = '''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            ldap boolean,
            fname text,
            lname text,
            username text,
            email text,
            password text,
            salt text,
            apikey text,
            admin boolean,
            blocked boolean
        )
        '''
        self.execute_sql_query(query)

    def create_galaxy_table(self):
        """Create the galaxy table
        """
        query = '''
        CREATE TABLE IF NOT EXISTS galaxy_accounts (
            galaxy_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            url text,
            apikey text,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
        '''
        self.execute_sql_query(query)

    def create_datasets_table(self):
        """Create the datasets table
        """
        query = '''
        CREATE TABLE IF NOT EXISTS datasets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            celery_id INTEGER,
            file_id INTEGER,
            name text,
            graph_name text,
            public boolean,
            status text,
            start int,
            end int,
            ntriples int,
            error_message text,
            FOREIGN KEY(user_id) REFERENCES users(user_id),
            FOREIGN KEY(file_id) REFERENCES files(id)
        )
        '''
        self.execute_sql_query(query)

    def create_integration_table(self):
        """Create the integration table
        """
        query = '''
        CREATE TABLE IF NOT EXISTS integration (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            filename text,
            state text,
            start int,
            end int,
            error text,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
        '''
        self.execute_sql_query(query)

    def create_query_table(self):
        """Create the query table
        """
        query = '''
        CREATE TABLE IF NOT EXISTS query (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            state text,
            start int,
            end int,
            data text,
            file text,
            preview text,
            graph text,
            variates text,
            nrows int,
            error text,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
        '''
        self.execute_sql_query(query)

    def create_endpoints_table(self):
        """Create the endpoints table
        """
        query = '''
        CREATE TABLE IF NOT EXISTS endpoints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name text,
            url text,
            auth text,
            enable boolean,
            message text
        )
        '''
        self.execute_sql_query(query)

    def create_files_table(self):
        """Create the files table
        """
        query = '''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name text,
            type text,
            path text,
            size int,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
        '''
        self.execute_sql_query(query)
