import sys
import os
import pkg_resources
from .list import get_requirements


def install():
    config_path = os.path.join(os.curdir, "requirements.ini")
    if not os.path.exists(config_path):
        with open(config_path, "w") as fp:
            fp.write(pkg_resources.resource_string("pyrequirements", "requirements.ini.tpl"))

def upgrade(name=None):
    print("You should manual run `pip install --upgrade -r requirements.txt`")


def main():
    """

    :return:
    """
    help_text = """Usage: pyrequirements [cmd]

    install     initial demo requirements.ini configure file
    show        show current python env freeze requirement package info
    """
    if len(sys.argv) > 1:
        if sys.argv[1].strip() == "install":
            install()
            exit()
        elif sys.argv[1].strip() == "upgrade":
            if len(sys.argv) > 2:
                upgrade(sys.argv[2])
            upgrade()
            exit()
        elif sys.argv[1].strip() == "show":
            print(get_requirements())
            exit()
    print(help_text)