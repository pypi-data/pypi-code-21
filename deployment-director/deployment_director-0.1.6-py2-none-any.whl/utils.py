from __future__ import print_function
import importlib, re

def interpolate(obj, context):
  # Split string by occurrences of our interpolation pattern ${...}
  # - odd split string positions are a no match, substitue our escape sequence only ('$${' -> '${')
  # - even positions are to be interpolated using the context
  return "".join([ ("{0." + x[2:-1] + "}").format(context) if i % 2 else x.replace('$${','${') for (i,x) in enumerate(re.split(r'((?<!\$)\$\{[^}]+\})', obj)) ])

def create_action(action_def):
  # Load "module.submodule.MyClass"
  ActionClass = getattr(importlib.import_module(".actions", "DeploymentDirector"), action_def.class_name)
  # Instantiate the class (pass arguments to the constructor, if needed)
  instance = ActionClass(**action_def.arguments)
  return instance
  
import sys

def eprint(*args, **kwargs):
  print(*args, file=sys.stderr, **kwargs)
