import json
import sys

from russell.client.base import RussellHttpClient
from russell.client.files import get_files_in_directory
from russell.exceptions import DuplicateException, NotFoundException
from russell.log import logger as russell_logger


class ModuleClient(RussellHttpClient):
    """
    Client to interact with modules api
    """
    def __init__(self):
        self.url = "/modules"
        super(ModuleClient, self).__init__()

    def create(self, module):
        try:
            upload_files, total_file_size = get_files_in_directory(path='.', file_type='code')
        except OSError:
            sys.exit("Directory contains too many files to upload. Add unused directories to .russellignore file."
                     "Or download data directly from the internet into RussellHub")

        request_data = {"json": json.dumps(module.to_dict())}
        russell_logger.info("Creating project run. Total upload size: {}".format(total_file_size))
        russell_logger.debug("Creating module. Uploading: {} files".format(len(upload_files)))
        russell_logger.info("Syncing code ...")
        try:
            response = self.request("POST",
                                self.url,
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
                     self.url,
                     params={'id': id})
        return True
