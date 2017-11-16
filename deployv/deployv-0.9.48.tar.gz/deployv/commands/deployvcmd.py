# coding: utf-8

import sys
import time
import click
import pip
import simplejson as json
from jinja2 import Template
import deployv
from deployv.base import commandv
from deployv.helpers import utils, build_helper, configuration, json_helper
from deployv.instance import instancev
import os
import re
import logging

logger = logging.getLogger(__name__)  # pylint: disable=C0103


class DeployvCLI(click.MultiCommand):

    _cmds = {}
    _build_warnings = []

    def __init__(self):
        super(DeployvCLI, self).__init__(
            invoke_without_command=True, no_args_is_help=True, callback=self._callback
        )
        addons = [[dist.key, dist.version]
                  for dist in pip.get_installed_distributions()
                  if dist.key.startswith("deployv-addon-")]
        for addon in addons:
            addon_name = addon[0].replace('-', '_')
            addon_module = __import__(addon_name)
            command_name = addon_name.replace('deployv_addon_', '')
            try:
                command = getattr(addon_module, command_name)
            except AttributeError:
                self._build_warnings.append(
                    "Addon '{addon}' has no '{method}' method.".format(
                        addon=addon[0], method=command_name))
            else:
                try:
                    assert isinstance(command, click.core.Command)
                except AssertionError:
                    self._build_warnings.append(
                        "Error in addon '{addon}': Every command must be an instance"
                        " of <click.core.Command> class.'".format(addon=addon[0])
                    )
                else:
                    self.add_command(command.name, command)
        click.option("-l", "--log_level", help="Log level to show.", default='INFO')(self)
        click.option("-h", "--log_file", help="Write log history to a file.")(self)
        click.option("-C", "--config", help="Additional .conf files.")(self)

    def _callback(self, log_level, log_file, config):
        utils.setup_deployv_logger(level=log_level, log_file=log_file)
        logger.log(getattr(logging, log_level), 'Deployv version: %s', deployv.__version__)
        for warning in self._build_warnings:
            logger.debug(warning)
        self.config_parser = configuration.DeployvConfig(config)
        self.config = self.config_parser.config

    def list_commands(self, ctx):
        return sorted(self._cmds)

    def get_command(self, ctx, name):
        return self._cmds[name] if name in self._cmds else None

    def command(self, **kwargs):
        def wrapper(function):
            doc = function.__doc__
            if doc and not kwargs.get('help'):
                kwargs['help'] = doc
            if doc and not kwargs.get('short_help'):
                kwargs['short_help'] = doc if len(doc) <= 50 else doc[:50]+'...'
                kwargs['short_help'] = doc

            def decorator():
                cmd = click.command(**kwargs)(function)
                return cmd
            self.add_command(function.__name__, decorator())
            return decorator
        return wrapper

    def add_command(self, name, function):
        self._cmds[name] = function

cli = DeployvCLI()  # pylint: disable=C0103


@cli.command()
@click.pass_context
@click.option("-f", "--config_file", help="Json file with the configuration",
              default=False, required=True)
@click.option("-z", "--backup-src", default=False, required=False,
              help=("Backup to be restored or directory where the backups are stored, if empty,"
                    " deployv will search for the backup_folder in the config json or in"
                    " deployv\'s config files if that parameter is not specified in the json"))
@click.option("-e", "--external", help=("Use external branches json file"
                                        " (generated with branchesv)"),
              default=False, required=False)
@click.option("-k", "--key_file", help="the key file to be used",
              default=False, required=False)
@click.option("--without-db", is_flag=True, default=False,
              help="If true, no database will be loaded inside the container. Default False")
@click.option("-d", "--database", help="Database name to be used",
              default=False, required=False)
@click.option("--without-demo", is_flag=True, default=False,
              help="If true, no database will be loaded demo data"
                   " inside the container. Default False")
def create(ctx, config_file, backup_src, external, key_file, without_db, database, without_demo):
    """Creates an instance then loads a backup from backup_dir folder.
    """
    config = ctx.parent.command.config
    if external and not utils.validate_external_file(external):
        sys.exit(1)
    if key_file and not utils.validate_external_file(key_file):
        sys.exit(1)
    config_dict = utils.merge_config(config_file, keys_file=key_file, branches=external)
    if not config_dict:
        sys.exit(1)
    config_dict = json.loads(Template(json.dumps(config_dict)).render(config_dict))
    config_dict.get("container_config").get("env_vars").update({"without_demo": without_demo})
    if database:
        config_dict.get("instance").get("config").update({"db_name": database})
    if not config_dict.get('container_config').get('db_owner'):
        config_dict.get('container_config').update({
            'db_owner': config.get('postgres', 'db_user')
        })
    if not config_dict.get('container_config').get('db_owner_passwd'):
        config_dict.get('container_config').update({
            'db_owner_passwd': config.get('postgres', 'db_password')
        })
    command = commandv.CommandV(config_dict)
    res_create = command.create()
    if not res_create.get('result'):
        logger.error('Could not create the instance, some error raised: %s',
                     res_create.get('error'))
        sys.exit(1)
    if without_db:
        sys.exit(0)
    time.sleep(10)
    if not backup_src:
        backup_src = utils.get_backup_src(config_dict=config_dict, deployv_config=config)
    res_restore = command.restore(backup_src, database_name=database)
    if res_restore.get('result', False):
        logger.info('Done')
    else:
        logger.warn(
            'Could not restore any backup to the desired instance: %s',
            res_restore.get('error'))
        sys.exit(1)
    sys.exit(0)


@cli.command()
@click.pass_context
@click.option("-f", "--config_file", help="Json file with the configuration",
              default=False, required=False)
@click.option("-z", "--backup-dir", default=False, required=False,
              help=("Directory where the backup will be stored, if empty, deployv will use the"
                    " backup_folder parameter in the config json (if specified) or"
                    " in deployv\'s config files"))
@click.option("-e", "--external", help=("Use external branches json file"
                                        " (generated with branchesv)"),
              default=False, required=False)
@click.option("-r", "--reason", help="Reason why the backup is being generated (optional)",
              default=False, required=False)
@click.option("--tmp-dir", help="Temp dir to use (optional)",
              default=False, required=False)
@click.option("-c", "--cformat", help="Compression format to be used (tar.bz2 or tar.gz)",
              default='bz2', required=False)
@click.option("-d", "--database", help="Database name",
              default=False, required=True)
@click.option("-n", "--container", help="Container name or id",
              default=False, required=False)
@click.option("-x", "--prefix", required=False,
              help="Prefix used for the database name and the backup database_name")
def backupdb(ctx, config_file, backup_dir, external, reason, tmp_dir, database, cformat,
             container, prefix):
    """Generates a backup and saves it in backup_dir folder.
    """
    if config_file and container:
        logger.error(
            'You cannot use both parameters, -n and -f. Use one or another')
        sys.exit(1)
    elif not config_file and not container:
        logger.error(
            'You must use one of the -z or -k parameters.')
        sys.exit(1)
    if config_file:
        if external and not utils.validate_external_file(external):
            sys.exit(1)
        config_dict = utils.merge_config(config_file, branches=external)
        if not config_dict:
            sys.exit(1)
        config_dict = json.loads(Template(json.dumps(config_dict)).render(config_dict))
    elif container:
        config_dict = {
            'container_config': {'container_name': container}
        }
    if not backup_dir:
        config = ctx.parent.command.config
        backup_folder = utils.get_backup_src(config_dict=config_dict,
                                             deployv_config=config)
        backup_dir = backup_folder or os.getcwd()
    command = commandv.CommandV(config_dict)
    res = command.backup(backup_dir, database, cformat, reason, tmp_dir, prefix)
    if res.get('result', False):
        logger.info('Backup generated: %s', res.get('result'))
        logger.info('Done')
    else:
        logger.error('Could not generate the backup: %s', res.get('error'))


@cli.command()
@click.pass_context
@click.option("-f", "--config_file", help="Json file with the configuration",
              default=False, required=True)
@click.option("-z", "--backup-src", default=False, required=False,
              help=("Backup to be restored or directory where the backups are stored, if empty,"
                    " deployv will search for the backup_folder in the config json or in"
                    " deployv\'s config files if that parameter is not specified in the json"))
@click.option("-d", "--database", help="Database name to be used",
              default=False, required=False)
@click.option("-n", "--container", help="Container name or id",
              default=False, required=False)
@click.option("-s", "--admin_pass", help="Admin password",
              default=False, required=False)
@click.option("-t", "--instance-type", type=click.Choice(instancev.INSTANCE_TYPES),
              help=("Specifies the type of instance. test, "
                    "develop, updates or production"))
@click.option("-x", "--prefix", required=False,
              help="Prefix used for the database name")
@click.option("--nginx-url", required=False,
              help=("Container's nginx url used to set the web url freeze parameter,"
                    " if empty the parameter will be deleted"))
def restore(ctx, config_file, backup_src, database, container, admin_pass,
            instance_type, prefix, nginx_url):
    """Restores a backup from a directory.
    """
    config = ctx.parent.command.config
    if config_file and container or not config_file and not container:
        logger.error(
            'You must use one, and only one of the -n or -f parameters.')
        sys.exit(1)
    if config_file:
        config_dict = utils.merge_config(config_file)
        if not config_dict:
            sys.exit(1)
        config_dict = json.loads(Template(json.dumps(config_dict)).render(config_dict))
    if container:
        config_dict = {
            'container_config': {'container_name': container},
            'instance': {'config': {'admin': admin_pass}}
        }
    if instance_type:
        config_dict.get('instance').update({'instance_type': instance_type})
    if prefix:
        config_dict.get('instance').update({'prefix': prefix.lower()})
    if not config_dict.get('container_config').get('db_owner'):
        config_dict.get('container_config').update({
            'db_owner': config.get('postgres', 'db_user')
        })
    if not config_dict.get('container_config').get('db_owner_passwd'):
        config_dict.get('container_config').update({
            'db_owner_passwd': config.get('postgres', 'db_password')
        })
    if nginx_url:
        config_dict.get('container_config').update({'nginx_url': nginx_url})
    command = commandv.CommandV(config_dict)
    if container and not prefix and not database:
        punctuation = '''!"#$%&'()*+,-.:;<=>?@[]^`{|}~'''
        dbfilter = command.instance_manager.docker_env.get('dbfilter', '')
        database = re.sub('[%s]' % re.escape(punctuation), '', dbfilter)
        if not database:
            logger.error(
                'Could not get the name of the database, '
                'please use the -x or -d parameter')
            sys.exit(1)
    if not backup_src:
        backup_src = utils.get_backup_src(config_dict=config_dict, deployv_config=config)
        if not backup_src:
            logger.error(
                'You "must" specify a backup to restore or the database folder. '
                'You can do it using the --backup-src (-z) option. '
                'Also in the json inside container_config > backup_folder. '
                'Or in the deployv config files inside deployer > backup_folder.')
            sys.exit(1)
    res = command.restore(backup_src, database_name=database)
    if res.get('result', False):
        message = "Backup {backup_name} restored in database {dbname}".\
            format(backup_name=res.get('result').get('backup'),
                   dbname=res.get('result').get('database_name'))
        logger.info(message)
        logger.info('Done')
    else:
        logger.error('Could not restore the backup: %s', res.get('error'))
        sys.exit(1)
    sys.exit(0)


@cli.command()
@click.option("-f", "--config_file", help="Json file with the configuration",
              default=False, required=True)
@click.option("-d", "--database", help="Database name to be updated",
              default=False, required=False)
def update(config_file, database):
    """Updates an existing instance, clone the branches to the specified ones and updates database.
    """
    config_dict = json_helper.load_json(config_file)
    if not config_dict:
        sys.exit(1)
    config_dict = json.loads(Template(json.dumps(config_dict)).render(config_dict))
    command = commandv.CommandV(config_dict)
    res_create = command.create()
    if res_create.get('result', False):
        res_update = command.updatedb(database)
        if res_update.get('error', False):
            logger.error(
                'An error was detected during update process: %s', res_update.get('error'))
            sys.exit(1)
        else:
            logger.info('Update done')
            sys.exit(0)
    else:
        logger.error('the instance was not created: %s',
                     res_create.get('error'))
        sys.exit(1)


@cli.command()
@click.option("-n", "--container", help="Container name or id")
@click.option("-d", "--database", help="Database name to be used")
@click.option("-s", "--admin_password", help="Password used to log in as admin in odoo",
              required=False, default=False)
@click.option("--nginx-url", required=False,
              help=("Container's nginx url used to set the web url freeze parameter,"
                    " if empty the parameter will be deleted"))
def deactivate(container, database, admin_password, nginx_url):
    """Deactivates a specific database inside a container.
    """
    config_dict = {
        'container_config': {
            'container_name': container,
            'nginx_url': nginx_url
        },
        'instance': {
            'config': {
                'admin': admin_password
            }
        }
    }
    command = commandv.CommandV(config_dict)
    command.deactivate(database)


@cli.command()
@click.pass_context
@click.option("-x", "--prefix", required=True,
              help="Prefix used for the database name and the backup database_name")
@click.option("-p", "--store_path", help="Directory where the deactivated backups will be stored",
              default=False, required=True)
@click.option("-z", "--backup-src", default=False, required=False,
              help=("Backup that will be deactivated or folder with backups to deactivate the"
                    " latest backup for the customer (-x parameter), if empty, deployv will"
                    " search for the backup_folder parameter in deployv\'s config files"))
@click.option("-s", "--admin_password", help="Password used to log in as admin in odoo",
              required=True)
@click.option("-c", "--cformat", default='bz2', required=False,
              help="Compression format to be used (tar.bz2 or tar.gz)")
@click.option("--upload", default=False, required=False,
              help="URL to upload the deactivated backup")
@click.option("--remove", is_flag=True, default=False, required=False,
              help="If true, only remove backup after it have been"
                   " successfully uploaded to the server")
@click.option("--nginx-url", required=False,
              help=("Container's nginx url used to set the web url freeze parameter,"
                    " if empty the parameter will be deleted"))
@click.option("--no-fs", is_flag=True, default=False, required=False,
              help=("If true, does not include file store in backup"))
def deactivate_backup(ctx, prefix, store_path, backup_src, admin_password,
                      cformat, upload, remove, nginx_url, no_fs):
    config = ctx.parent.command.config
    db_config = dict(config.items('postgres'))
    default_config = utils.load_default_config()
    command = commandv.CommandV(default_config)
    if not backup_src:
        backup_src = utils.get_backup_src(deployv_config=config)
        if not backup_src:
            logger.error(
                'You "must" specify a backup to deactivate or the database folder. '
                'You can do it using the --backup-src (-z) option. '
                'Or in the deployv config files inside deployer > backup_folder.')
            sys.exit(1)
    db_config.update({'nginx_url': nginx_url})
    res = command.deactivate_backup(db_config, backup_src, prefix,
                                    store_path, cformat, admin_password, no_fs=no_fs)
    if not res:
        sys.exit(1)
    logger.info('Deactivated backup stored in %s', res)
    if upload:
        utils.upload_file(res, upload)
        logger.info('File uploded to %s', upload)
        if remove:
            os.remove(res)
    logger.info('Done')


@cli.command()
@click.pass_context
@click.option("-f", "--config_file",
              help=("Config file where the parameters for the build will be taken from,"
                    " if the other parameters are specified, the config will be"
                    " updated accordingly. If not specified, a default config will be used."
                    " You have to use this parameter in order to build an image with more than"
                    " one base repo"))
@click.option("-u", "--repo", help="URL of the main github repository that will be used")
@click.option("-b", "--branch", help=("Branch of the repository that will be cloned."
                                      " If no branch is specified, then the version will be used"))
@click.option("-i", "--image-name",
              help=("Name of the docker image that will be used as a base to build the new image."
                    " Default: vauxoo/odoo-{version}-image"))
@click.option("-w", "--working-folder", default="/tmp",
              help=("Name of the folder where the files required for the build will be stored"
                    "(default /tmp)"))
@click.option("-v", "--version",
              help=("Version of the oca dependencies that will be used in the image"
                    " e.g. 8.0, 9.0, etc."))
@click.option("--force", is_flag=True, default=False,
              help="Removes the working folder if it already exists before creating it again")
@click.option("-O", "--odoo-repo",
              help=("Specific odoo repository to be cloned instead of the default one, must be"
                    " in the format namespace/reponame#branch. Example: odoo/odoo#8.0"))
@click.option("-T", "--tag", default=False,
              help="Custom name for the new image, if not specified a name will be generated")
def build(ctx, config_file, repo, branch, image_name, working_folder,
          version, force, odoo_repo, tag):
    config = ctx.parent.command.config
    if config_file:
        config_dict = json_helper.load_json(config_file)
        if not config_dict:
            sys.exit(1)
    else:
        config_dict = {}
    default_config = utils.load_default_config()
    config_dict = utils.merge_dicts(default_config, config_dict)
    if repo and not version or version and not repo:
        logger.error('If you specify the repo or the version you have to specify'
                     ' the other one as well')
        sys.exit(1)
    if branch and not repo:
        logger.error('If you specify a branch you have to specify the repo')
        sys.exit(1)
    if not branch:
        branch = version
    if repo and branch:
        repo_name = repo.split('/')[-1].split('.')[0]
        repo_path = os.path.join('extra_addons', repo_name)
        config_dict = build_helper.add_repo(config_dict, branch, repo_name, repo_path, repo)
    if odoo_repo:
        if not re.search('.*/.*#.*', odoo_repo):
            logger.error('The specified odoo repo does not have the correct format.'
                         ' Example format: odoo/odoo#8.0')
            sys.exit(1)
        parts = odoo_repo.split('#', 1)
        odoo_branch = parts[1]
        odoo_url = 'https://github.com/{repo}.git'.format(repo=parts[0])
        config_dict = build_helper.add_repo(config_dict, odoo_branch, 'odoo', 'odoo', odoo_url)
    config_dict.get('container_config').update({'base_image_name': image_name})
    if not config_dict.get('container_config').get('db_owner'):
        config_dict.get('container_config').update({
            'db_owner': config.get('postgres', 'db_user')
        })
    if not config_dict.get('container_config').get('db_owner_passwd'):
        config_dict.get('container_config').update({
            'db_owner_passwd': config.get('postgres', 'db_password')
        })
    config_dict.get('container_config').update({'build_image': True})
    res = build_helper.build_image(config_dict, version, working_folder, force, tag)
    if not res[0]:
        logger.error(res[1].get('error'))
        sys.exit(1)
    logger.info('Image built: %s', res[1].get('result'))
    sys.exit(0)


@cli.command(short_help="Creates the default configuration.")
@click.pass_context
def setup_config(ctx):
    """Creates the default configuration directories and files. These are
    located in `/etc/deployv` (system level) and `~/.config/deployv` (user
    level). You may have to use `sudo` to create the file at system level.
    """
    ctx.parent.command.config_parser.setup_config_dirs()


@cli.command()
@click.pass_context
@click.option('-f', '--config_file', help='Instance configuration file (json).')
@click.option('-n', '--container', help='Production container name.')
@click.option('-d', '--db_name', help='Production database name.')
@click.option('-u', '--db_user', help='Production database user.')
@click.option('-w', '--db_password', help='Production database password.')
@click.option('-h', '--db_host', help='Production database host.')
@click.option('-p', '--db_port', help='Production database port.')
@click.option('-z', '--backup_dir', help='Directory where the production backup will be saved.')
@click.option('-e', '--expected_backup_size',
              help='Expected size for the backup to make sure is available before generating it.')
@click.option('-i', '--image', help='Stable image name to update the production instance.')
@click.option('-v', '--version',
              help='Odoo version to detect bin file. If empty, will be gotten from the env vars.')
@click.option('-t', '--status_checks', default=4,
              help="How many times it will try to check the status of Odoo (running/stopped).")
@click.option('-c', '--cformat', default='bz2',
              help='Compression format to be used (tar.bz2 or tar.gz).')
@click.option('-m', '--tmp-dir', help='Temp directory where the backup is going to be generated.')
@click.option('-x', '--prefix', help='Prefix for the backup name.')
@click.option('-r', '--reason', help='Reason for the backup name.', default='preupdate')
def update_production(ctx, config_file, container, db_name, db_user, db_password, db_host, db_port,
                      version, backup_dir, expected_backup_size, image, status_checks,
                      cformat, tmp_dir, prefix, reason):
    """Updates a production instance.
    """
    config_dict = config_file and json_helper.load_json(config_file)
    if not config_dict:
        logger.error('Error loading the configuration dictionary.')
        logger.error('You must specify the json configuration file path (-f).')
        sys.exit(1)
    if container:
        config_dict['container_config'].update({'container_name': container})
    if not config_dict['container_config'].get('container_name') and not (
            config_dict['instance']['customer_id'] and config_dict['instance']['task_id']):
        logger.error('You must specify the container name (-n). '
                     'Or you can set it in the instance config file (-f) '
                     '(instance > customer_id + task_id).')
        sys.exit(1)
    json_db_config = config_dict['instance'].get('config') or {}
    db_config = {
        'db_name': db_name or json_db_config.get('db_name'),
        'db_user': db_user or json_db_config.get('db_user'),
        'db_password': db_password or json_db_config.get('db_password'),
        'db_host': db_host or json_db_config.get('db_host'),
        'db_port': db_port or json_db_config.get('db_port'),
        'dbfilter': db_name or json_db_config.get('db_name'),
    }
    if not all(db_config.values()):
        logger.error('Production database configuration is incomplete. '
                     'You must set name (-d), user (-u), password (-w), host (-h), and port (-p). '
                     'Or you can set it on the instance config file (-f) (instance > config).')
        sys.exit(1)
    config_dict.get('instance').get('config').update(db_config)
    if not backup_dir:
        backup_dir = utils.get_backup_src(
            config_dict=config_dict, deployv_config=ctx.parent.command.config
        ) or os.getcwd()
    if not os.access(backup_dir, os.F_OK | os.R_OK | os.W_OK):
        logger.error('You must specify a writable backup directory (-z). '
                     'Or you can do it on the Deployv config file (deployer > backup_folder).')
        sys.exit(1)
    if not expected_backup_size or not utils.byte_converter(expected_backup_size):
        logger.error('You must specify a valid expected size for the backup (-e). This to ensure '
                     'the space is available before generating the backup. For example: 50GB.')
        sys.exit(1)
    if image:
        config_dict['container_config'].update({'image_name': image})
    if not config_dict['container_config'].get('image_name'):
        logger.error('You must specify the docker image name to be used (-i). '
                     'Or you can set it on the instance configuration file (-f) '
                     '(container_config > image_name).')
        sys.exit(1)
    config_dict['container_config'].update({
        'image_name': '{img}:stable'.format(
            img=config_dict['container_config']['image_name'].split(':')[0])})
    command = commandv.CommandV(config_dict)
    res = command.update_production(
        backup_dir, expected_backup_size,
        odoo_version=version, status_checks=status_checks, cformat=cformat,
        tmp_dir=os.path.expanduser(tmp_dir or ''), prefix=prefix, reason=reason)
    if res.get('error'):
        logger.error(res.get('error'))
        sys.exit(1)
    logger.info('Update result: %s', json.dumps(res.get('result'), indent=2))
    sys.exit(0)
