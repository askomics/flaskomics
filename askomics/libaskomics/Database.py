"""Contain the Database class"""
import sqlite3
import textwrap

from askomics.libaskomics.Params import Params
from askomics.libaskomics.Utils import Utils


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
        if self.settings.getboolean('askomics', 'debug'):
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
        """Create all tables"""
        self.create_user_table()
        self.create_galaxy_table()
        self.create_integration_table()
        self.create_results_table()
        self.create_endpoints_table()
        self.create_files_table()
        self.create_datasets_table()
        self.create_abstraction_table()
        self.create_prefixes_table()
        self.create_ontologies_table()

    def create_user_table(self):
        """Create the user table"""
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
            blocked boolean,
            quota INTEGER,
            reset_token text,
            last_action INTEGER
        )
        '''
        self.execute_sql_query(query)
        self.update_users_table()

    def update_users_table(self):
        """Add the quota col on the users table

        Update the users table for the instance who don't have this column
        """
        default_quota = Utils.humansize_to_bytes(self.settings.get("askomics", "quota"))

        query = '''
        ALTER TABLE users
        ADD quota INTEGER NOT NULL DEFAULT {}
        '''.format(default_quota)
        try:
            self.execute_sql_query(query)
        except Exception:
            pass

        query = '''
        ALTER TABLE users
        ADD reset_token text NULL
        DEFAULT(null)
        '''
        try:
            self.execute_sql_query(query)
        except Exception:
            pass

        query = '''
        ALTER TABLE users
        ADD last_action INTEGER NULL
        DEFAULT(null)
        '''
        try:
            self.execute_sql_query(query)
        except Exception:
            pass

    def create_galaxy_table(self):
        """Create the galaxy table"""
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
        """Create the datasets table"""
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
        self.update_datasets_table()

    def update_datasets_table(self):
        """Add cols on the datasets table"""
        query = '''
        ALTER TABLE datasets
        ADD traceback text NULL
        DEFAULT(null)
        '''

        try:
            self.execute_sql_query(query)
        except Exception:
            pass

        query = '''
        ALTER TABLE datasets
        ADD percent real NULL
        DEFAULT(null)
        '''

        try:
            self.execute_sql_query(query)
        except Exception:
            pass

    def create_integration_table(self):
        """Create the integration table"""
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

    def create_results_table(self):
        """Create the results table"""
        query = '''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            celery_id text,
            status text,
            path text,
            start int,
            end int,
            graph_state text,
            nrows int,
            error text,
            public boolean,
            description text,
            size int,
            sparql_query text,
            traceback text,
            graphs_and_endpoints text,
            template boolean,
            has_form_attr boolean,
            form boolean,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
        '''
        self.execute_sql_query(query)
        self.update_results_table()

    def update_results_table(self):
        """Add the size and sparql_query cols on the results table"""
        query = '''
        ALTER TABLE results
        ADD size int NULL
        DEFAULT(null)
        '''

        try:
            self.execute_sql_query(query)
        except Exception:
            pass

        query = '''
        ALTER TABLE results
        ADD sparql_query text NULL
        DEFAULT(null)
        '''

        try:
            self.execute_sql_query(query)
        except Exception:
            pass

        query = '''
        ALTER TABLE results
        ADD traceback text NULL
        DEFAULT(null)
        '''

        try:
            self.execute_sql_query(query)
        except Exception:
            pass

        query = '''
        ALTER TABLE results
        ADD graphs_and_endpoints text NULL
        DEFAULT(null)
        '''

        try:
            self.execute_sql_query(query)
        except Exception:
            pass

        query = '''
        ALTER TABLE results
        ADD template boolean NULL
        DEFAULT(0)
        '''

        try:
            self.execute_sql_query(query)
        except Exception:
            pass

        query = '''
        ALTER TABLE results
        ADD has_form_attr boolean NULL
        DEFAULT(0)
        '''

        try:
            self.execute_sql_query(query)
        except Exception:
            pass

        query = '''
        ALTER TABLE results
        ADD form boolean NULL
        DEFAULT(0)
        '''

        try:
            self.execute_sql_query(query)
        except Exception:
            pass

    def create_endpoints_table(self):
        """Create the endpoints table"""
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
        """Create the files table"""
        query = '''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name text,
            type text,
            path text,
            size int,
            date int,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
        '''
        self.execute_sql_query(query)

        query = '''
        ALTER TABLE files
        ADD status text NOT NULL
        DEFAULT('available')
        '''

        try:
            self.execute_sql_query(query)
        except Exception:
            pass

        query = '''
        ALTER TABLE files
        ADD task_id text NULL
        DEFAULT(NULL)
        '''

        try:
            self.execute_sql_query(query)
        except Exception:
            pass

    def create_abstraction_table(self):
        """Create abstraction table"""
        query = """
        CREATE TABLE IF NOT EXISTS abstraction (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            abstraction text,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
        """
        self.execute_sql_query(query)

    def create_prefixes_table(self):
        """Create the prefix table"""
        query = '''
        CREATE TABLE IF NOT EXISTS prefixes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prefix text NOT NULL,
            namespace text NOT NULL
        )
        '''
        self.execute_sql_query(query)

    def create_ontologies_table(self):
        """Create the ontologies table"""
        query = '''
        CREATE TABLE IF NOT EXISTS ontologies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name text NOT NULL,
            uri text NOT NULL,
            short_name text NOT NULL,
            type text DEFAULT 'local'
        )
        '''
        self.execute_sql_query(query)
