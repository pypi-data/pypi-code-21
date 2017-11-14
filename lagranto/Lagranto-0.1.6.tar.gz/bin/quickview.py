#!/usr/bin/env python
# coding: utf-8
"""quickview.py

Description:
    Display trajectories on a map

Usage:
    quickview.py [options] <file>

Options:
    -h --help                       Show this screen
    -f FORMAT, --format=FORMAT      Define the format of the input file;
                                    available: asci, nc, gz
                                    [default: ascii]
    -d DOMAIN, --domain=DOMAIN      Choose the domain to plot;
                                    By default cover the domain
                                    of the trajectories;
                                    nh: north hermisphere, eu: europe;
                                    lon1,lon2,lat1,lat2
    -v VAR, --variable=VAR          Variable to plot (default is the last one)
    -s FILE, --save=FILE            Save image to filename

"""
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from docopt import docopt

from lagranto import Tra
from lagranto.plotting import CartoFigure


class EuMap(CartoFigure):
    default_projection = ccrs.Stereographic(central_longitude=180 - 170,
                                            central_latitude=90 - 43,
                                            true_scale_latitude=90 - 43)
    default_extent = (-15, 30, 30, 75)


class NorthMap(CartoFigure):
    default_extent = (-180, 180, 0, 90)
    default_resolution = '110m'


maps = {
    'eu': EuMap,
    'nh': NorthMap
}


def main(filename, domain, variable, fformat, picfile):

    # parameters
    extent = None
    if domain is not None and ',' in domain:
        extent = [float(coo) for coo in domain.split(',')]
        domain = None

    # -----------------------------------------
    # read the trajectories
    # -----------------------------------------
    trajs = Tra()
    if fformat in ['ascii', 'gz']:
        gz = False
        if fformat == 'gz':
            gz = True
        trajs.load_ascii(filename, usedatetime=False, gz=gz)
    elif fformat == 'nc':
        trajs.load_netcdf(filename, usedatetime=False)
    else:
        raise IOError('format need to be of: ascii, nc or gz')

    print(trajs.shape)
    if trajs.ntra > 500:
        it = int(trajs.ntra / 500)
        trajs.set_array(trajs[::it, :])
        printstring = 'Only {} trajectories are plotted (every {})'
        print(printstring.format(trajs.ntra, it))

    if domain is None:
        extent = [trajs['lon'].min(), trajs['lon'].max(),
                  trajs['lat'].min(), trajs['lat'].max()]
    # set default parameters
    if variable is None:
        variable = trajs.dtype.names[-1]
        printstring = "Fields available for plotting: \n {0}"
        print(printstring.format(trajs.dtype.names))

    # plot trajectories

    fig = plt.figure()
    themap = maps.get(domain, CartoFigure)
    ax = themap(extent=extent)
    ax.drawmap()
    lc = ax.plot_trajs(trajs, variable, rasterized=True)
    fig.colorbar(lc, orientation='vertical', label=variable)

    if picfile is None:
        plt.show()
    else:
        plt.savefig(picfile, bbox_inches='tight')


if __name__ == '__main__':
    arguments = docopt(__doc__)
    filenamea = arguments['<file>']
    domaina = arguments['--domain']
    variablea = arguments['--variable']
    formata = arguments['--format']
    picfilea = arguments['--save']
    main(filenamea, domaina, variablea, formata, picfilea)
