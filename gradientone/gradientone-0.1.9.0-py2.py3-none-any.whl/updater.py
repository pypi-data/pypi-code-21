"""

Copyright (C) 2016-2017 GradientOne Inc. - All Rights Reserved
Unauthorized copying or distribution of this file is strictly prohibited
without the express permission of GradientOne Inc.

"""
import collections
import imp
import json
import os
import pkgutil
import subprocess
import sys
import time
from configparser import ConfigParser
from types import ModuleType
from pkg_resources import DistributionNotFound, get_distribution
from subprocess import Popen, PIPE
from version import __version__
from gateway_helpers import logger
from controllers import ModuleHelper, MultiClientController


cfg = ConfigParser()
cfg.read('/etc/gradient_one.cfg')
COMMON_SETTINGS = cfg['common']
CLIENT_SETTINGS = cfg['client']
BASE_URL = "https://" + COMMON_SETTINGS['DOMAIN']
UPDATE_CHECK_INTERVAL = 5
DEFAULT_PYTHONPATH = '/usr/local/lib/python2.7/dist-packages'
DIRPATH = os.path.dirname(os.path.realpath(__file__))
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
GATEWAY = COMMON_SETTINGS["HARDWARENAME"]
GATEWAY_URL = BASE_URL + '/gateway'


class UpdateController(MultiClientController):

    """Handles running and updating the main client"""

    def __init__(self, *args, **kwargs):
        super(UpdateController, self).__init__(*args, **kwargs)
        version = __version__
        pkg = 'gradientone'
        logger.info("Initializing with version: %s" % version)
        self.pip_target = self.get_pip_target()
        self.pip_install(pkg, version)
        self.og_client_name = pkg
        self.og_version = version
        self.version = version
        self.prev_version = version
        self.client_name = pkg
        self.client_module = ModuleHelper(pkg).client_module
        self.my_pid = os.getpid()
        logger.info("UpdateController pid: %s" % self.my_pid)

    def start_checking(self):
        """Starts the client and checks for updates"""

        # start up other clients
        self.start_clients()

        # begin checks for updates
        while True:
            time.sleep(UPDATE_CHECK_INTERVAL)
            try:
                url = BASE_URL + '/gateway'
                msg = ("UpdateController - Current v " + self.version +
                       " checking:" + url)
                logger.info(msg)
                response = self.get(url, params={'name': GATEWAY})
                if not response.status_code == 200:
                    continue
                if not response.text:
                    continue
                data = json.loads(response.text)
                if 'install_update' in data and data['install_update']:
                    data['install_update'] = False
                    self.put(url, data=json.dumps(data))
                    self.process_update_cmd(data)
            except Exception:
                logger.error("Exception in pulling code", exc_info=True)

    def get_pip_target(self):
        try:
            py_path = os.environ['PYTHONPATH'].split(os.pathsep)
        except KeyError:
            py_path = []
        if not py_path:
            logger.warning("No python path found. Adding default: %s"
                           % DEFAULT_PYTHONPATH)
            sys.path.append(DEFAULT_PYTHONPATH)
            py_path.append(DEFAULT_PYTHONPATH)
        logger.info("PYTHONPATH is %s" % py_path)
        logger.info("Returning pip target as %s" % py_path[0])
        return py_path[0]

    def set_version(self, package='gradientone', version=''):
        """Sets current and previous version"""
        if not version:
            version = self.get_pip_show_version(package)
        if self.version == version:
            msg = ("Setting v-%s matches current v-%s. Backup stays as v-%s"
                   % (version, self.version, self.prev_version))
            logger.info(msg)
        else:
            self.prev_version = self.version
            msg = ("New v-%s replacing v-%s. The backup is now: v-%s"
                   % (version, self.version, self.prev_version))
            logger.info(msg)
            self.version = version
            payload = {
                'name': GATEWAY,
                'client_version': version,
                'company': COMMON_SETTINGS['COMPANYNAME'],
            }
            self.post(url=GATEWAY_URL, data=json.dumps(payload))

    def get_pip_show_version(self, package='gradientone'):
        """Gets version by parsing pip output"""
        pip_show_pkg = ['pip', 'show', package]
        output = Popen(pip_show_pkg, stdout=PIPE).communicate()[0]
        lines = output.split('\n')
        version = ""
        for line in lines:
            if line.startswith("Version:"):
                version = line.split(':')[1].strip()
        return version

    def pip_install(self, pkg_name='', version=''):
        if not pkg_name:
            pkg_name = self.client_name
        pip_args = ['install', '--upgrade']
        if version:
            logger.info("Installing version: %s" % version)
            pkg_string = pkg_name + '==' + str(version)
            pip_args.append(pkg_string)
        else:
            msg = "No version given. Simply installing " % pkg_name
            logger.info(msg)
            pip_args.append(pkg_name)
        cmd = 'pip ' + ' '.join(pip_args)
        logger.info("Making subprocess.call with %s" % cmd)
        subprocess.call(cmd, shell=True)

    def reload(self, pkg_name='', is_rollback=False, og_install=False):
        if not pkg_name:
            pkg_name = self.client_name
        if self.reload_by_name(pkg_name):
            logger.info("Successfully reloaded %s" % pkg_name)
        else:
            if og_install:
                msg = ("Unable to reload original client! This process will "
                       "continue polling for gateway client software updates."
                       "However, no gateway client that is running may not "
                       "have the latest update running. Restart required.")
                logger.warning(msg)
            elif is_rollback:
                self.install_original()
                self.start_clients(og_install=True)
            else:
                response = self.rollback()
                if "Success" in response:
                    self.start_clients(is_rollback=True)
                    return
                else:
                    self.install_original()
                    self.start_clients(og_install=True)

    def pip_uninstall(self, pkg_name=''):
        if not pkg_name:
            pkg_name = self.client_name
        subprocess.call('pip uninstall', shell=True)

    def install_original(self):
        self.pip_install(self.og_client_name, self.og_version)
        if self.verify_version_info(self.og_client_name, self.og_version):
            msg = ("Successfuly installed original client: %s v-%s"
                   % (self.og_client_name, self.og_version))
            logger.info(msg)
        else:
            msg = ("Failed to install original client: %s v-%s"
                   % (self.og_client_name, self.og_version))
            logger.warning(msg)
        return msg

    def update(self, pkg_name='gradientone', version='',
               force_uninstall=False, is_rollback=False):
        logger.info("Current client version: %s" % self.version)
        if force_uninstall:
            self.pip_uninstall(pkg_name)
        self.pip_install(pkg_name, version)
        if self.verify_version_info(pkg_name, version):
            return "Success! Current version is v-%s" % version
        elif is_rollback:
            logger.warning("Rollback update failed. Installing original")
            return self.install_original()
        else:
            msg = "Update failed"
            logger.warning(msg)
            return msg

    def verify_version_info(self, pkg_name, version=''):
        logger.info("Verifying version update...")
        v_from_pip_show = self.get_pip_show_version(pkg_name)
        if v_from_pip_show != version:
            msg = ("Verification of v-%s failed. Current version is: v-%s"
                   % (version, v_from_pip_show))
            logger.warning(msg)
            return None
        else:
            logger.warning("Verification of current client v-%s. Success!"
                           % v_from_pip_show)
            self.set_version(pkg_name, v_from_pip_show)
            return True

    def process_update_cmd(self, data):
        """Processes update command from server

        If the update succeeds then the new client is started.
        If the update fails then try a resinstall of current version
        If reinstall of current fails, try rollback to previous
        If rollback to previous fails, try install of original
        and try to start client regardless of og_install result.
        """
        update = collections.defaultdict(str, data)
        if update['new_client_version'] == self.version:
            msg = ("Server version:%s matches client. No action necessary"
                   % update['new_client_version'])
            logger.info(msg)
            return
        # stop client during update process
        self.stop_clients()
        if not update['client_package']:
            update['client_package'] = 'gradientone'
        result = self.update(pkg_name=update['client_package'],
                             version=update['new_client_version'])
        if 'Success' in result:
            logger.info("Update: %s" % result)
            self.start_clients()
        else:
            # If the update failed. Reinstall current version
            logger.info("Trying re-install of version: %s" % self.version)
            self.pip_install(self.client_name, self.version)
            # Verify the reinstall. If failed, rollback to previous v.
            if self.verify_version_info(self.client_name, self.version):
                self.start_clients()
            else:
                result = self.rollback()
                if "Success" in result:
                    logger.info("Rollback: %s" % result)
                    self.start_clients(is_rollback=True)
                else:
                    logger.info("Rollback failed. Installing original")
                    result = self.install_original()
                    self.start_clients(og_install=True)

    def reload_by_name(self, modname):
        """Safe reload(module) that accepts strings

        Allows str, unicode string, or ModuleType
        """
        if isinstance(modname, str):
            logger.info("Getting module from str: %s" % modname)
            self.client_module = ModuleHelper(modname).client_module
        elif isinstance(modname, ModuleType):
            logger.warning("Assigning modname as module")
            self.client_module = modname
        elif isinstance(modname, unicode):
            logger.info("Getting module from unicode: %s" % modname)
            try:
                self.client_module = ModuleHelper(str(modname)).client_module
            except Exception as e:
                logger.warning("Unexpected reload err:%s " % e)
                return None
        else:
            logger.warning("Unexpected modname type:%s" % type(modname))
            return None
        logger.info("Reloading module %s" % self.client_module)
        try:
            imp.reload(self.client_module)
            imp.reload(self.client_module.gateway_helpers)
            imp.reload(self.client_module.gateway_client)
            return True
        except Exception as e:
            logger.warning("Exception during reload: %s" % e)
            return None

    def rollback(self):
        logger.info("Rolling back to v-%s" % self.prev_version)
        self.stop_clients()
        response = self.update(pkg_name=self.client_name,
                               version=self.prev_version,
                               is_rollback=True)
        return response

    def start_clients(self, is_rollback=False, og_install=False):
        logger.info("Starting client: %s v-%s"
                    % (self.client_name, self.version))
        self.reload(self.client_name, is_rollback, og_install)
        try:
            gc = self.client_module.gateway_client.GatewayClient()
            self.start_process(target=gc.run_clients, name='run_clients')
        except Exception:
            logger.error("Exception in starting client", exc_info=True)
            if og_install:
                msg = ("Unable to start original client! This process will "
                       "continue polling for gateway client software updates."
                       "However, no gateway client is running until a "
                       "successful update happens.")
                logger.warning(msg)
            elif is_rollback:
                self.install_original()
                self.start_clients(og_install=True)
            else:
                self.rollback()
                self.start_clients(is_rollback=True)

    def stop_clients(self):
        logger.info("Stopping client processes")
        logger.info("UpdateController: stop_clients CHILD PROCESSES %s"
                    % self.child_processes)
        try:
            pid = self.get_pid_from_name('run_clients')
            self.stop_process(pid=pid)
        except Exception:
            logger.error("Exception in stopping client", exc_info=True)

    def restart_clients(self):
        logger.info("Preparing to restart client....")
        self.stop_clients()
        self.start_clients()

    def log(self, msg):
        logger.info(msg)

    def get_dist_version(self, package='gradientone'):
        """Gets version using pgk_resources"""
        try:
            _dist = get_distribution(package)
        except DistributionNotFound as e:
            self.version = 'Please install %s' % package
            logger.warning("DistributionNotFound: %s" % e)
        except Exception as e:
            logger.warning("Exception in get_distribution, %s" % e)
            self.version = 'No version info'
        else:
            self.version = _dist.version
            logger.warning("_dist.version: %s" % _dist.version)
        return self.version

    def rreload(self, package, parent_pkg='gradientone'):
        """Recursively reload packages."""
        logger.info("rreload on %s" % package)
        for importer, modname, ispkg in pkgutil.iter_modules(package.__path__):
            logger.info("Found submodule %s (is a package: %s)"
                        % (modname, ispkg))
            modname = parent_pkg + "." + modname
            logger.info("modname: %s" % modname)
            try:
                module = importer.find_module(modname).load_module(modname)
                if ispkg:
                    self.rreload(module, parent_pkg=modname)
                else:
                    self.simple_reload(module)
            except Exception as e:
                msg = "load module %s exc: %s" % (modname, e)
                logger.info(msg)
