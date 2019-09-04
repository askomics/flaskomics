from bioblend import galaxy
from askomics.libaskomics.FilesHandler import FilesHandler
from askomics.libaskomics.Params import Params
from askomics.libaskomics.Utils import Utils


class Galaxy(Params):
    """Connection with a Galaxy account

    Attributes
    ----------
    apikey : string
        Galaxy API key
    url : string
        Galaxy url
    """

    def __init__(self, app, session, url=None, apikey=None):
        """init

        Parameters
        ----------
        app : Flask
            flask app
        session :
            AskOmics session, contain the user
        url : string
            Galaxy url
        apikey : string
            Galaxy API key
        """
        Params.__init__(self, app, session)

        if not url and not apikey:
            self.url = self.session["user"]["galaxy"]["url"]
            self.apikey = self.session["user"]["galaxy"]["apikey"]
        else:
            self.url = url
            self.apikey = apikey

        self.upload_path = "{}/{}_{}/upload".format(
            self.settings.get("askomics", "data_directory"),
            self.session['user']['id'],
            self.session['user']['username']
        )

    def check_galaxy_instance(self):
        """Check the Galaxy credentials

        Returns
        -------
        Boolean
            True if URL and Key exists
        """
        try:
            galaxy_instance = galaxy.GalaxyInstance(self.url, self.apikey)
            galaxy_instance.config.get_config()
        except Exception:
            return False

        return True

    def get_datasets_and_histories(self, history_id=None, query=False):
        """Get Galaxy datasets of the current history and all histories

        Parameters
        ----------
        history_id : int, optional
            A history id
        query : bool, optional
            Get Datasets, or json datasets for query

        Returns
        -------
        dict
            Datasets and histories
        """
        allowed_files = ['json']
        if not query:
            allowed_files = ['tabular', 'tsv', 'ttl', 'gff', 'gff3', 'gff2', 'bed']

        galaxy_instance = galaxy.GalaxyInstance(self.url, self.apikey)
        results = {}

        # get current history
        if not history_id:
            history_id = galaxy_instance.histories. get_most_recently_used_history()['id']

        # Get all available history id and name
        histories = galaxy_instance.histories.get_histories()
        histories_list = []
        for history in histories:
            if history['id'] == history_id:
                history_dict = {"name": history['name'], "id": history['id'], "selected": True}
            else:
                history_dict = {"name": history['name'], "id": history['id'], "selected": False}
            histories_list.append(history_dict)

        # Get datasets of selected history
        dataset_list = []
        history_content = galaxy_instance.histories.show_history(history_id, contents=True)
        for dataset in history_content:
            if 'extension' not in dataset:
                continue
            if dataset['extension'] not in allowed_files:
                continue
            if 'deleted' in dataset:
                # Don't show deleted datasets
                if dataset['deleted']:
                    continue
            dataset_list.append(dataset)

        results['datasets'] = dataset_list
        results['histories'] = histories_list

        return results

    def download_datasets(self, datasets_id):
        """Download galaxy datasets into AskOmics

        Parameters
        ----------
        datasets_id : list
            List of Galaxy datasets id
        """
        galaxy_instance = galaxy.GalaxyInstance(self.url, self.apikey)
        files_handler = FilesHandler(self.app, self.session)

        for dataset_id in datasets_id:
            dataset = galaxy_instance.datasets.show_dataset(dataset_id)
            file_name = Utils.get_random_string(10)
            path = "{}/{}".format(self.upload_path, file_name)
            filetype = dataset["file_ext"]
            size = dataset["file_size"]

            galaxy_instance.datasets.download_dataset(dataset_id, file_path=path, use_default_filename=False)
            files_handler.store_file_info_in_db(dataset["name"], filetype, file_name, size)

    def get_dataset_content(self, dataset_id):
        """Get Galaxy dataset content

        Parameters
        ----------
        dataset_id : string
            dataset ID

        Returns
        -------
        string
            Content of the dataset
        """
        galaxy_instance = galaxy.GalaxyInstance(self.url, self.apikey)
        dataset = galaxy_instance.datasets.download_dataset(dataset_id).decode('utf-8')

        return dataset
