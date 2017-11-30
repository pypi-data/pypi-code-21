import os
import json
import sys

IGNOREFILES = [
    ".DS_Store",
    ".gitignore",
    ".git",
    "__init__.pyc",
    "__init__.py",
]

def convert_to_unicode(input):
    """convert strings into unicode"""
    if isinstance(input, dict):
        try:
            return {convert_to_unicode(key): convert_to_unicode(value) for key, value in iterate_items(input)}
        except AttributeError:
            return {convert_to_unicode(key): convert_to_unicode(value) for key, value in iterate_items(input)}
    elif isinstance(input, list):
        return [convert_to_unicode(element) for element in input]
    elif isinstance(input, str) or isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input

def iterate_items(to_iterate):
    # iterate command, compatible for python 2 and 3 
    if (sys.version_info > (3, 0)):
        # Python 3 code in this block
        return to_iterate.items()
    else:
        # Python 2 code in this block
        return to_iterate.iteritems()

def get_files_in_dir_no_subdirs(directory):
    report = os.path.realpath(directory)
    files=list()
    for file_ in os.listdir(directory):
        if file_ in IGNOREFILES or file_.startswith('.'):
            continue
        files.append(directory + '/' + file_)
    return files

def get_files_in_dir_with_subdirs(path):
    files = []
    for root, dirnames, filenames in os.walk(path):
        for filename in filenames:
            files.append(os.path.join(root, filename))
    return files

def save_to_jsonfile(file_path, file_content):
    with open(file_path, 'w') as output_file:
            dump = json.dumps(file_content, indent=4)
            output_file.write(dump)
            output_file.close()

def get_root_path(path):
    _ROOT = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(_ROOT, path)

def ignore_files(files):
    cleaned_files = [file for file in files if file.split("/")[-1] not in IGNOREFILES]
    return cleaned_files