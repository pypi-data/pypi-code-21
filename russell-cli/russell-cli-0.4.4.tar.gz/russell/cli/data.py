import click
import webbrowser
from tabulate import tabulate

import russell
from russell.client.data import DataClient
from russell.config import generate_uuid
from russell.manager.auth_config import AuthConfigManager
from russell.manager.data_config import DataConfig, DataConfigManager
from russell.model.data import DataRequest
from russell.log import logger as russell_logger


@click.group()
def data():
    """
    Subcommand for data operations
    """
    pass


@click.command()
@click.argument('name', nargs=1)
def init(name):
    """
    Initialize a new data upload.
    After init ensure that your data files are in this directory.
    Then you can upload them to Russell. Example:

        russell data upload
    """
    data_config = DataConfig(name=name, family_id=generate_uuid())
    DataConfigManager.set_config(data_config)
    russell_logger.info("Data source \"{}\" initialized in current directory".format(name))
    russell_logger.info("""
    You can now upload your data to Russell by:
        russell data upload
    """)


@click.command()
def upload():
    """
    Upload data in the current dir to Russell.
    """
    data_config = DataConfigManager.get_config()
    access_token = AuthConfigManager.get_access_token()
    version = data_config.version

    # Create data object
    data_name = "{}/{}:{}".format(access_token.username,
                                  data_config.name,
                                  version)
    data = DataRequest(name=data_config.name,
                       description=version,
                       version=version)
    data_id = DataClient().create(data)
    russell_logger.debug("Created data with id : {}".format(data_id))
    russell_logger.info("Upload finished")

    # Update expt config including predecessor
    data_config.increment_version()
    data_config.set_data_predecessor(data_id)
    DataConfigManager.set_config(data_config)

    # Print output
    table_output = [["DATA ID", "NAME", "VERSION"],
                    [data_id, data_name, version]]
    russell_logger.info(tabulate(table_output, headers="firstrow"))


@click.command()
@click.argument('id', required=False, nargs=1)
def status(id):
    """
    Show the status of a run with id.
    It can also list status of all the runs in the project.
    """
    if id:
        data_source = DataClient().get(id)
        print_data([data_source])
    else:
        data_sources = DataClient().get_all()
        print_data(data_sources)


def print_data(data_sources):
    headers = ["DATA ID", "CREATED", "DISK USAGE", "NAME", "VERSION"]
    data_list = []
    for data_source in data_sources:
        data_list.append([data_source.id, data_source.created_pretty,
                          data_source.size, data_source.name, data_source.version])
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
    data_url = "{}/files/data/{}/".format(russell.russell_host,id)
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
