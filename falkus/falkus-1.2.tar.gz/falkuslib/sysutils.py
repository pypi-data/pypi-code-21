import pip
import os
import sys
import logging
import subprocess
import shutil

def find_falkus_package_path():
    try:
        script_path = os.path.dirname(__file__)
    except NameError:
        script_path = os.path.dirname(sys.argv[0])
    script_path =  os.path.realpath(script_path)
    falkus_root = os.path.dirname(script_path)
    logging.info("falkus root path: %s", falkus_root)
    if not os.path.isfile(os.path.join(falkus_root, "falkus")):
        return None
    if not os.path.isfile(os.path.join(falkus_root, "setup.py")):
        return None
    if not os.path.isdir(os.path.join(falkus_root, "falkuslib")):
        return None
    return falkus_root


def pip_install(dependency, target_path):
    pip.main(['install', '--upgrade', '--target', target_path, dependency])


def pip_install_local_falkus(target_path):
    falkus_path = find_falkus_package_path()
    if falkus_path:
        logging.info("found a local version of falkus, using it (useful for falkus development)")
        try:
            import shutil
            src = os.path.join(falkus_path, "falkuslib")
            dst = os.path.join(target_path, "falkuslib")
            shutil.rmtree(dst, ignore_errors=True)
            shutil.copytree(src, dst)
            return
        except Exception:
            logging.exception("could not use the local version of falkus - using the standard one")
    logging.info("using the public release of falkus")
    pip.main(['install', '--upgrade', '--target', target_path, "falkus"])


def run_dynamodb_with_docker():
    subprocess.check_output(['docker', 'run', '-d', '-p', '8000:8000', "-v", "/tmp/data:/data/",
                             "dwmkerr/dynamodb", "-inMemory"])


def run_sam_local(frontend_dir):
    subprocess.check_call(['sam', 'local', 'start-api', '--static-dir', frontend_dir])


def run_sam_package(bucket_name):
    output = subprocess.check_output(
        ['sam', 'package', '--template-file', './template.yaml',
         "--s3-bucket", bucket_name, "--output-template-file", "packaged.yaml"])
    logging.info("SAM output: {}".format(output))


def run_sam_deploy(cf_stack_name):
    #TODO: if the region in ~/.aws/credentials is wrong this will push in the wrong region all the API and lambda
    logging.warning("the support for deploy is not yet full, make sure your region in ~/.aws/credentials [default]"
                    " is the same of the project, or lambda and api will end up in the wrong region")
    output = subprocess.check_output(['sam', 'deploy', '--template-file', './packaged.yaml',
                                      "--stack-name", cf_stack_name, "--capabilities", "CAPABILITY_IAM"])
    logging.info("SAM output: {}".format(output))


def run_s3_sync(dir, bucket_url):
    output = subprocess.check_output(['aws', 's3', 'sync', dir, bucket_url])
    logging.info("AWS cli output: {}".format(output))


def copy_directory_content(src, dst):
    for f in os.listdir(src):
        p = os.path.join(src, f)
        if os.path.isdir(p):
            shutil.copytree(p, os.path.join(dst, f))
        else:
            shutil.copy(p, os.path.join(dst, f))

