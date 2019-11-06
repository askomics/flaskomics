"""conftest"""
import os
import shutil
import tempfile
import json

from askomics.app import create_app, create_celery
from askomics.libaskomics.Dataset import Dataset
from askomics.libaskomics.FilesHandler import FilesHandler
from askomics.libaskomics.FilesUtils import FilesUtils
from askomics.libaskomics.LocalAuth import LocalAuth
from askomics.libaskomics.SparqlQueryLauncher import SparqlQueryLauncher
from askomics.libaskomics.Start import Start
from askomics.libaskomics.Result import Result
from askomics.libaskomics.SparqlQueryBuilder import SparqlQueryBuilder

import pytest


@pytest.fixture
def client():
    """Summary

    Returns
    -------
    TYPE
        Description
    """
    client = Client()

    yield client

    # teardown
    client.clean()


class Client(object):
    """Fixtrue class

    Attributes
    ----------
    app : TYPE
        Description
    client : TYPE
        Description
    config : TYPE
        Description
    ctx : TYPE
        Description
    db_path : TYPE
        Description
    dir_path : TYPE
        Description
    """

    def __init__(self, config="config/askomics.test.ini"):
        """Summary

        Parameters
        ----------
        config : str, optional
            Description
        """
        # Config
        self.config = config
        self.dir_path = tempfile.mkdtemp(prefix="askotest_")
        self.db_path = "{}/database.db".format(self.dir_path)

        # create app
        self.app = create_app(config=self.config)
        create_celery(self.app)
        self.app.iniconfig.set('askomics', 'data_directory', self.dir_path)
        self.app.iniconfig.set('askomics', 'database_path', self.db_path)

        # context
        self.ctx = self.app.app_context()
        self.ctx.push()

        # Client
        self.client = self.app.test_client()
        self.session = {}

        self.init_database()

    def get_config(self, section, entry, boolean=False):
        """Summary

        Parameters
        ----------
        section : TYPE
            Description
        entry : TYPE
            Description
        boolean : bool, optional
            Description

        Returns
        -------
        TYPE
            Description
        """
        if boolean:
            return self.app.iniconfig.getboolean(section, entry)
        return self.app.iniconfig.get(section, entry)

    def get_client(self):
        """Summary

        Returns
        -------
        TYPE
            Description
        """
        return self.client

    def log_user(self, username):
        """Summary

        Parameters
        ----------
        username : TYPE
            Description
        """
        with self.client.session_transaction() as sess:
            sess["user"] = {
                'id': 1 if username == "jdoe" else 2,
                'ldap': False,
                'fname': "John" if username == "jdoe" else "Jane",
                'lname': "Doe" if username == "jdoe" else "Smith",
                'username': username,
                'email': "{}@askomics.org".format(username),
                'admin': True if username == "jdoe" else False,
                'blocked': False,
                'quota': 0,
                'apikey': "000000000{}".format("1" if username == "jdoe" else "2"),
                "galaxy": None
            }

        self.session = sess

    def init_database(self):
        """Init database"""
        starter = Start(self.app, self.session)
        starter.start()

    def create_user(self, username):
        """Summary

        Parameters
        ----------
        username : TYPE
            Description

        Returns
        -------
        TYPE
            Description
        """
        uinfo = {
            "fname": "John" if username == "jdoe" else "Jane",
            "lname": "Doe" if username == "jdoe" else "Smith",
            "username": "jdoe" if username == "jdoe" else "jsmith",
            "password": "iamjohndoe" if username == "jdoe" else "iamjanesmith",
            "salt": "0000000000",
            "email": "jdoe@askomics.org" if username == "jdoe" else "jsmith@askomics.org",
            "apikey": "0000000001" if username == "jdoe" else "0000000002",
            "galaxy": None if username == "jdoe" else None,
            "quota": 0 if username == "jdoe" else 0,
        }

        auth = LocalAuth(self.app, self.session)
        user = auth.persist_user(uinfo)
        auth.create_user_directories(user["id"], user["username"])

        return user

    def create_two_users(self):
        """Create jdoe and jsmith"""
        self.create_user("jdoe")
        self.create_user("jsmith")

    def upload_file(self, file_path):
        """Summary

        Parameters
        ----------
        file_path : TYPE
            Description

        Returns
        -------
        TYPE
            Description
        """
        file_name = file_path.split("/")[-1]
        file_extension = os.path.splitext(file_path)[1]

        file_type = {
            ".tsv": "text/tab-separated-values",
            ".csv": "text/tab-separated-values"
        }

        with open(file_path, 'r') as file_content:
            content = file_content.read()

        file_data = {
            "first": True,
            "last": True,
            "chunk": content,
            "name": file_name,
            "type": file_type[file_extension],
            "size": os.path.getsize(file_path)
        }

        files = FilesHandler(self.app, self.session)
        filepath = files.persist_chunk(file_data)
        filedate = files.date

        return {
            "file_path": filepath,
            "file_date": filedate
        }

    def integrate_file(self, info, public=False):
        """Summary

        Parameters
        ----------
        info : TYPE
            Description

        Returns
        -------
        TYPE
            Description
        """
        files_handler = FilesHandler(self.app, self.session)
        files_handler.handle_files([info["id"], ])

        for file in files_handler.files:

            dataset_info = {
                "celery_id": "000000000",
                "file_id": file.id,
                "name": file.name,
                "graph_name": file.file_graph,
                "public": public
            }

            dataset = Dataset(self.app, self.session, dataset_info)
            dataset.save_in_db()

            file.integrate(info["columns_type"], public=public)

            # done
            dataset.update_in_db("success")
            dataset.set_info_from_db()

            return {
                "timestamp": file.timestamp,
                "start": dataset.start,
                "end": dataset.end
            }

    def upload(self):
        """Upload files

        Returns
        -------
        dict
            Files info
        """
        up_transcripts = self.upload_file("test-data/transcripts.tsv")
        up_de = self.upload_file("test-data/de.tsv")
        up_qtl = self.upload_file("test-data/qtl.tsv")

        return {
            "transcripts": {
                "upload": up_transcripts,
            },
            "de": {
                "upload": up_de,
            },
            "qtl": {
                "upload": up_qtl,
            }
        }

    def upload_and_integrate(self):
        """Summary

        Returns
        -------
        TYPE
            Description
        """
        # upload
        up_transcripts = self.upload_file("test-data/transcripts.tsv")
        up_de = self.upload_file("test-data/de.tsv")
        up_qtl = self.upload_file("test-data/qtl.tsv")

        # integrate
        int_transcripts = self.integrate_file({
            "id": 1,
            "columns_type": ["start_entity", "category", "text", "reference", "start", "end", "category", "strand", "text", "text"]
        })

        int_de = self.integrate_file({
            "id": 2,
            "columns_type": ["start_entity", "directed", "numeric", "numeric", "numeric", "text", "numeric", "numeric", "numeric", "numeric"]
        })

        int_qtl = self.integrate_file({
            "id": 3,
            "columns_type": ["start_entity", "ref", "start", "end"]
        })

        return {
            "transcripts": {
                "upload": up_transcripts,
                "timestamp": int_transcripts["timestamp"],
                "start": int_transcripts["start"],
                "end": int_transcripts["end"]
            },
            "de": {
                "upload": up_de,
                "timestamp": int_de["timestamp"],
                "start": int_de["start"],
                "end": int_de["end"]
            },
            "qtl": {
                "upload": up_qtl,
                "timestamp": int_qtl["timestamp"],
                "start": int_qtl["start"],
                "end": int_qtl["end"]
            }
        }

    def create_result(self):
        """Create a result entry in db

        Returns
        -------
        dict
            Result info
        """
        with open("tests/data/graphState_simple_query.json", "r") as file:
            file_content = file.read()

        json_query = json.loads(file_content)

        info = {
            "graph_state": json_query,
            "celery_id": '00000000-0000-0000-0000-000000000000'
        }

        result = Result(self.app, self.session, info)

        # Save job in database database
        result.save_in_db()

        # launch query
        query_builder = SparqlQueryBuilder(self.app, self.session)
        query_launcher = SparqlQueryLauncher(self.app, self.session)
        query = query_builder.build_query_from_json(json_query)
        headers, results = query_launcher.process_query(query)

        # write result to a file
        result.save_result_in_file(headers, results)

        # Update database status
        result.update_db_status("success")

        return {
            "id": result.id,
            "path": result.file_path,
            "start": result.start,
            "end": result.end
        }

    def delete_data_dir(self):
        """remove data directory"""
        shutil.rmtree(self.dir_path)

    def clean_triplestore(self):
        """remove all test graph in the triplestore"""
        query = '''
        SELECT ?graph
        WHERE {{
            GRAPH ?graph {{ ?s ?p ?o . }}
            FILTER (strStarts(str(?graph), "{}"))

        }}
        '''.format(self.get_config("triplestore", "default_graph"))

        query_launcher = SparqlQueryLauncher(self.app, {})

        header, data = query_launcher.process_query(query)
        for result in data:
            query_launcher.drop_dataset(result["graph"])

    def clean(self):
        """Clean"""
        self.delete_data_dir()
        self.clean_triplestore()

    def get_size_occupied_by_user(self):
        """Get size of logged user

        Returns
        -------
        int
            Size
        """
        files_utils = FilesUtils(self.app, self.session)
        return files_utils.get_size_occupied_by_user() if "user" in self.session else None
