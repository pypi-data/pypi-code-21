import json
import os
import shutil
from distutils import dir_util
import subprocess
from collections import OrderedDict

from jinja2 import Environment, FileSystemLoader, Template, select_autoescape

cwd = os.getcwd()

def cli():
    """Lawrence: Website Mockup Utility"""

    if not os.path.exists(os.path.join(cwd, "config.json")):
        config_file = os.path.join(cwd, "config.json")
        with open(config_file, 'w') as cfile:
            cfile.write(json.dumps(OrderedDict([("title", "My Website"),
                                                ("prebuild_cmds", []),
                                                ("postbuild_cmds", []),
                                                ("ignore", []),
                                                ("variables", {})]), indent=4))
        config = OrderedDict([("title", "My Website"), ("prebuild_cmds", []), ("postbuild_cmds", []), ("ignore", []), ("variables", {})])
    else:
        config_file = os.path.join(cwd, "config.json")
        if os.path.exists(config_file):
            with open(config_file) as f:
                config = json.load(f)
        else:
            config = []

    if not os.path.exists(os.path.join(cwd, "src")):
        os.mkdir(os.path.join(cwd, "src"))
    
    if not os.path.exists(os.path.join(cwd, "src", "assets")):
        os.mkdir(os.path.join(cwd, "src", "assets"))

    env = Environment(
        loader=FileSystemLoader(os.path.join(cwd, "src"))
    )

    def render(template, **values):
        prev = template.render(**values)
        while True:
            curr = Template(prev).render(**values)
            if curr != prev:
                prev = curr
            else:
                return curr

    for i in config["prebuild_cmds"]:
        subprocess.call(i, shell=True)

    if not os.path.exists(os.path.join(cwd, "build")):
        os.mkdir(os.path.join(cwd, "build"))

    for filename in os.listdir(os.path.join(cwd, "src")):
        if not filename.startswith("_") and not filename in config["ignore"] and not filename == "assets":
            with open(os.path.join(cwd, "src", filename)) as f:
                with open(os.path.join(cwd, "build", filename), 'w') as output:
                    output.write(render(env.get_template(filename),
                                        title=config["title"], **config["variables"]))
    
    dir_util.copy_tree(os.path.join(cwd, "src", "assets"), os.path.join(cwd, "build", "assets"), update=1)

    for i in config["postbuild_cmds"]:
        subprocess.call(i, shell=True)


if __name__ == '__main__':
    cli()
