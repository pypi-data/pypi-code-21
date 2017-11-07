from base64 import b64decode
from cytoolz import drop
from cytoolz import first
from cytoolz import unique
from merlin import functions as f
import logging
import math
import numpy as np
import requests

logger = logging.getLogger(__name__)

def get(url, x, y, acquired, ubids):
    """Returns aardvark chips for given x, y, date range and ubid sequence

    Args:
        url: full url to aardvark endpoint
        x: longitude
        y: latitude
        acquired: ISO8601 daterange '2012-01-01/2014-01-03'
        ubids: sequence of ubid strings
        url: string
        x: number
        y: number

    Returns:
        tuple: chips

    Example:
        >>> chips(url='http://host:port/landsat/chips',
                  x=123456,
                  y=789456,
                  acquired='2012-01-01/2014-01-03',
                  ubids=['LANDSAT_7/ETM/sr_band1', 'LANDSAT_5/TM/sr_band1'])
    """

    return tuple(requests.get(url, params={'x': x,
                                           'y': y,
                                           'acquired': acquired,
                                           'ubid': ubids}).json())


def difference(point, interval):
    """Calculate difference between a point and 'prior' point on an interval.

    The value of this function can be used to answer the question,
    what do I subtract from a point to find the point of the nearest
    chip that contains it?

    Geospatial raster data geometry can be somewhat counter-inuitive
    because coordinates and pixel geometry are expressed with both
    positive and negative values.

    Along the x-axis, pixel size (and thus the interval) is a positive
    number (e.g. 30 * 100). Along the y-axis though, the pixel size and
    interval is a _negative_ value. Even though this may seem peculiar,
    using a negative value helps us avoid special cases for finding the
    nearest tile-point.

    Args:
        point: a scalar value on the real number line
        interval: a scalar value describing regularly spaced points
            on the real number line

    Returns:
        difference between a point and prior point on an interval.
    """

    return point % interval


def near(point, interval, offset):
    """Find nearest point given an interval and offset.

    The nearest point will be lesser than the point for a positive
    interval, and greater than the point for a negative interval as
    is required when finding an 'upper-left' point on a cartesian
    plane.

    This function is used to calculate the nearest points along the
    x- and y- axis.

    Args:
        point: a scalar value on the real number line
        interval: a scalar value describing regularly spaced points
                  on the real number line
        offset: a scalar value used to shift point before and after
                finding the 'preceding' interval.

    Returns:
        a number representing a point.
    """

    # original clojure code
    # (-> point (- offset) (/ interval) (Math/floor) (* interval) (+ offset)))
    return ((math.floor((point - offset) / interval)) * interval) + offset


def point_to_chip(x, y, x_interval, y_interval, x_offset, y_offset):
    """Find the nearest containing chip's point.

    The resulting `x` value will be less than or equal to the input
    while the resulting `y` value will be greater than or equal.

    For this function to work properly, intervals and offsets must be
    expressed in terms of projection coordinate system 'easting' and
    'northing' units.

    Along the x-axis, this works as expected. The interval is a multiple
    of pixel size and tile size (e.g. 30 * 100 = 3000). Along the y-axis
    the interval is negative because the pixel size is negative, as you
    move from the origin of a raster file, the y-axis value _decreases_.

    The offset value is used for grids that are not aligned with the
    origin of the projection coordinate system.

    Args:
        x: longitudinal value
        y: latitude value
        x_interval:
        y_interval:
        x_offset:
        y_offset:

    Returns:
        tuple: x,y where x and y are the identifying coordinates of a chip.
    """

    return (near(x, x_interval, x_offset),
            near(y, y_interval, y_offset))


def snap(x, y, chip_spec):
    """Transform an arbitrary projection system coordinate (x,y) into the
    coordinate of the chip that contains it.

    This function only works when working with points on a cartesian plane,
    it cannot be used with other coordinate systems.

    Args:
        x: x coordinate
        y: y coordinate
        chip_spec: parameters for a chip's grid system

    Returns:
        tuple: chip x,y
    """

    chip_x = chip_spec['chip_x']
    chip_y = chip_spec['chip_y']
    shift_x = chip_spec['shift_x']
    shift_y = chip_spec['shift_y']
    chip = point_to_chip(x, y, chip_x, chip_y, shift_x, shift_y)
    return float(chip[0]), float(chip[1])


def coordinates(ulx, uly, lrx, lry, chip_spec):
    """Returns all the chip coordinates that are needed to cover a supplied
    bounding box.

    Args:
        ulx: upper left x
        uly: upper left y
        lrx: lower right x
        lry: lower right y
        chip_spec: dict containing chip_x, chip_y, shift_x, shift_y

    Returns:
        tuple: tuple of tuples of chip coordinates ((x1,y1), (x2,y1) ...)

    This example assumes chip sizes of 500 pixels.

    Example:
        >>> chip_coordinates = coordinates(1000, -1000, -500, 500, chip_spec)
        ((-1000, 500), (-500, 500), (-1000, -500), (-500, -500))
    """

    cwidth = chip_spec['chip_x']    # e.g.  3000 meters, width of chip
    cheight = chip_spec['chip_y']   # e.g. -3000 meters, height of chip

    start_x, start_y = snap(ulx, uly, chip_spec)
    end_x, end_y = snap(lrx, lry, chip_spec)

    return tuple((x, y) for x in np.arange(start_x, end_x + cwidth, cwidth)
                        for y in np.arange(start_y, end_y + cheight, cheight))


def bounds_to_coordinates(bounds, spec):
    """Returns chip coordinates from a sequence of bounds.  Performs minbox
    operation on bounds, thus irregular geometries may be supplied.

    Args:
        bounds: a sequence of bounds.
        spec: a chip spec representing chip geometry

    Returns:
        tuple: chip coordinates

    Example:
        >>> xys = bounds_to_coordinates(
                                    bounds=((112, 443), (112, 500), (100, 443)),
                                    spec=chip_spec)
        >>> ((100, 500),)
    """

    return coordinates(ulx=f.minbox(bounds)['ulx'],
                       uly=f.minbox(bounds)['uly'],
                       lrx=f.minbox(bounds)['lrx'],
                       lry=f.minbox(bounds)['lry'],
                       chip_spec=spec)


def locations(startx, starty, chip_spec):
    """Computes locations for array elements that fall within the shape
    specified by chip_spec['data_shape'] using the startx and starty as
    the origin.  locations() does not snap() the startx and starty... this
    should be done prior to calling locations() if needed.

    Args:
        startx: x coordinate (longitude) of upper left pixel of chip
        starty: y coordinate (latitude) of upper left pixel of chip

    Returns:
        a two (three) dimensional numpy array of [x, y] coordinates
    """

    cw = chip_spec['data_shape'][0]  # 100
    ch = chip_spec['data_shape'][1]  # 100

    pw = chip_spec['pixel_x']  # 30 meters
    ph = chip_spec['pixel_y']  # -30 meters

    # determine ends
    endx = startx + cw * pw
    endy = starty + ch * ph

    # ERROR: Transposed 90 degrees
    # x, y = np.mgrid[startx:endx:pw, starty:endy:ph]
    
    # build arrays of end - start / step shape
    # flatten into 1d, concatenate and reshape to fit chip
    # In order to generate the proper row major matrix
    # the order y and x are created inside mgrid matters
    y, x = np.mgrid[starty:endy:ph, startx:endx:pw]
    matrix = np.c_[x.ravel(), y.ravel()]
    return np.reshape(matrix, (cw, ch, 2))


def dates(chips):
    """Dates for a sequence of chips

    Args:
        chips: sequence of chips

    Returns:
        tuple: datestrings
    """

    return tuple([c['acquired'] for c in chips])


def trim(chips, dates):
    """Eliminates chips that are not from the specified dates

    Args:
        chips: Sequence of chips
        dates: Sequence of dates that should be included in result

    Returns:
        tuple: filtered chips
    """

    return tuple(filter(lambda c: c['acquired'] in dates, chips))


def chip_to_numpy(chip, chip_spec):
    """Removes base64 encoding of chip data and converts it to a numpy array

    Args:
        chip: A chip
        chip_spec: Corresponding chip_spec

    Returns:
        a decoded chip with data as a shaped numpy array
    """

    shape = chip_spec['data_shape']
    dtype = chip_spec['data_type'].lower()
    cdata = b64decode(chip['data'])

    chip['data'] = np.frombuffer(cdata, dtype).reshape(*shape)
    return chip


def to_numpy(chips, chip_specs_byubid):
    """Converts the data for a sequence of chips to numpy arrays

    Args:
        chips (sequence): a sequence of chips
        chip_specs_byubid (dict): chip_specs keyed by ubid

    Returns:
        sequence: chips with data as numpy arrays
    """

    return map(lambda c: chip_to_numpy(c, chip_specs_byubid[c['ubid']]), chips)


def identity(chip):
    """Determine the identity of a chip.

    Args:
        chip (dict): A chip

    Returns:
        tuple: Tuple of the chip identity field
    """

    return tuple([chip['x'], chip['y'],
                  chip['ubid'], chip['acquired']])


def deduplicate(chips):
    """Accepts a sequence of chips and returns a sequence of chips minus
    any duplicates.  A chip is considered a duplicate if it shares an x, y, UBID
    and acquired date with another chip.

    Args:
        chips (sequence): Sequence of chips

    Returns:
        tuple: A nonduplicated tuple of chips
    """

    return tuple(unique(chips, key=identity))
