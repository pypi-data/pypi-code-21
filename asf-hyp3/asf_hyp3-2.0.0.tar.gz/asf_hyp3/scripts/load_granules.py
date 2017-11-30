# load_granules.py
# Rohan Weeden, William Horn
# Created: June 16, 2017

# Searches a text file for granules and returns a list of all granules found.
# Takes a string of the filepath/name

from asf_hyp3.scripts import _granule_pattern
import re


def load_granules(filename):
    # If a str, treat it as a path
    if isinstance(filename, str):
        with open(filename, 'r') as granule_file:
            data = granule_file.read()
    # If a file object is passed
    elif isinstance(filename, file):
        data = filename.read()
    else:
        raise StandardError("Hyp3::scripts - Invalid arg ({}) passed to load_granules".format(filename))

    granules = set()
    # Iterat through adding matches to granules
    for match in re.finditer(_granule_pattern, data):
        granules.add(match.group(0))
    # Return all the granules found in the file with no repeats
    return list(granules)
