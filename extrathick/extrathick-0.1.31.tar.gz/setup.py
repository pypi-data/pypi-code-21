import json
from setuptools import setup

with open("config.json", "rb") as fp:
    config = json.loads(fp.read().decode("utf-8"))
with open("VERSION.txt", "rb") as fp:
    config["version"] = fp.read().strip().decode("ascii")

config["packages"] = [ config["name"] ]
config["url"] = "https://github.com/FoleyDiver/{name}".format(**config)
config["download_url"] = "{url}/archive/v{version}.tar.gz".format(**config)

setup(**config)
