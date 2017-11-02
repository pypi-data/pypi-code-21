#!/usr/bin/env python

import logging
import json
import glob


class ResourceGraphProcessor(object):
    def __init__(self, resources=[], variables={}):
        self.resources = resources
        self.variables = variables

    def add_resources(self, resources):
        self.resources.extend(resources)
        return self

    def add_resource(self, resource):
        self.resources.append(resource)
        return self

    def add_json_files(self, glob_pattern):
        for res_json_file in glob.glob(glob_pattern):
            with open(res_json_file, "r") as infile:
                res_json = json.load(infile)
                self.resources.extend(res_json)
        return self

    def add_python_files(self, glob_pattern):
        import imp
        for res_python_file in glob.glob(glob_pattern):
            try:
                resource_module = imp.load_source('resource_module', res_python_file)
            except Exception:
                logging.exception("error in loading resources python file %s" % res_python_file)
                raise Exception("error in loading resources python file %s" % res_python_file)
            try:
                self.resources.extend(resource_module.RESOURCES)
            except Exception:
                logging.exception("variable RESOURCES not accessible in python resource file %s" % res_python_file)
                raise Exception("variable RESOURCES not accessible in python resource file %s" % res_python_file)
        return self

    def keep_only_supported_resource(self, is_supported):
        self.resources = [r for r in self.resources if is_supported(r)]

    def process(self, processor):
        self.variables = process_resources(self.resources, processor, self.variables)
        return self.variables


def process_resources(resources, processor, res_variables={}):
    res_dep_tree = compute_resource_dep_tree(resources)
    sorted_resources = sort_resources(res_dep_tree)
    process_sorted_resources(sorted_resources, resources, processor, res_variables)
    return res_variables


def process_sorted_resources(sorted_resources, resources, processor, res_variables={}):
    resources_dic = {r["name"]:r for r in resources}
    for resource_name in sorted_resources:
        res = resources_dic[resource_name]
        res_resolved = clone_and_replace_references(res, res_variables)
        try:
            res_variables = processor(res_resolved, res_variables)
        except Exception:
            logging.error("processor error for resource: %s", json.dumps(res_resolved, indent=2))
            logging.error("processor error with variables: %s", json.dumps(res_variables, indent=2))
            raise
    return res_variables


def sort_resources(res_dep_tree):
    sorted_resources = []
    while len(res_dep_tree) > 0:
        free_resources = [res
                          for res, dependencies in res_dep_tree.iteritems()
                          if not [d for d in dependencies if d[0] not in sorted_resources]]
        if not free_resources:
            raise Exception("unresolved or circular references: %s" % str(res_dep_tree))
        sorted_resources.extend(free_resources)
        for free_res in free_resources:
            res_dep_tree.pop(free_res)
    return sorted_resources


def compute_resource_dep_tree(resources):
    res_dep_tree = {}
    for r in resources:
        if r["name"] in res_dep_tree:
            raise Exception("Duplicated resource name: %s" % r["name"])
        res_dep_tree[r["name"]] = find_resource_ref_in_resources(r)
    return res_dep_tree


def find_resource_ref_in_resources(resource):
    if isinstance(resource, dict):
        if resource.keys() == ["$RESOURCE_REF"]:
            ref = resource.values()[0]
            return [ref.split(".")]
        response = []
        for k, v in resource.iteritems():
            response.extend(find_resource_ref_in_resources(v))
        return response
    elif isinstance(resource, list):
        response = []
        for v in resource:
            response.extend(find_resource_ref_in_resources(v))
        return response
    else:
        return []


def clone_and_replace_references(resource, res_variables):
    if isinstance(resource, dict):
        if resource.keys() == ["$RESOURCE_REF"]:
            return get_variable(res_variables, resource.values()[0].split("."))
        else:
            return {k: clone_and_replace_references(v, res_variables) for k,v in resource.iteritems()}
    elif isinstance(resource, list):
        return [clone_and_replace_references(v, res_variables) for v in resource]
    else:
        return resource


def get_variable(res_variables, key_path):
    value = res_variables
    for k in key_path:
        try:
            value = value[k]
        except KeyError:
            logging.error("%s not found in getting %s from variables", k, ".".join(key_path))
            raise Exception("missing variables or invalid keypath %s" % ".".join(key_path))
    return value
