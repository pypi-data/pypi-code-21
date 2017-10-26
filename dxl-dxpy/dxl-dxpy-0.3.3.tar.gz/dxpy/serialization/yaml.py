"""
Add yaml support for generic classes.
Currently support:
- subcless of Enum
"""
from ruamel.yaml import YAML
yaml = YAML()


def register(cls):
    yaml.register_class(cls)
# from enum import Enum


# def add_yaml_support_enum(cls, tag):
#     fmt = 'YAML support added for {cls} with tag: {tag}.'
#     logger.info(fmt.format(cls=cls, tag=tag))

#     def representer(dumper, data):
#         return dumper.represent_scalar(tag, data.name)
#     yaml.add_representer(cls, representer)

#     def constructor(loader, node):
#         value = loader.construct_scalar(node)
#         for v in cls:
#             if v.name == value:
#                 return v
#         raise ValueError(
#             "Unkown value {value} of type {cls}.".format(value=value, cls=cls))
#     yaml.add_constructor(tag, constructor)


# def add_yaml_support(cls, tag):
#     if issubclass(cls, Enum):
#         add_yaml_support_enum(cls, tag)
