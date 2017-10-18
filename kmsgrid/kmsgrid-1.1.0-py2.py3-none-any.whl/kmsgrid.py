# -*- coding: utf-8 -*-
"""
kmsgrid.py

Parse and translate grid files from KMS/DTU.


### FORMAT DESCRIPTION ###

    Binary format of geoid tables.

    The table is interpolated bilinearly.

    The text (0:3) descibes bytes 0:3

    The binary tables are formated:

    Header (0:63)
    Table (64:length_of_table+63)

    Header::
    f777 (0:3)   int    :: table type, 777 == geoids
    BL   (4:51)  double :: Bmin, Bmax, Lmin, Lmax, dB, dL
                       B:: latitude, L:: longitude (unit = degree)
    ezf  (52:63) int    :: datum, cstm, mode
                   datum:: 4 == etrs89
                    cstm:: 0 == geographical
                    mode:: 0 when geographical

    rec_p_bl        = 16;
    n_max           = (int) ((Bmax - Bmin) / dB + 1.1);
    e_max           = (int) ((Lmax - Lmin) / dL + 1.1);
    estop           = ((e_max + rec_p_bl -1) / rec_p_bl) * rec_p_bl;
    blk_size        = rec_p_bl * sizeof(float); // (== 64)
    row_size        = estop / rec_p_bl * blk_size;
    length_of_table = n_max * row_size;

    Organisation of Table::
    Rows decreasing from Bmax to Bmin

    Organisation of Row(i) {i|0:(n_max-1)} ::
    values on latitude (B_max -(i*dB)) increasing from Lmin to Lmax.

    NB: the last elements of each row float(e_max:e_stop-1) is fill == 9999.99f;

    NB: blk_size is depending on the table type::
        2-dim transf.: blk_size = rec_p_bl *2* sizeof(float); // (== 128)
                       binary elements:: (dN, dE)
        3-dim transf.: blk_size = rec_p_bl *3* sizeof(float); // (== 192)
                       binary elements:: (dN, dE, dH)
        2-dim double:  blk_size = rec_p_bl *2* sizeof(double); // (== 256)
                       binary elements:: (dN, dE)

    NB: in some tables is datum, cstm and mode differently coded than above.
        This means that the datum and projections is different from geo_etrs89
"""
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import sys
import math
import argparse

import numpy as np
import gdal
import osr

# pylint: disable=invalid-name
# allow names like N, m, n and co

__version__='1.1.0'

gdal.UseExceptions()

SUPPORTED_DRIVERS = [
    'GTiff',
    'GTX',
    'NTv2',
    'CTable2',
]

# Record definition of geoid grid
HEADER_STRUCT = np.dtype([
    ('tabletype', '<i4'),
    ('latmin', '<f8'),
    ('latmax', '<f8'),
    ('lonmin', '<f8'),
    ('lonmax', '<f8'),
    ('dlat', '<f8'),
    ('dlon', '<f8'),
    ('datum', '<i4'),
    ('cstm', '<i4'),
    ('mode', '<i4')
])

RECS_PER_BLOCK = 16
BLOCK_SIZE = 64
NODATA = 9999

def limit_longitude(lon):
    """ Limit longitudes to sensible values.

    Based on ideas from http://stackoverflow.com/a/31125984
    """
    lon_reduced = math.fmod(lon, 360)
    if lon_reduced > 180.0:
        lon_reduced -= 360.0
    elif lon_reduced <= -180.0:
        lon_reduced += 360.0

    return lon_reduced


class KMSGrid(object):
    """Parse grid files from KMS/DTU."""

    def __init__(self, filename):
        """Reads KMS grids and translates them to a readable format.

        Input:
          filename:     path to grid file in KMS format.
        """

        self.filename = filename
        self.header = np.memmap(filename, dtype=HEADER_STRUCT, mode='r', shape=1)

        estop = ((self.nlon + RECS_PER_BLOCK - 1) // RECS_PER_BLOCK) * RECS_PER_BLOCK
        block_size  = RECS_PER_BLOCK * self.dims
        row_size = estop / RECS_PER_BLOCK * block_size
        tablelength = int(self.nlat * row_size)

        mmap = np.memmap(
            filename,
            dtype='<f4',
            mode='r',
            offset=64, # size of header
        )

        ncolumns = int(tablelength / self.nlat / self.dims)
        self.data = []
        for dim in range(self.dims):
            temp = mmap[dim:tablelength:self.dims]
            temp = np.reshape(temp, (self.nlat, ncolumns)) # matrix-style indices are used
            self.data.append(temp[0:self.nlat, 0:self.nlon])


    def __len__(self):
        return self.nlat*self.nlon

    def __str__(self):
        out = '%12s:  %s\n' % ('filename', self.filename)
        out += '%12s:  %s\n' % ('dimensions', self.dims)
        out += '%12s:  %s\n' % ('latmin', self.latmin)
        out += '%12s:  %s\n' % ('latmax', self.latmax)
        out += '%12s:  %s\n' % ('lonmin', self.lonmin)
        out += '%12s:  %s\n' % ('lonmax', self.lonmax)
        for dim in range(self.dims):
            out += ' data[%d].min:  %s\n' % (dim, np.min(self.data[dim]))
            out += ' data[%d].max:  %s\n' % (dim, np.max(self.data[dim]))
            out += 'data[%d].mean:  %s\n' % (dim, np.mean(self.data[dim]))
        out += '%12s:  %s\n' % ('dlat', self.dlat)
        out += '%12s:  %s\n' % ('dlon', self.dlon)
        out += '%12s:  %s\n' % ('nlat', self.nlat)
        out += '%12s:  %s\n' % ('nlon', self.nlon)
        out += '%12s:  %s\n' % ('datum', self.datum)
        out += '%12s:  %s\n' % ('mode', self.mode)
        out += '%12s:  %s\n' % ('tabletype', self.tabletype)
        return out

    @property
    def dims(self):
        """Dimensions of loaded grid"""
        dimensions = {
            777:    1,
            770:    3,
        }

        try:
            return dimensions[self.header['tabletype'].item()]
        except:
            return 1

    @property
    def latmin(self):
        """Minimum latitude of geoid grid."""
        return self.header['latmin'].item()

    @property
    def latmax(self):
        """Maximum latitude of geoid grid."""
        return self.header['latmax'].item()

    @property
    def lonmin(self):
        """Minimum longituide of geoid grid."""
        return limit_longitude(self.header['lonmin'].item())

    @property
    def lonmax(self):
        """Maximum longitide of geoid grid."""
        return limit_longitude(self.header['lonmax'].item())

    @property
    def nlat(self):
        """Number of latitudal cells."""
        latmax = self.header['latmax']
        latmin = self.header['latmin']
        return int((latmax - latmin) / self.dlat + 1)

    @property
    def nlon(self):
        """Number of longitudinal cells."""
        lonmin = self.header['lonmin']
        lonmax = self.header['lonmax']
        return int((lonmax - lonmin) / self.dlon + 1)

    @property
    def dlat(self):
        """Latitudinal step size in geoid grid."""
        return self.header['dlat'].item()

    @property
    def dlon(self):
        """Longitudinal step size in geoid grid."""
        return self.header['dlon'].item()

    @property
    def datum(self):
        """Datum of the geoid grid."""
        datum = self.header['datum'].item()

        datums = {}
        datums[0] = 'Undefined or implicit [{0}]'.format(datum)
        datums[1] = 'WGS84'
        datums[4] = 'ETRS89'
        datums[5] = 'Greenland Reference Frame 1996 (GR96)'
        datums[7] = 'ITRF19yy/20yy'
        datums[32] = 'Fehmarn Datum 2010'
        datums[62] = 'North American D.1983 Greenland'
        datums[129] = 'System 1934 Jylland'
        datums[130] = 'System 1934 Sjælland'
        datums[131] = 'System 1945 Bornholm'

        if datum not in datums.keys():
            datum = 0

        return datums[datum]

    @property
    def epsg(self):
        """EPSG of the geoid grid."""
        index = self.header['datum'].item()
        epsg = {}
        epsg[1] = 4326  # WGS84
        epsg[4] = 4258  # ETRS89
        epsg[5] = 4747  # GR96
        epsg[7] = 4258  # ETRS89

        if index not in epsg.keys():
            raise ValueError('EPSG code not defined for datum "{0}"!'.format(self.datum))

        return epsg[index]

    @property
    def mode(self):
        """Type of grid."""
        mode = self.header['mode'].item()

        modes = {}
        modes[0] = 'KMSGrid'
        modes[1] = 'Height difference'
        modes[99] = 'Undefined [{0}]'.format(mode)

        if mode not in modes.keys():
            mode = 99

        return modes[mode]

    @property
    def tabletype(self):
        """The first four bytes of the header in numerical form."""
        t = self.header['tabletype'].item()
        if t == 777:
            return 'geoid'

        if t == 770:
            return '3D'

        return t

    def export(self, filename, dimensions, gdal_driver='GTiff', create_options=None):
        """Export KMS grid file as georeferenced grid in standardized format.

        Each pixel represent a value in the grid where the corresponding
        coordinate is found at the upper left corner of the pixel.

        For more on coordinate systems in geotiffs have a look here:
            http://www.remotesensing.org/geotiff/spec/geotiff2.5.html

        """

        nbands = len(dimensions)
        if gdal_driver in ('NTv2', 'CTable2'):
            if len(dimensions) != 2:
                raise ValueError(
                    'Number of dimensions has to be exactly 2 when using the NTv2 driver.'
                )
            nbands = 4

        nodata = 9999.99
        if gdal_driver == 'GTX':
            nodata = -88.88880

        driver = gdal.GetDriverByName(gdal_driver)
        co = ['AREA_OR_POINT=POINT']
        if create_options is not None:
            co.extend(create_options.split(' '))

        srs = osr.SpatialReference()
        srs.ImportFromEPSG(self.epsg)

        data_src = driver.Create(
            filename,
            xsize=self.nlon,
            ysize=self.nlat,
            bands=nbands,
            eType=gdal.GDT_Float32,
        )

        for i, dim in enumerate(dimensions):
            band = data_src.GetRasterBand(i+1)
            band.SetNoDataValue(nodata)

            band.WriteArray(self.data[dim-1])
            band.FlushCache()

        # [top left x, w-e pixel res., 0, top left y, 0, n-s resolution]
        geo_tf = [self.lonmin-(self.dlon/2), self.dlon, 0,
                  self.latmax+(self.dlat/2), 0, -self.dlat]
        data_src.SetGeoTransform(geo_tf)
        data_src.SetProjection(srs.ExportToWkt())
        data_src.SetMetadataItem('AREA_OR_POINT', 'Point')


def run_translate(args):
    """Subprogram that translates between data formats."""

    if args.driver not in SUPPORTED_DRIVERS:
        print('Unknown driver "{driver}". Quitting.'.format(driver=args.driver))
        return 0

    grid = KMSGrid(args.grid)
    grid.export(args.out, args.dimensions, args.driver, args.creation_options)

def run_info(args):
    """Subprogram that prints geoid metadata or point data."""
    full_info = True
    grid = KMSGrid(args.grid)

    if args.point:
        full_info = False
        lon = int(args.point[0])
        lat = int(args.point[1])
        try:
            for dim in range(grid.dims):
                print('{:12.12f}'.format(grid.data[dim][lat,lon]), end=' ')
        except IndexError:
            print('Pixel location ({i},{j}) is out of bounds!'.format(i=lon, j=lat))

    if full_info:
        print(grid)

def run_help(args):
    """Subprogram the displays help text."""
    args.parser.print_help()


def main():
    """Main program - only used when called from command line."""
    argparser = argparse.ArgumentParser(description='Read binary grid files from trlib.',
                                        prog='kmsgrid')
    argparser.add_argument(
        '--version',
        action='version',
        version='%(prog)s {version}'.format(version=__version__),
    )

    subparsers = argparser.add_subparsers(
        title='Subcommands',
        description='Valid subcommands',
        help='additional help',
    )

    translate = subparsers.add_parser('translate')
    translate.add_argument('grid', help='Binary grid file.')
    translate.add_argument('out', help='Name of output grid file')
    translate.add_argument(
        '--driver',
        '-d',
        default='GTiff',
        help='Output format. Currently supports: {0}'.format(', '.join(SUPPORTED_DRIVERS)),
    )
    translate.add_argument(
        'dimensions',
        nargs='+',
        type=int,
        help='List of dimensions in output grid, e.g. "1 2"',
    )
    translate.add_argument(
        '--creation_options',
        '-co',
        help='Additional GDAL creation options. Has to be formatted like "PARAM1=foo PARAM2=bar".',
    )
    translate.set_defaults(func=run_translate)

    info = subparsers.add_parser('info')
    info.add_argument('grid', help='Binary grid file.')
    info.add_argument(
        '--point',
        nargs=2,
        metavar=('I', 'J'),
        help='Value(s) at a grid index (I,J). Prints values from all dimensions of the grid.',
    )
    info.set_defaults(func=run_info)

    helper = subparsers.add_parser('help')
    helper.set_defaults(func=run_help, parser=argparser)

    args = argparser.parse_args(sys.argv[1:])
    args.func(args)

if __name__ == '__main__':
    main()

