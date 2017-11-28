import os
import json

IGNOREFILES = [
    ".DS_Store",
    ".gitignore",
    ".git"
]

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