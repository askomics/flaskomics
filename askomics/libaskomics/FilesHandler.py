import os

from askomics.libaskomics.CsvFile import CsvFile
from askomics.libaskomics.Database import Database
from askomics.libaskomics.Params import Params
from askomics.libaskomics.Utils import Utils


class FilesHandler(Params):
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

    def __init__(self, app, session, host_url=None):
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
        Params.__init__(self, app, session)
        self.files = []
        self.host_url = host_url
        self.upload_path = "{}/{}_{}/upload".format(
            self.settings.get("askomics", "data_directory"),
            self.session['user']['id'],
            self.session['user']['username']
        )

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
                self.files.append(CsvFile(self.app, self.session, file, host_url=self.host_url))

    def get_files_infos(self, files_id=None, return_path=False):
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
            SELECT id, name, type, size, path
            FROM files
            WHERE user_id = ?
            AND {}
            '''.format(subquery_str)

            rows = database.execute_sql_query(query, (self.session['user']['id'], ) + tuple(files_id))

        else:

            query = '''
            SELECT id, name, type, size, path
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
                'size': row[3]
            }
            if return_path:
                file['path'] = row[4]
            files.append(file)

        return files

    def get_file_name(self):
        """Get a random file name

        Returns
        -------
        string
            file name
        """
        return Utils.get_random_string(10)

    def write_data_into_file(self, data, file_name, mode):
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
        with open(file_path, mode) as file:
            file.write(data)

    def store_file_info_in_db(self, name, filetype, file_name, size):
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
            ?
        )
        '''

        # Type
        if filetype == 'text/tab-separated-values':
            filetype = 'csv/tsv'
        else:
            # Default is csv/tsv
            filetype = 'csv/tsv'

        database.execute_sql_query(query, (self.session['user']['id'], name, filetype, file_path, size))

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
                self.delete_file_from_fs("{}/{}".format(self.upload_path, file_name))
            except Exception:
                pass
            raise(e)

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
            return 'gff'
        elif file_ext in ('.bed', ):
            return 'bed'

        # Default is csv
        return 'csv/tsv'

    def delete_files(self, files_id):
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
            self.delete_file_from_fs(file_path)
            self.delete_file_from_db(fid)

        return self.get_files_infos()

    def delete_file_from_db(self, file_id):
        """remove a file for the database

        Parameters
        ----------
        file_id : int
            the file id to remove
        """
        database = Database(self.app, self.session)

        query = '''
        DELETE FROM files
        WHERE id=? AND user_id=?
        '''

        database.execute_sql_query(query, (file_id, self.session['user']['id']))

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
