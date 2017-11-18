import argparse
import bottle
import json
import os
import sys
import threading

from lod import execEnv
from lod import basics
from lod import utilities

###############################################################################################
# constants
###############################################################################################


_CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'CONFIG.txt')
_config = None
def _get_config():
    """
    load constants from a configuration file.
    Uses a cache.
    """
    global _config
    if _config is None:
        with open(_CONFIG_FILE, 'r') as f:
            _config = json.load(f)
    return _config

def _get_server_url():
    """
    get a connection string that can be used to connect to the server
    """
    use_local_server = _get_config()['use_local_server']
    if use_local_server:
        url = basics.get_shared_truth()['debug_server_url']
    else:
        url = basics.get_shared_truth()['server_url']
    return url

def _get_json_encoding_of_server():
    """
    get the type of encoding that the server uses for encoding JSON strings
    """
    res = basics.get_shared_truth()['json_encoding']
    return res

def _get_docker_registry_login_data():
    """
    get the registry, username and password for logging into the Docker registry
    """
    registry = basics.get_shared_truth()['docker_registry']
    username = basics.get_shared_truth()['docker_registry_username']
    password = basics.get_shared_truth()['docker_registry_password']
    return registry, username, password


##############################################################################################################
# main - initialize
##############################################################################################################


parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()


##############################################################################################################
# helper functions for authorization
##############################################################################################################


def require_collab_authentication(subparser):
    subparser.add_argument('-e', '--email', default=None,
        help="the password of your LOD account. This can be skipped if you have already used the 'configure' command.")
    subparser.add_argument('-p', '--password', default=None,
        help="the password of your LOD account. This can be skipped if you have already used the 'configure' command.")

def check_if_collab_credentials_are_configured(args):
    """
    if the arguments contain an email and password, return them.
    If not, check if there is a configuration file and use it.
    """
    if args.email is not None and args.password is not None:
        return
    l = [args.email, args.password]
    if not all(v is None for v in l) and not all(v is not None for v in l):
        raise ValueError("either both or neither of email and password must be specified.")
    if os.path.isfile(_CONFIG_FILE):
        with open(_CONFIG_FILE, 'r') as f:
            config = json.load(f)
            args.email = config['email']
            args.password = config['password']
    else:
        raise ValueError("email and password for Collab must be specified. Either use a configuration file for this or provide them as arguments. See --help for details.")

def require_docker_authentication(subparser):
    subparser.add_argument('-dr', '--docker-registry', default=None,
        help="the name of the registry of your Docker account. This can be skipped if you have already used the 'configure' command.")
    subparser.add_argument('-du', '--docker-user', default=None,
        help="the password of your Docker account. This can be skipped if you have already used the 'configure' command.")
    subparser.add_argument('-dp', '--docker-password', default=None,
        help="the password of your Docker account. This can be skipped if you have already used the 'configure' command.")

def check_if_docker_credentials_are_configured(args):
    """
    if the arguments contain an email and password, return them.
    If not, check if there is a configuration file and use it.
    """
    if args.docker_registry is not None and args.docker_user is not None and args.docker_password is not None:
        return
    l = [args.docker_registry, args.docker_user, args.docker_password]
    if not all(v is None for v in l) and not all(v is not None for v in l):
        raise ValueError("either all or none of docker's registry, username and password must be specified.")
    if os.path.isfile(_CONFIG_FILE):
        with open(_CONFIG_FILE, 'r') as f:
            config = json.load(f)
            args.docker_registry = config['docker_registry']
            args.docker_user = config['docker_user']
            args.docker_password = config['docker_password']
    else:
        raise ValueError("username and password for Docker must be specified. Either use a configuration file for this or provide them as arguments. See --help for details.")


##############################################################################################################
# main - functions
##############################################################################################################


def configure(args):
    with open(_CONFIG_FILE, 'w') as f:
        config = {
            'email' : args.email,
            'password' : args.password,
            'docker_registry' : args.docker_registry,
            'docker_user' : args.docker_user,
            'docker_password' : args.docker_password,
            'exec_env_root_folder' : args.exec_env_root_folder,
            'local_exec_env_port' : int(args.local_exec_env_port),
            'debug_mode' : args.debug_mode,
            'serverside_exec_env_recognition_key' : args.serverside_exec_env_recognition_key,
        }
        if args.use_debug_server:
            # if this is running with the debugging server, use the debugging server's url
            config['server_contact_url'] = basics.get_shared_truth()['debug_server_url']
        else:
            if args.serverside_exec_env_recognition_key is not None:
                # if a serverside_exec_env_recognition_key is given, this program is running locally on the server
                # it should contact the server through localhost
                config['server_contact_url'] = 'http://localhost:80/'
            else:
                # if no serverside_exec_env_recognition_key is given, contact the server through its official url
                config['server_contact_url'] = basics.get_shared_truth()['server_url']
        json.dump(config, f)
    print("successfully created configuration file.")

subparser = subparsers.add_parser('configure',
    help="""creates a configuration file to store your login credentials, so you don't have to specify them every time.
    Be aware that anyone who steals this configuration file will be able to log in with your credentials unless you delete the file again.""")
subparser.add_argument('-e', '--email', required=True,
    help="the email of your Collab account.")
subparser.add_argument('-p', '--password', required=True,
    help="the password of your Collab account.")
subparser.add_argument('-dr', '--docker-registry', required=True,
    help="the name of your Docker registry.")
subparser.add_argument('-du', '--docker-user', required=True,
    help="the username of your Docker registry.")
subparser.add_argument('-dp', '--docker-password', required=True,
    help="the password of your Docker registry.")
subparser.add_argument('-r', '--exec-env-root-folder', required=True,
    help="""the path to the root folder with which this Docker Container is being executed.
    This container needs to know this in addition to being mounted in that volume,
    because it gets access to Docker outside of its own container so that it can start other containers on this same volume.""")
subparser.add_argument('-port', '--local_exec_env_port', required=True,
    help="the port on which the ExecEnv will listen to incoming requests.")
subparser.add_argument('--use-debug-server', action='store_true',
    help="A debugging option for developers. If you don't know what this does, ignore it")
subparser.add_argument('--debug-mode', action='store_true',
    help="A debugging option for developers. If you don't know what this does, ignore it")
subparser.add_argument('-key', '--serverside_exec_env_recognition_key', required=False, default=None,
    help="a masterkey used only on the server. If you don't know what this does, ignore it.")
subparser.set_defaults(func=configure)


def delete_configuration(args):
    if os.path.isfile(_CONFIG_FILE):
        os.remove(_CONFIG_FILE)
        return
    else:
        raise ValueError("no config file exists.")

subparser = subparsers.add_parser('delete-configuration',
    help="""deletes the configuration file that stores your login credentials.""")
subparser.set_defaults(func=delete_configuration)


def delete_files_of_executions(args):
    if os.path.isfile(_CONFIG_FILE):
        exec_env_root_folder = _get_config()['exec_env_root_folder']
        for f in os.listdir(exec_env_root_folder):
            path = os.path.join(exec_env_root_folder, f)
            utilities.delete_file_or_folder(path)
        return
    else:
        raise ValueError("no config file exists.")

subparser = subparsers.add_parser('clean',
    help="""deletes the content of the folder that was specified as the exec_env_root_folder during configuration.
    This deletes all files that were generated while executing Scenarios.""")
subparser.set_defaults(func=delete_files_of_executions)


def run_in_loop(args):
    check_if_collab_credentials_are_configured(args)
    check_if_docker_credentials_are_configured(args)
    # create the ExecEnvManager
    execEnv.initialize_execution_environment_manager(_get_config(), basics.get_shared_truth(), args)
    # close ExecEnvs that have no incoming requests for too long (this happens if the Scenario has been closed but not properly shut down by the user)
    _shut_down_idle_exec_envs()
    # start listening for incoming messages
    port_to_listen_to = _get_config()['local_exec_env_port']
    print("listening on port %s..." % (port_to_listen_to,))
    bottle_is_quiet = (not args.verbose)
    try:
        # note: host='localhost' ensures that this can ony be accessed from the localhost
        bottle.run(host='localhost', port=port_to_listen_to, quiet=bottle_is_quiet)
    except (KeyboardInterrupt, SystemExit):
        print('keyboard interrupt')


subparser = subparsers.add_parser('run', help="Starts running the ExecEnv so that the website can connect to it.")
subparser.add_argument('-v', '--verbose', action='store_true',
    help="print additional information to the console.")
require_collab_authentication(subparser)
require_docker_authentication(subparser)
subparser.set_defaults(func=run_in_loop)


##############################################################################################################
# code for the server that listens for requests
##############################################################################################################


@bottle.route('/', method='POST')
def main_server_input():
    request_data = bottle.request.forms['request_data']
    request_data = json.loads(request_data)
    try:
        response_data = execEnv._the_manager.process_message_from_scenario(request_data)
    except:
        error_message = utilities.get_error_message_details()
        error_message = "Exception during processing of command:\n%s" % (error_message,)
        print(error_message)
        response_data = {
            'success' : False,
            'error_message' : error_message,
        }
    return(json.dumps(response_data))


@bottle.hook('after_request')
def enable_cors():
    """
    add some headers to each request.
    """
    # tell any requests from server_contact_url that they are ok
    the_server_url = _get_config()['server_contact_url']
    if the_server_url.endswith('/'):
        the_server_url = the_server_url[:-1]
    bottle.response.headers['Access-Control-Allow-Origin'] = the_server_url
    bottle.response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
    bottle.response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'


##############################################################################################################
# shutting down idle ExecEnvs
##############################################################################################################


def _shut_down_idle_exec_envs():
    """
    close ExecEnvs that have no incoming requests for too long (this happens if the Scenario has been closed but not properly shut down by the user)
    This function restarts itself so that it is called every few seconds.
    """
    # start this function again in a few seconds
    t = threading.Timer(5.0, _shut_down_idle_exec_envs)
    t.daemon = True # this needs to be a Daemon so that KeyboardInterrupt works
    t.start()
    # shut down all idle ExecEnvs
    execEnv._the_manager.shut_down_idle_exec_envs()


##############################################################################################################
# shutting down everything when the program is shut down
##############################################################################################################


import atexit
def exit_handler():
    if execEnv._the_manager is not None:
        execEnv._the_manager.shut_down_and_wait()
atexit.register(exit_handler)


##############################################################################################################
# main - finalize
##############################################################################################################


def main():
    if len(sys.argv)==1:
        # if the program is called without arguments, print the help menu and exit
        parser.print_help()
        sys.exit(1)
    else:
        args = parser.parse_args()
        args.func(args)

if __name__ == '__main__':
    main()






