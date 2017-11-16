import logging as log
import numpy as np
from numpy import abs, pi, cos, sin
from scipy import special

log.basicConfig(level=log.INFO)

import tecplot as tp
from tecplot.session import set_style
from tecplot.constant import ColorMapDistribution

shape = (200, 600)


log.info('creating spherical harmonic data')
r = 0.3
phi = np.linspace(0, pi, shape[0])
theta = np.linspace(0, 2*pi, shape[1])

ttheta, pphi = np.meshgrid(theta, phi, indexing='ij')

xx = r * sin(pphi) * cos(ttheta)
yy = r * sin(pphi) * sin(ttheta)
zz = r * cos(pphi)

n = 5
m = 4

ss = special.sph_harm(m, n, ttheta, pphi).real
ss /= ss.max()

log.info('creating tecplot dataset')
ds = tp.active_frame().create_dataset('Data', ['x','y','z','s'])

sphere_zone = ds.add_ordered_zone(
    'SphericalHarmonic({}, {}) Sphere'.format(m, n),
    shape)

sphere_zone.values('x')[:] = xx.ravel()
sphere_zone.values('y')[:] = yy.ravel()
sphere_zone.values('z')[:] = zz.ravel()
sphere_zone.values('s')[:] = ss.ravel()

tp.session.zones_added(sphere_zone)

log.info('creating shaped zone')
shaped_zone = ds.add_ordered_zone(
    'SphericalHarmonic({}, {}) Shaped'.format(m, n),
    shape)

shaped_zone.values('x')[:] = (abs(ss)*xx).ravel()
shaped_zone.values('y')[:] = (abs(ss)*yy).ravel()
shaped_zone.values('z')[:] = (abs(ss)*zz).ravel()
shaped_zone.values('s')[:] = ss.ravel()

log.info('state changed: zones added')
tp.session.zones_added(shaped_zone)

log.info('setting plot type to Cart3D')
tp.active_frame().plot_type = tp.constant.PlotType.Cartesian3D
plot = tp.active_frame().plot()

'''
The lines below are equivalent to the macro commands.

Notice that PyTecplot indexes universally from zero where the
macro indexes from one.

$!FIELDLAYERS SHOWCONTOUR = YES
$!FIELDLAYERS USETRANSLUCENCY = YES
$!FIELDMAP [1]  EFFECTS { SURFACETRANSLUCENCY = 70 }
$!FIELDMAP [2]  EFFECTS { SURFACETRANSLUCENCY = 30 }
$!GLOBALCONTOUR 1  COLORMAPFILTER { COLORMAPDISTRIBUTION = CONTINUOUS }
$!GLOBALCONTOUR 1  COLORMAPNAME = 'Sequential - Yellow/Green/Blue'
'''
plot.show_contour = True
plot.use_translucency = True
plot.fieldmap(sphere_zone).effects.surface_translucency = 70
plot.fieldmap(shaped_zone).effects.surface_translucency = 30
plot.contour(0).colormap_filter.distribution = ColorMapDistribution.Continuous
plot.contour(0).colormap_name = 'Sequential - Yellow/Green/Blue'

filename = 'spherical_harmonic_{}_{}'.format(m, n)

for axis in plot.axes:
    axis.fit_range()

log.info('saving image')
tp.export.save_png(filename + '.png', 600, supersample=3)

log.info('saving packaged layout file')
tp.save_layout(filename + '.lpk', include_data=True)

log.info('releasing license')
