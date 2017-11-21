import os
from jinja2 import Environment, FileSystemLoader
import yaml

class Obj(object):
    def __init__(self, d):
        for a, b in d.items():
            if isinstance(b, (list, tuple)):
                setattr(self, a, [Obj(x) if isinstance(x, dict) else x for x in b])
            else:
                setattr(self, a, Obj(b) if isinstance(b, dict) else b)

class Settings:
    def __init__(self, fname):
        template_loader = FileSystemLoader(searchpath="./")
        j2_env = Environment(loader=template_loader,
                             trim_blocks=True)
        j2_env.filters['env_override'] = self.env_override
        d = yaml.load(j2_env.get_template(fname).render())
        for a, b in d.items():
            if isinstance(b, (list, tuple)):
                setattr(self, a, [Obj(x) if isinstance(x, dict) else x for x in b])
            else:
                setattr(self, a, Obj(b) if isinstance(b, dict) else b)

    def env_override(self, value, key):
        return os.getenv(key, value)
