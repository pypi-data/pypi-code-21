import argparse
import code
import os

from cobweb.adapters.http import HttpAdapter

EMPTY_PROJECT_CODE = """from cobweb import Cobweb

START_URL = "example.com"


def process_callback(response):
    pass


if __name__ == "__main__":
    cobweb = Cobweb()
    cobweb.start_from(START_URL)
    cobweb.default_process_function = process_callback
    cobweb.populate_spiders()
    cobweb.start()
"""


def main():
    parser = argparse.ArgumentParser(description='Cobweb helper line')
    parser.add_argument('command',
                        help='command to be executed',
                        choices=["init", "shell"],
                        type=str
                        )
    parser.add_argument("parameter",
                        help="parameter to the command",
                        type=str,
                        nargs="?",
                        )
    args = parser.parse_args()

    if args.command == "init":
        if not args.parameter:
            print("No project name")
        else:
            init(args.parameter)
    elif args.command == "shell":
        if not args.parameter:
            print("No url passed to shell")
        else:
            shell(args.parameter)


def init(name):
    current_directory = os.getcwd()
    project_name = os.path.join(current_directory, name)

    if os.path.exists(project_name):
        raise OSError("Folder with name '{}' already exists".format(name))

    os.makedirs(os.path.join(project_name, "adapters"))
    os.makedirs(os.path.join(project_name, "spiders"))
    with open(os.path.join(project_name, "__main__.py"), "w") as file:
        file.write(EMPTY_PROJECT_CODE)


def shell(url):
    response = HttpAdapter().invoke(url)
    code.interact(local=dict(globals(), **locals()))
