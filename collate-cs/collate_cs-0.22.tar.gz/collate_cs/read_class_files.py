import os
import process_method
import replace_keywords

def _(address, class_name, files):
    methods = {}
    for filename in files:
        if '.cs' not in filename:
            continue
        path = os.sep.join(address) + '/' + class_name + '/' + filename
        with open(path, 'r') as f:
            method = process_method._(f.read())
            methods[filename] = replace_keywords._(method, filename, class_name)
    return methods
