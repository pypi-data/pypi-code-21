#!/usr/bin/env python
import subprocess
import json
import glob
from collections import OrderedDict
import re
import sys
import inspect
import importlib
import argparse


def warn(msg, *args, **kwargs):
    print("[WARN]", msg.format(*args, **kwargs))


def normalized_type(schema):
    type_ = schema.get("type", [])
    if isinstance(type_, list):
        return type_
    return [type_]


def guess_indentation(f):
    f.readline()
    second_line = f.readline()
    f.seek(0)
    match = re.match(" +", second_line)
    if match:
        return len(match.group(0))
    return 2


def walk_subschemas(schema, path=[]):
    yield schema, path
    if "properties" in schema:
        for k, v in schema["properties"].items():
            yield from walk_subschemas(v, path + [k])
    if "items" in schema:
        yield from walk_subschemas(schema["items"], path + ["items"])


def walk_missing_additional_properties(schema):
    for subschema, path in walk_subschemas(schema):
        is_missing = ("type" in subschema
                      and "object" in normalized_type(subschema)
                      and "additionalProperties" not in subschema)
        if is_missing:
            yield subschema, path


def additional_properties_check(args, schemas):
    for tap_stream_id, schema in schemas:
        for subschema, path in walk_missing_additional_properties(schema):
            warn('"additionalProperties" not found: {} {}', tap_stream_id, path)


def empty_schemas_check(args, schemas):
    for tap_stream_id, schema in schemas:
        for subschema, path in walk_subschemas(schema):
            if subschema == {}:
                warn("empty schema found: {} {}", tap_stream_id, path)


def no_typing_check(args, schemas):
    for tap_stream_id, schema in schemas:
        for subschema, path in walk_subschemas(schema):
            if "type" in subschema and normalized_type(subschema) in [[], ["null"]]:
                warn("empty 'type' found: {} {}", tap_stream_id, path)


def check_for_critical_log(mod):
    source = inspect.getsource(mod.main)
    if "critical" not in source:
        warn("no critical log found in main function")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tap", required=True)
    parser.add_argument("--config", "-c", required=True)
    return parser.parse_args()


def read_schemas(args):
    out = subprocess.check_output([args.tap, "-c", args.config, "-d"])
    disc = json.loads(out.decode("utf-8"))
    return [(s["tap_stream_id"], s["schema"]) for s in disc["streams"]]


def main():
    args = parse_args()
    mod = importlib.import_module(args.tap.replace("-", "_"))
    schemas = read_schemas(args)
    additional_properties_check(args, schemas)
    empty_schemas_check(args, schemas)
    no_typing_check(args, schemas)
    check_for_critical_log(mod)


if __name__ == "__main__":
    main()
