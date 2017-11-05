from cytoolz import first
from cytoolz import second
from merlin import chips
from merlin import chip_specs


def chips_and_specs(point, specs_fn, chips_url, chips_fn, acquired, query):
    """Returns chips and specs for a given chip spec query

    Args:
        point (tuple): (x, y) which is within the extents of a chip
        specs_fn (function):  Function that accepts a url query and returns
                              chip specs
        chips_url (str): URL to the chips host:port/context
        chips_fn (function):  Function that accepts x, y, acquired, url,
                               ubids and returns chips.
        acquired (str): ISO8601 date range
        query (str): URL query to retrieve chip specs
    Returns:
        tuple: [chips], [specs]
    """

    specs = specs_fn(query)
    chips = chips_fn(x=first(point),
                     y=second(point),
                     acquired=acquired,
                     url=chips_url,
                     ubids=chip_specs.ubids(specs))
    return (chips, specs)


def locate(point, spec):
    """Returns chip_x, chip_y and all chip locations given a point and spec

    Args:
        point (sequence): sequence of x,y
        spec (dict): chip spec

    Returns:
        tuple: (chip_x, chip_y, chip_locations), where chip_locations is a
        two dimensional chip-shaped numpy array of (x,y)
    """
    chip_x, chip_y = chips.snap(*point, chip_spec=spec)
    chip_locations = chips.locations(chip_x, chip_y, spec)
    return (chip_x, chip_y, chip_locations)
