# -*- coding: utf-8 -*-

import ast
import os
import click
from tqdm import tqdm

def attr(value):
    if 'attr' in value._fields:
        return value.attr
    else:
        return node_value(value)


def node_value(value):
    if type(value) == ast.Str:
        return value.s
    elif type(value) == ast.Num:
        return str(value.n)
    elif type(value) == ast.Name:
        return value.id
    elif type(value) == ast.List:
        return '|'.join([node_value(x) for x in value.elts])
    elif type(value) == ast.Tuple:
        return ','.join([node_value(x) for x in value.elts])
    elif type(value) == ast.Attribute:
        if 'value' in value._fields:
            return node_value(value.value)
        return value.attr
    else:
        return ''


class AstFile(object):
    data = {}

    def __init__(self, paths):
        paths = tqdm(paths)
        for path in paths:
            file_content = open(path).read()
            try:
                obj = ast.parse(file_content)
            except:
                click.secho('Can not process : %s' % path, fg='red')
                continue
            self.data[path] = []
            for item in ast.iter_child_nodes(obj):
                if type(item) == ast.ClassDef:
                    class_name = item.name
                    class_base = ','.join([node_value(x) for x in item.bases])
                    if not class_base:
                        continue
                    object_name = False
                    fields = {}
                    funcs = {}
                    inherits = []
                    onchange_fields = []
                    for child in ast.iter_child_nodes(item):
                        if type(child) == ast.FunctionDef:
                            funcs[child.name] = [node_value(x) for x in child.args.args]
                        if type(child) == ast.FunctionDef and 'decorator_list' in child._fields:
                            for decorator in child.decorator_list:
                                if type(decorator) == ast.Call:
                                    if 'args' in decorator._fields and 'func' in decorator._fields:
                                        if attr(decorator.func) == 'onchange':
                                            for arg in decorator.args:
                                                field = node_value(arg)
                                                if field and field not in onchange_fields:
                                                    onchange_fields.append(field)
                        if type(child) == ast.Assign:
                            attributes = [node_value(x) for x in child.targets if node_value(x)]
                            if type(child.value) == ast.Str and '_name' in attributes:
                                object_name = child.value.s
                            elif type(child.value) == ast.List and 'elts' in child.value._fields:
                                for elt in child.value.elts:
                                    if type(elt) == ast.Str:
                                        inherits.append(elt.s)
                            elif type(child.value) == ast.Str and '_inherit' in attributes:
                                object_name = child.value.s
                                inherits = [object_name]
                            elif type(child.value) == ast.Call:
                                if 'value' in child.value.func._fields and type(child.value.func.value) == ast.Name:
                                    if child.value.func.value.id == 'fields':
                                        for field in attributes:
                                            fields.setdefault(field, {'type': child.value.func.attr})
                                            for keyword in child.value.keywords:
                                                if type(keyword) == ast.keyword:
                                                    fields[field].update({
                                                        keyword.arg: node_value(keyword.value),
                                                    })
                                            i = 0
                                            for arg in child.value.args:
                                                fields[field].update({
                                                    'without_%s' % i: node_value(arg),
                                                })
                                                i += 1
                            elif type(child.value) == ast.Dict and '_columns' in attributes:
                                for k, v in zip(child.value.keys, child.value.values):
                                    field = node_value(k)
                                    if type(v) == ast.Call:
                                        if 'value' in v.func._fields:
                                            if node_value(v.func.value) == 'fields':
                                                fields.setdefault(field, {'type': v.func.attr})
                                                for keyword in v.keywords:
                                                    if type(keyword) == ast.keyword:
                                                        fields[field].update({
                                                            keyword.arg: node_value(keyword.value),
                                                        })
                                                i = 0
                                                for arg in v.args:
                                                    fields[field].update({
                                                        'without_%s' % i: node_value(arg),
                                                    })
                                                    i += 1
                    for f_key, v_key in fields.iteritems():
                        if f_key in onchange_fields:
                            fields[f_key].update({
                                'onchange': 'True',
                            })
                    if object_name:
                        self.data[path].append((class_name, class_base, object_name, inherits, fields, funcs))

    def get_models(self, model_args=[], field_args=[], func_args=[]):
        data = self.get_processed(model_args, field_args, func_args)
        root = []
        for model, model_data in data.iteritems():
            if field_args:
                for key in model_data.get('fields', {}).keys():
                    if key not in field_args:
                        del model_data['fields'][key]
            if func_args:
                for key in model_data.get('funcs', {}).keys():
                    if key not in func_args:
                        del model_data['funcs'][key]
            root.append((model, model_data))
        return root

    def get_processed(self, model_args=[], field_args=[], func_args=[]):
        root = dict()
        for path, data in self.data.iteritems():
            for item in data:
                model_classes = item[0]
                model_base_classes = item[1]
                model_name = item[2]
                model_inherits = item[3]
                model_fields = item[4]
                model_funcs = item[5]
                if model_args:
                    if model_name not in model_args:
                        continue
                if field_args:
                    if not set(field_args) & set(model_fields):
                        continue
                if func_args:
                    if not (set(func_args) & set(model_funcs)):
                        continue
                if model_name not in root:
                    root[model_name] = {
                        'funcs': model_funcs,
                        'fields': model_fields,
                        'inherits': model_inherits,
                        'paths': [path],
                        'base_classes': [model_base_classes],
                        'classes': [model_classes],
                    }
                else:
                    data_fields = root[model_name].get('fields', {})
                    data_fields.update(model_fields)
                    data_funcs = root[model_name].get('funcs', {})
                    data_funcs.update(model_funcs)
                    data_inherits = root[model_name].get('inherits', [])
                    for model_inherit in model_inherits:
                        if model_inherit not in data_inherits:
                            data_inherits.append(model_inherit)
                    data_paths = root[model_name].get('paths', [])
                    if path not in data_paths:
                        data_paths.append(path)
                    data_base_classes = root[model_name].get('base_classes', [])
                    if model_base_classes not in data_base_classes:
                        data_base_classes.append(model_base_classes)
                    data_classes = root[model_name].get('classes', [])
                    if model_classes not in data_classes:
                        data_classes.append(model_classes)
                    root[model_name] = {
                        'funcs': data_funcs,
                        'fields': data_fields,
                        'inherits': data_inherits,
                        'paths': data_paths,
                        'base_classes': data_base_classes,
                        'classes': data_classes,
                    }
        return root


class AstDir(object):
    def __init__(self, path):
        self.py_files = []
        self.xml_files = []
        for root, dirs, files in os.walk(path):
            for name in files:
                file = os.path.join(root, name)
                if file.lower().endswith('.py'):
                    self.py_files.append(file)
                if file.lower().endswith('.xml'):
                    self.xml_files.append(file)

    def get_py_files(self):
        return self.py_files

    def get_xml_files(self):
        return self.xml_files
