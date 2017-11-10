import subprocess
import os, sys
import json
from textwrap import dedent
from helpers.compose import paint
from helpers.ui import string_input, options_input

# JSON functions duplicated here to avoid circular imports with file_manager
def json_read(path):
    with open(path, 'r') as file:
        return json.load(file)

def json_write(path, content):
    with open(path, 'w') as file:
        json.dump(content, file, indent = 4)

checked = []
current_path = os.getcwd()


def find_config_path():
    def check():
        # reactjo.json exists?
        cfg_path = os.path.join(current_path, 'reactjorc/config.json')
        config_file = os.path.isfile(cfg_path)
        checked.append(os.getcwd())
        return found() if config_file else bubble_up()

    def bubble_up():
        parent_path = os.path.dirname(current_path)
        # Escape the recursion if already at highest level.
        if current_path == parent_path:
            raise Exception()
        else:
            current_path = parent_path
            check()

    def found():
        checked = []
        return os.path.join(current_path, 'reactjorc/config.json')

    return check()

def get_cfg():
    try:
        return json_read(find_config_path())
    except:
        print(dedent("""
            Sorry, couldn't find the config.json file. cd to that directory,
            or a child directory. If there really is no config.json, you
            probably need to create a project. Try running:
                        ----------------------
                            reactjo rc
                        ----------------------
            Paths checked for a reactjorc/config.json:
        """))
        for path in checked:
            print(path)

def set_cfg(content):
    json_write(find_config_path(), content)

def build_cfg():
    LATEST_VERSION = '2.4.0'
    project_name = ""
    while project_name == "":
        project_name = string_input("Please name your project: ")

    py_cmd = ""
    while py_cmd == "":
        py_cmd = options_input(
            "What command do you use for python 3.6: ",
            ['python', 'python3', 'unsure'],
            'python'
        )

        if py_cmd == 'unsure':
            print(paint(''))
            print(paint('Type these commands to find out, and then run `reactjo rc` again:'))
            print(paint('python --version'))
            print(paint('python3 --version'))
            print(paint(''))
            print(paint('If neither one was 3.6 or higher, you will need to either update or install one of them.'))
            sys.exit()

    default_config = {
        "paths": {
            "super_root": os.getcwd(),
            "reactjorc": os.getcwd() + "/reactjorc",
            "project_root": os.getcwd() + "/" + project_name
        },
        "extensions": [
            {
                "rc_home": "reactjo_django",
                "uri": "https://github.com/aaron-price/reactjo-django.git",
                "branch": 'v' + LATEST_VERSION
            },
            {
                "rc_home": "reactjo_nextjs",
                "uri": "https://github.com/aaron-price/reactjo-nextjs.git",
                "branch": 'v' + LATEST_VERSION
            }
        ],
        "project_name": project_name,
        "py_cmd": py_cmd,
        "models": [],
        "serializers": [],
        "views": [],
        "current_scaffold": {},
        "worklist": []
    }

    with open('reactjorc/config.json', 'w') as file:
        json.dump(default_config, file, indent = 4)
