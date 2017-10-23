#!/usr/bin/python
# -*- coding: utf-8 -*-

import jinja2
from . import templates

__all__ = ['get_template']

__text_templates = {
    'cbf_header': templates.cbf_header,
    'edf_header': templates.edf_header,
    'esp_header': templates.esp_header,
    'parfile': templates.pafile,
    'aliases': templates.dectrisaliases_ini,
    'monitor': templates.dectris_monitor,
    'set2M': templates.setfile2M,
    'set6M': templates.setfile6M,
    'set300K': templates.setfile300K,
    'set1M': templates.setfile1M,
    'setFrelon': templates.setfileFrelon,
    'CrysalisExpSettings.ini': templates.crysalisExpSettings_ini,
}

__bin_templates = {
    'sel_od': templates.sel_od,
    'sel_odEsp': templates.sel_odEsp,
    'ccd1m': templates.ccd1M,
    'ccd2m': templates.ccd2M,
    'ccd6m': templates.ccd6M,
    'ccdesperanto': templates.ccdEsp,
}

__env = jinja2.Environment(loader=jinja2.DictLoader(__text_templates), newline_sequence='\r\n')


def get_template(name):
    if name in __text_templates:
        return __env.get_template(name)
    elif name in __bin_templates:
        return __bin_templates[name]
    raise KeyError(f'There is no template with name {name}')
