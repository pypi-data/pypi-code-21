"""
Functions for working with local data.
This module allows merlin functions to test using local data rather than
requiring external systems such as aardvark to be available.

Mock servers (such as aardvark) live in other modules, not here.

There are functions contained for updating the data that lives under
merlin/support/data.  The locations of this data is controlled by values
in merlin/support/__init__.py
"""

from merlin import chips as mc
from merlin import chip_specs as mcs
from merlin import functions as f
from merlin import files
from merlin import support
from urllib.parse import urlparse
import glob
import json
import os
import re


CHIPS_DIR = support.data_config()['chips_dir']
SPECS_DIR = support.data_config()['specs_dir']


def chips(spectra, root_dir=CHIPS_DIR):
    '''Return chips for named spectra

    Args:
        spectra (str): red, green, blue, nir, swir1, swir2, thermal or cfmask
        root_dir (str): directory where chips are located

    Returns:
        sequence of chips
    '''

    path = ''.join([root_dir, os.sep, '*', spectra, '*'])
    filenames = glob.glob(path)
    chips = [json.loads(files.read(filename)) for filename in filenames]
    return tuple(f.flatten(chips))


def chip_specs(spectra, root_dir=SPECS_DIR):
    '''Returns chip specs for the named spectra.

    Args:
        spectra (str): red, green, blue, nir, swir1, swir2, thermal or cfmask
        root_dir (str): directory where chip specs are located

    Returns:
        sequence of chip specs
    '''

    path = ''.join([root_dir, os.sep, '*', spectra, '*'])
    filenames = glob.glob(path)
    return json.loads(files.read(filenames[0]))


def chip_ids(root_dir=CHIPS_DIR):
    '''Returns chip ids for available chip data in root_dir

    Args:
        root_dir: directory where chips are located

    Returns:
        tuple of tuples of chip ids (UL coordinates)
    '''

    def getxy(fpath):
        _fs = fpath.split('_')
        return _fs[1], _fs[2]

    glob_exp = ''.join([root_dir, os.sep, '*blue*'])
    return tuple({getxy(i) for i in glob.glob(glob_exp)})


def spectra_index(specs):
    '''Returns a dict keyed by ubid that maps to the spectra name

    Args:
        specs (dict): A dict of spectra: chip_specs

    Returns:
        A dict of ubid: spectra
    '''

    def rekey_by_ubid(chip_spec, spectra):
        return dict((ubid, spectra) for ubid in mcs.ubids(chip_spec))

    return f.merge([rekey_by_ubid(cs, s) for s, cs in specs.items()])


def spectra_from_specfile(filename):
    '''Returns the spectra the named chip spec file is associated with

    Args:
        filename (str): File to obtain spectra from

    Returns:
        str: spectra associated with file
    '''

    return os.path.basename(filename).split('_')[0]


def spec_query_id(url):
    '''Generates identifier for spec query url based on the querystring

    Args:
        url (str): url containing a querystring

    Returns:
        str: query identifier
    '''

    return re.compile('[: =]').sub('_', urlparse(url).query)


def spec_query_ids(specs_url):
    '''Returns a dictionary of key: query from a specs_url

    Args:
        specs_url (str): URL to chip specs

    Returns:
        dict: key:query for all the queries associated with specs_url
    '''

    return {k: spec_query_id(v)
            for k, v in support.chip_spec_queries(specs_url).items()}


def spectra_from_queryid(queryid, root_dir=SPECS_DIR):
    '''Returns the spectra name for a chip spec from the supplied queryid

    Args:
        queryid (str): query identifier
        root_dir (str): directory where chip specs are located

    Returns:
        list: spectra names associated with the query identifier
    '''

    path = ''.join([root_dir, os.sep, '*', queryid, '*'])
    filenames = glob.glob(path)
    return [os.path.basename(filename).split('_')[0] for filename in filenames]


def test_specs(root_dir=SPECS_DIR):
    '''Returns a dict of all test chip specs keyed by spectra

    Args:
        root_dir (str): directory where chip specs are located

    Returns:
        dict: spectra: [chip_spec1, chip_spec2, ...]
    '''

    path = ''.join([root_dir, os.sep, '*'])
    fnames = glob.glob(path)
    return {spectra_from_specfile(f): json.loads(files.read(f)) for f in fnames}


def live_specs(specs_url):
    '''Returns a dict of all chip specs defined by the driver.chip_spec_urls
    keyed by spectra

    Args:
        specs_url (str): chip spec query

    Returns:
        dict: spectra: [chip_spec1, chip_spec2, ...]
    '''

    return {k: mcs.get(v)
            for k, v in support.chip_spec_queries(specs_url).items()}


def update_specs(specs_url, conf=support.data_config()):
    '''Updates the spec test data

    Args:
        specs_url (str): chip spec query
        conf (dict): key:values for data_config

    Returns:
        bool: True or Exception
    '''

    specs = live_specs(specs_url)
    qids = spec_query_ids(specs_url)

    for spectra in specs.keys():
        filename = '{}_{}.json'.format(spectra, qids[spectra])
        output_file = os.path.join(conf['specs_dir'], filename)
        files.write(files.mkdirs(output_file), json.dumps(specs[spectra]))
    return True


def update_chips(chips_url, specs_url, conf=support.data_config()):
    '''Updates the chip test data

    Args:
        chips_url (str): chips url
        specs_url (str): chip spec query
        conf (dict): key:values for data_config

    Returns:
        bool: True or Exception
    '''

    x = conf['x']
    y = conf['y']
    dname = conf['dataset_name']
    acquired = conf['acquired']
    chips_dir = conf['chips_dir']
    specs = live_specs(specs_url)

    for spectra in specs.keys():
        filename = '{}_{}_{}_{}_{}.json'.format(spectra, x, y, dname,
                                                acquired.replace('/', '_'))
        output_file = os.path.join(chips_dir, filename)
        files.write(files.mkdirs(output_file),
                    json.dumps(mc.get(chips_url, x, y, acquired,
                                      mcs.ubids(specs[spectra]))))
    return True
