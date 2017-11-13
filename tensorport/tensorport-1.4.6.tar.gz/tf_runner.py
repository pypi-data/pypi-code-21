import os
import argparse
import subprocess
import sys
import time
import atexit
import signal
import time
from multiprocessing import Pool, Process
import shutil
import stat

# List that stores all the children processes of this module
jobs = []
processes = []


def cleanup():
    """ Kills all the children processes.
    """
    for job in jobs:
        job.terminate()
        job.join()


# Register cleanup function to the exit of this module
atexit.register(cleanup)


def which(pgm):
    path = os.getenv('PATH')
    for p in path.split(os.path.pathsep):
        p = os.path.join(p, pgm)
        if os.path.exists(p) and os.access(p, os.X_OK):
            return p


def build_env(name, requirements=None, current_env=False, tf_version=''):
    if current_env:
        try:
            pybin = os.path.join(os.environ['VIRTUAL_ENV'], 'bin/python')
        except:
            pybin = sys.executable
    else:
        virtualenv_path = os.path.expanduser("~/.tensorport/env/%s/" % name)
        env_script_path = os.path.expanduser("~/.tensorport/env/%s/bootstrap.sh" % name)
        try:
            os.makedirs(virtualenv_path)
        except:
            shutil.rmtree(virtualenv_path)
            os.makedirs(virtualenv_path)
        activate_cmd = os.path.join(virtualenv_path, 'bin/activate')
        pybin = os.path.join(virtualenv_path, 'bin/python')
        virtualenv_bin = which('virtualenv')

        if tf_version is not '':
            tf_version = '==%s' % tf_version

        with open(env_script_path, 'w') as f:
            f.write("#!/bin/bash\n")
            f.write("%s %s\n" % (virtualenv_bin, virtualenv_path))
            f.write("source %s\n" % (activate_cmd))
            f.write("pip install tensorflow%s\n" % (tf_version))
            f.write("pip install tensorport\n")
            if requirements is not None:
                requirements_cmd = 'pip install -r %s' % requirements
                f.write("pip install -r %s\n" % (requirements))

        st = os.stat(env_script_path)
        os.chmod(env_script_path, st.st_mode | stat.S_IEXEC | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        p = subprocess.Popen("%s" % (env_script_path), shell=True)
        (output, error) = p.communicate()
    return pybin


def run_cmd(pybin, cmd, cwd, env={}):
    """
        run command in shell and captures output.
        args:
            name: string,
            cmd: string, the command.
            cwd: string, working directory for the command.
            env: dictionary, enviroment variables
    """

    env_cmd = '%s %s' % (pybin, cmd)
    signal.signal(signal.SIGINT, signal_handler)
    p = subprocess.Popen(env_cmd, cwd=cwd, env=env, shell=True)
    processes.append(p)
    (output, error) = p.communicate()
    if error:
        print("%s - ERROR: " % error)


def signal_handler(signal, frame):
    for p in processes:
        p.terminate()
    sys.exit(0)


def run_tf(cwd,
           package_path,
           module,
           mode,
           worker_replicas,
           ps_replicas,
           requirements=None,
           current_env=False,
           tf_version=''):
    assert (not module == '')

    # If package path exists then runs package_path.module else runs module only
    if package_path:
        package_path = '%s.' % package_path
    else:
        package_path = ''

    pybin = build_env('test',
                      requirements=requirements,
                      current_env=current_env,
                      tf_version=tf_version)

    # Single mode
    if mode == 'single-node':
        cmd = '-m %s%s' % (package_path, module)
        run_cmd(pybin, cmd, cwd, {})

    # Distributed mode
    if mode == 'distributed':
        # Compute ps_hosts string, assuming ps_hosts serve on ports 11000+
        ps_hosts = "localhost:11000"
        for i in range(ps_replicas - 1):
            ps_hosts += ",localhost:%d" % (11000 + i + 1)

        # Compute worker_hosts string, assuming worker_hosts serve on ports 12000+
        worker_hosts = "localhost:12000"
        for i in range(worker_replicas - 1):
            worker_hosts += ",localhost:%d" % (12000 + i + 1)

        # Spin up workers
        for i in range(worker_replicas):
            cmd = '-m %s%s' % (package_path, module)
            env = {
                "JOB_NAME": "worker",
                "TASK_INDEX": str(i),
                "PS_HOSTS": ps_hosts,
                "WORKER_HOSTS": worker_hosts
            }
            p = Process(target=run_cmd, args=(pybin, cmd, cwd, env,))
            p.daemon = True
            p.start()
            jobs.append(p)

        # Spin up parameter servers
        for i in range(ps_replicas):
            cmd = '-m %s%s' % (package_path, module)
            env = {
                "JOB_NAME": "ps",
                "TASK_INDEX": str(i),
                "PS_HOSTS": ps_hosts,
                "WORKER_HOSTS": worker_hosts
            }
            p = Process(target=run_cmd, args=(pybin, cmd, cwd, env,))
            p.daemon = True
            p.start()
            jobs.append(p)

        for job in jobs:
            job.join()


if __name__ == "__main__":
    """
        python tf_runner.py -module mnist -mode distributed -worker_replicas 2 -ps_replicas 1
    """
    parser = argparse.ArgumentParser(description='Run TF experiment')
    parser.add_argument('--module', type=str, help="Python module")
    parser.add_argument(
        '--package-path', type=str, default=None, help="Python package path")
    parser.add_argument(
        '--mode', type=str, default='single', help="distributed or single-node")
    parser.add_argument(
        '--worker-replicas',
        type=int,
        default=0,
        help="Number of worker replicas")
    parser.add_argument(
        '--ps-replicas',
        type=int,
        default=0,
        help="Number of parameter server replicas")
    parser.add_argument(
        '--requirements',
        type=int,
        default=0,
        help="Number of parameter server replicas")
    args = parser.parse_args()
    assert (args.mode in ('single', 'distributed'))
    run_tf(
        cwd=os.getcwd(),
        package_path=args.package_path,
        module=args.module,
        mode=args.mode,
        worker_replicas=args.worker_replicas,
        ps_replicas=args.ps_replicas)
