#
# Copyright (c) 2017 Cisco Systems, Inc. and others.  All rights reserved.
#
__author__ = "mlipman"
__copyright__ = "Copyright(c) 2015, Cisco Systems, Inc."
__version__ = "0.1"
__status__ = "alpha"

import logging
import os.path
import importlib.util
import subprocess
import socket

from magen_logger.logger_config import LogDefaults, initialize_logger
from magen_utils_apis.singleton_meta import Singleton
from magen_rest_apis.server_urls import ServerUrls

from hwa.hwa_server.hwa_utils import read_dict_from_file

logger = logging.getLogger(LogDefaults.default_log_name)


class HwaUrls(metaclass=Singleton):
    __instance = None

    def __init__(self, hwa_app_tag="hwa"):
        self.__source_version = False
        self.__production_mode = True

        self.__put_json_headers = {'content-type': 'application/json', 'accept': 'application/json', 'cache-control': "no-cache"}
        self.__get_json_headers = {'accept': 'application/json'}

        self.__hwa_app_tag = hwa_app_tag

        self.__ingest_file_suffix = ".html" # html container format

        self.__local_server_host = "0.0.0.0"
        self.__local_server_port = '5002'

        server_urls = ServerUrls.get_instance()

        self.__hwa_dns_cluster = server_urls.domain_name

        self.__hwa_url_scheme = "https"
        self.__ids_clt_oauth_callback_url_path = None

        hwa_root = os.path.expanduser('~/magen_data/hwa/')
        self._data_dir_update(hwa_root + "data/")

    def _data_dir_update(self, value, override=False):
        self.__data_dir = value.rstrip('/') + '/' # set exactly one trailing '/'
        self.__data_dir_override = override
        # Update data_dir dependencies
        self.__data_secrets_dir = self.__data_dir + "secrets/"
        self.__server_cert_base = self.__data_secrets_dir + "hwa_server_cert"
        self.dns_host_update_from_data_dir()

    def dns_host_update_from_data_dir(self):
        if self.__hwa_dns_cluster == 'localhost':
            hwa_config = read_dict_from_file(self.hwa_cfg_file)
            hwa_dns_host = hwa_config.get('hostname')
            # absent configuration, use localhost rather than gethostname
            # if not hwa_dns_host:
            #    hwa_dns_host = socket.gethostname()
            if not hwa_dns_host:
                hwa_dns_host = self.__hwa_dns_cluster
        else:
            hwa_dns_host = self.__hwa_app_tag + '.' + self.__hwa_dns_cluster
        self.__hwa_dns_host = hwa_dns_host

        hwa_external_url_authority = hwa_dns_host
        if self.__hwa_dns_cluster == 'localhost':
            hwa_external_url_authority += (":" + self.__local_server_port)
        self.hwa_external_url_authority = hwa_external_url_authority

    def data_files_check(self):
        """
        Create any automatically generatable config files that are missing

        For expediency in implementation, use existing shell script
        with existing fragments rather than translating to a python library,
        even though that leads to more mechanism and fragility.
        """
        cfgfile_maker='magen_svc_cfgfile_gen.sh'
        if self.src_version:
            srcfile_path = os.path.abspath(__file__)
            hwa_root = os.path.dirname(os.path.dirname(srcfile_path))
            repo_root = os.path.dirname(hwa_root) + '/'
            cfgfile_maker = repo_root + 'lib/magen_helper/helper_scripts/' + cfgfile_maker
        if not os.path.isfile(self.hwa_flask_secret_file):
            subprocess.call(['bash', cfgfile_maker,
                             '-svc', 'hwa',
                             '-dir', self.__data_secrets_dir,
                             '-op', 'flask'])
        if not os.path.isfile(self.hwa_server_cert_pvt_key):
            subprocess.call(['bash', cfgfile_maker,
                             '-svc', 'hwa',
                             '-dir', self.__data_secrets_dir,
                             '-op', 'cert'])            

    @property
    def src_version(self):
        """
        Production (default) or test mode.
        Used primarily for explicit mocking that will not be needed
        when policy unit test upgraded to use patch-style mocking.

        :return: true if production mode, false if unit test mode
        :rtype: boolean
        """
        return self.__src_version

    @src_version.setter
    def src_version(self, value):
        self.__src_version = value
        # location of data files, both checked-in and secret/not checked-in,
        # based on location of this sourcefile
        if self.__src_version and not self.__data_dir_override:
            srcfile_path = os.path.abspath(__file__)
            # directory containing data/ subdir
            hwa_root = os.path.dirname(os.path.dirname(srcfile_path)) + "/"
            self._data_dir_update(hwa_root + "data/")

    @property
    def production_mode(self):
        """
        Production (default) or test mode.
        Used primarily for explicit mocking that will not be needed
        when policy unit test upgraded to use patch-style mocking.

        :return: true if production mode, false if unit test mode
        :rtype: boolean
        """
        return self.__production_mode

    @production_mode.setter
    def production_mode(self, value):
        self.__production_mode = value

    @property
    def hwa_app_tag(self):
        return self.__hwa_app_tag

    @property
    def ingest_file_suffix(self):
        return self.__ingest_file_suffix

    @property
    def hwa_data_dir(self):
        return self.__data_dir

    @hwa_data_dir.setter
    def hwa_data_dir(self, value):
        self._data_dir_update(value, override = True)

    @property
    def hwa_fs_dir(self):
        return self.__data_dir + "fs/"

    @property
    def hwa_cfg_file(self):
        return self.__data_secrets_dir + "hwa_config.json"

    @property
    def hwa_server_cert_crt(self):
        return self.__server_cert_base + ".crt"

    @property
    def hwa_server_cert_pvt_key(self):
        return self.__server_cert_base + ".pvt_key"

    @property
    def hwa_flask_secret_file(self):
        return self.__data_secrets_dir + "hwa_flask_secrets.json"

    @property
    def datadogclt_secret_file(self):
        return self.__data_secrets_dir + "hwa_datadog_secrets.json"

    @property
    def idsclt_secret_file(self):
        return self.__data_secrets_dir + "hwa_idsvc_secrets.json"

    @property
    def get_json_headers(self):
        return self.__get_json_headers

    @property
    def put_json_headers(self):
        return self.__put_json_headers

    @property
    def local_server_host(self):
        return self.__local_server_host

    @property
    def local_server_port(self):
        return self.__local_server_port

    # this server's host and port
    @property
    def local_server_host_port(self):
        return self.__local_server_host + ":" + self.__local_server_port

    @local_server_host_port.setter
    def local_server_host_port(self, value):
        (host, port) = value.split(":")
        if not host:
            host = "0.0.0.0"
        assert port, "port not specified"
        self.__local_server_host = host
        self.__local_server_port = port

    @property
    def hwa_url_scheme(self):
        return self.__hwa_url_scheme

    @hwa_url_scheme.setter
    def hwa_url_scheme(self, value):
        self.__hwa_url_scheme = value

    @property
    def hwa_external_url_authority(self):
        return self.__hwa_external_url_authority

    @hwa_external_url_authority.setter
    def hwa_external_url_authority(self, value):
        self.__hwa_external_url_authority = value

    @property
    def hwa_external_url_base(self):
        return self.hwa_url_scheme + "://" + self.hwa_external_url_authority

    @property
    def ids_issuer(self):
        server_urls = ServerUrls.get_instance()
        ids_url_scheme = "https"
        ids_url_authority = server_urls.identity_server_url_host_port
        return ids_url_scheme + "://" + ids_url_authority

    @property
    def ids_redirect_issuer(self):
        server_urls = ServerUrls.get_instance()
        ids_url_scheme = "https"
        if self.__hwa_dns_cluster == "localhost":
            # remote browser cannot handle redirect to "localhost"
            # instead, use hwa's redirect_url_authority and replace
            # hwa port w/id port
            # issuer = "https://" + server_urls.identity_server_url_host_port
            ids_url_authority = self.hwa_external_url_authority.replace(
                self.local_server_port, str(server_urls.identity_port))
        else:
            ids_url_authority = server_urls.identity_server_url_host_port
        return ids_url_scheme + "://" + ids_url_authority

    @property
    def ids_clt_oauth_callback_url_path(self):
        return self.__ids_clt_oauth_callback_url_path

    @ids_clt_oauth_callback_url_path.setter
    def ids_clt_oauth_callback_url_path(self, value):
        # the "path" portion of hwa's callback url
        self.__ids_clt_oauth_callback_url_path = value

    @property
    def ids_clt_oauth_callback_url(self):
        ## this webapp's callback url, supplied as an argument to id svc oauth
        ## redirect, for id svc to redirect back to us
        return (self.hwa_external_url_base +
                self.__ids_clt_oauth_callback_url_path)
