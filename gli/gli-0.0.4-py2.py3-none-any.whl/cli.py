"""
gli - Gitlab Client

Usage:
  gli get_project  --list [-d] [--gitlab=<gitlab_config>]
  gli get_project  --project-name=<project_name> [--list] [-d] [--gitlab=<gitlab_config>]
  gli get_variable --project-name=<project_name> --key=<variable_name> [--list] [-d] [--gitlab=<gitlab_config>]
  gli get_variable --project-name=<project_name> --list [-d] [--gitlab=<gitlab_config>]
  gli set_variable --project-name=<project_name> --key=<variable_name> --value=<variable_value> [-d] [--gitlab=<gitlab_config>]
  gli delete_variable --project-name=<project_name> --key=<variable_name> [-d] [--gitlab=<gitlab_config>]
  gli get_environment --project-name=<project_name> --key=<environment_name> [--list] [-d] [--gitlab=<gitlab_config>]
  gli get_environment --project-name=<project_name> --list [-d] [--gitlab=<gitlab_config>]
  gli delete_environment --project-name=<project_name> --key=<environment_name> [--list] [-d] [--gitlab=<gitlab_config>]
  gli toggle_registry --project-name=<project_name> [-d] [--gitlab=<gitlab_config>]
  gli -h | --help
  gli -v | --version

Options:
  -d                            Debug mode.
  -h --help                     Show this screen.
  --list                        List object
  --key=key                     Key for object
  --value=value                 Value for object
  --gitlab=python-gitlab-conf   Gitlab Configuration name in ~/.python-gitlab.cfg
  -v --version                  Show version.

Commands:
  get_project : get details on a gitlab project
  get_variable: Retrieve list or value for Gitlab variables
  set_variable: Create or Update value for a Gitlab Pipeline variable
  delete_variable: Delete a Gitlab Pipeline variable
  get_environment: Retrieve environment 
  delete_environment: Delete an environment
  toggle_registry: allow to activate or deactivete the GitLab Container Registry

Examples:
  gli

Help:
  For help using this tool, please open an issue on the GitLab repository:
  https://gitlab.orangeportails.net/sallamand/gli/
"""


from inspect import getmembers, isclass
from docopt import docopt
from . import __version__ as VERSION

from . import utils
from pprint import pprint

def main():
    """Main CLI entrypoint."""
    import gli.commands
    options = docopt(__doc__, version=VERSION)


    #activate debuger
    #import ipdb; ipdb.set_trace()
    
    # Here we'll try to dynamically match the command the user is trying to run
    # with a pre-defined command class we've already created.
    for (k, v) in options.items(): 
        if hasattr(gli.commands, k) and v:
            module = getattr(gli.commands, k)
            gli.commands = getmembers(module, isclass)
            command = [command[1] for command in gli.commands if command[0].lower() == k.lower()][0]
            u = utils.Utils(options)
            command = command(u, options)
            command.run()
