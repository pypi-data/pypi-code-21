import argparse
import docker
import io
import json
import os
import requests
import shutil
import sys
import zipfile

from collab import basics
from collab import utilities

##############################################################################################################
# constants
##############################################################################################################


PATH_PREFIX = '/collab'
INPUT_FILE_LOCATION = os.path.join(PATH_PREFIX, 'in.txt')
OUTPUT_FILE_LOCATION = os.path.join(PATH_PREFIX, 'out.txt')

_CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'CONFIG.txt')
_DOCKER_EXAMPLE_NAME = 'fibonacci'
_DOCKER_EXAMPLE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), _DOCKER_EXAMPLE_NAME)
_INPUT_EXAMPLE_NAME = 'input_example'
_INPUT_EXAMPLE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), _INPUT_EXAMPLE_NAME)
_RULE_EXAMPLE_NAME = 'rule_example'
_RULE_EXAMPLE_PATH_TUTORIAL = os.path.join(os.path.dirname(os.path.abspath(__file__)), _RULE_EXAMPLE_NAME, 'tutorial_rule.txt')
_RULE_EXAMPLE_PATH_BLANK = os.path.join(os.path.dirname(os.path.abspath(__file__)), _RULE_EXAMPLE_NAME, 'blank_rule.txt')

def _get_server_url():
    """
    get a connection string that can be used to connect to the server
    """
    use_local_server = False
    if os.path.isfile(_CONFIG_FILE):
        with open(_CONFIG_FILE, 'r') as f:
            config = json.load(f)
            use_local_server = config['use_local_server']
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
        help="the password of your Collab account. This can be skipped if you have already used the 'configure' command.")
    subparser.add_argument('-p', '--password', default=None,
        help="the password of your Collab account. This can be skipped if you have already used the 'configure' command.")

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


def docker_connect(args, use_local_registry=False):
    """
    connect to a Docker registry
    """
    if use_local_registry:
        client = docker.from_env()
    else:
        client = docker.from_env()
        client.login(username=args.docker_user, password=args.docker_password, registry=args.docker_registry)
    return client


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
            'use_local_server' : args.use_local_server,
        }
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
subparser.add_argument('--use-local-server', action='store_true',
    help="A debugging option for developers. If you don't know what this does, ignore it")
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


def generate_example_program(args):
    dst = args.folder
    if os.path.exists(dst):
        raise ValueError("the specified path already exists: %s" % dst)
    shutil.copytree(_DOCKER_EXAMPLE_PATH, dst)
    # manually delete the pycache that gets created for some reason...
    cache = os.path.join(dst, '__pycache__')
    if os.path.exists(cache):
        shutil.rmtree(cache)


subparser = subparsers.add_parser('generate-example-program', help="creates an example program, as a tutorial what the files of a program for Collab should look like.")
subparser.add_argument('-f', '--folder', required=True, help="the path to the folder in which the example program will be generated.")
subparser.set_defaults(func=generate_example_program)


def generate_example_input_folder(args):
    dst = args.folder
    if os.path.exists(dst):
        raise ValueError("the specified path already exists: %s" % dst)
    shutil.copytree(_INPUT_EXAMPLE_PATH, dst)


subparser = subparsers.add_parser('generate-example-input-folder',
    help="creates a folder with files for testing a program. To be used with test-program-offline")
subparser.add_argument('-f', '--folder', required=True, help="the path to the folder containing the Dockerfile of the program to generate.")
subparser.set_defaults(func=generate_example_input_folder)


def test_program_offline(args):
    # copy files to prepare the folder in which the Docker Image will be executed
    if args.preparation_folder is not None:
        src = args.preparation_folder
        dst = args.execution_folder
        utilities.copy_and_overwrite(src, dst)
    # build the Docker Image
    if not args.quiet:
        print("compiling Docker Image...")
    client = docker_connect(None, use_local_registry=True)
    image = client.images.build(path=args.program_folder, nocache=args.force_docker_recompilation)
    # execute the Image
    if not args.quiet:
        print("executing Docker Image as Docker Container...")
    try:
        folder_mapping = {
            args.execution_folder : {
                'bind' : "/collab",
                'mode' : 'rw',
            },
        }
        client.containers.run(image=image, volumes=folder_mapping)
    except docker.errors.ContainerError as error:
        print("encountered error while executing Docker Container:")
        error_message = error.stderr.decode("utf-8")
        print(error_message)


subparser = subparsers.add_parser('test-program-offline',
    help="creates a Docker Image locally, based on a program folder. Executes that Image the same way it will be executed on the server. Deletes the Image.")
subparser.add_argument('-p', '--program-folder', required=True, help="the path to the folder containing the Dockerfile of the program to generate.")
subparser.add_argument('-e', '--execution-folder', required=True, help="the path to the folder in which the Docker Image will be executed.")
subparser.add_argument('-prep', '--preparation-folder', default=None,
    help="the path to a folder containing files that will be copied into the execution-folder before the execution, overwriting it. Use generate-example-input-folder to create an example of this.")
subparser.add_argument('--force-docker-recompilation', action='store_true',
    help="ignore the Docker cache and always recompile. This may be useful for debugging if you are e.g. modifying external dependencies, since Docker will skip recompilation if the only thing that changed were external files.")
subparser.add_argument('-q', '--quiet', action='store_true',
    help="don't print anything to the console.")
subparser.set_defaults(func=test_program_offline)


def upload_program(args):
    if args.quiet and args.verbose:
        raise ValueError("can't be both quiet and verbose at the same time")
    check_if_collab_credentials_are_configured(args)
    check_if_docker_credentials_are_configured(args)
    folder = args.folder
    if folder is None:
        folder = os.getcwd()
    image_name = args.name
    # when used locally, a suffix is added to the uploaded program
    # NOTE: this is just a debugging measure: it ensures that when I upload the same program twice, once locally and once to the server,
    # it will create two different Docker images
    use_local_server = False
    if os.path.isfile(_CONFIG_FILE):
        with open(_CONFIG_FILE, 'r') as f:
            config = json.load(f)
            use_local_server = config['use_local_server']
    if use_local_server:
        image_name = image_name + 'local'
    program_description = args.description
    docker_registry = args.docker_registry
    docker_user_name = args.docker_user
    full_image_name_with_registry = "%s/%s/%s" % (docker_registry, docker_user_name, image_name,)
    #
    # get the description
    #
    descr_file_path = os.path.join(folder, 'DESCRIPTION.txt')
    if program_description is None:
        if os.path.isfile(descr_file_path):
            with open(descr_file_path, 'r') as f:
                program_description = f.read()
        else:
            program_description = "no description given."
    #
    # get miscellaneous arguments
    #
    max_execution_duration = args.max_execution_duration
    if max_execution_duration is None:
        max_execution_duration = basics.get_shared_truth()['new_program_default_max_execution_duration']
    #
    # build the Docker image
    #
    # find out how many versions of the Image already exist, if any
    if not args.quiet:
        print("compiling Docker Image...")
    client = docker_connect(args, use_local_registry=use_local_server)
    image = client.images.build(path=folder, nocache=args.force_docker_recompilation)
    #
    # if required, upload the source code as well
    #
    no_source_upload = args.no_source_upload
    files = {}
    if not no_source_upload:
        virtual_file = io.BytesIO()
        zip_handle = zipfile.ZipFile(virtual_file, 'w', zipfile.ZIP_DEFLATED)
        utilities.zipdir(folder, zip_handle)
        zip_handle.close()
        files['source_files_archive'] = virtual_file.getvalue()
    #
    # notify the Collab server
    # (and optionally upload the files)
    #
    if not args.quiet:
        print("contacting Collab server...")
    data = {
        'email' : args.email,
        'password' : args.password,
        'full_image_name_with_registry' : full_image_name_with_registry,
        'docker_user_name' : docker_user_name,
        'program_name' : image_name,
        'program_description' : program_description,
        'max_execution_duration' : max_execution_duration,
    }
    url = _get_server_url() + 'api/upload_program/'
    resp = requests.post(url, data=data, files=files)
    resp = json.loads(resp._content.decode(_get_json_encoding_of_server()))
    #
    # print the response received from the server
    #
    if 'error' in resp:
        print("error message from server:\n%s" % (resp['error'],))
        print("---\ncancelling upload.")
        return
    program_id = resp['id']
    program_name = resp['name']
    version = resp['version']
    response_text = resp['response_text']
    if args.verbose:
        print(response_text)
    #
    # Tag the Image with the right version number and push it to the registry server
    #
    # tag the image
    if not args.quiet:
        print("tagging and uploading Docker Image...")
    tag = "version-%d" % (version,)
    full_identifier = '%s:%s' % (full_image_name_with_registry, tag)
    # (tagging with this API apparently works by just building the Image again and relying on the cache to avoid actually rebuilding it)
    image = client.images.build(path=folder, tag=full_identifier)
    # push to the registry
    # (unless we are running in the developer-only local mode for faster testing of the website)
    if not use_local_server:
        for line in client.images.push(full_image_name_with_registry, tag=tag, stream=True):
            msgs = [json.loads(a) for a in line.decode('utf-8').split('\n') if a != ""]
            for msg in msgs:
                if 'error' in msg:
                    raise Exception(msg['error'])
                elif 'status' in msg:
                    if args.verbose:
                        print("\t%s" % (msg['status'],))
    if not args.quiet:
        print("done. Created version %d of Program '%s' with id=%d, with Docker Image:\n%s" % (version, program_name, program_id, full_identifier,))

subparser = subparsers.add_parser('upload-program',
    help="""upload a program to the server, making it available for use by execution rules.
    Can be used for creating new programs, or updating existing ones.""")
subparser.add_argument('-f', '--folder', default=None,
    help="the path to the folder that should be uploaded. This should target the directory in which the Dockerfile is located. Defaults to the current directory.")
subparser.add_argument('-n', '--name', required=True,
    help="the name of the program. If an existing name is given, a new version of it will be created. Otherwise, a new program is created.")
subparser.add_argument('-d', '--description', default=None,
    help="a short description of the program. If none is given, defaults to the content of the file 'DESCRIPTION.txt' stored in the folder that is being uploaded, if one exists.")
subparser.add_argument('--max-execution-duration', type=float, default=None,
    help="the time, in seconds, that the program will be executed for before being quit by force, unless this is specified otherwise by whatever caused the program's execution. Defaults to %f" % (basics.get_shared_truth()['new_program_default_max_execution_duration'],))
subparser.add_argument('--no-source-upload', action='store_true',
    help="do not upload the source files to the Collab server, to make them available for inspection.")
subparser.add_argument('--force-docker-recompilation', action='store_true',
    help="ignore the Docker cache and always recompile. This may be useful for debugging if you are e.g. modifying external dependencies, since Docker will skip recompilation if the only thing that changed were external files.")
subparser.add_argument('-q', '--quiet', action='store_true',
    help="don't print anything to the console.")
subparser.add_argument('-v', '--verbose', action='store_true',
    help="print lots of extra information to the console.")
require_collab_authentication(subparser)
require_docker_authentication(subparser)
subparser.set_defaults(func=upload_program)


def download_program(args):
    check_if_collab_credentials_are_configured(args)
    folder = args.folder
    if folder is None:
        folder = os.getcwd()
    id = args.identifier
    name = args.name
    version = args.version
    if id is None and name is None:
        raise ValueError("either the name or the ID of the program must be given.")
    if id is not None and name is not None:
        raise ValueError("only one out of the name and the ID of the program must be given, not both.")
    if name is not None and '#' in name:
        if version is not None:
            raise ValueError("don't specify the version both directly and indirectly (as part of the name). One of the two suffices.")
        tmp = name.split('#')
        name = tmp[0]
        version = tmp[1]
        if len(tmp) != 2:
            raise ValueError("invalid name format. Use either '<program_name>'' or '<program_nam>#<version>'.")
    if id is not None and version is not None:
        raise ValueError("don't specify a version along with an ID. IDs identify programs unambiguously. Only names are ambiguous and need clarification.")
    #
    # notify the Collab server
    #
    data = {}
    if name is not None:
        data['name'] = name
    if version is not None:
        data['version'] = int(version)
    if id is not None:
        data['id'] = int(id)
    url = _get_server_url() + 'api/download_program/'
    resp = requests.post(url, data=data)
    #
    # print the response received from the server
    #
    response_file = resp._content
    response_data = json.loads(resp.headers['additional_response_data'])
    if 'error' in response_data:
        print("error message from server:\n%s" % (response_data['error'],))
        return
    response_text = response_data['response_text']
    id = response_data['id']
    name = response_data['name']
    version = response_data['version']
    source_code_exists = response_data['source_code_exists']
    if not args.quiet:
        print(response_text)
    #
    # unzip the file, if there is one
    #
    if not args.quiet:
        print("retrieved program: id=%d, name='%s', version=%d" % (id, name, version,))
    if source_code_exists:
        if not args.quiet:
            print("unpacking files...")
        unzipped_path = os.path.join(folder, "%s-version-%d" % (name, version,))
        zip_ref = zipfile.ZipFile(io.BytesIO(response_file), 'r')
        zip_ref.extractall(unzipped_path)
        zip_ref.close()
        if not args.quiet:
            print("done.")
    else:
        if not args.quiet:
            print("no source code for this Program and version was made available.")

subparser = subparsers.add_parser('download-program',
    help="""download a program from the server.""")
subparser.add_argument('-f', '--folder', default=None,
    help="the path to the folder where the downloaded program should be placed. The folder containing the program will be put inside this folder. Defaults to the current directory.")
subparser.add_argument('-id', '--identifier', default=None,
    help="the ID of the program to download.")
subparser.add_argument('-n', '--name', default=None,
    help="""the name of the program to download. If no version is provided along with this, you get the latest version.
    The version can either be specified explicitly, through the --version tag, or by appending '#<version>' to the name.""")
subparser.add_argument('-v', '--version', default=None,
    help="the version of the program to download. This is only meaningful when combined with the program's name.")
subparser.add_argument('-q', '--quiet', action='store_true',
    help="don't print anything to the console.")
require_collab_authentication(subparser)
subparser.set_defaults(func=download_program)


def generate_example_rule(args):
    src_file = _RULE_EXAMPLE_PATH_BLANK if args.blank else _RULE_EXAMPLE_PATH_TUTORIAL
    print(src_file)
    dst_file_name = args.name if args.name is not None else 'example.txt'
    dst = os.path.join(args.folder, dst_file_name)
    shutil.copyfile(src_file, dst)
    print("created file '%s'." % (dst,))


subparser = subparsers.add_parser('generate-example-rule', help="creates an example file that explains how to define a rule, as a tutorial.")
subparser.add_argument('-f', '--folder', required=True, help="the path to the folder in which the example program will be generated.")
subparser.add_argument('-b', '--blank', action='store_true', help="instead of generating a file that explains how to define a rule, generate a blank file that can be filled out quickly.")
subparser.add_argument('-n', '--name', help="the name of the file to generate. This overwrites the defaults.")
subparser.set_defaults(func=generate_example_rule)


def upload_rule(args):
    check_if_collab_credentials_are_configured(args)
    # load the file
    with open(args.file, 'r') as f:
        rule_dictionary = json.load(f)
    # determine the name of the rule, either from the filename or from the explicitly given name
    rule_name = args.name
    if rule_name is None:
        rule_name = os.path.splitext(os.path.basename(args.file))[0]
    # send a request to the server
    data = {
        'email' : args.email,
        'password' : args.password,
        'rule_name' : rule_name,
        'rule_as_dictionary' : json.dumps(rule_dictionary),
        'deactivate_older_versions' : json.dumps(True if args.deactivate else False),
    }
    url = _get_server_url() + 'api/upload_rule/'
    resp = requests.post(url, data=data)
    resp = json.loads(resp._content.decode(_get_json_encoding_of_server()))
    #
    # print the response received from the server
    #
    if 'error' in resp:
        print("error message from server:\n%s" % (resp['error'],))
        print("---\ncancelling upload.")
        return
    response_text = resp['response_text']
    print(response_text)
    cleaned_rule_dict = json.loads(resp['rule_as_dictionary'])
    if args.result is not None:
        print("creating file for the final rule: '%s'" % args.result)
        with open(args.result, 'w') as f:
            json.dump(cleaned_rule_dict, f, indent=4)


subparser = subparsers.add_parser('upload-rule', help="uploads a file describing a rule, which generates a new rule.")
subparser.add_argument('-n', '--name', required=False, help="the name of the rule. Defaults to the filename.")
subparser.add_argument('-f', '--file', required=True, help="the path to the file to be uploaded.")
subparser.add_argument('-d', '--deactivate', default=False, help="whether or not to deactivate all existing rules with the same name.")
subparser.add_argument('-r', '--result',
    help="""if this parameter is given, the fully parsed and created rule is written to the selected file.
    This may differ in some ways from the original file, for instance because default values are set.""")
require_collab_authentication(subparser)
subparser.set_defaults(func=upload_rule)


def delete_rule(args):
    check_if_collab_credentials_are_configured(args)
    # send a request to the server
    data = {
        'email' : args.email,
        'password' : args.password,
        'rule_id' : args.id,
        'rule_name' : args.name,
        'rule_version' : args.version,
    }
    url = _get_server_url() + 'api/delete_rule/'
    resp = requests.post(url, data=data)
    resp = json.loads(resp._content.decode(_get_json_encoding_of_server()))
    #
    # print the response received from the server
    #
    if 'error' in resp:
        print("error message from server:\n%s" % (resp['error'],))
        return
    response_text = resp['response_text']
    print(response_text)


subparser = subparsers.add_parser('delete-rule', help="deletes one or more existing rules you own.")
subparser.add_argument('-i', '--id', required=False, help="the ID of the rule.")
subparser.add_argument('-n', '--name', required=False, help="the name of the rule.")
subparser.add_argument('-v', '--version', required=False, help="the version of the rule.")
require_collab_authentication(subparser)
subparser.set_defaults(func=delete_rule)


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


