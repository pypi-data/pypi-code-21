from functools import lru_cache
from collections import defaultdict
from argparse import ArgumentParser
from yaml import load
from shutil import which
from os.path import isfile, isdir
from os import walk
from subprocess import call

@lru_cache(maxsize=None)
def are_fallbacks_skipped():
    """Check once for --config fallback_binaries=false"""
    parser = ArgumentParser()
    parser.add_argument("--config", "-C", nargs="*")
    known_args, _ = parser.parse_known_args()
    if not known_args.config:
        return False
    else:
        config = {
            t.split("=")[0]: t.split("=")[1]
            for t in known_args.config
        }
        if "fallback_binaries" not in config:
            return False
        else:
            return config["fallback_binaries"].lower() in ("false", "no", "0")

def make_slim(rule):
    """Remove redundant keys from rule, return as a None-factory defaultdict"""
    slim_rule = defaultdict(lambda: None, rule)
    for key in "executables", "fallback":
        if key in slim_rule:
            del slim_rule[key]
    return slim_rule

def get_executables(rule_name, rule):
    """For every possible fallback, yield: alias, file match, fallback"""
    if "fallback" in rule:
        yield rule_name, rule_name, rule["fallback"]
        if "alias" in rule:
            yield rule["alias"], rule_name, rule["fallback"]
    elif "executables" in rule:
        for entry in rule["executables"]:
            if "match" in entry and "fallback" in entry:
                yield entry["match"], entry["match"], entry["fallback"]
                if "alias" in entry:
                    yield entry["alias"], entry["match"], entry["fallback"]

def check_bad_names(self):
    """Return a set of tool names/aliases that conflict with class internals"""
    reserved = set(dir(self))
    proposed = set(self._rules.keys())
    return reserved & proposed

def bad_names_error(bad_names):
    """Generate a KeyError with nice formatting"""
    return KeyError("Bad tool names: {}".format(", ".join(bad_names)))

def check_and_pull(repo_path):
    """If the directory is empty and not initialized as a submodule, do it"""
    try:
        _, files, folders = next(walk(repo_path))
    except StopIteration:
        return
    if (not files) and (not folders):
        try:
            git_cmd = ["git", "submodule", "update", "--init", "--recursive"]
            if call(git_cmd + ["--", repo_path]):
                error_message = "{} is not a submodule".format(repo_path)
                raise FileNotFoundError(error_message)
        except FileNotFoundError:
            return

def perform_git_post_action(action, repo_path):
    """Do `action` for the submodule in the `repo_path` directory"""
    error_message = ("Rule asks to perform git action, " +
        "but target is not a submodule: {}".format(repo_path))
    if not repo_path:
        raise OSError(error_message)
    git_footprint = repo_path + "/.git"
    if (not isfile(git_footprint)) and (not isdir(git_footprint)):
        raise OSError(error_message)
    if action == "ignore":
        call(["git", "update-index", "--assume-unchanged", repo_path])
    if action == "reset":
        call("git", "reset", "--hard", "HEAD", cwd=repo_path)
    if action == "clean":
        call("git", "clean", "-fxd", cwd=repo_path)

class Tools:
    """Supply paths to binaries and build on-demand if necessary"""
    _functional = {}
    _rules = {}
 
    def __init__(self, rules, make_jobs=1):
        """Store YAML rules for building on-demand"""
        if isinstance(rules, str):
            loaded_rules = load(rules)
        elif isinstance(rules, dict):
            loaded_rules = rules
        else:
            error_message = "Unsupported type for argument 'rules': {}"
            raise TypeError(error_message.format(type(rules)))
        for rule_name, rule in loaded_rules.items():
            slim_rule = make_slim(rule)
            for name, match, fallback in get_executables(rule_name, rule):
                self._rules[name] = slim_rule.copy()
                self._rules[name]["fallback"] = fallback
                self._rules[name]["match"] = match
        self._make_jobs = make_jobs
        bad_names = check_bad_names(self)
        if bad_names:
            raise bad_names_error(bad_names)
 
    def __getattr__(self, tool):
        """Check in order: match exists, fallback exists, fallback buildable"""
        if tool not in self._rules:
            raise AttributeError("No attribute {}".format(tool))
        if tool not in self._functional:
            match = self._rules[tool]["match"]
            if are_fallbacks_skipped() or which(match):
                self._functional[tool] = match
            else:
                rule = self._rules[tool]
                fallback_path = rule["fallback"]
                if isfile(fallback_path):
                    call(["chmod", "+x", fallback_path])
                else:
                    check_and_pull(rule["repo"] or rule["wd"])
                    make_cmd = ["make -j{}".format(self._make_jobs)]
                    cwd = rule["wd"] or rule["repo"]
                    for cmd in (rule["commands"] or make_cmd):
                        if call(cmd, shell=True, cwd=cwd):
                            raise OSError("Building '{}' failed".format(tool))
                for action in (rule["git_post"] or []):
                    perform_git_post_action(action, rule["repo"] or rule["wd"])
                self._functional[tool] = fallback_path
        return self._functional[tool]
