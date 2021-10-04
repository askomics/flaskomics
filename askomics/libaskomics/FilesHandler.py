import os
import time
import requests

from askomics.libaskomics.BedFile import BedFile
from askomics.libaskomics.CsvFile import CsvFile
from askomics.libaskomics.FilesUtils import FilesUtils
from askomics.libaskomics.GffFile import GffFile
from askomics.libaskomics.RdfFile import RdfFile
from askomics.libaskomics.Database import Database
from askomics.libaskomics.Utils import Utils


class FilesHandler(FilesUtils):
    """Handle files

    Attributes
    ----------
    files : list
        list of File
    host_url : string
        AskOmics url, for the triplestore
    upload_path : string
        Upload path
    """

    def __init__(self, app, session, host_url=None, external_endpoint=None, custom_uri=None):
        """init

        Parameters
        ----------
        app : Flask
            flask app
        session :
            AskOmics session, contain the user
        host_url : None, optional
            AskOmics url, for the triplestore
        """
        FilesUtils.__init__(self, app, session)
        self.files = []
        self.host_url = host_url
        self.upload_path = "{}/{}_{}/upload".format(
            self.settings.get("askomics", "data_directory"),
            self.session['user']['id'],
            self.session['user']['username']
        )
        self.date = None
        self.external_endpoint = external_endpoint
        self.custom_uri = custom_uri

    def handle_files(self, files_id):
        """Handle file

        Parameters
        ----------
        files_id : list
            id of files to handle
        """
        files_infos = self.get_files_infos(files_id=files_id, return_path=True)

        for file in files_infos:
            if file['type'] == 'csv/tsv':
                self.files.append(CsvFile(self.app, self.session, file, host_url=self.host_url, external_endpoint=self.external_endpoint, custom_uri=self.custom_uri))
            elif file['type'] == 'gff/gff3':
                self.files.append(GffFile(self.app, self.session, file, host_url=self.host_url, external_endpoint=self.external_endpoint, custom_uri=self.custom_uri))
            elif file['type'] in ('rdf/ttl', 'rdf/xml', 'rdf/nt'):
                self.files.append(RdfFile(self.app, self.session, file, host_url=self.host_url, external_endpoint=self.external_endpoint, custom_uri=self.custom_uri))
            elif file['type'] == 'bed':
                self.files.append(BedFile(self.app, self.session, file, host_url=self.host_url, external_endpoint=self.external_endpoint, custom_uri=self.custom_uri))

    def get_files_infos(self, files_id=None, files_path=None, return_path=False):
        """Get files info

        Parameters
        ----------
        files_id : None, optional
            list of files id
        return_path : bool, optional
            return the path if True

        Returns
        -------
        list
            list of files info
        """
        database = Database(self.app, self.session)

        if files_id:
            subquery_str = '(' + ' OR '.join(['id = ?'] * len(files_id)) + ')'

            query = '''
            SELECT id, name, type, size, path, date, status
            FROM files
            WHERE user_id = ?
            AND {}
            '''.format(subquery_str)

            rows = database.execute_sql_query(query, (self.session['user']['id'], ) + tuple(files_id))

        elif files_path:
            subquery_str = '(' + ' OR '.join(['path = ?'] * len(files_path)) + ')'

            query = '''
            SELECT id, name, type, size, path, date, status
            FROM files
            WHERE user_id = ?
            AND {}
            '''.format(subquery_str)

            rows = database.execute_sql_query(query, (self.session['user']['id'], ) + tuple(files_path))

        else:

            query = '''
            SELECT id, name, type, size, path, date, status
            FROM files
            WHERE user_id = ?
            '''

            rows = database.execute_sql_query(query, (self.session['user']['id'], ))

        files = []
        for row in rows:
            file = {
                'id': row[0],
                'name': row[1],
                'type': row[2],
                'size': row[3],
                'date': row[5],
                'status': row[6]
            }
            if return_path:
                file['path'] = row[4]
            files.append(file)

        return files

    def get_all_files_infos(self):

        if not self.session['user']['admin']:
            return []

        database = Database(self.app, self.session)

        query = '''
        SELECT files.id, files.name, files.type, files.size, files.date, files.status, users.username
        FROM files
        INNER JOIN users ON files.user_id=users.user_id
        '''

        rows = database.execute_sql_query(query, ())

        files = []
        for row in rows:
            file = {
                'id': row[0],
                'name': row[1],
                'type': row[2],
                'size': row[3],
                'date': row[4],
                'status': row[5],
                'user': row[6]
            }
            files.append(file)

        return files

    def get_file_name(self):
        """Get a random file name

        Returns
        -------
        string
            file name
        """
        name = Utils.get_random_string(10)
        file_path = "{}/{}".format(self.upload_path, name)
        # Make sure it is not in use already
        while os.path.isfile(file_path):
            name = Utils.get_random_string(10)
            file_path = "{}/{}".format(self.upload_path, name)

        return name

    def write_data_into_file(self, data, file_name, mode, should_exist=False):
        """Write data into a file

        Parameters
        ----------
        data : string
            data to write
        file_name : string
            Local file name
        mode : string
            open mode (w or a)
        """
        file_path = "{}/{}".format(self.upload_path, file_name)
        if mode == "a":
            if not os.path.isfile(file_path):
                raise Exception("No file exists at this path")
            # Check this path does not already exists in database (meaning, already uploaded)
            if len(self.get_files_infos(files_path=[file_path])) > 0:
                raise Exception("A file with this path already exists in database")

        with open(file_path, mode) as file:
            file.write(data)

    def store_file_info_in_db(self, name, filetype, file_name, size, status="available", task_id=None):
        """Store the file info in the database

        Parameters
        ----------
        name : string
            Name of the file
        filetype : string
            Type (csv ...)
        file_name : string
            Local file name
        size : string
            Size of file
        status: string
            Status of the file (downloading, available, unavailable)
        Returns
        -------
        str
            file id
        """
        file_path = "{}/{}".format(self.upload_path, file_name)

        database = Database(self.app, self.session)
        query = '''
        INSERT INTO files VALUES(
            NULL,
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

        # Type
        if filetype in ('text/tab-separated-values', 'tabular'):
            filetype = 'csv/tsv'
        elif filetype in ('text/turtle', 'ttl'):
            filetype = 'rdf/ttl'
        elif filetype == "text/xml":
            filetype = "rdf/xml"
        elif filetype == "application/n-triples":
            filetype = "rdf/nt"
        elif filetype in ('gff', ):
            filetype = 'gff/gff3'
        else:
            filetype = self.get_type(os.path.splitext(name)[1])

        self.date = int(time.time())

        return database.execute_sql_query(query, (self.session['user']['id'], name, filetype, file_path, size, self.date, status, task_id), get_id=True)

    def update_file_info(self, file_id, size=None, status="", task_id=""):
        """Update file size and status

        Parameters
        ----------
        file_id : str
            File id
        file_size : str
            File current size
        status : str
            File status
        task_id : str
            Current task id
        """

        if not (size is not None or status or task_id):
            return

        query_vars = []
        database = Database(self.app, self.session)

        size_query = ""
        status_query = ""
        task_query = ""

        # Should be a cleaner way of doing this...
        if size is not None:
            size_query = "size=?," if (status or task_id) else "size=?"
            query_vars.append(size)

        if status:
            status_query = "status=?," if task_id else "status=?"
            query_vars.append(status)

        if task_id:
            task_query = "task_id=?"
            query_vars.append(task_id)

        query_vars.append(file_id)

        query = '''
        UPDATE files SET
        {}
        {}
        {}
        WHERE id=?
        '''.format(size_query, status_query, task_query)

        database.execute_sql_query(query, tuple(query_vars))

    def persist_chunk(self, chunk_info):
        """Persist a file by chunk. Store info in db if the chunk is the last

        Parameters
        ----------
        chunk_info : dict
            Info about the chunk

        Returns
        -------
        str
            local filename
        """
        try:
            # 1 chunk file
            if chunk_info["first"] and chunk_info["last"]:
                # Write data into file
                file_name = self.get_file_name()
                self.write_data_into_file(chunk_info["chunk"], file_name, "w")
                # store file info in db
                self.store_file_info_in_db(chunk_info["name"], chunk_info["type"], file_name, chunk_info["size"])
            # first chunk of large file
            elif chunk_info["first"]:
                file_name = self.get_file_name()
                self.write_data_into_file(chunk_info["chunk"], file_name, "w")
            # last chunk of large file
            elif chunk_info["last"]:
                file_name = chunk_info["path"]
                self.write_data_into_file(chunk_info["chunk"], file_name, "a")
                self.store_file_info_in_db(chunk_info["name"], chunk_info["type"], file_name, chunk_info["size"])
            # chunk of large file
            else:
                file_name = chunk_info["path"]
                self.write_data_into_file(chunk_info["chunk"], file_name, "a")

            return file_name
        except Exception as e:
            # Rollback
            try:
                file_path = "{}/{}".format(self.upload_path, file_name)
                # Delete if it does not exists in DB
                if len(self.get_files_infos(files_path=[file_path])) == 0:
                    self.delete_file_from_fs(file_path)
            except Exception:
                pass
            raise(e)

    def download_url(self, url, task_id):
        """Download a file from an URL and insert info in database

        Parameters
        ----------
        url : string
            The file url
        """
        # Get name, path; est and type
        name = url.split("/")[-1]
        file_name = self.get_file_name()
        path = "{}/{}".format(self.upload_path, file_name)
        file_id = self.store_file_info_in_db(name, "", file_name, 0, "downloading", task_id)

        # Get file
        try:
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                count = 0
                with open(path, 'wb') as file:
                    for chunk in r.iter_content(chunk_size=1024 * 1024 * 10):
                        # Update size every ~1GO
                        # + Check quota
                        if count == 100:
                            if self.session['user']['quota'] > 0:
                                total_size = self.get_size_occupied_by_user() + os.path.getsize(path)
                                if total_size >= self.session['user']['quota']:
                                    raise Exception("Exceeded quota")
                            self.update_file_info(file_id, size=os.path.getsize(path))
                            count = 0

                        file.write(chunk)
                        count += 1

            # Update final value
            self.update_file_info(file_id, size=os.path.getsize(path), status="available")

        except Exception:
            self.update_file_info(file_id, size=os.path.getsize(path), status="error")

    def get_type(self, file_ext):
        """Get files type, based on extension

        TODO: sniff file to get type

        Parameters
        ----------
        file_ext : string
            file extension

        Returns
        -------
        string
            file type
        """
        if file_ext in ('.csv', '.tsv', '.tabular'):
            return 'csv/tsv'
        elif file_ext in ('.gff', '.gff2', '.gff3'):
            return 'gff/gff3'
        elif file_ext in ('.bed', ):
            return 'bed'
        elif file_ext in ('.ttl', '.turtle'):
            return 'rdf/ttl'
        elif file_ext in ('.xml', ):
            return 'rdf/xml'
        elif file_ext in ('.nt', ):
            return 'rdf/nt'
        # Default is csv
        return 'csv/tsv'

    def delete_files(self, files_id, admin=False):
        """Delete files from database and filesystem

        Parameters
        ----------
        files_id : list
            list of file id

        Returns
        -------
        list
            list of files info
        """
        for fid in files_id:
            file_path = self.get_file_path(fid)
            if os.path.isfile(file_path):
                self.delete_file_from_fs(file_path)
            self.delete_file_from_db(fid, admin=admin)

        if admin and self.session['user']['admin']:
            return self.get_all_files_infos()
        else:
            return self.get_files_infos()

    def delete_file_from_db(self, file_id, admin=False):
        """remove a file for the database

        Parameters
        ----------
        file_id : int
            the file id to remove
        """

        database = Database(self.app, self.session)

        if admin and self.session['user']['admin']:
            query_params = (file_id,)
            where_query = ""

        else:
            query_params = (file_id, self.session['user']['id'])
            where_query = "AND user_id=?"

        query = '''
        DELETE FROM files
        WHERE id=?
        {}
        '''.format(where_query)

        database.execute_sql_query(query, query_params)

    def delete_file_from_fs(self, file_path):
        """Delete a file from filesystem

        Parameters
        ----------
        file_path : string
            Path to the file
        """
        os.remove(file_path)

    def get_file_path(self, file_id):
        """Get the file path with id

        Parameters
        ----------
        file_id : int
            the file id

        Returns
        -------
        string
            file path
        """
        database = Database(self.app, self.session)

        query = '''
        SELECT path
        FROM files
        WHERE id=?
        '''

        row = database.execute_sql_query(query, (file_id, ))

        return row[0][0]
