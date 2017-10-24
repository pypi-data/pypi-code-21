import os
import yaml

with open(os.path.expanduser("~/mua-config.yml")) as f:
    conf = yaml.load(f.read())
