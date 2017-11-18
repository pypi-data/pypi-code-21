# coding=utf-8

import requests
import sys
import os
import russell
from russell.manager.auth_config import AuthConfigManager
from russell.exceptions import *
from russell.log import logger as russell_logger
import json
import tarfile
import zipfile

class RussellHttpClient(object):
    """
    Base client for all HTTP operations
    """
    def __init__(self):
        self.base_url = russell.russell_host + "/api/v{}"
        self.access_token = AuthConfigManager.get_access_token()

    def request(self,
                method,
                url,
                params=None,
                data=None,
                json=None,
                files=None,
                timeout=5,
                access_token=None,
                stream=False,
                api_version=1):
        """
        Execute the request using requests library
        """
        request_url = self.base_url.format(api_version) + url
        russell_logger.debug("Starting request to url: {} with params: {}, data: {}".format(request_url, params, data))
        if access_token:
            headers = {"Authorization": "Basic {}".format(access_token)}
        else:
            headers = {"Authorization": "Basic {}".format(
                self.access_token.token if self.access_token else None)
            }

        try:
            response = requests.request(method,
                                        request_url,
                                        params=params,
                                        headers=headers,
                                        data=data,
                                        json=json,
                                        files=files,
                                        timeout=timeout,
                                        stream=stream)
        except requests.exceptions.ConnectionError:
            sys.exit("Cannot connect to the Russell server. Check your internet connection.")
        if not stream:
            try:
                russell_logger.debug("Response Content: {}, Headers: {}".format(response.json(), response.headers))
            except Exception:
                russell_logger.debug("Request failed. Response: {}".format(response.content))
            try:
                self.check_response_status(response)
            except Exception as e:
                raise e
            else:
                result = response.json().get("data", "")
                return result
        else:
            russell_logger.debug('HTTP Stream Request/Response...')
            try:
                self.check_response_status(response)
            except Exception as e:
                raise e
            else:
                return response

    def check_response_status(self, response):
        """
        Check if response is successful. Else raise Exception.
        """
        if not response.headers.get('Content-Type') in ('application/json', 'text/html'):
            return

        if not (200 <= response.status_code < 300):
            if response.status_code == 401:
                raise AuthenticationException()
            elif response.status_code == 404:
                raise NotFoundException()
            else:
                raise InvalidResponseException()
        try:
            resp_json = response.json()
        except:
            raise InvalidResponseException

        code = resp_json.get("code")

        if not (200 <= code < 300):
            try:
                message = response.json().get("data", "")
            except Exception:
                message = None
            russell_logger.debug("Error received : status_code: {}, message: {}".format(code,
                                                                                      message or response.content))
            if code == 517:
                raise NotFoundException()
            elif code == 512:
                raise AuthenticationException()
            elif code == 519:
                raise BadRequestException()
            elif code == 518:
                raise NoRequestException()
            elif code == 520:
                raise OverLimitException()
            elif code == 521:
                raise DuplicateException()
            elif code == 522:
                raise OverPermissionException()
            elif code == 525:
                raise TaskSubmitException()
            elif code == 526:
                raise VersionTooOldException()
            elif code == 527:
                raise NoBalanceException()
            elif code == 503:
                raise ServiceBusyException()
            elif code == 529:
                raise NotFoundException()
            elif code == 530:
                raise ResourceUnavailableException()
            else:
                response.raise_for_status()

    def download(self, url, filename, timeout=10, api_version=1):
        """
        Download the file from the given url at the current path
        """
        russell_logger.debug("Downloading file from url: {}".format(url))

        try:
            # response = requests.get(request_url,
            #                         headers=request_headers,
            #                         timeout=timeout,
            #                         stream=True)
            response = self.request(method='GET',
                                    url=url,
                                    stream=True,
                                    timeout=timeout,
                                    api_version=api_version
                                    )
            self.check_response_status(response)
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            return filename
        except requests.exceptions.ConnectionError as exception:
            russell_logger.debug("Exception: {}".format(exception))
            sys.exit("Cannot connect to the Russell server. Check your internet connection.")

    def download_compressed(self, url, compression='tar', uncompress=True, delete_after_uncompress=False, dir=None, api_version=1):
        """
        Download and optionally uncompress the tar file from the given url
        """
        if dir:
            if os.path.exists(dir):
                raise ExistedException
            else:
                os.mkdir(dir)
                os.chdir(dir)
        try:
            russell_logger.info("Downloading the tar file to the current directory ...")
            filename = self.download(url=url, filename='output', api_version=api_version)
            if filename and os.path.isfile(filename) and uncompress:
                russell_logger.info("Uncompressring the contents of the file ...")
                if compression == 'tar':
                    tar = tarfile.open(filename)
                    tar.extractall()
                    tar.close()
                elif compression == 'zip':
                    zip = zipfile.ZipFile(filename)
                    zip.extractall()
                    zip.close()
            if delete_after_uncompress:
                russell_logger.info("Cleaning up the compressed file ...")
                os.remove(filename)
            return filename
        except requests.exceptions.ConnectionError as e:
            russell_logger.error("Download ERROR! {}".format(e))
            return False


