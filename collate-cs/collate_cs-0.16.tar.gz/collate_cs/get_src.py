import os
import read_class_files as read
import process_class_files as process

def _(path, namespace_depth):
    top = {'namespaces': {}, 'classes': {}}

    for root, dirs, files in os.walk(path):
        if len(files) == 0:
            continue
        address = root.split(os.sep)
        class_name = address.pop()

        parent = top
        for namespace in address:
            if (namespace not in parent['namespaces']):
                parent['namespaces'][namespace] = {
                        'namespaces': {}, 'classes': {}}
            parent = parent['namespaces'][namespace]

        methods = read._(address, class_name, files)
        methods = process._(methods, address[namespace_depth:], class_name)
        parent['classes'][class_name] = methods
    return top
