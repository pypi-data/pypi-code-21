#!/usr/bin/env python
from sys import argv
from argparse import ArgumentParser
from collections import OrderedDict
from shutil import which
from subprocess import check_output, PIPE
from yaml import load, dump

arg_rules = OrderedDict([
    (("-f", "--freeze-conda"), {
        "help": "Write Conda and Pip configs separately",
        "action": "store_true"
    })
])

def get_args(arg_rules=arg_rules):
    parser = ArgumentParser()
    for rule_unnamed, rule_named in arg_rules.items():
        parser.add_argument(*rule_unnamed, **rule_named)
    if len(argv) == 1:
        exit(parser.print_help() or 1)
    else:
        return parser.parse_args()

def get_current_environment():
    if which("conda"):
        cmd = ["conda", "info", "--envs"]
        raw_info = check_output(cmd, universal_newlines=True)
        for line in raw_info.strip("\n").split("\n"):
            fields = line.split()
            if (len(fields) > 2) and (fields[1] == "*"):
                return fields[0], fields[2]
    return None, None

def get_conda_config(env_prefix):
    cmd = ["conda", "env", "export"]
    conda_yaml = check_output(cmd, universal_newlines=True, stderr=PIPE)
    conda_config = load(conda_yaml)
    if "prefix" in conda_config:
        del conda_config["prefix"]
    for i, dependency in enumerate(conda_config["dependencies"]):
        if isinstance(dependency, dict):
            if "pip" in dependency:
                del dependency["pip"]
            if not dependency:
                del conda_config["dependencies"][i]
            break
    return conda_config

def get_pip_config(env_prefix):
    pip_location = env_prefix + "/bin/pip"
    if which(pip_location):
        cmd = [pip_location, "freeze"]
        return check_output(cmd, stderr=PIPE, universal_newlines=True)
    else:
        return ""

def freeze_conda(env_file="environment.yml", req_file="requirements.txt"):
    env_name, env_prefix = get_current_environment()
    if env_name and (env_name != "root"):
        with open(env_file, "w") as environment_file:
            conda_config = get_conda_config(env_prefix)
            dump(conda_config, environment_file, default_flow_style=False)
        with open(req_file, "w") as requirements_file:
            freeze = get_pip_config(env_prefix)
            requirements_file.write(freeze)
    else:
        raise OSError("Not inside a Conda environment")

def main():
    args = get_args()
    if args.freeze_conda:
        freeze_conda()
    return 0

exit(main())
