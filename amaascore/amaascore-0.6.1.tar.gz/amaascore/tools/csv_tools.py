from __future__ import absolute_import, division, print_function, unicode_literals

import csv


def csv_filename_to_objects(filename, json_handler):
    with open(filename, 'r') as f:
        objects = csv_stream_to_objects(f, json_handler=json_handler)
    return objects


def csv_stream_to_objects(stream, json_handler, params=dict()):
    reader = csv.DictReader(stream)
    objects = []
    for row in reader:
        objects.append(json_handler(row, params))
    return objects


def objects_to_csv(objects, filename, clazz=None):
    with open(filename, 'w') as csvfile:
        objects_to_csv_stream(objects=objects, stream=csvfile, clazz=clazz)


def objects_to_csv_stream(objects, stream, clazz=None):
    if not objects:
        return
    object_dicts = []
    for obj in objects:
        obj_dict = obj.to_json()
        if clazz and hasattr(clazz, 'children'):
            # FOR NOW - remove all children
            [obj_dict.pop(child, None) for child in clazz.children().keys()]
        object_dicts.append(obj_dict)
    fieldnames = object_dicts[0].keys()
    writer = csv.DictWriter(stream, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(object_dicts)
