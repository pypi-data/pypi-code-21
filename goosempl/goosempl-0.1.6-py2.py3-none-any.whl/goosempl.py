'''
This module provides some extensions to matplotlib.

:references:

  * `Colormaps <http://matplotlib.org/examples/color/colormaps_reference.html>`_

:dependencies:

  * numpy
  * matplotlib

:copyright:

  | Tom de Geus
  | tom@geus.me
  | http://www.geus.me
'''

import matplotlib.pyplot as plt
import matplotlib        as mpl
import numpy             as np
import os,re,sys

# ==================================================================================================

def cdf(data,mode='continuous',**kwargs):
  '''
Plot cumulative probability density.

:arguments:

  **data** (``<numpy.ndarray>``)
    Input data, to plot the distribution for.

:options:

  **mode** ([``'continuous'``] | ``'line'`` | ``'bar'``)
    Plot modes. The data is binned, unless ``continuous`` is used.

  **ax** (``<matplotlib>``)
    Specify an axis to include to plot in. By default the current axis is used.

:barstyle:

  **facecolor** (``<str>``)
    Face color of the patch-objects.

  **edgecolor** (``<str>``)
    Edge color of the patch-objects.

  **linestyle** ([``'solid'``] | ``'dashed'`` | ``'dashdot'`` | ``'dotted'``)
    Line-style of the outline of the patch-objects.

  **linewidth** ([``1.0``] | ``<float>``)
    Line-width of the outline of the patch-objects.

:histogram:

  **density** ([``True``] | ``False``)
    If set to ``True`` the area under the curve is normalized to one.

  **bins** ([``10``] | ``<int>``)
    Number of bins.

  **range** (``<list>``) *optional*
    Lower and upper limit of the bins. If not provided, range is simply
    ``(data.min(),data.max())``. NB: values outside the range are ignored.

  **weights** (``<numpy.ndarray>``) *optional*
    Weights, of the same shape as ``data``.

:recommended options:

  **linestyle** ([``'-'``] | ``'--'`` | ``'-.'`` | ``None``)
    Line-style

  **linewidth** (``<float>``)
    Line-width (e.g. ``1.0``).

  **marker** (``<str>``)
    Marker.

.. seealso::

  * `matplotlib.patches.Rectangle
    <http://matplotlib.org/api/patches_api.html#matplotlib.patches.Rectangle>`_.

  * `matplotlib.pyplot.plot
    <http://matplotlib.org/api/pyplot_api.html#matplotlib.pyplot.plot>`_.
  '''

  ax = kwargs.pop('ax',plt.gca())

  # plot continuous
  # ---------------

  if mode in ['continuous','c']:
    return ax.plot(np.sort(data),np.linspace(0.0,1.0,len(data)),**kwargs)

  # plot in bins
  # ------------

  histogram            = {}
  histogram['density'] = kwargs.pop('density',True)
  for key in ['bins','range','weights']:
    if key in kwargs:
      histogram[key] = kwargs.pop(key)

  # calculate histogram
  data,bin_edges = np.histogram(data,**histogram)
  data           = np.cumsum(data)
  data          /= data[-1]
  bin_edges     += np.diff(bin_edges)[0]/2.

  # plot as curve
  if mode in ['line','lines','l']:
    return ax.plot(np.cumsum(np.diff(bin_edges))+bin_edges[0]-np.diff(bin_edges)[0]/2.,data,**kwargs)

  # plot as bars
  if mode in ['bars','bar','b']:
    for i,(x0,dx,dy) in enumerate(zip(bin_edges[:-1],bin_edges[1:]-bin_edges[:-1],data)):
      ax.add_patch(mpl.patches.Rectangle((x0,0),dx,dy,**kwargs))

  return None

# ==================================================================================================

def patch(*args,**kwargs):
  '''
Add patches to plot. The color of the patches is indexed according to a specified color-index.

:example:

  Plot a finite element mesh: the outline of the undeformed configuration, and the deformed
  configuration for which the elements get a color e.g. based on stress::

    import matplotlib.pyplot as plt
    import goosempl          as gplt

    fig,ax = plt.subplots()

    p = gplt.patch(coor=coor+disp,conn=conn,ax=ax,cindex=stress,cmap='YlOrRd',edgecolor=None)
    _ = gplt.patch(coor=coor     ,conn=conn,ax=ax)

    cbar = fig.colorbar(p,ax=ax,aspect=10)

    plt.show()

:arguments - option 1/2:

  **patches** (``<list>``)
    List with patch objects. Can be replaced by specifying ``coor`` and ``conn``.

:arguments - option 2/2:

  **coor** (``<numpy.ndarray>`` | ``<list>`` (nested))
    Matrix with on each row the coordinates (positions) of each node.

  **conn** (``<numpy.ndarray>`` | ``<list>`` (nested))
    Matrix with on each row the number numbers (rows in ``coor``) which form an element (patch).

:options:

  **cindex** (``<numpy.ndarray>``)
    Array with, for each patch, the value that should be indexed to a color.

  **ax** (``<matplotlib>``)
    Specify an axis to include to plot in. By default the current axis is used.

  **autoscale** ([``True``] | ``False``)
    Automatically update the limits of the plot (currently automatic limits of Collections are not
    supported by matplotlib).

:recommended options:

  **cmap** (``<str>`` | ...)
    Specify a colormap.

  **linewidth** (``<float>``)
    Width of the edges.

  **edgecolor** (``<str>`` | ...)
    Color of the edges.

  **clim** (``(<float>,<float>)``)
    Lower and upper limit of the color-axis.

:returns:

  **handle** (``<matplotlib>``)
    Handle of the patch objects.

.. seealso::

  * `matplotlib example
    <http://matplotlib.org/examples/api/patch_collection.html>`_.
  '''

  from matplotlib.collections import PatchCollection
  from matplotlib.patches     import Polygon

  # check dependent options
  if ( 'coor' not in kwargs or 'conn' not in kwargs ):
    raise IOError('Specify both "coor" and "conn"')

  # extract local options
  ax        = kwargs.pop( 'ax'        , plt.gca() )
  cindex    = kwargs.pop( 'cindex'    , None      )
  coor      = kwargs.pop( 'coor'      , None      )
  conn      = kwargs.pop( 'conn'      , None      )
  autoscale = kwargs.pop( 'autoscale' , True      )
  # set defaults
  kwargs.setdefault('edgecolor','k')

  # no color-index -> set transparent
  if cindex is None:
    kwargs.setdefault('facecolor',(0.,0.,0.,0.))

  # convert mesh -> list of Polygons
  if coor is not None and conn is not None:
    poly = []
    for iconn in conn:
      poly.append(Polygon(coor[iconn,:]))
    args = (poly,*args)

  # convert patches -> matplotlib-objects
  p = PatchCollection(*args,**kwargs)
  # add colors to patches
  if cindex is not None:
    p.set_array(cindex)
  # add patches to axis
  ax.add_collection(p)

  # rescale the axes manually
  if autoscale:
    # - get limits
    xlim = [ np.min(coor[:,0]) , np.max(coor[:,0]) ]
    ylim = [ np.min(coor[:,1]) , np.max(coor[:,1]) ]
    # - set limits +/- 10% extra margin
    plt.xlim([xlim[0]-.1*(xlim[1]-xlim[0]),xlim[1]+.1*(xlim[1]-xlim[0])])
    plt.ylim([ylim[0]-.1*(ylim[1]-ylim[0]),ylim[1]+.1*(ylim[1]-ylim[0])])

  return p

# ==================================================================================================
