# -*- coding: utf-8 -*-
import configparser


def load_conf(path, target=None):
    parser = configparser.ConfigParser()
    parser.read(path)
    res = {
        ("%s_%s" % (section_name, key)).upper(): value
        for section_name, section in parser.items()
        for key, value in section.items()
    }
    if target:
        target.update(res)
    else:
        return res


def write_conf(path, **values):
    parser = configparser.ConfigParser()
    parser.read(path)
    if not values:
        return
    for k, v in values.items():
        section, key = k.split("_", 1)
        if section not in parser:
            parser.add_section(section)
        parser.set(section, key, v)
    with open(path, "w") as f:
        parser.write(f)
