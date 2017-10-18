from __future__ import (absolute_import, division, print_function)

import copy
import fnmatch
import json
import pprint
import os
import re
import shutil
from pydoc import locate

import click
from ansible.plugins.filter.core import FilterModule
from frkl.frkl import Frkl, PLACEHOLDER, UrlAbbrevProcessor, dict_merge
from jinja2 import Environment
from jinja2.ext import Extension
from nsbl import nsbl, tasks as nsbl_tasks
from six import string_types

from .config import FrecklesConfig

try:
    set
except NameError:
    from sets import Set as set

import yaml
from .freckles_defaults import *


def to_freckle_desc_filter(url, target, target_is_parent, profiles, include, exclude):
    return create_freckle_desc(url, target, target_is_parent, profiles, include, exclude)


class FrecklesUtilsExtension(Extension):
    def __init__(self, environment):
        super(Extension, self).__init__()
        fm = FilterModule()
        filters = fm.filters()
        filters["to_freckle_desc"] = to_freckle_desc_filter
        environment.filters.update(filters)


freckles_jinja_utils = FrecklesUtilsExtension

DEFAULT_FRECKLES_CONFIG = FrecklesConfig()


class VarsType(click.ParamType):
    name = 'vars_type'

    def convert(self, value, param, ctx):

        if os.path.exists(value):
            if not os.path.isfile(value):
                self.fail("Can't open file to read vars: {}".format(value))

            with open(value, 'r') as f:
                file_vars = yaml.safe_load(f)
                if not file_vars:
                    file_vars = {}

                return file_vars

        else:
            try:
                string_vars = json.loads(value)
                if not string_vars:
                    string_vars = {}
                return string_vars
            except (ValueError) as e:
                self.fail("Can't read vars: {}".format(value))


class RepoType(click.ParamType):
    name = 'repo'

    def convert(self, value, param, ctx):

        try:

            print_repos_expand(value, warn=True)
            result = nsbl_tasks.expand_string_to_git_repo(value, DEFAULT_ABBREVIATIONS)

            return result
        except:
            self.fail('%s is not a valid repo url' % value, param, ctx)


class FreckleUrlType(click.ParamType):
    name = 'repo'

    def convert(self, value, param, ctx):

        if not isinstance(value, string_types):
            raise Exception("freckle url needs to a string: {}".format(value))
        try:
            frkl_obj = Frkl(value, [
                UrlAbbrevProcessor(init_params={"abbrevs": DEFAULT_ABBREVIATIONS, "add_default_abbrevs": False, "verbose": True})])
            result = frkl_obj.process()
            return result[0]
        except:
            self.fail('%s is not a valid repo url' % value, param, ctx)


FRECKLES_REPO = RepoType()
FRECKLES_URL = FreckleUrlType()

DEFAULT_ABBREVIATIONS = {
    'gh':
        ["https://github.com/", PLACEHOLDER, "/", PLACEHOLDER, ".git"],
    'bb': ["https://bitbucket.org/", PLACEHOLDER, "/", PLACEHOLDER, ".git"]
}


def url_is_local(url):
    if url.startswith("~") or url.startswith(os.sep):
        return True
    return os.path.exists(os.path.expanduser(url))


def create_freckle_desc(freckle_url, target, target_is_parent=True, profiles=[], includes=[], excludes=[]):
    freckle_repo = {}

    if isinstance(profiles, string_types):
        profiles = [profiles]
    if isinstance(includes, string_types):
        includes = [includes]
    if isinstance(excludes, string_types):
        excludes = [excludes]

    if not freckle_url:
        if not target:
            raise Exception("Need either url or target for freckle")
        freckle_url = target
        is_local = True
    else:
        is_local = url_is_local(freckle_url)

    if is_local:
        freckle_repo["path"] = os.path.abspath(os.path.expanduser(freckle_url))
        freckle_repo["url"] = None
    else:
        repo = nsbl.ensure_git_repo_format(freckle_url, target, target_is_parent)
        freckle_repo["path"] = repo["dest"]
        freckle_repo["url"] = repo["repo"]

    freckle_repo["profiles"] = profiles
    freckle_repo["include"] = includes
    freckle_repo["exclude"] = excludes

    return freckle_repo


def replace_string(template_string, replacement_dict):
    result = Environment(extensions=[freckles_jinja_utils]).from_string(template_string).render(replacement_dict)
    return result


def render_dict(obj, replacement_dict):
    # print("OBJ")
    # pprint.pprint(obj)
    # print("REPLACEMNT")
    # pprint.pprint(replacement_dict)
    # print("")
    # print("")
    if isinstance(obj, dict):
        # dictionary
        ret = {}
        for k, v in obj.iteritems():
            ret[render_dict(k, replacement_dict)] = render_dict(v, replacement_dict)
        return ret
    elif isinstance(obj, string_types):
        # string
        return replace_string(obj, replacement_dict)
    elif isinstance(obj, (list, tuple)):
        # list (or the like)
        ret = []
        for item in obj:
            ret.append(render_dict(item, replacement_dict))
        return ret
    else:
        # anything else
        return obj


def render_vars_template(vars_template, replacement_dict):
    result = Environment(extensions=[freckles_jinja_utils]).from_string(vars_template).render(replacement_dict)
    return result


def find_supported_profiles(config=None):
    if not config:
        config = DEFAULT_FRECKLES_CONFIG

    trusted_repos = config.trusted_repos
    repos = nsbl_tasks.get_local_repos(trusted_repos, "adapters", DEFAULT_LOCAL_REPO_PATH_BASE, DEFAULT_REPOS, DEFAULT_ABBREVIATIONS)

    result = {}
    for r in repos:
        p = get_adapters_from_repo(r)
        result.update(p)

    return result


def print_task_list_details(task_config, task_metadata={}, output_format="default", ask_become_pass="auto",
                            run_parameters={}):
    click.echo("")
    click.echo("frecklecutable: {}".format(task_metadata.get("command_name", "n/a")))
    click.echo("path: {}".format(task_metadata.get("command_path", "n/a")))
    click.echo("generated ansible environment: {}".format(run_parameters.get("env_dir", "n/a")))
    click.echo("config:")
    click.echo(pprint.pformat(task_config))
    click.echo("")


def create_cli_command(config, command_name=None, command_path=None, extra_options={}):
    doc = config.get("doc", {})
    # TODO: check format of config
    options = config.get("args", {})
    vars = config.get("vars", {})
    tasks = config.get("tasks", None)
    default_vars = config.get("defaults", {})

    key_map = {}
    argument_key = None

    options_list = []
    args_that_are_vars = []
    value_vars = []  # vars where we add all values seperately to the 'vars' instead of as a single value

    options_all = copy.deepcopy(extra_options)
    options_all.update(options)

    for opt, opt_details in options_all.items():

        opt_type = opt_details.get("type", None)
        if isinstance(opt_type, string_types):
            opt_type_converted = locate(opt_type)
            if not opt_type_converted:
                raise Exception("No type found for: {}".format(opt_type))
            if issubclass(opt_type_converted, click.ParamType):
                opt_details['type'] = opt_type_converted()
            else:
                opt_details['type'] = opt_type_converted

        key = opt_details.pop('arg_name', opt)
        extra_arg_names = opt_details.pop('extra_arg_names', [])
        if isinstance(extra_arg_names, string_types):
            extra_arg_names = [extra_arg_names]
        key_map[key] = opt

        is_var = opt_details.pop('is_var', True)
        if is_var:
            args_that_are_vars.append(key)

        use_value = opt_details.pop('use_value', False)
        if use_value:
            value_vars.append(key)

        # cli arguments
        is_argument = opt_details.pop('is_argument', False)
        if is_argument:
            if argument_key:
                raise Exception("Multiple arguments are not supported (yet): {}".format(config["vars"]))
            argument_key = key
            required = opt_details.pop("required", None)

            o = click.Argument(param_decls=[key], required=required, **opt_details)
        else:

            arg_names_for_option = ["--{}".format(key)] + extra_arg_names
            o = click.Option(param_decls=arg_names_for_option, **opt_details)
        options_list.append(o)

    return {"options": options_list, "key_map": key_map, "command_path": command_path, "tasks": tasks, "vars": vars,
            "default_vars": default_vars, "doc": doc, "args_that_are_vars": args_that_are_vars,
            "value_vars": value_vars,
            "metadata": {"extra_options": extra_options, "command_path": command_path, "command_name": command_name,
                         "config": config}}


def get_vars_from_cli_input(input_args, key_map, task_vars, default_vars, args_that_are_vars, value_vars):
    # exchange arg_name with var name
    new_args = {}


    for key, value in key_map.items():
        temp = input_args.pop(key.replace('-', '_'))
        if key not in args_that_are_vars:
            if isinstance(temp, tuple):
                temp = list(temp)
            new_args[value] = temp
        else:
            task_vars[value] = temp

        # replace all matching strings in value_vars
        for i, var_name in enumerate(value_vars):
            if var_name == key:
                value_vars[i] = value

    # now overimpose the new_args over template_vars
    new_args = dict_merge(default_vars, new_args)

    final_vars = {}

    for key, template in task_vars.items():
        if isinstance(template, string_types) and "{" in template:
            template_var_string = render_vars_template(template, new_args)
            try:
                template_var_new = yaml.safe_load(template_var_string)
                final_vars[key] = template_var_new
            except (Exception) as e:
                raise Exception("Could not convert template '{}': {}".format(template_var_string, e.message))
        else:
            final_vars[key] = template

    new_vars = {}

    for key in value_vars:

        values = final_vars.pop(key, {})

        if values and not isinstance(values, dict):
            raise Exception("value for '{}' not a dict: {}".format(key, values))
        if values:
            dict_merge(new_vars, values, copy_dct=False)

    dict_merge(new_vars, final_vars, copy_dct=False)

    return new_args, new_vars




def download_extra_repos(ctx, param, value):

    output = ctx.find_root().params.get("output", "default")

    if not value:
        return
    repos = list(value)

    print_repos_expand(repos, repo_source="using extra repo(s)", warn=True)

    click.echo("\n# processing extra repos...")

    task_config = [{'tasks':
                    [
                        # {'install-pkg-mgrs': {   #
                        # 'pkg_mgr': 'auto',
                        # 'pkg_mgrs': ['homebrew']}},
                      {'makkus.freckles-config': {
                          'freckles_extra_repos': repos,
                          'freckles_config_update_repos': True
                      }
                     }]
    }]


    create_and_run_nsbl_runner(task_config, task_metadata={}, output_format=output, ask_become_pass=False)

    if hasattr(ctx.find_root().command, "config"):
        ctx.find_root().command.config.add_repos(repos)
    elif hasattr(ctx.find_root(), "obj"):
        ctx.find_root().obj["config"].add_repos(repos)

def execute_run_box_basics(output="default"):

    if os.path.exists(DEFAULT_LOCAL_FRECKLES_BOX_BASICS_MARKER):
        return {"return_code": -1}

    task_config = [{'tasks':
                    ['makkus.box-basics']
    }]

    result = create_and_run_nsbl_runner(task_config, task_metadata={}, output_format=output, ask_become_pass=True, run_box_basics=False)

    if result["return_code"] == 0:
        with open(DEFAULT_LOCAL_FRECKLES_BOX_BASICS_MARKER, 'a'):
            os.utime(DEFAULT_LOCAL_FRECKLES_BOX_BASICS_MARKER, None)


    return result


def print_repos_expand(repos, repo_source=None, verbose=True, warn=False):

    expanded = expanded_repos_dict(repos)

    exp = False

    if not expanded:
        return

    click.echo("")

    if repo_source:
        click.echo("# {}:".format(repo_source))
    else:
        click.echo("# using repo(s):")

    click.echo("")

    for r, value in expanded.items():
        click.echo(" - {}".format(r))
        for v in value:

            if v["url"]:
                if r != v["url"]:
                    exp = True
                    click.echo("     -> remote: '{}'".format(v["url"]))
            if v["path"]:
                if r != v["path"]:
                    exp = True
                    click.echo("     -> local: '{}'".format(v["path"]))

    if warn and exp:
        click.echo(" * NOTE: don't rely on abbreviated urls for anything important as that feature might change in a future release, use full urls if in doubt\n")

def expanded_repos_dict(repos):

    if isinstance(repos, string_types):
        repos = [repos]

    result = {}
    for p in repos:
        expanded = expand_repos(p)
        if p not in DEFAULT_REPOS.keys() and p != expanded[0]:
            result[p] = expanded

    return result

def expand_repos(repos):
    """Expands a list of stings to a list of tuples (repo_url, repo_path).
    """

    if isinstance(repos, string_types):
        repos = [repos]

    result = []
    for repo in repos:
        fields = ["url", "path"]
        r = nsbl_tasks.get_default_repo(repo, DEFAULT_REPOS)

        if not r:

            if os.path.exists(repo):
                temp = {"url": None, "path": repo}
            else:
                repo_url = nsbl_tasks.expand_string_to_git_repo(repo, DEFAULT_ABBREVIATIONS)
                relative_repo_path = nsbl_tasks.calculate_local_repo_path(repo_url)
                repo_path = os.path.join(DEFAULT_LOCAL_REPO_PATH_BASE, relative_repo_path)
                temp = {"url": repo_url, "path": repo_path}
            result.append(temp)
        else:
            role_tuples = r.get("roles", [])

            if role_tuples:
                temp = [dict(zip(fields, t)) for t in role_tuples]
                result.extend(temp)

            adapter_tuples = r.get("adapters", [])
            if adapter_tuples:
                temp = [dict(zip(fields, t)) for t in adapter_tuples]
                result.extend(temp)
            frecklecutable_tuples = r.get("frecklecutables", [])
            if frecklecutable_tuples:
                temp = [dict(zip(fields, t)) for t in frecklecutable_tuples]
                result.extend(temp)

    return result


def find_supported_profile_names(config=None):
    return sorted(list(set(find_supported_profiles(config).keys())))


ADAPTER_CACHE = {}


def get_adapters_from_repo(adapter_repo):
    if not os.path.exists(adapter_repo) or not os.path.isdir(os.path.realpath(adapter_repo)):
        return {}

    if adapter_repo in ADAPTER_CACHE.keys():
        return ADAPTER_CACHE[adapter_repo]

    result = {}
    for root, dirnames, filenames in os.walk(os.path.realpath(adapter_repo), topdown=True, followlinks=True):

        dirnames[:] = [d for d in dirnames if d not in DEFAULT_EXCLUDE_DIRS]

        for filename in fnmatch.filter(filenames, "*.{}".format(ADAPTER_MARKER_EXTENSION)):
            adapter_metadata_file = os.path.realpath(os.path.join(root, filename))
            adapter_folder = os.path.abspath(os.path.dirname(adapter_metadata_file))

            profile_name = ".".join(os.path.basename(adapter_metadata_file).split(".")[0:-1])

            result[profile_name] = adapter_folder

    ADAPTER_CACHE[adapter_repo] = result
    return result


def find_adapter_files(extension, valid_profiles=None, config=None):
    profiles = find_supported_profiles(config)

    task_files_to_copy = {}

    for profile_name, profile_path in profiles.items():

        if valid_profiles and profile_name not in valid_profiles:
            continue

        profile_child_file = os.path.join(profile_path, "{}.{}".format(profile_name, extension))

        if not os.path.exists(profile_child_file) or not os.path.isfile(profile_child_file):
            continue

        task_files_to_copy[profile_name] = profile_child_file

    return task_files_to_copy


def get_all_adapters_in_repos(repos):
    result = []
    repos = nsbl_tasks.get_local_repos(repos, "adapters", DEFAULT_LOCAL_REPO_PATH_BASE, DEFAULT_REPOS, DEFAULT_ABBREVIATIONS)
    for repo in repos:
        adapters = get_adapters_from_repo(repo)
        result.extend(adapters)

    return result


def find_adapter_files_callback(extensions, valid_profiles=None):
    if isinstance(extensions, string_types):
        extensions = [extensions]

    task_files_to_copy = {}
    for extension in extensions:
        files = find_adapter_files(extension, valid_profiles)
        for key, value in files.items():
            task_files_to_copy.setdefault(extension, {})[key] = value

    def copy_callback(ansible_environment_root):

        for name, path in task_files_to_copy.get(ADAPTER_INIT_EXTENSION, {}).items():
            target_path = os.path.join(ansible_environment_root, "roles", "internal", "makkus.freckles", "tasks",
                                       "init-{}.yml".format(name))
            shutil.copyfile(path, target_path)

        for name, path in task_files_to_copy.get(ADAPTER_TASKS_EXTENSION, {}).items():
            target_path = os.path.join(ansible_environment_root, "roles", "internal", "makkus.freckles", "tasks",
                                       "items-{}.yml".format(name))
            shutil.copyfile(path, target_path)

    return copy_callback


def get_adapter_dependency_roles(profiles):
    dep_files = find_adapter_files(ADAPTER_MARKER_EXTENSION, profiles)

    all_deps = set()
    for profile_name, dep_file in dep_files.items():

        with open(dep_file, 'r') as f:
            deps = yaml.safe_load(f)
            if not deps:
                deps = {}
            all_deps |= set(deps.get("role-dependencies", {}))

    return list(all_deps)


def extract_all_used_profiles(freckle_repos):
    all_profiles = []
    for fr in freckle_repos:
        all_profiles.extend(fr.get("profiles", []))

    return list(set(all_profiles))


def create_freckles_run(freckle_repos, extra_profile_vars, ask_become_pass="true", no_run=False,
                        output_format="default"):
    profiles = extract_all_used_profiles(freckle_repos)
    callback = find_adapter_files_callback([ADAPTER_INIT_EXTENSION, ADAPTER_TASKS_EXTENSION], profiles)

    additional_roles = get_adapter_dependency_roles(profiles)

    task_config = [{"vars": {"freckles": freckle_repos, "user_vars": extra_profile_vars}, "tasks": ["freckles"]}]

    return create_and_run_nsbl_runner(task_config, output_format=output_format, ask_become_pass=ask_become_pass,
                                      pre_run_callback=callback, no_run=no_run, additional_roles=additional_roles, run_box_basics=True)


def create_and_run_nsbl_runner(task_config, task_metadata={}, output_format="default", ask_become_pass="true",
                               pre_run_callback=None, no_run=False, additional_roles=[], config=None, run_box_basics=False):

    if run_box_basics:
        result = execute_run_box_basics(output_format)

        if result["return_code"] > 0:
            return result

    if not config:
        config = DEFAULT_FRECKLES_CONFIG

    config_trusted_repos = config.trusted_repos
    local_role_repos = nsbl_tasks.get_local_repos(config_trusted_repos, "roles", DEFAULT_LOCAL_REPO_PATH_BASE, DEFAULT_REPOS, DEFAULT_ABBREVIATIONS)

    role_repos = defaults.calculate_role_repos(local_role_repos, use_default_roles=False)

    task_descs = config.task_descs

    nsbl_obj = nsbl.Nsbl.create(task_config, role_repos, task_descs, wrap_into_localhost_env=True, pre_chain=[],
                                additional_roles=additional_roles)

    runner = nsbl.NsblRunner(nsbl_obj)
    run_target = os.path.expanduser(DEFAULT_RUN_LOCATION)
    ansible_verbose = ""
    stdout_callback = "nsbl_internal"
    ignore_task_strings = []
    display_sub_tasks = True
    display_skipped_tasks = False

    if output_format == "verbose":
        stdout_callback = "default"
        ansible_verbose = "-vvvv"
    elif output_format == "ansible":
        stdout_callback = "default"
    elif output_format == "skippy":
        stdout_callback = "skippy"
    elif output_format == "default_full":
        stdout_callback = "nsbl_internal"
        display_skipped_tasks = True
    elif output_format == "default":
        ignore_task_strings = DEFAULT_IGNORE_STRINGS
        stdout_callback = "nsbl_internal"
    else:
        raise Exception("Invalid output format: {}".format(output_format))

    force = True

    return runner.run(run_target, force=force, ansible_verbose=ansible_verbose, ask_become_pass=ask_become_pass,
                      extra_plugins=EXTRA_FRECKLES_PLUGINS, callback=stdout_callback, add_timestamp_to_env=True,
                      add_symlink_to_env=DEFAULT_RUN_SYMLINK_LOCATION, no_run=no_run,
                      display_sub_tasks=display_sub_tasks, display_skipped_tasks=display_skipped_tasks,
                      display_ignore_tasks=ignore_task_strings, pre_run_callback=pre_run_callback)
