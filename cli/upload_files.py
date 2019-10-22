"""CLI to upload files from a directory to AkOmics"""
import os
import argparse

from askomics.app import create_app, create_celery
from askomics.libaskomics.FilesHandler import FilesHandler
from askomics.libaskomics.LocalAuth import LocalAuth
from askomics.libaskomics.Start import Start


class UploadFiles(object):
    """Upload files from a directory to AskOmics

    Attributes
    ----------
    application : Flask app
        Flask App
    args : args
        User arguments
    celery : Celery
        Celery
    session : dict
        Empty session
    user : dict
        The New user
    """

    def __init__(self):
        """Get Args"""
        parser = argparse.ArgumentParser(description="Upload files from a directory to AskOmics")

        parser.add_argument("-c", "--config-file", type=str, help="AskOmics config file", required=True)

        parser.add_argument("-d", "--files-directory", type=str, help="Directory of files to upload", required=True)
        parser.add_argument("-k", "--api-key", type=str, help="AskOmics user apikey", required=True)

        self.args = parser.parse_args()

        self.application = create_app(config=self.args.config_file)
        self.celery = create_celery(self.application)
        self.session = {}
        self.user = None

        self.chunk_size = 1024 * 1024 * 10  # 10MB

        starter = Start(self.application, self.session)
        starter.start()

        self.authenticate_user()

    def authenticate_user(self):
        """Authenticate user and set session"""
        local_auth = LocalAuth(self.application, self.session)
        results = local_auth.authenticate_user_with_apikey(self.args.api_key)
        self.user = results["user"]
        self.session["user"] = self.user

    def generator_is_last(self, generator):
        """Iter over an generator and know if the iteration is the last one

        Parameters
        ----------
        o : Object
            The object to iterate

        Yields
        ------
        (boolean, iteration)
            True/False if last, and the generator content
        """
        iterator = generator.__iter__()
        current = iterator.__next__()
        while True:
            try:
                nxt = iterator.__next__()
                yield (False, current)
                current = nxt
            except StopIteration:
                yield (True, current)
                break

    def read_in_chunks(self, file_object, chunk_size=1024):
        """Lazy function (generator) to read a file piece by piece.

        Parameters
        ----------
        file_object : file pointer
            The file pointer
        chunk_size : int, optional
            The chunk size

        Yields
        ------
        string
            Chunk content
        """
        while True:
            data = file_object.read(chunk_size)
            if not data:
                break
            yield data

    def main(self):
        """Upload the files"""
        for file_name in os.listdir(self.args.files_directory):
            file_path = os.path.join(self.args.files_directory, file_name)
            file_size = os.path.getsize(file_path)
            file_path_on_askomics = None
            file_ext = os.path.splitext(file_name)[1]

            files = FilesHandler(self.application, self.session)

            fp = open(file_path)
            first = True
            for (last, chunk) in self.generator_is_last(self.read_in_chunks(fp, self.chunk_size)):
                data = {
                    "first": first,
                    "last": last,
                    "chunk": chunk,
                    "path": file_path_on_askomics,
                    "name": file_name,
                    "size": file_size,
                    "type": files.get_type(file_ext)
                }
                first = False
                file_path_on_askomics = files.persist_chunk(data)

if __name__ == '__main__':
    """main"""
    UploadFiles().main()
