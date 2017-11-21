import json
import sys

from russell.client.base import RussellHttpClient
from russell.cli.utils import get_files_in_directory
from russell.exceptions import DuplicateException, NotFoundException
from russell.log import logger as russell_logger
from russell.model.module import Module


class ModuleClient(RussellHttpClient):
    """
    Client to interact with modules api
    """
    def __init__(self):
        self.url = "/modules"
        super(ModuleClient, self).__init__()

    def create(self, module):
        try:
            upload_files, total_file_size_fmt, total_file_size = get_files_in_directory(path='.', file_type='code')
        except OSError:
            sys.exit("Directory contains too many files to upload. Add unused directories to .russellignore file."
                     "Or download data directly from the internet into RussellHub")
        json_dict = module.to_dict()
        json_dict['size'] = total_file_size
        request_data = {"json": json.dumps(json_dict)}
        russell_logger.info("Creating project run. Total upload size: {}".format(total_file_size_fmt))
        russell_logger.debug("Creating module. Uploading: {} files".format(len(upload_files)))
        russell_logger.info("Syncing code ...")
        try:
            response = self.request("POST",
                                url="/modules",
                                data=request_data,
                                files=upload_files,
                                timeout=3600)
        except NotFoundException:
            return False
        except DuplicateException:
            return False
        return response

    def delete(self, id):
        self.request("DELETE",
                     url="/module",
                     params={'id': id})
        return True

    def get(self, id):
        module_dict = self.request("GET",
                     url="/module",
                     params={'id': id})
        return Module.from_dict(module_dict)