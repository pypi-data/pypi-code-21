from __future__ import unicode_literals
import logging
import traceback

import datetime
import requests

from MammothAnalytics.errors import AuthError, UnknownError
from urls import get_url
import time

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("requests").setLevel(logging.WARNING)


def handleError(f):
    def new_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except (AuthError, UnknownError) as e:
            raise e
        except Exception as e:
            fname = f.__name__
            log.error({
                'function_name': fname,
                'args': args,
                'kwrgs': kwargs
            })
            log.error(''.join(traceback.format_exc()))
            raise UnknownError('Error in: {0}'.format(fname))

    new_function.__name = f.__name__
    new_function.__doc__ = f.__doc__
    return new_function


class MammothConnector():
    def __init__(self, email, password, account_id=None):
        """
        The main class for handling Mammoth Analytics API
        :param email: The email of the user
        :param password: The password of the user
        :param account_id: Account ID. If not given now, it can be given after `select accounts`
        """
        response = requests.post(get_url('/login'), json=dict(email=email, password=password, is_long_term=True))
        if response.status_code != 200:
            raise AuthError("username or password is not correct")
        self.__token = response.json()['token']
        self.__account_id = None
        if account_id is not None:
            self.select_account(account_id)
        else:
            self.auto_select_account()

    def __del__(self):
        try:
            if self.__token:
                self.logout()
        except:
            pass

    def _make_signed_request(self, rtype, api, **kwargs):
        headers = {'X-API-KEY': self.__token}
        if self.__account_id:
            headers['X-ACCOUNT-ID'] = str(self.__account_id)
        if 'headers' in kwargs.keys():
            kwargs['headers'].update(headers)
        else:
            kwargs['headers'] = headers
        method_maps = {
            'get': requests.get,
            'post': requests.post,
            'delete': requests.delete,
            'patch': requests.patch
        }
        api_url = get_url(api)
        response = method_maps[rtype](api_url, **kwargs)
        if response.status_code == 200:
            return response
        else:
            log.error("Error while trying url {0} with method {1}".format(api_url, rtype))
            try:
                log.error('response json :{0}'.format(response.json()))
            except:
                pass
            raise UnknownError('Server responded with status code :{0}'.format(response.status_code))

    @handleError
    def list_accounts(self):
        """
        Returns a list of accounts user has access to
        :return: List of dictionaries. Each dictionary contains id, name and other properties associated with an account
        """
        response = self._make_signed_request('get', '/accounts')
        return response.json()['accounts']

    @handleError
    def select_account(self, account_id):
        """
        Sets the account id on the class. This is important to use any other method in the class
        :param account_id: Account id to be selected
        :return: None
        """
        accounts = self.list_accounts()
        account_ids = [a['id'] for a in accounts]
        if account_id in account_ids:
            self.__account_id = account_id
        else:
            raise AuthError("Account ID is not valid")

    @handleError
    def auto_select_account(self):
        """
        selects the first account in the list of accounts the user belongs to
        """
        accounts = self.list_accounts()
        self.select_account(accounts[0]['id'])

    @handleError
    def logout(self):
        """
        Will log out from Mammoth. This is also done automatically when the object is garbage collected.
        :return:
        """
        self._make_signed_request('post', '/logout', json={})

    @handleError
    def list_datasets(self):
        """
        Returns a list of datasets in the system
        :return: List of dictionaries containing info about the datasets in the system. Contains info such as id, name etc.
        """
        response = self._make_signed_request('get', '/datasets')
        return response.json()['datasets']

    @handleError
    def create_dataset(self, name, metadata, display_properties=None):
        """
        Create a dataset in Mammoth Analytics.

        TODO: explain metadata and display properties somewhere and put links here

        :param name: Name of the dataset
        :param metadata: Metadata for the given dataset. This is a list of dict objects. Each dict should contain `display_name`,
            `internal_name` and `type`. `type` should be one of `NUMERIC`, `TEXT` or `DATE`
        :param display_properties: A dictionary of display properties.
        :return: Datasource id
        """
        if not display_properties:
            display_properties = {'FORMAT_INFO': {}, "SORT": []}
        response = self._make_signed_request(
            'post', '/datasets',
            json={'name': name, 'metadata': metadata,
                  'display_properties': display_properties})
        return response.json()['id']

    @handleError
    def get_dataset(self, ds_id):
        """
        Returns a dataset information dictionary for the given ID
        :param ds_id: The datasource id
        :return: dictionary containing information on the dataset
        """
        response = self._make_signed_request('get', '/datasets/{0}'.format(ds_id))
        return response.json()

    @handleError
    def add_data_to_dataset(self, ds_id, data, end_batch=False):
        """
        Add data to a dataset as a list of dictionaries.

        :param ds_id: The target dataset id
        :param data: a list of dictionaries. Each dictionary represents a row of data where key is the column internal name and value is the value of the cell.
        :param end_batch: If true , this would be considered an end of batch.
        :return: A processing response dictionary
        """
        response = self._make_signed_request('post', '/datasets/{0}/data'.format(ds_id),
                                             json={"rows": data, "endBatch": end_batch})
        return response.json()

    @handleError
    def add_data_to_dataset_as_csv(self, ds_id, file_path, has_header):
        """
        To add clean data to a dataset as a csv. Should contain a csv that has the same structure has the metadata.
        use this only if you are sure that all the rows of the right format. That is, each row should contain comma
        separated values in the same order as dataset metadata

        :param has_header: If the file has a header row.
        :param ds_id: the destination ds id
        :param file_path: the path of the file where you want to upload
        """
        header_string = 'true'
        if not has_header:
            header_string = 'false'
        files = {'file': open(file_path, 'rb')}
        response = self._make_signed_request('post', '/datasets/{0}/data'.format(ds_id),
                                             files=files, data={"has_header": header_string})
        return response.json()

    @handleError
    def upload_csv(self, file_path, target_datasource_id=None, replace=False):
        """
        To upload an arbitrary csv file to the system. The system would return a file id based on which one can track
        the progress of the file through the mammoth system.

        :param file_path: The file path
        :param target_datasource_id: if this is set to a dataset id, the arbitrary csv would be appended to the
            data of the dataset.
        :return: A file id.
        """
        files = {'file': open(file_path, 'rb')}
        post_data = {}
        if target_datasource_id:
            post_data = {'append_to_ds_id': target_datasource_id}
            if replace:
                post_data['replace'] = "true"
        response = self._make_signed_request('post', '/files', files=files, data=post_data)
        log.info(response.json())
        return response.json()['id']

    @handleError
    def wait_till_file_processing_get_ds(self, file_id):
        """
        Method will wait till the file with given id has finished processing. Works only for csv files right now.
        TODO: Write logic to support excel, zip files.
        :param file_id:
        :return: A dataset dictionary
        """
        while True:
            response = self._make_signed_request('get', '/files/{0}'.format(file_id))
            file_info = response.json()['file']
            status = file_info['status']
            if status != 'processing':
                log.info(file_info)
                break
            else:
                time.sleep(1)

        while True:
            ds = self.get_ds_for_file(file_id)
            status = ds['status']
            if status != 'processing':
                break
            else:
                time.sleep(1)

        return ds


    @handleError
    def get_ds_for_file(self, file_id):
        """
        Will return the dataset for the given file.
        :param file_id: The file id
        :return: A ds information dictionary
        """
        datasets = self.list_datasets()
        for i in range(len(datasets)):
            ds = datasets[len(datasets) - 1 - i]
            if 'source_id' in ds.keys():
                if ds['source_id'] == file_id and ds['source_type'] == 'file':
                    return ds

    @handleError
    def list_views(self, ds_id):
        """
        Returns a list of views a dataset has
        :param ds_id: Dataset ID
        :return: list of workspace dictionaries
        """
        response = self._make_signed_request('get', '/datasets/{0}/workspaces'.format(ds_id))
        return response.json()['workspaces']

    @handleError
    def run_transform(self, view_id, param):
        r = self._make_signed_request('post', '/workspaces/{0}/tasks'.format(view_id), json={'param': param})
        return r.json()

    @handleError
    def get_view_details(self, view_id):
        r = self._make_signed_request('get', '/workspaces/{0}'.format(view_id))
        return r.json()

    @handleError
    def wait_till_view_is_ready(self, view_id):
        while True:
            time.sleep(1)
            view = self.get_view_details(view_id)
            if view['status'] == 'ready':
                break

    @handleError
    def copy_template_from_view(self, ds_id, view_id):
        """
        use this method to copy template from another view and apply to the dataset's view. If the dataset has an
        empty view, it will be reused. Else, a new view will get created.

        :param ds_id: The dataset id
        :param view_id: The view ID from which you want to copy the template from.
        :return: Nothing
        """
        self._make_signed_request('post',
                                  '/datasets/{0}/workspaces'.format(ds_id),
                                  json={'clone_config_from': view_id})

    @handleError
    def _run_action(self, view_id, param):
        """
        Runs an action.
        :param view_id: The view on which the action is to be performed
        :param param: The param for the action.
        :return: Request Id for the action
        """
        r = self._make_signed_request('post', '/workspaces/{0}/actions'.format(view_id), json={'param': param})
        return r.json()['request_id']

    def _wait_till_request_is_complete_get_data(self, view_id, request_id):
        while True:
            time.sleep(1)
            r = self._make_signed_request('get',
                                          '/workspaces/{0}/requests/{1}'.format(view_id, request_id))
            data = r.json()
            if data['status'] == 'success' or data['status'] == 'failure':
                return data

    @handleError
    def push_view_data_to_mysql(self, view_id, host, username, password, database, target_table):
        action_param = {
            'run_immediately': True,
            'target_properties': {
                'username': username,
                'password': password,
                'database': database,
                'host': host,
                'table': target_table
            },
            'trigger_type': 'none',
            'additional_properties': {},
            'handler_type': 'mysql'
        }
        request_id = self._run_action(view_id, action_param)
        self._wait_till_request_is_complete_get_data(view_id, request_id)

    @handleError
    def push_view_to_s3_as_csv(self, view_id):
        action_param = {
            'run_immediately': True,
            'target_properties': {},
            'trigger_type': 'none',
            'additional_properties': {},
            'handler_type': 's3'
        }
        request_id = self._run_action(view_id, action_param)
        result = self._wait_till_request_is_complete_get_data(view_id, request_id)
        log.error(result)
        return result['information']['url']

    @handleError
    def download_view_as_csv(self, view_id, file_path):
        url = self.push_view_to_s3_as_csv(view_id)
        r = requests.get(url, stream=True)
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        return file_path

