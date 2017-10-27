# -*- coding: utf-8 -*-

"""Main module."""

import re
import logging
from . import parser

logger = logging.getLogger(__name__)


def size_to_gb(raw):
    '''
    Convert dmidecode memory size description to GB

    Parameters
    ----------
    raw:str

    Returns
    -------
    float
        value in GB
    '''
    nb = re.search('[0-9]+', raw)
    if nb:
        nb = int(re.search('[0-9]+', raw).group())
    else:
        return 0

    if 'MB' in raw:
        return nb / 1024 if nb else 0
    elif 'GB' in raw:
        return nb
    else:
        return 0


def total_ram(memory):
    '''
    Sum all memory slot size in GB 

    Parameters
    ----------
    memory:list

    Returns
    -------
    float
    '''
    return sum([size_to_gb(elt['Size']) for elt in memory])


def to_gist(raw):
    '''
    Summarize dmidecode output

    Parameters
    ----------
    raw:str
        raw output from a parser command

    Returns
    -------
    dict
    '''
    def get_key_revision(keys):
        return [key for key in keys if 'Revision' in key][0]

    parsed = parser.parse_dmi(raw)
    bios = [section[1] for section in parsed if section[0] == 'bios'][0]
    system = [section[1] for section in parsed if section[0] == 'system'][0]
    # only non empty slot
    memory = [item[1] for item in parsed if item[0] == 'memory device']
    processor = [item[1] for item in parsed if item[0] == 'processor']

    return {'serial_number': system['Serial Number'],
            'manufacturer': system['Manufacturer'],
            'model': system['Product Name'],
            'firmware': bios[get_key_revision(bios.keys())],
            'ram_gb': total_ram(memory),
            # hypothese : all proc are the same
            'cpu_description': processor[0]['Version'],
            'nb_processor': len(processor),
            'nb_thread': sum([int(proc['Thread Count']) for proc in processor])
            }


def to_gist_batch(data):
    '''
    Parameters
    ----------
    data:dict
        look like {'hostname':raw dmidecode,...}
    Returns
    -------
    iterator
        [{'hostname':x.z,serial_number: XXX...},{'hostname':x.z.z, ...}]
    '''
    for hostname,raw in data.items():
        try:
            yield {**{'hostname':hostname},**(to_gist(raw))}
        except Exception as e:
            yield {}
            logger.info("can't parse "+hostname)
