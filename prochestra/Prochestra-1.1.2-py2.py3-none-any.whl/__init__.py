import subprocess
import datetime
import os
import argparse
import json
import shlex
import yaml

__version__ = "1.1.2"


class Prochestra(object):

    def __init__(self, log=None, log_prefix="PROCHESTRA ", silent=False):
        self.log_file = log
        self.log_prefix = log_prefix
        self.silent = silent
        self.state = {}

    def info(self, text, *args):
        if self.log_file:
            ts = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            print(ts + ' ' + self.log_prefix + text.format(*args),
                  file=self.log_file, flush=True)

    def run(self, job_list):
        jobs = job_list.jobs
        self.state = dict.fromkeys(list(map(lambda j: j.id, jobs)), None)
        for job in jobs:
            if not all(map(lambda dep: self.state[dep] if dep in self.state else None, job.dependencies)):
                self.info("{} SKIPPED", job.id)
                continue
            self.info("{} STARTED", job.id)
            # combine the cmd and the args into one string, because of shell=True
            argv = [' '.join([job.cmd] + [shlex.quote(arg) for arg in job.args])]
            p = subprocess.run(argv, shell=True,
                               stderr=subprocess.DEVNULL if self.silent else self.log_file,
                               stdout=subprocess.DEVNULL if self.silent else self.log_file)
            self.state[job.id] = p.returncode == 0
            if p.returncode != 0:
                print("Prochestra: job '{}' exited with code {}.".format(job.id, p.returncode))
                self.info("{} FAILED WITH CODE {}.", job.id, p.returncode)
            else:
                self.info("{} FINISHED", job.id)

        return all(self.state.values())


class Job(object):
    def __init__(self, data):
        self.id = data['id']
        self.cmd = data['cmd']

        args = data['args'] if 'args' in data else []
        self.args = [args] if type(args) is str else args

        dependencies = data['dependencies'] if 'dependencies' in data else []
        self.dependencies = [dependencies] if type(dependencies) is str else dependencies


class JobList(object):
    def __init__(self, data):
        self.data = data
        if 'jobs' in self.data:
            self.jobs = list(map(lambda entry: Job(entry), self.data['jobs']))
        else:
            self.jobs = []


def _file_format(path):
    _, ext = os.path.splitext(path)
    return ext[1:].lower() if ext.startswith('.') else ext.lower()


def _load_data(file, file_format):
    if file_format == 'json':
        data = json.load(file)
        file.close()
    elif file_format == 'yaml' or file_format == 'yml':
        data = yaml.load(file)
        file.close()
    else:
        raise Exception("Unsupported file type: {}".format(file_format))
    return data


class JobListFile(argparse.Action):
    def __call__(self, parser, namespace, values, option_strings=None):
        path = os.path.abspath(values)
        try:
            file = argparse.FileType('r', encoding='UTF-8')(path)
        except argparse.ArgumentTypeError as ate:
            raise argparse.ArgumentError(self, ate)
        try:
            data = _load_data(file, _file_format(path))
            setattr(namespace, self.dest, JobList(data))
        except Exception as e:
            raise argparse.ArgumentError(self, "Error while loading jobfile: {}".format(e))


def command_line(argv=None):
    parser = argparse.ArgumentParser(prog='prochestra')
    parser.add_argument('jobfile', action=JobListFile,
                        help="A path to a JSON or YAML file with the job list.")
    parser.add_argument('--log', '-l', type=argparse.FileType('a', encoding='UTF-8'),
                        help="A path to a log file to write the output to.")
    parser.add_argument('--silent', '-s', action='store_true',
                        help="Dismiss the output of the executed processes.")
    parser.add_argument('--version', '-v', action='version', version=__version__)
    args = parser.parse_args(args=argv)

    runner = Prochestra(log=args.log, silent=args.silent)
    result = runner.run(args.jobfile)
    return 0 if result else 1
