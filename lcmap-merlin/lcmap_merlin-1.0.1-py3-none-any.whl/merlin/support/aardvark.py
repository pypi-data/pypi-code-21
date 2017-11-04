''' Filesystem based local aardvark operations.'''

from merlin import functions as f
from merlin.support import data

index = data.spectra_index(data.test_specs())

def chips(x, y, acquired, url, ubids):
    '''Return chips from local disk

    Args:
        x (number): x coordinate
        y (number): y coordinate
        acquired (str): ISO8601 date range string
        url (str): Not used.  Necessary to support chips interface
        ubids (sequence): universal band ids

    Returns:
        tuple: sequence of chips
    '''

    spectra = set(index[ubid] for ubid in ubids)
    return tuple(f.flatten([data.chips(s) for s in spectra]))


def chip_specs(url):
    '''Return chip specs from local disk

    Args:
        url (str): chip spec query

    Returns:
        tuple: sequence of chip specs matching query
    '''

    spectra = set(data.spectra_from_queryid(data.spec_query_id(url)))
    return tuple(f.flatten([data.chip_specs(s) for s in spectra]))
