import json
import sys

from russell.client.base import RussellHttpClient
from russell.cli.utils import get_files_in_directory, get_size
from russell.manager.auth_config import AuthConfigManager
from russell.log import logger as russell_logger
from russell.model.module import Module

class DataClient(RussellHttpClient):
    """
    Client to interact with Data api
    """
    def __init__(self):
        self.url = "/data/"  # Data is a subclass of modules
        super(DataClient, self).__init__()

    def create_module(self, data_module):
        request_data = data_module.to_dict()
        request_data.update({'size': get_size()})
        try:
            response = self.request("PUT",
                                url="/module",
                                data=json.dumps(request_data),
                                timeout=3600)
        except Exception as e:
            sys.exit(e)
        else:
            return response

    def get(self, id):
        module_dict = self.request("GET",
                                 url="/module",
                                 params={'id': id})
        return Module.from_dict(module_dict)

    def get_all(self, dataset_id):
        '''
        :return:
        '''
        response = self.request("GET",
                                url="/modules",
                                params={"module_type": "data",
                                        "entity_id": dataset_id})
        module_dicts = response.get('list', [])
        return [Module.from_dict(module_dict) for module_dict in module_dicts]

    def delete(self, id):
        self.request("DELETE",
                     url="/module",
                     params={'id': id})
        return True

    def get_data_info_by_name(self, user_name, data_name):
        data = self.request("GET",
                            url="/{}/dataset/{}".format(user_name, data_name),
                            params={})
        return data

    def get_data_info_by_id(self, id):
        data = self.request("GET",
                            url="/{}/dataset/{}".format("anonymous", "anonymous"),
                            params={'id': id})
        return data


    def _create(self, data):
        '''
        Deprecated
        :param data:
        :return:
        '''
        try:
            upload_files, total_file_size_fmt, total_file_size = get_files_in_directory(path='.', file_type='data')
        except OSError:
            sys.exit("Directory contains too many files to upload. Add unused directories to .russellignore file. "
                     "Or download data directly from the internet into RussellHub")

        json_dict = data.to_dict()
        json_dict[u'size'] = total_file_size
        request_data = {"json": json.dumps(json_dict)}
        russell_logger.info("Creating data source. Total upload size: {}".format(total_file_size_fmt))
        russell_logger.debug("Total files: {}".format(len(upload_files)))
        russell_logger.info("Uploading files ...".format(len(upload_files)))
        response = self.request("POST",
                                self.url,
                                data=request_data,
                                files=upload_files,
                                timeout=3600)
        return response.get("id")
