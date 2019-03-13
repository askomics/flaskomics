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

    def persist_files(self, input_files):
        """Persist files into the filesystem, and the database

        Parameters
        ----------
        input_files : list
            list of files to persist

        Returns
        -------
        list
            list of files info
        """
        upload_path = "{}/{}_{}/upload".format(
            self.settings.get("askomics", "data_directory"),
            self.session['user']['id'],
            self.session['user']['username']
        )

        for file in input_files:

            # Get name, extension local name (a random string), and path
            splitted_name = os.path.splitext(input_files[file].filename)
            file_name = splitted_name[0]
            file_ext = splitted_name[1].lower()
            file_local_name = Utils.get_random_string(10)
            file_path = "{}/{}".format(upload_path, file_local_name)

            # save in user upload directory
            input_files[file].save("{}/{}".format(upload_path, file_local_name))
            # Get file size
            file_size = os.path.getsize(file_path)
            # Get file type
            file_type = self.get_type(file_ext)

            # Save in db
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

            database.execute_sql_query(query, (self.session['user']['id'], file_name, file_type, file_path, file_size))

        return self.get_files_infos()

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