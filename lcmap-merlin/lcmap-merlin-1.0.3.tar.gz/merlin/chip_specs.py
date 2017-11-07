import requests

def get(query):
    """Queries aardvark and returns chip_specs

    Args:
        query (str): full url query for aardvark

    Returns:
        tuple: sequence of chip specs

    Example:
        >>> chip_specs('http://host/v1/landsat/chip-specs?q=red AND sr')
        ('chip_spec_1', 'chip_spec_2', ...)
    """

    return tuple(requests.get(query).json())


def byubid(chip_specs):
    """Organizes chip_specs by ubid

    Args:
        chip_specs (sequence): a sequence of chip specs

    Returns:
        dict: chip_specs keyed by ubid
    """

    return {cs['ubid']: cs for cs in chip_specs}


def ubids(chip_specs):
    """Extract ubids from a sequence of chip_specs

    Args:
        chip_specs (sequence): a sequence of chip_spec dicts

    Returns:
        tuple: a sequence of ubids
    """

    return tuple(cs['ubid'] for cs in chip_specs if 'ubid' in cs)
