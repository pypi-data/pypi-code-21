from __future__ import print_function
import click
import sys
from tabulate import tabulate
from time import sleep

from russell.cli.utils import (get_task_url, get_module_task_instance_id,
                             get_mode_parameter, wait_for_url)
from russell.client.experiment import ExperimentClient
from russell.client.module import ModuleClient
from russell.manager.auth_config import AuthConfigManager
from russell.manager.experiment_config import ExperimentConfigManager
from russell.constants import CPU_INSTANCE_TYPE, GPU_INSTANCE_TYPE,ENV_LIST
from russell.model.module import Module
from russell.model.experiment import ExperimentRequest
from russell.log import logger as russell_logger
import webbrowser



@click.command()
@click.option('--gpu/--cpu', default=False, help='Run on a gpu instance')
@click.option('--data', help='Data source id to use')
@click.option('--mode',
              help='Different russell modes',
              default='job',
              type=click.Choice(['job', 'jupyter', 'serve']))
@click.option('--env',
              help='Environment type to use',
              default='keras',
              type=click.Choice(sorted(ENV_LIST)))
@click.argument('command', nargs=-1)
@click.pass_context
def run(ctx, gpu, env, data, mode, command):
    """
    Run a command on Russell. Russell will upload contents of the
    current directory and run your command remotely.
    This command will generate a run id for reference.
    """
    command_str = ' '.join(command)
    experiment_config = ExperimentConfigManager.get_config()
    experiment_config.increment_version()
    ExperimentConfigManager.set_config(experiment_config)

    access_token = AuthConfigManager.get_access_token()
    version = experiment_config.version
    experiment_name = "{}/{}:{}".format(access_token.username,
                                        experiment_config.name,
                                        version)

    # Create module
    module = Module(name=experiment_config.name,
                    description=version,
                    command=command_str,
                    mode=get_mode_parameter(mode),
                    family_id=experiment_config.family_id,
                    default_env=env,
                    version=version,
                    project_id=experiment_config.project_id)
    module_resp = ModuleClient().create(module)
    if not module_resp:
        russell_logger.error("Remote project does not existed")
        return

    module_id = module_resp.get('id')
    project_id = module_resp.get('project_id')
    if not project_id == experiment_config.project_id:
        russell_logger.error("Project conflict")

    russell_logger.debug("Created module with id : {}".format(module_id))

    # Create experiment request
    instance_type = GPU_INSTANCE_TYPE if gpu else CPU_INSTANCE_TYPE
    experiment_request = ExperimentRequest(name=experiment_config.name,
                                           description=version,
                                           module_id=module_id,
                                           data_id=data,
                                           predecessor=experiment_config.experiment_predecessor,
                                           family_id=experiment_config.family_id,
                                           project_id=experiment_config.project_id,
                                           version=version,
                                           instance_type=instance_type)
    experiment_id = ExperimentClient().create(experiment_request)
    russell_logger.debug("Created experiment : {}".format(experiment_id))

    # Update expt config including predecessor
    experiment_config.set_module_predecessor(module_id)
    experiment_config.set_experiment_predecessor(experiment_id)
    ExperimentConfigManager.set_config(experiment_config)

    table_output = [["RUN ID", "NAME", "VERSION"],
                    [experiment_id, experiment_name, version]]
    russell_logger.info(tabulate(table_output, headers="firstrow"))
    russell_logger.info("")

    if mode in ['jupyter', 'serve']:
        while True:
            # Wait for the experiment / task instances to become available
            try:
                experiment = ExperimentClient().get(experiment_id)
                if experiment.task_instances:
                    break
            except Exception:
                russell_logger.debug("Experiment not available yet: {}".format(experiment_id))

            russell_logger.debug("Experiment not available yet: {}".format(experiment_id))
            sleep(1)
            continue

        # Print the path to jupyter notebook
        if mode == 'jupyter':
            # jupyter_url = get_task_url(get_module_task_instance_id(experiment.task_instances))
            jupyter_url = get_task_url(experiment_id, gpu)
            print("Setting up your instance and waiting for Jupyter notebook to become available ...")
            if wait_for_url(jupyter_url, sleep_duration_seconds=2, iterations=900):
                russell_logger.info("\nPath to jupyter notebook: {}".format(jupyter_url))
                webbrowser.open(jupyter_url)
            else:
                russell_logger.info("\nPath to jupyter notebook: {}".format(jupyter_url))
                russell_logger.info("Notebook is still loading or can not be connected now. View logs to track progress")

        # Print the path to serving endpoint
        if mode == 'serve':
            russell_logger.info("Path to service endpoint: {}".format(
                get_task_url(get_module_task_instance_id(experiment.task_instances),gpu)))

    russell_logger.info("""
    To view logs enter:
        russell logs {}
            """.format(experiment_id))
