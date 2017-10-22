import argparse
import os
import subprocess
import urllib2
import utils
from shutil import copyfile
from agent import run_agent


def main():
    s3_base_link = 'https://s3.amazonaws.com/spotinst-public/services/spotinst-agent'
    s3_base_workers_link = s3_base_link + "/workers"
    s3_base_collectors_link = s3_base_link + "/collectors"
    modules_path = '/etc/spotinst/agent/modules'

    results = parse_arguments()
    action = results.action
    argument = results.argument
    second_argument = results.second_argument

    args = vars(results)
    verbose = False
    debug = False

    if args['verbose']:
        verbose = True

    if args['debug']:
        debug = True

    if action == "add-worker":
        if argument is not None:
            install_worker(modules_path, s3_base_workers_link, argument)
        else:
            print ("Please enter the name of the worker which you want to add.")

    elif action == "add-collector":
        if argument is not None:
            install_collector(argument, modules_path, s3_base_collectors_link)
        else:
            print ("Please enter the name of the collector which you want to add.")

    elif action == "run":
        run_agent(debug, verbose)

    elif action == "configure":
        if argument is not None:
            print ("configuring " + argument)
        else:
            print ("Spotinst agent configuration")

    elif action == "init":
        install_and_init_agent(argument, second_argument, modules_path)

    else:
        print ("Unrecognized action. Please use one of the following : add-worker, add-collector, configure")


def install_and_init_agent(token, account_id, modules_path):
    print ("Initializing agent")

    # Paths
    dirname, filename = os.path.split(os.path.abspath(__file__))
    script_full_path = os.path.join(dirname, 'data/installation/agent-init.sh')
    spotinst_agent_path = os.path.join(dirname, 'agent.py')
    create_agent_local_folders()
    handle_base_modules(dirname, modules_path)
    handle_yml_file(dirname)
    handle_credentials(account_id, script_full_path, spotinst_agent_path, token)
    handle_agent_path(spotinst_agent_path)
    runscript = subprocess.Popen(script_full_path)
    runscript.wait()
    print ('result : ' + str(runscript.communicate()))


def create_agent_local_folders():
    if not os.path.exists('/etc/spotinst'):
        os.makedirs('/etc/spotinst')
    if not os.path.exists('/etc/spotinst/agent'):
        os.makedirs('/etc/spotinst/agent')
    if not os.path.exists('/etc/spotinst/agent/config'):
        os.makedirs('/etc/spotinst/agent/config')
    if not os.path.exists('/var/log/spotinst'):
        os.makedirs('/var/log/spotinst')


def handle_base_modules(dirname, modules_path):
    basemodule_yml_path = os.path.join(dirname, 'data/configuration/basemodule.yml')
    utils_path = os.path.join(dirname, 'utils.py')
    basemodule_template_path = os.path.join(dirname, 'basemodule.py')

    if not os.path.exists(modules_path):
        os.makedirs(modules_path)
    copyfile(basemodule_template_path, modules_path + '/basemodule.py')
    copyfile(basemodule_yml_path, modules_path + '/basemodule.yml')
    copyfile(utils_path, modules_path + '/utils.py')


def handle_yml_file(dirname):
    default_agent_yml = os.path.join(dirname, 'data/configuration/spotinst-agent.yml')
    default_yml_destination = '/etc/spotinst/agent/config/spotinst-agent.yml'
    if not os.path.exists('/etc/spotinst/agent/config/spotinst-agent.yml'):
        copyfile(default_agent_yml, default_yml_destination)


def handle_credentials(account_id, script_full_path, spotinst_agent_path, token):
    if token is not None:
        print ("Creating Spotinst credentials directory")

        creds_file, creds_path = create_creds_file()
        write_creds_path(account_id, creds_file, token)
        os.chmod(creds_path, 0o777)

    else:
        # Credentials already exist - retrieve from file
        creds = utils.retrieve_creds()
        token = creds["token"]
        account_id = creds["account_id"]

    os.putenv("SPOTINST_TOKEN", token)
    os.putenv("SPOTINST_ACCOUNT_ID", account_id)
    os.putenv("SPOTINST_AGENT_PATH", spotinst_agent_path)
    os.chmod(script_full_path, 0o777)


def write_creds_path(account_id, creds_file, token):
    if account_id is not None:
        creds_file.write('token = ' + token + '\n' + 'account_id = ' + account_id)
    else:
        creds_file.write('token = ' + token)


def create_creds_file():
    if not os.path.exists('/root/.spotinst'):
        os.makedirs('/root/.spotinst')
    creds_path = '/root/.spotinst/credentials'
    creds_file = open(creds_path, 'w')
    return creds_file, creds_path


def handle_agent_path(spotinst_agent_path):
    try:
        os.symlink(spotinst_agent_path, '/usr/local/bin/spotinst-agent-service')
    except OSError:
        print ('Symlink exists. Skipping symlink creation.')
    os.chmod(spotinst_agent_path, 0o777)


def parse_arguments():
    parser = argparse.ArgumentParser(description='Spotinst Agent')
    parser.add_argument('action',
                        action="store",
                        help='The action to be performed. Options : add-worker / add-collector / configure.')
    parser.add_argument('argument',
                        action="store",
                        help='The name of worker or collector to add or configure.',
                        nargs='?')
    parser.add_argument('second_argument',
                        action="store",
                        help='Additional argument.',
                        nargs='?')
    parser.add_argument('--verbose', help='Verbose mode', required=False, action='store_true')
    parser.add_argument('--debug', help='Mock credentials', required=False, action='store_true')
    results = parser.parse_args()
    return results


def install_worker(modules_path, s3_base_workers_link, worker_name):
    print ("adding worker " + worker_name)
    try:
        handle_prerequisites(s3_base_workers_link, worker_name)
        get_worker_files(modules_path, s3_base_workers_link, worker_name)

    except Exception as e:
        print ("Could not get worker " + str(worker_name) + " Exception : " + str(e))


def install_collector(collector_name, modules_path, s3_base_collectors_link):
    print ("adding collector " + collector_name)
    try:
        handle_prerequisites(s3_base_collectors_link, collector_name)
        get_collector_files(collector_name, modules_path, s3_base_collectors_link)

    except Exception as e:
        print (e)
        print ("Could not get collector " + collector_name)


def get_worker_files(modules_path, s3_base_workers_link, worker_name):
    with open(modules_path + '/' + worker_name + '.py', 'wb') as worker:
        response = urllib2.urlopen(s3_base_workers_link + '/' + worker_name + '/' + worker_name + '.py')
        worker.write(response.read())
    with open(modules_path + '/' + worker_name + '.yml', 'wb') as worker_cfg:
        response = urllib2.urlopen(s3_base_workers_link + '/' + worker_name + '/' + worker_name + '.yml')
        worker_cfg.write(response.read())


def get_collector_files(collector_name, modules_path, s3_base_collectors_link):
    with open(modules_path + '/' + collector_name + '.py', 'wb') as collector:
        response = urllib2.urlopen(s3_base_collectors_link + '/' + collector_name + '/' + collector_name + '.py')
        collector.write(response.read())
    with open(modules_path + '/' + collector_name + '.yml', 'wb') as collector_cfg:
        response = urllib2.urlopen(s3_base_collectors_link + '/' + collector_name + '/' + collector_name + '.yml')
        collector_cfg.write(response.read())


def handle_prerequisites(s3_base_module_link, module_name):
    try:
        response = urllib2.urlopen(s3_base_module_link + '/' + module_name + '/' + module_name + '.req')
        requirements_file = response.read()
        requirements_names = requirements_file.split("\n")
        print ("This module requires the following packages to be installed:")
        for requirement in requirements_names:
            print (requirement)

        if len(requirements_names) > 0:
            import pip
            installed_packages = pip.get_installed_distributions()
            flat_installed_packages = [package.project_name for package in installed_packages]

            missing_packages = []
            for requirement in requirements_names:
                if requirement not in flat_installed_packages:
                    missing_packages.append(requirement)

            if len(missing_packages) <= 0:
                print ("All prerequisites have been met.")
                pass
            else:
                print ("Some prerequisites for this module have not been met. " \
                      "Please install the following before proceeding: " + str(missing_packages))
                exit(1)

    except Exception:
        pass
