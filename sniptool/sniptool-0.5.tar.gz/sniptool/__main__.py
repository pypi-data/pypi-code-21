#!/usr/bin/env python
##################################################
# Copyright (C) 2017, All rights reserved.
##################################################

from __future__ import print_function
import argparse
import inflection
import jinja2
import jinja2.meta
import os
import pyperclip
import sys

from pyprelude.file_system import make_path
from pysimplevcs.git import Git

from sniptool import __description__, __project_name__, __version__
from sniptool.config import Config

def _public_callable_attrs(cls):
    for f in dir(cls):
        attr = getattr(cls, f)
        if not f.startswith("_") and callable(attr):
            yield attr

def _set_clipboard_text(s):
    pyperclip.copy(s)

def _has_prefix(s, prefix):
    return s[len(prefix) : ] if s.startswith(prefix) else None

def _has_suffix(s, suffix):
    return s[: -len(suffix)] if s.endswith(suffix) else None

def _read_source(path):
    with open(path, "rt") as f:
        return f.read()

def _read_metadata(source):
    metadata = {}
    defaults = {}
    for line in source.splitlines():
        line = _has_prefix(line, "{#")
        if not line: continue
        line = _has_suffix(line, "#}")
        if not line: continue
        line = line.strip(" -")
        line = _has_prefix(line, ".")
        if not line: continue
        index = line.find(":")
        if not index: continue

        key = line[0 : index].strip()
        value = line[index + 1:].strip()

        t = _has_prefix(key, "default(")
        if t is not None:
            default_key = _has_suffix(t, ")").strip()
            if default_key is not None:
                defaults[default_key] = value
                continue

        metadata[key] = value

    return metadata, defaults

def _prompt(env, source, defaults):
    template = env.parse(source)
    values = {}
    for key in sorted(jinja2.meta.find_undeclared_variables(template)):
        default_value = defaults.get(key, None)
        if default_value is None:
            value = raw_input("Enter value for \"{}\": ".format(key))
            values[key] = value
        else:
            value = raw_input("Enter value for \"{}\" (default: \"{}\"): ".format(key, default_value))
            values[key] = default_value if len(value) == 0 else value

    return values

def _show_metadata(path, metadata, defaults, indent=0):
    prefix = "  " * indent
    print("{}Path: {}".format(prefix, path))
    print("{}Name: {}".format(prefix, metadata.get("name", "(unnamed)")))
    print("{}Description: {}".format(prefix, metadata.get("description", "(no description)")))
    if len(defaults) > 0:
        print("{}Defaults:".format(prefix))
        for key, value in defaults.iteritems():
            print("{}  {}={}".format(prefix, key, value))

def _do_update(config, args):
    print(config.template_dir)
    git = Git(config.repo_dir)
    original_commit = git.rev_parse("HEAD").strip()
    git.pull("--rebase")
    new_commit = git.rev_parse("HEAD").strip()

    if original_commit == new_commit:
        print("Repository already at latest revision {}".format(new_commit))
    else:
        print("Repository updated to latest revision {}".format(new_commit))

def _do_gen(config, args):
    env = jinja2.Environment(undefined=jinja2.StrictUndefined)

    env.filters["encode_cpp_literal"] = lambda s: "\"" + s.replace("\\", "\\\\") + "\"" # TODO: Implement full set of C++ literal encoding rules

    for f in _public_callable_attrs(inflection):
        env.filters[f.__name__] = f

    path = make_path(config.template_dir, args.template_name)
    source = _read_source(path)
    metadata, defaults = _read_metadata(source)

    print("Template: {}".format(args.template_name))
    _show_metadata(path, metadata, defaults, 1)
    values = _prompt(env, source, defaults)

    output = env.from_string(source, values).render()
    print("==========")
    print(output)
    print("==========")

    if args.output_path is None:
        _set_clipboard_text(output)
        print("Text sent to clipboard")
    else:
        with open(args.output_path, "wt") as f:
            f.write(output)
        print("Text written to file {}".format(args.output_path))

def _do_list(config, args):
    for p in os.listdir(config.template_dir):
        print("Template: {}".format(p))
        path = make_path(config.template_dir, p)
        source = _read_source(path)
        metadata, defaults = _read_metadata(source)
        _show_metadata(path, metadata, defaults, 1)
        print()

def _main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    config_dir = make_path(os.path.expanduser(os.environ.get("SNIPTOOL_DIR", "~/.sniptool")))
    config = Config(config_dir)

    parser = argparse.ArgumentParser(prog=__project_name__, description=__description__)
    parser.add_argument("--version", action="version", version="{} version {}".format(__project_name__, __version__))

    subparsers = parser.add_subparsers(help="subcommand help")

    update_parser = subparsers.add_parser("update", help="Update local snippet repository")
    update_parser.set_defaults(func=_do_update)

    gen_parser = subparsers.add_parser("gen", help="Generate code snippet")
    gen_parser.set_defaults(func=_do_gen)
    gen_parser.add_argument(
        "template_name",
        help="Template name")
    gen_parser.add_argument(
        "--output-file",
        "-f",
        dest="output_path",
        default=None,
        type=make_path,
        help="Write to specified file instead of clipboard")

    list_parser = subparsers.add_parser("list", help="List available templates")
    list_parser.set_defaults(func=_do_list)

    args = parser.parse_args(argv)
    args.func(config, args)

if __name__ == "__main__":
    _main()
