"""Contain the Files class
"""
import os
import random
import magic

from askomics.libaskomics.Utils import Utils
from askomics.libaskomics.Params import Params
from askomics.libaskomics.Database import Database

class Files(Params):

    def __init__(self, app, session, new_files=None):

        Params.__init__(self, app, session)
        self.new_files = new_files


    def persist_files(self):

        uploaded_files = []

        upload_path = "{}/{}_{}/upload".format(
            self.settings.get("askomics", "data_directory"),
            self.session['user']['id'],
            self.session['user']['username']
        )

        for file in self.new_files:

            file_name = self.new_files[file].filename
            file_local_name = Utils.get_random_string(10)
            file_path = "{}/{}".format(upload_path, file_local_name)

            # save in user upload
            self.new_files[file].save("{}/{}".format(upload_path, file_local_name))
            file_size = os.path.getsize(file_path)
            file_type = magic.from_file(file_path, mime=True)

            # save in db
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

            file_id = database.execute_sql_query(query, (self.session['user']['id'], file_name, file_type, file_path, file_size), get_id=True)

        return self.get_files()


    def get_files_with_path(self, files_id):

        database = Database(self.app, self.session)

        subquery_str = '(' + ' OR '.join(['id = ?'] * len(files_id)) + ')'

        query = '''
        SELECT id, name, type, size, path
        FROM files
        WHERE user_id = ?
        AND {}
        '''.format(subquery_str)

        rows = database.execute_sql_query(query, (self.session['user']['id'], ) + tuple(files_id))

        files = []
        for row in rows:
            file = {
                'id': row[0],
                'name': row[1],
                'type': row[2],
                'size': row[3],
                'path': row[4]
            }
            files.append(file)

        return files


    def get_files(self, files_id=None):

        database = Database(self.app, self.session)

        if files_id:
            subquery_str = '(' + ' OR '.join(['id = ?'] * len(files_id)) + ')'

            query = '''
            SELECT id, name, type, size
            FROM files
            WHERE user_id = ?
            AND {}
            '''.format(subquery_str)

            rows = database.execute_sql_query(query, (self.session['user']['id'], ) + tuple(files_id))

        else:

            query = '''
            SELECT id, name, type, size
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
            files.append(file)

        return files

    def delete_files(self, files_id):

        for fid in files_id:
            file_path = self.get_file_path(fid)
            self.delete_file_from_fs(file_path)
            self.delete_file_from_db(fid)

        return self.get_files()


    def delete_file_from_db(self, file_id):

        database = Database(self.app, self.session)

        query = '''
        DELETE FROM files
        WHERE id=? AND user_id=?
        '''

        database.execute_sql_query(query, (file_id, self.session['user']['id']))

    def delete_file_from_fs(self, file_path):

        os.remove(file_path)

    def get_file_path(self, file_id):

        database = Database(self.app, self.session)

        query = '''
        SELECT path
        FROM files
        WHERE id=?
        '''

        row = database.execute_sql_query(query, (file_id, ))


        return row[0][0]
