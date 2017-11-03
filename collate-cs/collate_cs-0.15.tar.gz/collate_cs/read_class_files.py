import os
import process_method

def _(address, class_name, files):
    methods = {}
    for filename in files:
        if '.cs' not in filename:
            continue
        path = os.sep.join(address) + '/' + class_name + '/' + filename
        with open(path, 'r') as f:
            methods[filename] = process_method._(f.read())
    return methods
