"""conftest"""
import os
import shutil
import tempfile
import json
import random
import time

from bioblend.galaxy import GalaxyInstance

from askomics.app import create_app, create_celery
from askomics.libaskomics.Database import Database
from askomics.libaskomics.Dataset import Dataset
from askomics.libaskomics.FilesHandler import FilesHandler
from askomics.libaskomics.FilesUtils import FilesUtils
from askomics.libaskomics.LocalAuth import LocalAuth
from askomics.libaskomics.PrefixManager import PrefixManager
from askomics.libaskomics.OntologyManager import OntologyManager
from askomics.libaskomics.SparqlQueryLauncher import SparqlQueryLauncher
from askomics.libaskomics.Start import Start
from askomics.libaskomics.Result import Result
from askomics.libaskomics.SparqlQuery import SparqlQuery
from askomics.libaskomics.Utils import Utils

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

        # Galaxy
        self.gurl = "http://localhost:8081"
        self.gkey = "fakekey"
        self.galaxy_history = None

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

    def log_user(self, username, quota=0, blocked=False, ldap=False):
        """Summary

        Parameters
        ----------
        username : TYPE
            Description
        """
        galaxy = None
        if username == "jdoe":
            galaxy = {"url": "http://localhost:8081", "apikey": "fakekey"}

        with self.client.session_transaction() as sess:
            sess["user"] = {
                'id': 1 if username == "jdoe" else 2,
                'ldap': ldap,
                'fname': "John" if username == "jdoe" else "Jane",
                'lname': "Doe" if username == "jdoe" else "Smith",
                'username': username,
                'email': "{}@askomics.org".format(username),
                'admin': True if username == "jdoe" else False,
                'blocked': blocked,
                'quota': quota,
                'apikey': "000000000{}".format("1" if username == "jdoe" else "2"),
                "galaxy": galaxy
            }

        self.session = sess

    def logout(self):
        """logout user"""
        with self.client.session_transaction() as sess:
            sess.pop("user", None)
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
        galaxy = None
        if username == "jdoe":
            galaxy = {"url": "http://localhost:8081", "apikey": "fakekey"}

        uinfo = {
            "fname": "John" if username == "jdoe" else "Jane",
            "lname": "Doe" if username == "jdoe" else "Smith",
            "username": "jdoe" if username == "jdoe" else "jsmith",
            "password": "iamjohndoe" if username == "jdoe" else "iamjanesmith",
            "salt": "0000000000",
            "email": "jdoe@askomics.org" if username == "jdoe" else "jsmith@askomics.org",
            "apikey": "0000000001" if username == "jdoe" else "0000000002",
            "galaxy": None,
            "quota": 0 if username == "jdoe" else 0,
        }

        auth = LocalAuth(self.app, self.session)
        user = auth.persist_user(uinfo)
        if galaxy:
            self.session["user"] = user
            user = auth.add_galaxy_account(user, galaxy["url"], galaxy["apikey"])["user"]
            self.session = {}
        auth.create_user_directories(user["id"], user["username"])

        return user

    def set_config(self, entry, key, value):
        """update ini config"""
        self.app.iniconfig.set(entry, key, value)

    def create_two_users(self):
        """Create jdoe and jsmith"""
        self.create_user("jdoe")
        self.create_user("jsmith")

    def create_reset_token(self, username, old_token=False):
        """Create a reset token"""
        if old_token:
            old_timestamp = int(time.time()) - 14400
            token = "{}:{}".format(old_timestamp, Utils.get_random_string(20))
            database = Database(self.app, self.session)
            query = """
            UPDATE users
            SET reset_token=?
            WHERE username=?
            """
            database.execute_sql_query(query, (token, username))
            return token
        else:
            auth = LocalAuth(self.app, self.session)
            return auth.create_reset_token(username)

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
            ".csv": "text/tab-separated-values",
            ".gff3": "null",
            ".bed": "null"
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

    def upload_file_url(self, file_url):
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

        files = FilesHandler(self.app, self.session)
        files.download_url(file_url, "1")
        return files.date

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

            if file.type == "csv/tsv":
                file.integrate(dataset.id, info["columns_type"], public=public)
            elif file.type == "gff/gff3":
                file.integrate(dataset.id, info["entities"], public=public)
            elif file.type == "bed":
                file.integrate(dataset.id, info["entity_name"], public=public)

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
        up_gene_gff = self.upload_file("test-data/gene.gff3")
        up_bed = self.upload_file("test-data/gene.bed")

        return {
            "transcripts": {
                "upload": up_transcripts,
            },
            "de": {
                "upload": up_de,
            },
            "qtl": {
                "upload": up_qtl,
            },
            "gene": {
                "upload": up_gene_gff,
            },
            "bed": {
                "upload": up_bed,
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
        up_gff = self.upload_file("test-data/gene.gff3")
        up_bed = self.upload_file("test-data/gene.bed")

        # integrate
        int_transcripts = self.integrate_file({
            "id": 1,
            "columns_type": ["start_entity", "label", "category", "text", "reference", "start", "end", "category", "strand", "text", "text", "date"]
        })

        int_de = self.integrate_file({
            "id": 2,
            "columns_type": ["start_entity", "directed", "numeric", "numeric", "numeric", "text", "numeric", "numeric", "numeric", "numeric"]
        })

        int_qtl = self.integrate_file({
            "id": 3,
            "columns_type": ["start_entity", "ref", "start", "end"]
        })

        int_gff = self.integrate_file({
            "id": 4,
            "entities": ["gene", "transcript"]
        })

        int_bed = self.integrate_file({
            "id": 5,
            "entity_name": "gene"
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
            },
            "gff": {
                "upload": up_gff,
                "timestamp": int_gff["timestamp"],
                "start": int_gff["start"],
                "end": int_gff["end"]
            },
            "bed": {
                "upload": up_bed,
                "timestamp": int_bed["timestamp"],
                "start": int_bed["start"],
                "end": int_bed["end"]
            }
        }

    def create_result(self, has_form=False):
        """Create a result entry in db

        Returns
        -------
        dict
            Result info
        """
        # Query: transcript concerned by DE and included in QTL

        if has_form:
            with open("tests/data/graphState_simple_query_form.json", "r") as file:
                file_content = file.read()

        else:
            with open("tests/data/graphState_simple_query.json", "r") as file:
                file_content = file.read()

        json_query = json.loads(file_content)

        # Get query and endpoints and graphs of the query
        query = SparqlQuery(self.app, self.session, json_query)
        query_launcher = SparqlQueryLauncher(self.app, self.session)
        query.build_query_from_json(preview=False, for_editor=False)

        info = {
            "graph_state": json_query,
            "query": query.sparql,
            "celery_id": '00000000-0000-0000-0000-000000000000',
            "graphs": query.graphs,
            "endpoints": query.endpoints
        }

        # Save job in database database
        result = Result(self.app, self.session, info)

        result.save_in_db()

        # Execute query and write result to file
        headers, results = query_launcher.process_query(query.sparql)
        file_size = result.save_result_in_file(headers, results)

        # Update database status
        result.update_db_status("success", size=file_size)

        return {
            "id": result.id,
            "path": result.file_path,
            "start": result.start,
            "end": result.end,
            "size": file_size
        }

    def publicize_result(self, result_id, public=True):
        """Publicize a result"""

        result_info = {"id": result_id}
        result = Result(self.app, self.session, result_info)
        result.publish_query(public)

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
        if self.galaxy_history:
            self.delete_galaxy_history()

    def get_size_occupied_by_user(self):
        """Get size of logged user

        Returns
        -------
        int
            Size
        """
        files_utils = FilesUtils(self.app, self.session)
        return files_utils.get_size_occupied_by_user() if "user" in self.session else None

    def init_galaxy(self):
        """Create a new galaxy history"""
        history_name = "askotest_{}".format(self.get_random_string(5))

        galaxy = GalaxyInstance(self.gurl, self.gkey)
        self.galaxy_history = galaxy.histories.create_history(history_name)

    def upload_dataset_into_galaxy(self):
        """Upload a dataset into galaxy"""
        if not self.galaxy_history:
            self.init_galaxy()
        file_path = "test-data/transcripts.tsv"
        filename = "transcripts.tsv"

        galaxy = GalaxyInstance(self.gurl, self.gkey)
        return galaxy.tools.upload_file(file_path, self.galaxy_history['id'], file_name=filename, file_type='tabular')

    def upload_query_into_galaxy(self):
        """Upload a json query into galaxy"""
        if not self.galaxy_history:
            self.init_galaxy()
        file_path = "tests/data/graphState_simple_query.json"
        filename = "graphstate.json"

        galaxy = GalaxyInstance(self.gurl, self.gkey)
        return galaxy.tools.upload_file(file_path, self.galaxy_history['id'], file_name=filename, file_type='json')

    def delete_galaxy_history(self):
        """Delete the galaxy history"""
        galaxy = GalaxyInstance(self.gurl, self.gkey)
        galaxy.histories.delete_history(self.galaxy_history["id"], purge=True)

    def create_prefix(self):
        """Create custom prefix"""
        pm = PrefixManager(self.app, self.session)
        pm.add_custom_prefix("OBO", "http://purl.obolibrary.org/obo/")

    def create_ontology(self):
        """Create ontology"""
        om = OntologyManager(self.app, self.session)
        om.add_ontology("Open Biological and Biomedical Ontology", "http://purl.obolibrary.org/obo/agro.owl", "OBO")

    @staticmethod
    def get_random_string(number):
        """return a random string of n character

        Parameters
        ----------
        number : int
            number of character of the random string

        Returns
        -------
        str
            a random string of n chars
        """
        alpabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        return ''.join(random.choice(alpabet) for i in range(number))
