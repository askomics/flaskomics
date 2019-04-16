"""conftest"""
import os
import shutil
import tempfile

from askomics.app import create_app, create_celery
from askomics.libaskomics.Dataset import Dataset
from askomics.libaskomics.FilesHandler import FilesHandler
from askomics.libaskomics.LocalAuth import LocalAuth
from askomics.libaskomics.SparqlQueryLauncher import SparqlQueryLauncher
from askomics.libaskomics.Start import Start

import pytest


def init_database(dir_path):
    """Initalize the AskOmics db in a tmp directory

    Parameters
    ----------
    dir_path : string
        AskOmics data directory path
    """
    current_app = create_app(config='config/askomics.test.ini')

    db_path = "{}/database.db".format(dir_path)

    current_app.iniconfig.set('askomics', 'data_directory', dir_path)
    current_app.iniconfig.set('askomics', 'database_path', db_path)

    # Create data dir and init database
    starter = Start(current_app, {})
    starter.start()


def create_users(dir_path):
    """Initialize the AskOmics database and create users inside

    Parameters
    ----------
    dir_path : string
        AskOmics data directory path
    """
    current_app = create_app(config='config/askomics.test.ini')

    db_path = "{}/database.db".format(dir_path)

    current_app.iniconfig.set('askomics', 'data_directory', dir_path)
    current_app.iniconfig.set('askomics', 'database_path', db_path)

    # Create data dir and init database
    starter = Start(current_app, {})
    starter.start()

    # Fill the DB with users
    uinfo_1 = {
        "fname": "John",
        "lname": "Doe",
        "username": "jdoe",
        "password": "iamjohndoe",
        "salt": "0000000000",
        "email": "jdoe@askomics.org",
        "apikey": "0000000000"
    }
    uinfo_2 = {
        "fname": "Jane",
        "lname": "Smith",
        "username": "jsmith",
        "password": "iamjanesmith",
        "salt": "0000000000",
        "email": "jsmith@askomics.org",
        "apikey": "0000000000"
    }

    auth = LocalAuth(current_app, {})
    user_1 = auth.persist_user(uinfo_1)
    auth.create_user_directories(user_1["id"], user_1["username"])
    user_2 = auth.persist_user(uinfo_2)
    auth.create_user_directories(user_2["id"], user_2["username"])


def load_file(dir_path, file_path, user_session):
    """Load a file into AskOmics

    Parameters
    ----------
    dir_path : string
        AskOmics data directory
    file_path : string
        Path of file to upload
    user_session : dict
        user session

    Returns
    -------
    string
        Path of uploaded file
    """
    current_app = create_app(config='config/askomics.test.ini')

    db_path = "{}/database.db".format(dir_path)

    current_app.iniconfig.set('askomics', 'data_directory', dir_path)
    current_app.iniconfig.set('askomics', 'database_path', db_path)

    with open(file_path, 'r') as content_file:
        content = content_file.read()

    file_data = {
        "first": True,
        "last": True,
        "chunk": content,
        "name": "gene",
        "type": "csv/tsv",
        "size": os.path.getsize(file_path)
    }

    files = FilesHandler(current_app, user_session)
    return files.persist_chunk(file_data)


def interate_dataset(dir_path, file_info, user_session, public):
    """integrate some files"""
    current_app = create_app(config='config/askomics.test.ini')

    db_path = "{}/database.db".format(dir_path)

    current_app.iniconfig.set('askomics', 'data_directory', dir_path)
    current_app.iniconfig.set('askomics', 'database_path', db_path)

    files_handler = FilesHandler(current_app, user_session)
    files_handler.handle_files([file_info["id"], ])

    for file in files_handler.files:

        dataset_info = {
            "celery_id": "000000000",
            "file_id": file.id,
            "name": file.name,
            "graph_name": file.file_graph,
            "public": public
        }

        dataset = Dataset(current_app, user_session, dataset_info)
        dataset.save_in_db()

        file.integrate(file_info["columns_type"], public=public)
        file_timestamp = file.timestamp

        # done
        dataset.update_in_db()

        return file_timestamp


@pytest.fixture
def app():
    """app"""
    current_app = create_app(config='config/askomics.test.ini')
    create_celery(current_app)

    # dirpath in config
    dir_path = tempfile.mkdtemp(prefix="askotest_")
    db_path = "{}/database.db".format(dir_path)

    current_app.iniconfig.set('askomics', 'data_directory', dir_path)
    current_app.iniconfig.set('askomics', 'database_path', db_path)

    # Establish an application context before running the tests.
    ctx = current_app.app_context()
    ctx.push()

    return current_app


@pytest.fixture
def client_no_db():
    """client, with no db"""
    current_app = create_app(config='config/askomics.test.ini')
    create_celery(current_app)

    # dirpath in config
    dir_path = tempfile.mkdtemp(prefix="askotest_")
    db_path = "{}/database.db".format(dir_path)

    current_app.iniconfig.set('askomics', 'data_directory', dir_path)
    current_app.iniconfig.set('askomics', 'database_path', db_path)

    # Establish an application context before running the tests.
    ctx = current_app.app_context()
    ctx.push()

    client = current_app.test_client()

    yield client

    shutil.rmtree(dir_path)


@pytest.fixture
def client_empty_db():
    """client, with an empty db"""
    current_app = create_app(config='config/askomics.test.ini')
    create_celery(current_app)

    # dirpath in config
    dir_path = tempfile.mkdtemp(prefix="askotest_")
    db_path = "{}/database.db".format(dir_path)

    current_app.iniconfig.set('askomics', 'data_directory', dir_path)
    current_app.iniconfig.set('askomics', 'database_path', db_path)

    init_database(dir_path)

    # Establish an application context before running the tests.
    ctx = current_app.app_context()
    ctx.push()

    client = current_app.test_client()

    yield client

    shutil.rmtree(dir_path)


@pytest.fixture
def client_filled_db():
    """Client, db with users inside"""
    current_app = create_app(config='config/askomics.test.ini')
    create_celery(current_app)

    # dirpath in config
    dir_path = tempfile.mkdtemp(prefix="askotest_")
    db_path = "{}/database.db".format(dir_path)

    current_app.iniconfig.set('askomics', 'data_directory', dir_path)
    current_app.iniconfig.set('askomics', 'database_path', db_path)

    create_users(dir_path)

    # Establish an application context before running the tests.
    ctx = current_app.app_context()
    ctx.push()

    client = current_app.test_client()

    yield client

    shutil.rmtree(dir_path)


@pytest.fixture
def client_logged_as_jdoe():
    """Logged client (jdoe, admin), db with users inside"""
    current_app = create_app(config='config/askomics.test.ini')
    create_celery(current_app)

    # dirpath in config
    dir_path = tempfile.mkdtemp(prefix="askotest_")
    db_path = "{}/database.db".format(dir_path)

    current_app.iniconfig.set('askomics', 'data_directory', dir_path)
    current_app.iniconfig.set('askomics', 'database_path', db_path)

    create_users(dir_path)

    # Establish an application context before running the tests.
    ctx = current_app.app_context()
    ctx.push()

    client = current_app.test_client()

    # log as jdoe
    with client.session_transaction() as sess:
        sess["user"] = {
            'id': 1,
            'ldap': False,
            'fname': "John",
            'lname': "Doe",
            'username': "jdoe",
            'email': "jdoe@askomics.org",
            'admin': True,
            'blocked': False,
            'apikey': "0000000000"
        }

    yield client

    shutil.rmtree(dir_path)


@pytest.fixture
def client_logged_as_jsmith():
    """Logged client (jsmith, non admin), db with users inside"""
    current_app = create_app(config='config/askomics.test.ini')
    create_celery(current_app)

    # dirpath in config
    dir_path = tempfile.mkdtemp(prefix="askotest_")
    db_path = "{}/database.db".format(dir_path)

    current_app.iniconfig.set('askomics', 'data_directory', dir_path)
    current_app.iniconfig.set('askomics', 'database_path', db_path)

    create_users(dir_path)

    # Establish an application context before running the tests.
    ctx = current_app.app_context()
    ctx.push()

    client = current_app.test_client()

    # log as jsmith
    with client.session_transaction() as sess:
        sess["user"] = {
            'id': 1,
            'ldap': False,
            'fname': "Jane",
            'lname': "Smith",
            'username': "jsmith",
            'email': "jsmith@askomics.org",
            'admin': False,
            'blocked': False,
            'apikey': "0000000000"
        }

    yield client

    shutil.rmtree(dir_path)


@pytest.fixture
def client_logged_as_jdoe_with_data():
    """Logged client (jdoe, admin), db with users inside, and data loaded and integrated"""
    current_app = create_app(config='config/askomics.test.ini')
    create_celery(current_app)

    # dirpath in config
    dir_path = tempfile.mkdtemp(prefix="askotest_")
    db_path = "{}/database.db".format(dir_path)

    current_app.iniconfig.set('askomics', 'data_directory', dir_path)
    current_app.iniconfig.set('askomics', 'database_path', db_path)

    create_users(dir_path)

    # Establish an application context before running the tests.
    ctx = current_app.app_context()
    ctx.push()

    client = current_app.test_client()

    # store dirpath
    client.dir_path = dir_path

    # log as jsmith
    # log as jdoe
    with client.session_transaction() as sess:
        sess["user"] = {
            'id': 1,
            'ldap': False,
            'fname': "John",
            'lname': "Doe",
            'username': "jdoe",
            'email': "jdoe@askomics.org",
            'admin': True,
            'blocked': False,
            'apikey': "0000000000"
        }
        user_session = sess

    # Upload people.tsv
    fpath = load_file(dir_path, 'test-data/gene.tsv', user_session)
    client.gene_file_path = fpath

    # Integrate
    file_info = {
        "id": 1,
        "columns_type": ["start_entity", "organism", "chromosome", "strand", "start", "end"]
    }

    gene_timestamp = interate_dataset(dir_path, file_info, user_session, False)
    client.gene_timestamp = gene_timestamp

    yield client

    shutil.rmtree(dir_path)
    # clean triplestore
    query_launcher = SparqlQueryLauncher(current_app, user_session)
    query_launcher.drop_dataset('urn:sparql:askomics_test:1_jdoe:gene_{}'.format(gene_timestamp))
