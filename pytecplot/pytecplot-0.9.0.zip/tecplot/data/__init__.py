"""`Dataset` access and manipulation.

A `Dataset` consists of a matrix of `Zones <data_access>` and `Variables
<Variable>`. Each ``Zone <data_access>``-`Variable` pair corresponds to a data
object which can always be treated as a 1D array, but which may be interpreted
as 2D or 3D in the case of *ijk*-ordered data. In general, the `Zone
<data_access>` defines the size, shape and connectivity of the data while the
`Variable` defines the underlying data type and whether the data is nodal or
cell-centered.

.. warning:: Zero-based Indexing

    It is important to know that all indexing in |PyTecplot| scripts are
    zero-based. This is a departure from the macro language which is one-based.
    This is to keep with the expectations when working in the python language.
    However, |PyTecplot| does not modify strings that are passed to the
    |Tecplot Engine|. This means that one-based indexing should be used when
    running macro commands from python or when using `execute_equation()
    <tecplot.data.operate.execute_equation>`.

"""
from . import create, extract, operate, query
from .array import Array
from .dataset import Dataset
from .face_neighbors import FaceNeighbors
from .facemap import Facemap
from .load import (load_tecplot, load_tecplot_szl, load_cgns, load_fluent,
                   load_plot3d)
from .nodemap import Nodemap, NodemapArray
from .save import save_tecplot_ascii, save_tecplot_plt, save_tecplot_szl
from .variable import Variable
from .zone import ClassicFEZone, OrderedZone, PolyFEZone
