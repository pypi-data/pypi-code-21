# coding: utf-8
""" As this class is a :class:`~base.DockerV` extension need to have the same values in the config
dictionary, but inside a config_container key::

        "container_config": {
            "apt_install": [],
            "pip_install": [],
            "domain": "localhost",
            "command": "sleep 20",
            "env_vars": {
                "odoo_config_file": "/home/odoo/.openerp_serverrc",
                "odoo_home": "/home/odoo",
                "odoo_user": "odoo"
            },
            "image_name": "busybox",
            "mem_limit": "768m",
            "ports": {
                "8069": 8069,
                "8072": None
            },
            "remove_previous": True,
            "working_folder": "/path/to/docker_volumes",
            "volumes":{
                "filestore": "/home/odoo/.local/share/Odoo",
                "logs": "/var/log/supervisor",
                "ssh": "/home/odoo/.ssh",
                "tmp": "/tmp"
            }
        },
        "instance": {
            "action_type": "replace",
            "task_id":"t1234",
            "customer_id": "customer80",
            "config": {
                "admin": "admin_pass",
                "admin_passwd": "123",
                "db_host": "172.17.42.1",
                "db_name": "{{ instance.task_id }}_{{ instance.customer_id }}",
                "db_password": "psql_user",
                "db_user": "psql_pass",
                "dbfilter": "{{ instance.task_id }}_{{ instance.customer_id }}.*",
                "list_db": True
            },
            "ssh_key":"base64_encoded_key",
            "repositories": [
                {
                    "branch": "8.0",
                    "commit": "8f159f276e7c8da4e5475e604e9057dcaadfedf9",
                    "depth": 1,
                    "is_dirty": False,
                    "name": "odoo",
                    "path": "odoo",
                    "repo_url": {
                        "origin": "git@github.com:Vauxoo/odoo.git"
                    },
                    "type": "git"
                },
            ],
            "update_module":"all",
            "install_module": None
        }

.. note:: For more information about *container_config* keys and values check
    :class:`~deployv.base.dockerv.DockerV` documentation

Where:

* *action_type*: Replace/create Odoo container
* *task_id*: associated task/issue/user story in the instance un the format [tiu]id
* *customer_id*: Unique customer id
* *config*: Dict with the values to be changed inside Odoo configuration file
* *ssh_key*: the id_rsa key ot be used to clone private repos, must be in base64 format
* *repositories*: A list of repos to be updated/added.
  Check `backupws <https://github.com/ruiztulio/backupws/blob/master/branches.py>`_
  if you want more detail about the format

"""
import tarfile
import logging
import base64
import github
from os import path
from tempfile import gettempdir, mkdtemp
from uuid import uuid4
import shutil
import time
import re
import psycopg2
import simplejson as json
from passlib.context import CryptContext
from deployv.base.dockerv import DockerV
from deployv.base.postgresv import PostgresShell, PostgresConnector
from deployv.base import postgresv
from deployv.helpers import utils, container, build_helper, database_helper, configuration
from deployv.base import errors
from deployv.instance import ODOO_BINARY, SAAS_VERSIONS
from datetime import datetime


logger = logging.getLogger(__name__)  # pylint: disable=C0103
INSTANCE_TYPES = ['test', 'develop', 'updates', 'production']
UPDATE = ['develop', 'updates']
DEACTIVATE = ['test', 'develop', 'updates']
INSTALL_RIBBON = ['test', 'develop', 'updates']


class InstanceV(DockerV):

    def __init__(self, config, timeout=300, docker_url="unix://var/run/docker.sock"):
        self.__full_config = config
        container_config = config.get('container_config')
        logger.debug('Container config : %s',
                     json.dumps(container_config, sort_keys=True, indent=2))
        if not container_config.get('container_name', False):
            container_config.update({
                'container_name': '{prefix}_odoo'.format(
                    prefix=config.get('instance').get('prefix'))})
            if container_config.get('postgres_container'):
                pg_container = '{prefix}_postgres'.format(
                    prefix=config.get('instance').get('prefix'))
                container_config.update({'postgres_container_name': pg_container})
            env_vars = config.get('instance').get('config').copy()
            if not env_vars.get('admin'):
                env_vars.update({'admin': utils.random_string(6)})
            if not env_vars.get('admin_passwd'):
                env_vars.update({'admin_passwd': utils.random_string(6)})
            env_vars.update({'instance_type':
                             config.get('instance').get('instance_type', 'production'),
                             'customer': config.get('instance').get('customer_id')})
            self._update_env_vars(env_vars)
        super(InstanceV, self).__init__(container_config,
                                        timeout=timeout, docker_url=docker_url)

    def start_odoo_container(self):
        """ Specifically starts an Odoo container and configure all the parameters,
        see :func:`~dockerv.DockerV.basic_info` for more information about the format and content

        :return: A dict with the basic info of container
        """
        logger.debug('Psql in container: %s', self.config.get('postgres_container', False))
        # if it will be a full stack container all the parameters are changed (no matter what is
        # specified in the config) to target the local env and added the nginx, postgres and ssh
        # ports
        if self.config.get('full_stack', False):
            db_config = self.db_config
            self.config.get('ports').update({
                '22': None,
                '5432': None
            })
            self.config.get('env_vars').update({
                'db_host': '127.0.0.1',
                'db_port': 5432,
                'pghost': '127.0.0.1',
                'pgport': 5432,
                'pguser': db_config.get('db_user', 'odoo'),
                'pgpassword': db_config.get('db_password', 'odoo'),
                'pgdatabase': self.__full_config.get('instance').get('config').get('db_name')
            })
        self.pull_image()
        logger.info('Starting Odoo container %s',
                    self.config.get('container_name'))
        self.config.update({'container_hostname': container.generate_hostname(self.__full_config)})
        info = self.deploy_container()
        time.sleep(10)
        if self.config.get('full_stack', False):
            self.add_authorized_keys()
            supervisor_status = self.check_supervisor()
            if not supervisor_status:
                return {'error': 'Supervisor process could not start'}
            start_psql = self.exec_cmd('supervisorctl start postgresql')
            logger.info('starting postgres: %s', start_psql.strip())
            postgres_connection = self.check_postgres()
            if not postgres_connection.get('success'):
                return postgres_connection
        self.set_global_env_vars()
        logger.info('Odoo container "%s" created. Ports %s',
                    info.get('name'), info.get('ports'))
        return info

    @utils.traceback_docker_error
    def check_supervisor(self):
        retry = 0
        supervisor_process = self.exec_cmd('pgrep supervisord')
        if supervisor_process:
            return True
        while True:
            retry += 1
            chown_process = self.exec_cmd('pgrep chown')
            if chown_process:
                logger.debug('chown command is still running, retrying %s', retry)
                time.sleep(3)
                continue
            supervisor_process = self.exec_cmd('pgrep supervisord')
            if supervisor_process:
                return True
            return False

    def check_postgres(self):
        res = {'success': True}
        retry = 0
        config = self.db_config.copy()
        config.update({'db_name': 'template1'})
        while retry <= 3:
            logger.info('Testing postgres connection')
            try:
                conn = PostgresConnector(utils.odoo2postgres(config))
                conn.check_config()
                logger.info('Postgres connection test passed')
                return res
            except psycopg2.OperationalError as error:
                if 'the database system is starting up' in error.message:
                    retry += 1
                    logger.warn('Postgres is starting up, retry %s', retry)
                    time.sleep(5)
                    continue
                else:
                    logger.error(
                        'Could not connect to the postgres server: %s',
                        error.message)
                    res.update({'success': False, 'error': error.message})
                    return res

    def add_authorized_keys(self, tmp='/tmp'):
        git_cli = github.Github()
        users = ['nhomar', 'ruiztulio', 'moylop260'] +\
            self.__full_config.get('instance').get('authorized_users', [])
        authorized_keys_path = path.join(tmp, 'authorized_keys')
        authorized_keys_tar_path = path.join(tmp, 'keys.tar')
        with open(authorized_keys_path, 'w') as authorized_keys:
            for user in users:
                user_keys = []
                try:
                    user_keys = git_cli.get_user(user).get_keys()
                except github.GithubException as error:
                    error_msg = error.data.get('message')
                    if 'Not Found' in error_msg:
                        logger.warning('User not found %s, could not retrieve any key', user)
                    else:
                        logger.warning(error_msg)
                for user_key in user_keys:
                    authorized_keys.write(user_key.key + '\n')
        with tarfile.open(authorized_keys_tar_path, 'w') as tar_keys:
            tar_keys.add(authorized_keys_path, arcname='authorized_keys')
        with open(authorized_keys_tar_path, 'r') as tar_data:
            self.cli.put_archive(self.config.get('container_name'),
                                 '/home/odoo/.ssh/', tar_data.read())
            self.exec_cmd('cp /home/odoo/.ssh/authorized_keys /root/.ssh/')
        utils.clean_files([authorized_keys_tar_path, authorized_keys_path])

    @property
    @utils.traceback_docker_error
    def is_running(self):
        """ If the Odoo instance ins running inside the container (or at least supervisord
        detects it) return True, False otherwise. If an unexpected state is detected raises
        a TypeError exception

        :return: True or False
        """
        retry_triggers = ['refused connection', 'no such file', 'STARTING', 'STOPPING']
        retry = 0
        while retry <= 3:
            try:
                res = self.exec_cmd('supervisorctl status odoo')
            except errors.NotRunning:
                retry += 1
                logger.debug('Container not running, retry %s', retry)
                time.sleep(4)
                continue
            logger.debug('is_running: %s', res.strip())
            if 'RUNNING' in res:
                return True
            elif 'STOPPED' in res:
                return False
            elif retry < 3 and any([msg for msg in retry_triggers if msg in res or res == '']):
                retry += 1
                logger.debug('The Odoo process is in an intermediate state or'
                             ' is not running yet, retrying %s', retry)
                time.sleep(4)
            else:
                raise TypeError('Unknown state: %s' % res)

    @property
    def instance_type(self):
        """ The instance type

        :return: Instance type: production, test, develop or false if it not set
        """
        return self.__full_config.get('instance').get('instance_type') or\
            self.docker_env.get('instance_type', 'production')

    @property
    def temp_folder(self):
        """ This is a very important property because the tmp folder is used to share files between
            the container and the host, widely used along the code.
            The best way (so far) is iterating all the mounted volumes until we find the /tmp

        :return: Full host path where the tmp volume is mounted
        """
        inspected = self.inspect()
        volumes = inspected.get('Mounts')
        res = None
        for volume in volumes:
            if volume.get("Destination") == '/tmp' and volume:
                res = volume.get("Source")
                break
        return res

    @property
    def odoo_binary(self):
        odoo_version = self.docker_env.get('version', '8.0')
        return ODOO_BINARY[odoo_version]

    def start_instance(self):
        """ Start an instance inside a docker container using supervisord

        :return: Supervisord response
        """
        res = 'RUNNING'
        if not self.is_running:
            res = self.exec_cmd('supervisorctl start odoo')
            logger.debug('start_instance: %s', res.strip())
        return res

    def stop_instance(self):
        """ Stop an instance inside a docker container using supervisord

        :return: Supervisord response
        """
        res = 'STOPPED'
        if self.is_running:
            res = self.exec_cmd('supervisorctl stop odoo')
            logger.info('stop_instance: %s', res.strip())
        return res

    def ensure_process_check(self, process, check, possible_exceptions=False, max_tries=False):
        """Runs a given process and ensures that the result is the one that you want. If it is
        not, the process will run as many times as specified in max_tries, or until the check
        is passed.

        :param process: The process you want to run until it checks out. Should be a lambda
            function that receives the instance as the only param and returns the result of the
            process to be validated.
        :type process: lambda
        :param check: The check method for the value returned from process. Should be a lambda
            function that receives the result of the process function as the only param, checks
            the value is the expected one, and returns a boolean with that result.
        :type check: lambda
        :param possible_exceptions: A set of possible exceptions (classes) that can be raised
            from the process.
        :type possible_exceptions: set
        :param max_tries: The amount of times the given process will run until the result of the
            process is the expected one.
        :type max_tries: int
        """
        ok = False
        tries = 0
        if not possible_exceptions:
            possible_exceptions = Exception
        while tries < (max_tries or 99) and not ok:
            tries += 1
            try:
                process_result = process(self)
            except possible_exceptions:  # pylint: disable=E0712,W0703
                ok = False
            else:
                ok = check(self, process_result)
            if not ok:
                time.sleep(3)
        return ok

    def ensure_instance_status(self, ensure_running, max_tries=False):
        """Starts/stops an instance and ensures is either running or not, checking as many
        times as specified in max_tries.

        :param ensure_running: If True, it will start and ensure that the instance is running.
            If False, it will stop and ensure that the instance is not running.
        :type ensure_running: bool
        :param max_tries: The amount of times it will check
        :type max_tries: int
        """
        supervisor = self.ensure_process_check(
            lambda ins: ins.exec_cmd('pgrep supervisord'),
            lambda ins, res: bool(res),
            False, max_tries)
        if not supervisor:
            return False
        command = self.ensure_process_check(
            lambda ins: (
                ins.start_instance() if ensure_running
                else ins.stop_instance()
            ),
            lambda ins, res: bool(res),
            TypeError, max_tries)
        if not command:
            return False
        status = self.ensure_process_check(
            lambda ins: ins.is_running,
            lambda ins, res: res is ensure_running,
            False, max_tries)
        return status

    def deploy_key(self):
        """ Deploy a ssh_key into the container

        """
        ssh_key = utils.decode(base64.b64decode(self.__full_config.get('instance').get('ssh_key')))
        known_hosts = self.__full_config.get('instance').get('known_hosts', [])
        logger.info('Deploying keys')
        ssh_key_filename = path.join(self.temp_folder, 'id_rsa')
        with open(ssh_key_filename, 'w') as key_file:
            key_file.write(ssh_key)
        odoo_home = self.config.get('env_vars').get('odoo_home')
        odoo_user = self.config.get('env_vars').get('odoo_user')
        bash_lines = [
            'mv /tmp/id_rsa {home}/.ssh/id_rsa'.format(home=odoo_home),
            'chown -R {user}:{user} {home}/.ssh/id_rsa'.format(home=odoo_home, user=odoo_user),
            'chmod 0600 {home}/.ssh/id_rsa'.format(home=odoo_home)
        ]
        known_hosts = known_hosts + ['github.com', 'git.vauxoo.com']
        known_hosts = list(set(known_hosts))
        for known_host in known_hosts:
            command = 'su {user} -c "ssh-keyscan {known_host} >> {home}/.ssh/known_hosts"'.\
                format(home=odoo_home, user=odoo_user, known_host=known_host)
            bash_lines.append(command)
        for line in bash_lines:
            logger.debug('Executing "%s"', line)
            res = self.exec_cmd(line)
            logger.debug('Response "%s"', res.strip())

    def run_and_log(self, command, skip_summary=False):
        """ Executes an Odoo related command inside the container (i.e.: update, install) and
            returns the resumed log and full path to the generated log. See
            :func:`~dockerv.helpers.utils.resume_log` for detailed information about
            the return format

        :param command: Command line to be executed inside Odoo container
        :return: Resumed log and full path to the generated file
        """
        self.stop_instance()
        logger.debug('run_and_log: %s', command)
        res = self.exec_cmd(command)
        resume = utils.resume_log(res.split('\n'))
        self.start_instance()
        working_path = path.join(
            self.temp_folder,
            'cmd_{timestamp}.log'.format(timestamp=utils.get_strtime())
        )
        with open(working_path, 'w') as log_file:
            log_file.write(res)
        resume.update({'log_file': working_path})
        if not skip_summary:
            logger.info('+-- Critical errors %s', len(resume.get('critical')))
            logger.info('+-- Errors %s', len(resume.get('errors')))
            logger.info('+-- Import errors %s', len(resume.get('import_errors')))
            logger.info('+-- Warnings %s', len(resume.get('warnings')))
            logger.info('+-- Translation Warnings %s', len(resume.get('warnings_trans')))
        logger.info('Logger was saved to: "%s"', working_path)
        return resume

    def update_db(self, modules, db_name):
        """ Executes "-u module" or "-u module1,module2" on the selected database and returns
            resumed log and full path to the generated log. See
            :func:`~dockerv.helpers.utils.resume_log` for detailed information about
            the return format

        :param modules: Module (str) o modules (list) to be updated
        :param db_name: Database name to be updated
        :return: Resumed log and full path to the generated file
        """
        if utils.is_iterable(modules):
            modules = modules[0]
        logger.info('Updating database %s, modules %s', db_name, modules)
        command_odoo = self.odoo_binary
        if self.config.get('env_vars'):
            env_vars = self.config.get('env_vars')
            if env_vars.get('odoo_home') and env_vars.get('odoo_user'):
                odoo_home = env_vars.get('odoo_home')
                odoo_user = env_vars.get('odoo_user')
        else:
            odoo_home = self.docker_env.get('odoo_home')
            odoo_user = self.docker_env.get('odoo_user')
        update_command = ('su {user} -c "{home}/instance/odoo/{odoo}'
                          ' -d {database} -u {modules} --stop-after-init"') \
            .format(home=odoo_home, user=odoo_user, database=db_name, modules=modules,
                    odoo=command_odoo)
        skip_modules = ['web_environment_ribbon_isolated']
        skip_summary = all(module in skip_modules for module in modules.split(','))
        return self.run_and_log(update_command, skip_summary)

    def install_module(self, modules, db_name, without_demo=True):
        """ Executes "-i module" or "-i module1,module2" on the selected database and returns
            resumed log and full path to the generated log. See
            :func:`~dockerv.helpers.utils.resume_log` for detailed
            information about the return format

        :param modules: Module (str) o modules (list) to be installed
        :param db_name: Database name to be updated
        :param without_demo: Install the mdule/s with or without demo,
            if true will use --without-demo=all, if false omit the option,
            otherwise the module list
        :return: Resumed log and full path to the generated file
        """
        if utils.is_iterable(modules):
            modules_str = ','.join(modules)
        else:
            modules_str = modules

        if isinstance(without_demo, bool):
            wodemo = '--without-demo=all' if without_demo else ''
        elif utils.is_iterable(modules):
            wodemo = '--without-demo={}'.format(','.join(modules))
        elif isinstance(without_demo, str):
            wodemo = '--without-demo={}'.format(modules)
        logger.info('Installing modules %s in database %s',
                    modules_str, db_name)
        command_odoo = self.odoo_binary
        if self.config.get('env_vars'):
            env_vars = self.config.get('env_vars')
            if env_vars.get('odoo_home') and env_vars.get('odoo_user'):
                odoo_home = env_vars.get('odoo_home')
                odoo_user = env_vars.get('odoo_user')
        else:
            odoo_home = self.docker_env.get('odoo_home')
            odoo_user = self.docker_env.get('odoo_user')

        update_command = ('su {user} -c "{home}/instance/odoo/{odoo}'
                          ' -d {database} -i {modules} --stop-after-init {wodemo}"') \
            .format(home=odoo_home, user=odoo_user, database=db_name, modules=modules_str,
                    wodemo=wodemo, odoo=command_odoo)
        skip_modules = ['web_environment_ribbon_isolated']
        skip_summary = all(module in skip_modules for module in modules_str.split(','))
        return self.run_and_log(update_command, skip_summary)

    def move_file(self, filename):
        """Moves a file into the container temp shared volume

        :filename: File to be moved
        """
        actual_path = path.dirname(path.realpath(__file__))
        file_lib_src = path.join(
            actual_path, '..', 'helpers', filename)
        file_lib_dst = path.join(self.temp_folder, filename)
        shutil.copyfile(file_lib_src, file_lib_dst)

    def build_instance(self):
        """ Build the instance inside the container using the specified branches and repos

        :return: True if all the branches are cloned successfully otherwise False
        """
        success = (True, 'Build successfully')
        logger.info('Building branches')
        res = self.check_supervisor()
        if isinstance(res, dict) and res.get('error'):
            return (False, res.get('error'))
        try:
            self.stop_instance()
        except TypeError:
            return (False, "process manager supervisord could not start")
        odoo_home = self.config.get('env_vars').get('odoo_home')
        odoo_user = self.config.get('env_vars').get('odoo_user')
        branches_filename = path.join(self.temp_folder, 'branches.json')
        getaddons_path = path.join(path.dirname(path.abspath(__file__)), '..',
                                   'templates', 'files', 'getaddons.py')
        shutil.copyfile(getaddons_path, path.join(self.temp_folder, 'getaddons.py'))
        self.move_file('helpers-requirements.txt')
        self.move_file('clone_oca_dependencies.py')
        self.add_repo_web()
        with open(branches_filename, 'w') as fout:
            json.dump(self.__full_config.get('instance').get('repositories'),
                      fout, indent=4, ensure_ascii=False,
                      separators=(',', ':'))
        bash_lines = [
            'pip install -r /tmp/helpers-requirements.txt -q ',
            'su {user} -c "branchesv load -p {home}/instance -f /tmp/branches.json"'
        ]
        for line in bash_lines:
            res = self.exec_cmd(line.format(home=odoo_home, user=odoo_user))
            logger.debug(res)
            regex = re.compile(r'Cloning repo (.*?) - branch (.*)')
            matches = regex.finditer(res)
            if matches:
                for match in matches:
                    logger.debug('Object %s', str(match))
                    logger.debug('Groups %s', match.groups())
                    repo = match.group(1)
                    branch = match.group(2)
                    logger.debug('Gotten repo: %s', repo)
                    logger.debug('Gotten branch: %s', branch)
            error_regex = re.compile(r'[fatal|ERROR]: (.*)')
            fatal = error_regex.search(res)
            if fatal:
                logger.error(fatal.group(1))
                success = (False, fatal.group(1))
        if success[0]:
            addons_path = "{home}/instance/extra_addons".format(home=odoo_home)
            self.get_oca_dependencies()
            self.exec_cmd('python /tmp/getaddons.py {paths}'.format(paths=addons_path))
            self.exec_cmd('su {user} -c "branchesv save -p {home}/instance -f {p}"'.
                          format(home=odoo_home, p='/tmp/post_process.json', user=odoo_user))
            self.exec_cmd("reqgenv {home}/full_requirements.txt --path {home}/instance".
                          format(home=odoo_home))
            self.exec_cmd("pip install -r {home}/full_requirements.txt".
                          format(home=odoo_home))
        logger.debug(success)
        self.start_instance()
        return success

    def pull_image(self):
        """ This method updates a docker image
        """
        try:
            logger.info('pulling %s', self.config.get('image_name'))
            self.pull(self.config.get('image_name'))
        except errors.NoSuchImage:
            logger.debug('Image not found in hub')
            image = self.inspect_image(self.config.get('image_name'))
            logger.debug('Image info %s', image)
            logger.debug('Using built image: %s', self.config.get('image_name'))

    def start_postgres_container(self):
        """ Specifically starts an Postgres container and configure users and connections,
        see :func:`~dockerv.DockerV.basic_info` for more information about the format and content

        :return: A dict with the basic info of container
        """
        if not self.__full_config.get('container_config').get('postgres_container'):
            return {}
        psql_version = self.__full_config.get('container_config').\
            get('postgres_version', '9.5')
        psql_image = "postgres:{version}".format(version=psql_version)
        config = self.config.copy()
        self.config.update({"image_name": psql_image})
        self.pull_image()
        self.config.update({'ports': {'5432': None}})
        self.config.get('env_vars').update({
                'db_host': '127.0.0.1',
                'db_port': 5432,
                'postgres_password': 'postgres'
        })
        self.config.update({"container_name": self.config.get('postgres_container_name')})
        self.config.update({'container_hostname': container.generate_hostname(self.__full_config)})
        self.config.update({'command': ''})
        info = self.deploy_container()
        time.sleep(5)
        cmd = "psql -c \"create user {user} with password '{password}' createdb\"".\
            format(user=self.db_config.get('db_user'),
                   password=self.db_config.get('db_password'))
        self.exec_cmd(cmd, user='postgres')
        ipaddress = self.inspect().get('NetworkSettings').get('IPAddress')
        self.config = config
        self.config.get('env_vars').update({'db_host': ipaddress})
        return info

    def get_oca_dependencies(self):
        odoo_home = self.config.get('env_vars').get('odoo_home')
        odoo_user = self.config.get('env_vars').get('odoo_user')
        odoo_version = self.docker_env.get("version")
        extra_addons_path = "{home}/instance/extra_addons".format(home=odoo_home)
        bash_lines = ['su {user} -c "python /tmp/clone_oca_dependencies.py '
                      '{path} {path} {version}"',
                      'su {user} -c "branchesv load -p {home}/instance -f /tmp/branches.json"']
        for line in bash_lines:
            self.exec_cmd(line.format(path=extra_addons_path, version=odoo_version,
                                      user=odoo_user, home=odoo_home))

    def add_repo_web(self):
        for repo in self.__full_config.get("instance").get("repositories"):
            if repo.get('name') == 'isolated_addons':
                logger.debug('Repository for the isolated addons is already in the json, skipping')
                return
        version = self.docker_env.get('version', '8.0')
        branch = (utils.version_cid(self.__full_config.get("instance").get('customer_id')) or
                  SAAS_VERSIONS.get(version) or version)
        branch_web = {
            "branch": branch,
            "commit": "",
            "depth": 1,
            "is_dirty": False,
            "name": "isolated_addons",
            "path": "extra_addons/isolated_addons",
            "repo_url": {
                "origin": "https://git.vauxoo.com/vauxoo/isolated_addons.git"
            },
            "type": "git"}
        if not self.__full_config.get("instance").get("repositories"):
            self.__full_config.get("instance").update({'repositories': [branch_web]})
        else:
            self.__full_config.get("instance").get("repositories").append(branch_web)

    @property
    def db_config(self):
        """ Parse env vars from a container to get the needed parameters to dump the database

        :return: dict with the needed configuration parameter
        """

        env_vars = self.docker_env
        logger.debug(json.dumps(env_vars, sort_keys=True, indent=2))
        if env_vars is None:
            logger.warn(
                "No such container (or not started yet)")
            instance_cfg = self.__full_config.get("instance").get("config")
            logger.debug("Instance config dict from json: %s",
                         str(instance_cfg))
            res = {
                'db_host': instance_cfg.get('db_host') or '127.0.0.1',
                'db_port': instance_cfg.get('db_port') or 5432,
                'db_user': instance_cfg.get('db_user') or 'odoo',
                'db_password': instance_cfg.get('db_password') or 'odoo',
            }
        else:
            db_host = env_vars.get('db_host') or '127.0.0.1'
            db_port = env_vars.get('db_port') or 5432
            if self.basic_info.get('ports').get('5432'):
                db_port = self.basic_info.get('ports').get('5432')
                if db_port and isinstance(db_port, list):
                    db_port = db_port[0].split(':')[1]
            res = {
                'db_host': db_host,
                'db_port': db_port,
                'db_user': env_vars.get('db_user') or 'odoo',
                'db_password': env_vars.get('db_password') or 'odoo',
            }
            inspected = self.inspect()
            volumes = inspected.get('Mounts')
            for volume in volumes:
                if '.local/share/Odoo' in volume.get('Destination') and volume:
                    res.update({'data_dir': volume.get('Source')})
                    break
            else:
                logger.error(
                    'Datadir not found, wont be able to backup attachments')

            if not res.get('data_dir'):
                logger.error(('The attachments directory was not mounted from the host,'
                              ' wont be able to backup attachments'))
            res.update({'odoo_container': self.docker_id})
        regex = re.compile(r'172\.17\.\d+\.1$')
        match = regex.match(res.get('db_host'))
        if match or res.get('db_host') == 'localhost':
            res.update({'db_host': '127.0.0.1'})
        return res

    def restore_database(self, db_name=False, backup_dir=False):
        res = {}
        customer_id = self.__full_config.get('instance').get('customer_id') or\
            self.docker_env.get("customer")
        use_template = self.__full_config.get('container_config').get('use_template')
        db_owner = self.__full_config.get('container_config').get('db_owner')
        db_owner_password = self.__full_config.get('container_config').get('db_owner_passwd')
        db_config = self.db_config.copy()
        db_config.update({'db_user': db_owner, 'db_password': db_owner_password})
        pg_shell = PostgresShell(utils.odoo2postgres(db_config))
        working_dir = mkdtemp(prefix='deployv_')
        helper_obj = database_helper.DatabaseHelper.get_helper(use_template)
        db_helper = helper_obj(utils.odoo2postgres(self.db_config))
        if use_template:
            search_res = db_helper.search_candidate(customer_id)
            if not search_res[0]:
                return search_res
            candidate = search_res[1]
            filestore_dir = candidate.replace('original_', '')
            filestore = path.join(path.expanduser(self.config.get('backup_folder')),
                                  filestore_dir, 'filestore')
        else:
            if not backup_dir:
                deployv_config = configuration.get_config()
                backup_dir = utils.get_backup_src(
                    config_dict=self.__full_config, deployv_config=deployv_config)
            search_res = db_helper.search_candidate(backup_dir, customer_id)
            if not search_res[0]:
                return search_res
            try:
                dest_dir = utils.decompress_files(search_res[1], working_dir)
            except (EOFError, IOError) as error:
                utils.clean_files(working_dir)
                return (False, utils.get_error_message(error))
            candidate = dest_dir
            filestore = path.join(candidate, 'filestore')
        if not db_name:
            if self.__full_config.get('instance').get('config').get('db_name'):
                db_name = self.__full_config.get('instance').get('config').get('db_name')
            else:
                db_name = utils.generate_dbname(self.__full_config,
                                                path.basename(search_res[1]),
                                                self.__full_config.get('instance').get('prefix'))
        self.stop_instance()
        db_name = db_name.lower()
        create_res = db_helper.create_database(candidate, db_name,
                                               db_owner, db_owner_password)
        if not create_res[0]:
            return create_res
        create_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.restore_filestore(filestore, db_name)
        res.update({"result": {'database_name': db_name, 'source': candidate,
                               'create_date': create_date}})
        utils.clean_files(working_dir)
        pg_shell.create_extension_unaccent(db_name)
        return (True, res)

    def files2backup(self, database_name, tmp_dir):
        """ Generates the files that will be added to the backup, such as
        json with the information of the repositories used in that instance,
        filestore and db dump.

        :param database_name: Name of the database that will be dumped
        :param tmp_dir: Temporal directory where the dump will be stored
        :returns: List of the files that will be compressed in the backup
        """
        files = []
        odoo_home = self.config.get('env_vars').get('odoo_home')
        odoo_user = self.config.get('env_vars').get('odoo_user')
        postgres_cfg = self.db_config.copy()
        postgres_cfg.update({'database': database_name})
        postgres = PostgresShell(utils.odoo2postgres(postgres_cfg))
        dump_name = path.join(tmp_dir, 'database_dump.sql')
        dump_name = postgres.dump(database_name, dump_name)
        if not dump_name:
            logger.error('Database could not be dumped')
            return files
        files.append(dump_name)
        if postgres_cfg.get('data_dir'):
            attachments_folder = path.join(postgres_cfg.get('data_dir'),
                                           'filestore',
                                           postgres_cfg.get('database'))
            if path.exists(attachments_folder):
                logger.debug('Attachments folder "%s"', attachments_folder)
                files.append((attachments_folder, 'filestore'))
            else:
                logger.warn(('Folder "%s" does not exists,'
                             ' attachments are not being added to the backup'), attachments_folder)
        else:
            logger.info('There is not attachments folder to backup')
        cmd_output = self.exec_cmd(
            ('su {user} -c "branchesv save -p {home}/instance -f /tmp/repositories.json"')
            .format(user=odoo_user, home=odoo_home)
        )
        logger.debug('Branchesv result:\n%s', cmd_output)
        json_repos = path.join(self.temp_folder, 'repositories.json')
        if path.exists(json_repos):
            files.append((json_repos, 'repositories.json'))
        return files

    def compress_files(self, files, backup_name, destination, cformat):
        """ Creates a compressed file in the specified destination with the name,
        format, and files provided.

        :param files: List of  files that will be added to the compressed file
        :param backup_name: Name of the compressed file that will be created
        :param destination: Directory where the compressed file will be created
        :param cformat: Format used to compress the files (bz2, gz)
        :return: Name of the new compressed file
        """
        logger.info('Compressing files')
        logger.debug('Files : %s', str(files))
        full_name = utils.compress_files(
            backup_name, files, dest_folder=destination, cformat=cformat)
        logger.info('Compressed backup, cleaning')
        for element in files:
            if not hasattr(element, '__iter__'):
                utils.clean_files(element)
        return full_name

    def generate_backup(self, database_name, dest_folder=False,
                        cformat=False, reason=False, tmp_dir=False, prefix=False):
        """ Generate an instance backup that contains:
            - Database dump in sql format
            - A folder with instance attachments called *filestore*
            - Json file with the repos ans hashes from the actual instance

        .. note:: If the method cannot access the filestore folder it won't be included in the
            backup

        :param dest_folder: Folder where the backup will be stored
        :param  reason: Optional parameter that is used in case
                          there is a particular reason for the backup
        :param tmp_dir (str): Optional parameter to store the temporary working dir,
                                default is /tmp
        :return: Full path to the generated backup
        """
        if not dest_folder:
            deployv_config = configuration.get_config()
            dest_folder = utils.get_backup_src(
                config_dict=self.__full_config, deployv_config=deployv_config)
        if not tmp_dir:
            tmp_dir = gettempdir()
        tmp_dir = mkdtemp(dir=tmp_dir, prefix='deployv_')
        try:
            files = self.files2backup(database_name, tmp_dir)
        except errors.DumpError as error:
            logger.error('An error raise during the database backup, cleaning up')
            raise error  # pylint: disable=E0702
        bkp_name = utils.generate_backup_name(database_name, reason, prefix)
        if not cformat:
            return {'files': files, 'name': bkp_name, 'tmp_dir': tmp_dir}
        backup = self.compress_files(files, bkp_name, dest_folder, cformat)
        shutil.rmtree(tmp_dir)
        return backup

    def restore_filestore(self, src_folder, database_name):
        """ Restore a filestore folder into a docker container that is already running
            and has the /tmp folder mounted as a volume un the host

        :param src_folder: Full path to the folder that contains the filestore you want to restore
        :param database_name: Database name being restored
        """
        dest_folder = path.join(self.temp_folder, path.basename(src_folder))
        try:
            shutil.copytree(src_folder, dest_folder)
        except shutil.Error as error:
            if "already exists" in str(error):
                logger.info("%s folder already exists, replacing", dest_folder)
                utils.clean_files(dest_folder)
                shutil.move(src_folder, dest_folder)
            else:
                raise
        except OSError as error:
            if "No such file or directory" in str(error):
                logger.warn("No filestore in the backup file")
            else:
                raise
        data_dir = self._get_fstore_from_config()
        fs_name = path.join(data_dir, "filestore", database_name)
        bash_lines = [
            "rm -rf {fsname}",
            "mkdir -p {newfs}",
            "mv /tmp/filestore {fsname}",
            "chown -R {user}:{user} {fsname}",
            "chmod -R o+r {fsname}"
        ]
        for bash_cmd in bash_lines:
            cmd = bash_cmd.format(
                fsname=fs_name,
                user=self.docker_env.get('odoo_user'),
                newfs=path.join(data_dir, "filestore"))
            res = self.exec_cmd(cmd)
            logger.debug('Command "%s", returned "%s"', cmd, res)

    def _get_fstore_from_config(self):
        data_dir = None
        container_name = self.docker_id
        odoo_config_file = self.docker_env.get('odoo_config_file')
        logger.debug('Copying %s from the container %s', odoo_config_file, container_name)
        try:
            res = self.cli.get_archive(container_name, odoo_config_file)
            logger.debug('Got from get_archive: %s', str(res))
        except errors.FileNotFoundInContainer:
            logger.error("Odoo config file is not in the path '%s'", odoo_config_file)
            return None
        for line in utils.decode(res[0].data).split('\n'):
            if line.strip().startswith("data_dir"):
                data_dir = line.split("=")[1].strip()
                break
        return data_dir

    def clone_db(self, database):
        """ Creates a new database copy of another database

        :param database: Name of the database that will be copied
        :return: Name of the new database copy of the one passed as parameter
        """
        psql_dict = self.db_config.copy()
        db_owner = self.config.get('db_owner')
        db_owner_passwd = self.config.get('db_owner_passwd')
        new_db = 'copy_{db}'.format(db=database)
        postgres_cfg = utils.odoo2postgres(psql_dict)
        postgres_cfg.update({'isolation_level': True, 'owner': db_owner,
                             'owner_password': db_owner_passwd})
        pg_shell = PostgresShell(postgres_cfg)
        pg_shell.drop(new_db, force=True)
        postgres_cfg.update({'dbname': 'template1'})
        with PostgresConnector(postgres_cfg) as db:
            db.execute("CREATE DATABASE \"{new}\" OWNER {owner} TEMPLATE \"{template}\""
                       .format(new=new_db, owner=psql_dict.get('db_user'),
                               template=database))
        return new_db

    def execute_query(self, database, sql):
        """ Retrieves all the translations from the provided database

        :param database: Name of the database from where deployv will
                         retrieve all the translations.
        :return: Dictionary containing all the translatins from the
                 provided database.
        """
        psql_dict = self.db_config.copy()
        psql_dict.update({'db_name': database})
        with PostgresConnector(utils.odoo2postgres(psql_dict)) as db:
            res = db.execute(sql)
        return res

    def get_views(self, database):
        arch_exists = self.execute_query(
            database,
            "select 1 from information_schema.columns where"
            " table_name='ir_ui_view' and column_name='arch'"
        )
        arch_column = 'arch' if arch_exists else 'arch_db'
        sql = """SELECT ir_model_data.module || '.' || ir_model_data.name xml_id, {arch} as arch
            FROM ir_model_data
            JOIN ir_ui_view ON res_id = ir_ui_view.id
            WHERE ir_model_data.model = 'ir.ui.view'
            ORDER BY xml_id;""".format(arch=arch_column)
        views = self.execute_query(database, sql)
        return views

    def compare_views(self, original_views, modified_views):
        """
        Compare all the views from views from production with the views from updates and returns
        a proper report

        :param original_views: The views from production database (a copy of course)
        :param modified_views: The views from the db with all changes applied
            (-u all, -u app_module).
        :return: a dict with the added, deleted and updated views. In the case of updated will
            return the diff between the production database and the updates database
        """
        res = {
            'updated': list(),
            'added': list(),
            'deleted': list()
        }
        checked = []
        for view_modified in modified_views:
            for view_original in original_views:
                if view_original['xml_id'] == view_modified['xml_id']:
                    checked.append(view_original)
                    if view_original['arch'] != view_modified['arch']:
                        res.get('updated').append({
                            'xml_id': view_original['xml_id'],
                            'original': view_original['arch'],
                            'modified': view_modified['arch']
                        })
                    break
            else:
                res.get('added').append(view_modified)
        for original_view in original_views:
            if original_view not in checked:
                res.get('deleted').append(original_view)
        return res

    def get_translations(self, database):
        translations = self.execute_query(
            database,
            """SELECT value,id,name,module FROM ir_translation"""
        )
        return translations

    def compare_translations(self, original_translations, modified_translations):
        """ Compare all the translated fields from two databases and returns a proper report

        :param original_translations: The translations contained in the production
                                      database (copy of course).
        :param modified_translations: The translations contained in the updates database with
                                      all the changes that will be applied in the
                                      production database.
        :return: A dict with the added, updated and removed translations between the production
                 database and the updates database.
        """
        checked = list()
        res = {
            'updated': list(),
            'added': list(),
            'deleted': list()
        }
        for modified_translation in modified_translations:
            for original_translation in original_translations:
                if original_translation['id'] == modified_translation['id']:
                    checked.append(original_translation)
                    if original_translation['value'] != modified_translation['value']:
                        res.get('updated').append({
                            'name': original_translation['name'],
                            'module': original_translation['module'],
                            'original': original_translation['value'],
                            'modified': modified_translation['value']
                        })
                    break
            else:
                res.get('added').append({
                    'name': modified_translation['name'],
                    'module': modified_translation['module'],
                    'value': modified_translation['value']
                })
        for original_translation in original_translations:
            if original_translation not in checked:
                res.get('deleted').append({
                    'name': original_translation['name'],
                    'module': original_translation['module'],
                    'value': original_translation['value'],
                })
        return res

    def get_menus(self, database):
        """ Retrieves all the menus from the provided database

        :param database: Name of the database from where deployv will
                         retrieve all the menus.
        :return: Dictionary containing all the menus from the
                 provided database.
        """
        res = dict()
        sql = """SELECT ir_model_data.module || '.' || ir_model_data.name AS xml_id,
                    res_id, ir_ui_menu.name
                FROM ir_model_data
                JOIN ir_ui_menu ON res_id = ir_ui_menu.id
                WHERE ir_model_data.model = 'ir.ui.menu';"""
        menus = self.execute_query(database, sql)
        for menu in menus:
            res.update({
                menu['xml_id']: menu
            })
        return res

    def menu_tree(self, menu_id, database):
        sql = """
        WITH RECURSIVE search_menu(id, parent_id, name, depth, hierarchypath) AS (
        SELECT menu.id, menu.parent_id, menu.name, 1, ppmenu.name || '->' || menu.name
        as hierarchypath
        FROM ir_ui_menu AS menu
        JOIN ir_ui_menu AS ppmenu
        ON menu.parent_id = ppmenu.id
        UNION ALL
            SELECT menu.id, menu.parent_id, menu.name, pmenu.depth + 1,
                hierarchypath || '->' || menu.name
            FROM ir_ui_menu as menu
            JOIN search_menu as pmenu
            ON menu.parent_id = pmenu.id
        )
        SELECT * FROM search_menu WHERE id = {menu} ORDER BY depth DESC LIMIT 1;
        """
        res = {}
        tree = self.execute_query(database, sql.format(menu=menu_id))
        if tree:
            res = tree[0]
        return res

    def compare_menus(self, original_menus, modified_menus,
                      original_database, modified_database):
        res = {
            'updated': list(),
            'added': list(),
            'deleted': list()
        }
        for uxml_id, urecord in modified_menus.items():
            if uxml_id in original_menus \
                    and original_menus[uxml_id]['name'] != urecord['name']:
                menu = self.menu_tree(urecord['res_id'], modified_database)
                res['updated'].append({
                    'xml_id': uxml_id,
                    'original': original_menus[uxml_id]['name'],
                    'modified': urecord['name'],
                    'hierarchypath': menu.get('hierarchypath')
                })
            if uxml_id not in original_menus:
                menu = self.menu_tree(urecord['res_id'], modified_database)
                res['added'].append({
                    'xml_id': uxml_id,
                    'name': urecord['name'],
                    'hierarchypath': menu.get('hierarchypath')
                })
        for pxml_id, precord in original_menus.items():
            if pxml_id not in modified_menus:
                menu = self.menu_tree(precord['res_id'], original_database)
                res['deleted'].append({
                    'xml_id': precord['xml_id'],
                    'name': precord['name'],
                    'hierarchypath': menu.get('hierarchypath')
                })
        return res

    def get_fields(self, database):
        """Gets all the fields from the specified database and returns
            their basic information.

        :param database: name of the database from where the fields will be
            retrieved.
        :return: List of dicts with the information of the fields::
            .. code-block:: json

                    [
                        {
                            'model': model,
                            'name': field,
                            'description': description,
                            'type': field_type \
                        } \
                    ]
        """
        sql = """
        select model, name, field_description as description,
        ttype as type from ir_model_fields;
        """
        res = self.execute_query(database, sql)
        return res

    def compare_fields(self, original_fields, modified_fields):
        res = {
            'updated': list(), 'added': list(), 'deleted': list(),
        }
        checked = []
        for modified in modified_fields:
            for original in original_fields:
                if modified['model'] == original['model']\
                        and modified['name'] == original['name']:
                    checked.append(original)
                    if modified['type'] != original['type']\
                            or modified['description'] != original['description']:
                        updated = {
                            'model': original['model'],
                            'name': original['name'],
                            'original': {'type': original['type'],
                                         'description': original['description']},
                            'modified': {'type': modified['type'],
                                         'description': modified['description']},
                        }
                        res.get('updated').append(updated)
                    break
            else:
                res.get('added').append(original)
        for original in original_fields:
            if original not in checked:
                res.get('deleted').append(original)
        return res

    def get_odoo_users(self, database):
        """ Retrieves the user ids of all the current users registered in
        the odoo instance.

        :param database: Name of the database where deployv will retrieve
                         the users ids from.
        :return: List of users ids
        """
        psql_dict = self.db_config
        psql_dict.update({'db_name': database})
        with PostgresConnector(utils.odoo2postgres(psql_dict)) as db:
            users = db.execute("SELECT id,login FROM res_users")
        return users

    @staticmethod
    def change_password(user_id, new_pass, db_name, db_config):
        """ Changes the specified user_id password

        :param user_id: Users id
        :param new_pass: New password that will be set to the user
        :param db_name: Database name to be updated
        :return: True if the password was changed, None otherwise
        """
        logger.info('Changing password for user_id %s', user_id)
        default_crypt_context = CryptContext(
            ['pbkdf2_sha512', 'md5_crypt'],
            deprecated=['md5_crypt'],
        )
        db_config.update({'db_name': db_name})
        with PostgresConnector(utils.odoo2postgres(db_config)) as db:
            try:
                res_user = db.execute(("select * from res_users where id = %(id)s"),
                                      {'id': user_id})
            except psycopg2.ProgrammingError as error:
                error_msg = ("Failed to change the password of the user {user}: {error}"
                             .format(user=user_id, error=str(error)))
                logger.error(error_msg)
                return {'error': error_msg}
            res = {"result": True}
            if res_user and res_user[0].get('password_crypt'):
                logger.info('Encrypted password')
                crypted_passwd = default_crypt_context.encrypt(new_pass)
                db.execute(("update res_users set password='',"
                            " password_crypt=%(passwd)s where id = %(id)s"),
                           {'passwd': crypted_passwd, 'id': user_id})
            elif res_user and res_user[0].get('password'):
                logger.info('Non encrypted password')
                db.execute("update res_users set password=%(passwd)s where id = %(id)s",
                           {'passwd': new_pass, 'id': user_id})
        res.update({"result": new_pass})
        return res

    def check_keys(self):
        """ Check if the provided keys into the docker container allows the user to connect
            github.com but does not check permissions

        :return: True if it is a valid key, False otherwise
        """
        logger.info('Checking keys in container %s', self.docker_id)
        res = self.exec_cmd('su {user} -c "ssh -T git@github.com"'
                            .format(user=self.config.get('env_vars').get('odoo_user')))
        if u'successfully authenticated, but GitHub does not provide shell access.' in res:
            logger.info('Keys checked properly')
            return True
        logger.error(
            'An error occurred while trying to connect to github.com: %s', res.strip())
        return False

    def install_deps(self):
        """ Install dependencies specified in the config json (if any). To see the return
        format check :func:`~deployv.base.dockerv.DockerV.install_packages`

        :return: A dic with the installation process
        """
        apt_list = self.config.get('apt_install', None)
        pip_list = self.config.get('pip_install', None)
        res = self.install_packages(apt_list, pip_list)
        return res

    def build_image(self):
        """ Calls the build helper in order to build the image that
        will be used to create the container, updates the configuration
        with the name of the new image and removes all the repos in the config
        if the build_image parameter is true so the repos in the image are not
        overriden when the container is created.

        :return: dict with the result of the build
        """
        build_res = build_helper.build_image(self.__full_config)
        if build_res[0] and build_res[1].get('result'):
            new_image = build_res[1].get('result')
            logger.debug('New image %s', new_image)
            self.config.update({'image_name': new_image})
        return build_res

    def _update_env_vars(self, env):
        """ Export enviroment when create container
            updated the dictionary env_vars
        :param env: dictionary with new variable environment to export
        """
        default_vars = self._generate_default_env_vars()
        for var in default_vars:
            if env.get(var):
                continue
            env.update({var: default_vars.get(var)})
        self.__full_config.get('container_config').get('env_vars').update(env)

    def _generate_default_env_vars(self):
        """ Method used that generates the default env vars that should be in the container.

        :return: Dict with the variables and their default values
        """
        res = {}
        db_name = (self.__full_config.get('instance', {}).get('config', {}).get('db_name', '') or
                   utils.generate_dbname(self.__full_config))
        res.update({'list_db': False, 'dbfilter': db_name})
        return res

    def clean_volumes(self):
        """Removes all the files in the /tmp folder, .ssh directory, in the filestore,
        and the logs inside the container. This method is used to clean the files before
        destroying a container so they are not present the next time we deploy the same container
        """
        logger.info('Cleaning volumes')
        for volume in self.config.get('volumes').values():
            logger.info('Removing volume: %s', volume)
            self.exec_cmd('rm -rf {volume}'.format(volume=volume))

    def set_parameters(self, db_name, parameters):
        """Inserts the provided parameters in the ir.config_parameter
        table of the provided database.

        :param db_name: Name of the database where the parameters will be inserted
        :param parameters: Dictionary with the parameters that will be created in the db where
            each key in the dictionary is the name (key) of the parameter and the value of that key
            is the value of that parameter.
        :type parameters: dict
        """
        config = self.db_config.copy()
        config.update({'db_name': db_name})
        with PostgresConnector(utils.odoo2postgres(config)) as db:
            for key, value in parameters.items():
                date = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                sql = (
                    "INSERT INTO ir_config_parameter ("
                    "    create_uid, write_date, value, write_uid, key, create_date)"
                    " VALUES (1, '{date}', '{value}', 1, '{key}', '{date}');"
                    .format(value=value, key=key, date=date))
                try:
                    db.execute(sql)
                except psycopg2.IntegrityError as error:
                    error_msg = utils.get_error_message(error)
                    if 'duplicate key value violates unique constraint' not in error_msg:
                        raise
                    # Remove parameter from the new db and insert it again with the new values
                    db.execute("delete from ir_config_parameter where key = '{key}'"
                               .format(key=key))
                    db.execute(sql)
        return True

    def set_global_env_vars(self, rcfile=False):
        """Adds the environment variables specified in the config json to the
            sh rc file so all users that connect to the instance can use them.

        :param rcfile: full path to the rc file where the env vars will be set
            (bash.bashrc, zshrc, etc), if no path is specified /etc/bash.bashrc will be used
        :type rcfile: str

        """
        env_vars = []
        if not rcfile:
            rcfile = '/etc/bash.bashrc'
        for var, value in self.config.get('env_vars', {}).items():
            var_string = 'export {var}={value}'.format(var=var.upper(), value=value)
            env_vars.append(var_string)
        vars_string = "bash -c \"echo -e '{env_vars}' | tee -a {rcfile}\"".format(
            env_vars='\n'.join(env_vars), rcfile=rcfile)
        self.exec_cmd(vars_string)


def deactivate_database(config, db_name):
    """ Deactivate a database: mail, cron (all but osv_memory.autovacuum, pac

    :param config: Config dict used to create the container and instance
    :param db_name: Database to be deactivated
    """

    logger.info('Deactivating database %s', db_name)

    # Sqls to be executed
    sqls = {
        'partner': "UPDATE res_partner SET opt_out = True;",
        'out_mail': ("UPDATE ir_mail_server"
                     " SET active = False, smtp_user = 'user', smtp_pass = 'pass';"),
        'in_mail': ("UPDATE fetchmail_server"
                    " SET active = False, \"user\" = 'user', password = 'pass';"),
        'old_pac': "UPDATE params_pac SET active = False;",
        'pac': "UPDATE res_pac SET active = False;",
        'cron': "UPDATE ir_cron SET active = False WHERE model <> 'osv_memory.autovacuum';",
        'saas_cron': ("UPDATE ir_cron SET active = False FROM ir_act_server WHERE "
                      "ir_cron.cron_name = ir_act_server.name AND ir_act_server.model_name"
                      " != 'ir.autovacuum';"),
        'notify': "UPDATE res_partner SET notify_email = 'none'",
        'ir_action': ("UPDATE base_action_rule SET active = False"
                      " WHERE name LIKE '%Create Sale from Purchase%'"),
        'rules': "UPDATE base_action_rule SET active = False WHERE kind = 'on_time';",
        'del_certificate': "DELETE FROM res_certificate;",
        'orchest_settings': ("UPDATE res_config_settings "
                             "SET github_access_token = '', gitlab_access_token = '', "
                             "odoo_listener_id = '', docker_hub_access_token = '', "
                             "quay_io_access_token = '', worker_security_token = ''"),
        'stored_passwords': "UPDATE network_software_logpass SET password = '123456'",
        'rabbit_active': ("UPDATE network_service SET active = False,"
                          " host = '0.0.0.0', virtual_host = 'vhost'"),
        'instance_ssh': "update deploy_group set ssh_file = null;",
        'db_uuid': ("UPDATE ir_config_parameter SET value = '{0}'"
                    " WHERE key = 'database.uuid';".format(uuid4())),
        'google_analytics': "UPDATE website SET google_analytics_key = ''",
        'payment_acquirer': "UPDATE payment_acquirer SET environment='test';",
        'abastotal_hotjar': ("UPDATE ir_ui_view SET active=false"
                             " WHERE key='theme_abastotal.hotjar';"),
        'l10n_pe_sunat': ("UPDATE res_company SET l10n_pe_edi_sunat_username = 'MODDATOS',"
                          " l10n_pe_edi_sunat_password = 'MODDATOS',"
                          " l10n_pe_edi_sunat_url ="
                          " 'https://e-beta.sunat.gob.pe/ol-ti-itcpfegem-beta/billService?wsdl'"),
        's3_config': ("UPDATE s3_config_settings"
                      " SET s3_bucket='', s3_secret_key='', s3_access_key_id=''"),
        's3_irconfig': ("UPDATE ir_config_parameter SET value = ''"
                        " WHERE key IN ('s3.access_key_id', 's3.bucket', 's3.secret_key')"),
    }

    psql_dict = {
        'dbname': db_name,
        'user': config.get('db_user'),
        'host': config.get('db_host'),
        'password': config.get('db_password'),
        'port': config.get('db_port', 5432)
    }
    if config.get('nginx_url'):
        parameters = [('url_freeze', 'web.base.url.freeze'), ('web_base_url', 'web.base.url')]
        for param in parameters:
            sql = (
                "UPDATE ir_config_parameter SET value='{url}' WHERE key='{key}';"
                .format(url=config.get('nginx_url'), key=param[1])
            )
            sqls.update({param[0]: sql})
    else:
        sqls.update({
            'url_freeze': "DELETE FROM ir_config_parameter WHERE key = 'web.base.url.freeze';",
        })
    try:
        with postgresv.PostgresConnector(psql_dict) as db:
            for name, sql in sqls.items():
                logger.debug('Running %s', name)
                try:
                    db.execute(sql)
                except psycopg2.ProgrammingError as error:
                    str_error = str(error)
                    if 'relation' in str_error:
                        logger.warn('This database has not %s, nothing to execute', str_error)
                    elif 'does not exist' in str_error:
                        logger.warn('An error ocurred, skipping %s. %s',
                                    name, str_error.split('\n')[0])
                    else:
                        raise
    except psycopg2.OperationalError as error:
        logger.exception('Could not deactivate the database: %s', error.message)
        return False
