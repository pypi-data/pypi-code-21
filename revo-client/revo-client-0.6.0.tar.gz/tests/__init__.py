import os
import json


def load_json(path):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, path)
    with open(file_path, "r") as fp:
        return json.load(fp)


def load_content(path):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, path)
    with open(file_path, "rb") as fp:
        return fp.read()
