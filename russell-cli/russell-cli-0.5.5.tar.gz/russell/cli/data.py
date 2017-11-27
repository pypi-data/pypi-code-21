import click
import webbrowser
import traceback
from tabulate import tabulate
import sys
import russell
from russell.client.data import DataClient
from russell.client.files import FsClient, SOCKET_STATE
from russell.client.module import ModuleClient
from russell.config import generate_uuid
from russell.manager.auth_config import AuthConfigManager
from russell.manager.data_config import DataModuleConfig, DataConfigManager
from russell.model.module import *
from russell.log import logger as russell_logger

@click.group()
def data():
    """
    Subcommand for data operations
    """
    pass


@click.command()
@click.option('--id',
              help='Remote dataset id to init')
@click.option('--name',
              help='Remote dataset name to init')
# @click.argument('name', nargs=1)
def init(id, name):
    """
    Initialize a new data upload.
    After init ensure that your data files are in this directory.
    Then you can upload them to Russell. Example:

        russell data upload
    """
    if not id and not name:
        russell_logger.error("Neither id or name offered")
        return
    data_info = {}
    access_token = AuthConfigManager.get_access_token()
    dc = DataClient()
    try:
        if id:
            data_info = dc.get_data_info_by_id(id=id)
        elif name:
            data_info = dc.get_data_info_by_name(access_token.username, name)
    except Exception as e:
        russell_logger.error(traceback.format_exc())
        return

    name = data_info.get('name')
    data_id = data_info.get('id')
    latest_version = data_info.get('latest_version')    # mostly as 0 on remote
    data_config = DataModuleConfig(name=name,
                                   dataset_id=data_id,
                                   version=latest_version,
                                   family_id=generate_uuid())
    DataConfigManager.set_config(data_config)
    russell_logger.info("Data source \"{}\" initialized in current directory".format(name))
    russell_logger.info("""
    You can now upload your data to Russell by:
        russell data upload
    """)


@click.command()
def _upload():
    """
    Deprecated: Upload data in the current dir to Russell.
    """
    data_config = DataConfigManager.get_config()
    access_token = AuthConfigManager.get_access_token()
    version = data_config.version + 1

    # Create data object
    data_name = "{}/{}:{}".format(access_token.username,
                                  data_config.name,
                                  version)
    data = ModuleRequest(name=data_config.name,
                         description=version,
                         version=version,
                         entity_id=data_config.dataset_id,
                         module_type="data")
    data_id = DataClient()._create(data)
    russell_logger.debug("Created data with id : {}".format(data_id))
    russell_logger.info("Upload finished")

    # Update expt config including predecessor
    data_config.increment_version()
    data_config.set_data_predecessor(data_id)
    DataConfigManager.set_config(data_config)

    # Print output
    table_output = [["DATA ID", "NAME", "VERSION"],
                    [data_id, data_name.encode("utf-8"), version]]
    russell_logger.info(tabulate(table_output, headers="firstrow"))

@click.command()
@click.option('-r',
              default=False,
              help='Remote dataset upload status')
@click.option('-m',
              help='Message to commit',
              type=click.STRING,
              default="")
@click.pass_context
def upload(ctx, r, m):
    """
    Upload data in the current dir to Russell.
    """
    if m and len(m) > 1024:
        russell_logger.error("Message body length over limit")
        sys.exit()
    message = m
    try:
        data_config = DataConfigManager.get_config()
        access_token = AuthConfigManager.get_access_token()
    except Exception as e:
        russell_logger.error("Configuration Error")
        return

    # version = data_config.version + 1
    version = data_config.version

    # Create data object

    data = ModuleRequest(name=data_config.name,
                         description=message,
                         module_type="data",
                         entity_id=data_config.dataset_id,
                         version=version)

    dc = DataClient()
    if r:
        module_info = ModuleClient().get(id=data_config.data_predecessor)
        print_upload([module_info])
        return

    create_module_info = dc.create_module(data)
    data_module_id = create_module_info.get('id')
    data_module_version = int(create_module_info.get('version'))

    # Update expt config including predecessor
    data_config.set_version(data_module_version)
    data_config.set_data_predecessor(data_module_id)
    DataConfigManager.set_config(data_config)

    fc = FsClient()
    try:
        fc.socket_upload(file_type="data",
                         filename="./",
                         access_token=access_token.token,
                         file_id=data_module_id,
                         user_name=access_token.username,
                         data_name=data_config.name)
    except Exception as e:
        sys.exit(e)

    russell_logger.debug("Created data with id : {}".format(data_module_id))
    russell_logger.info("\nUpload finished")

    data_name = "{}/{}:{}".format(access_token.username,
                                  data_config.name,
                                  data_module_version)
    # Print output
    table_output = [["DATA ID", "NAME", "VERSION"],
                    [data_module_id, data_name.encode("utf-8"), data_module_version]]
    russell_logger.info(tabulate(table_output, headers="firstrow"))
    russell_logger.info('''
Upload finished, start extracting to data module\n
    To check data status enter:
        russell data status {}\n'''.format(data_module_id))

@click.command()
@click.argument('id', required=False, nargs=1)
def status(id):
    """
    Show the status of a run with id.
    It can also list status of all the runs in the project.
    """
    if id:
        datamodule_source = DataClient().get(id)
        print_data([datamodule_source])
    else:
        data_config = DataConfigManager.get_config()
        data_sources = DataClient().get_all(dataset_id=data_config.dataset_id)
        if isinstance(data_sources, list) and len(data_sources) > 0:
            print_data(data_sources)


def print_data(data_sources):
    headers = ["DATA ID", "CREATED", "STATE", "DISK USAGE", "NAME", "VERSION"]
    data_list = []
    for data_source in data_sources:
        data_list.append([data_source.id,
                          data_source.created_pretty,
                          data_source.state,
                          data_source.size_pretty,
                          data_source.name,
                          str(data_source.version)])
    russell_logger.info(tabulate(data_list, headers=headers))

def print_upload(module_sources):
    headers = ["MODULE ID", "STATE" "CREATED", "DISK USAGE", "VERSION"]
    data_list = []
    for data_source in module_sources:
        data_list.append([data_source.id,
                          data_source.state,
                          data_source.created_pretty,
                          data_source.size_pretty,
                          data_source.name.encode('utf-8'),
                          str(data_source.version)])
    russell_logger.info(tabulate(data_list, headers=headers))

@click.command()
@click.option('-u', '--url', is_flag=True, default=False, help='Only print url for viewing data')
@click.argument('id', nargs=1)
def output(id, url):
    """
    Shows the output url of the run.
    By default opens the output page in your default browser.
    """
    # data_source = DataClient().get(id)
    data_url = "{}/files/data/{}/".format(russell.russell_host, id)
    if url:
        russell_logger.info(data_url)
    else:
        russell_logger.info("Opening output directory in your browser ...")
        webbrowser.open(data_url)


@click.command()
@click.argument('id', nargs=1)
@click.option('-y', '--yes', is_flag=True, default=False, help='Skip confirmation')
def delete(id, yes):
    """
    Delete data set.
    """
    data_source = DataClient().get(id)

    if not yes:
        click.confirm('Delete Data: {}?'.format(data_source.name), abort=True, default=False)

    if DataClient().delete(id):
        russell_logger.info("Data deleted")
    else:
        russell_logger.error("Failed to delete data")

data.add_command(delete)
data.add_command(init)
data.add_command(upload)
data.add_command(status)
data.add_command(output)
