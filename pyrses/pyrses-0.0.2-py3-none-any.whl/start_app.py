import json
import sys
import yaml
import importlib
from AsciiApp import AsciiApp

# load the apps yaml file
appyaml = 'test/examples/America/America.yml'
appyaml = open(appyaml)
appctlr = {}

appyaml = yaml.safe_load(appyaml)
app = AsciiApp(appyaml)

