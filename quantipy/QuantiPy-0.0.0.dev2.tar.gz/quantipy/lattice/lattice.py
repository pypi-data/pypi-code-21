# -*- coding: utf-8 -*-
"""
 Module for dealing with Lattices

 :author: Alexander Wietek, Michael Schuler
"""

import numpy as np
import scipy
import scipy.spatial
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import itertools

import copy

from quantipy.utils import _axes_decorator, _axes_decorator_3d,\
    _torusdistance, _wignerseitz, unique_rows, _kwtolegkw, _validunitcell
import quantipy.spglib.spglib
import quantipy.spglib.spglib2d
import quantipy.symmetries as symmetries
from distutils.version import StrictVersion


__all__ = ['read', 'Lattice', 'Square', 'Honeycomb', 'Kagome', 'Triangular',
           'Cubic', 'FCC', 'BCC', 'Diamond', 'Pyrochlore', 'Hyperhoneycomb']


def read(filename):
    """
    Reads a Lattice from a lattice file

    :type filename: str
    :param filename: filename of the lattice file
    :rtype: QuantiPy Lattice object
    :return: QuantiPy Lattice object read from input filename
    """

    fobj = open(filename,"r")

    unitcell = None
    basiscoordinates = None
    simulation_torus = None
    simulation_torus_matrix = None
    dimension = None
    coordinates = None


    # Find line defining unit cell
    unitcell_line = [line for line in fobj if "# Lattice vectors: " in line]
    if len(unitcell_line) > 1:
        raise ValueError("Error reading lattice: multiple lines " +
                         "defining unit cell found!")

    elif len(unitcell_line) == 1:
        unitcell_line = str(unitcell_line[0])

        # get dimension
        dimension = 1
        if "a2" in unitcell_line:
            dimension = 2
        if "a3" in unitcell_line:
            dimension = 3

        unitcell = np.zeros((dimension, dimension))
        for idx in range(dimension):
            unitcell[idx,:] = np.fromstring(
                unitcell_line.split("=")[idx+1].replace("(","").split(")")[0],
                sep=",")

        # print unitcell

    elif len(unitcell_line) == 0:
        fobj.seek(0,0)
        for line in fobj:
            if "[Dimension]" in line:
                dimension = int(line.strip().split("=")[1])


    fobj.seek(0,0)

    # Find line defining basiscoordinates
    basiscoordinates_line = [line for line in fobj
                             if "# Basis coordinates: " in line]
    if len(basiscoordinates_line) > 1:
        raise ValueError("Error reading lattice: multiple lines " +
                         "defining basiscoordinates found!")


    # lattice defines basiscoordinates
    if len(basiscoordinates_line) == 1:
        basiscoordinates_line = \
            basiscoordinates_line[0].replace("# Basis coordinates: ", "")
        n_basiscoordinates = len(basiscoordinates_line.split(")")) - 1
        basiscoordinates = np.zeros((n_basiscoordinates,dimension))
        for idx in range(n_basiscoordinates):

            coordstr = \
                basiscoordinates_line.split(")")[idx].replace("(","").\
                replace(",","")
            basiscoordinates[idx,:] = np.fromstring(coordstr, sep=' ')

    fobj.seek(0,0)


    # Find line defining simulation torus
    simulation_torus_line = [line for line in fobj
                             if "# Simulation torus vectors: " in line]
    if len(simulation_torus_line) > 1:
        raise ValueError("Error reading lattice: multiple lines defining " +
                         "simulation torus cell found!")
    if len(simulation_torus_line) == 1:
        simulation_torus_line = simulation_torus_line[0]

        # get dimension
        dimension = 1
        if "t2" in simulation_torus_line:
            dimension = 2
        if "t3" in simulation_torus_line:
            dimension = 3


        simulation_torus = np.zeros((dimension, dimension))
        for idx in range(dimension):
            simulation_torus[idx,:] = \
            np.fromstring(
                simulation_torus_line.split("=")[idx+1].replace("(","").split(")")[0],
                sep=",")
        # print simulation_torus

    fobj.seek(0,0)

    # Find line defining simulation torus matrix
    simulation_torus_matrix_line = [line for line in fobj
                                    if "# Simulation torus matrix: " in line]
    if len(simulation_torus_matrix_line) > 1:
        raise ValueError("Error reading lattice: multiple lines defining " +
                         "simulation matrix cell found!")
    if len(simulation_torus_matrix_line) == 1:
        simulation_torus_matrix_line = \
        simulation_torus_matrix_line[0].replace("# Simulation torus matrix: ",
                                                "")

        # get dimension
        dimension = simulation_torus_matrix_line.count("),") + 1
        simulation_torus_matrix = np.zeros((dimension, dimension))
        split = simulation_torus_matrix_line.split("),")
        for idx in range(dimension):
            string = split[idx].replace("(","").replace(")","")
            # print string, dimension
            simulation_torus_matrix[idx,:] = np.fromstring(string, sep=",")
        # print simulation_torus_matrix



    fobj.seek(0,0)


    # Find line defining sym center
    symcenter = None
    symcenter_line = [line for line in fobj if "# Symmetry center: " in line]
    if len(symcenter_line) > 1:
        raise ValueError("Error reading lattice: multiple lines " +
                         "defining symcenter found!")

    # lattice defines symcenter
    if len(symcenter_line) == 1:
        symcenter_line = \
            symcenter_line[0].replace("# Symmetry center: ", "").\
            replace("(","").replace(")","")
        symcenter = np.fromstring(symcenter_line,sep=",")
        dimension = len(symcenter)

    fobj.seek(0,0)

    # Read Coordinates
    # Only reads geometry
    is_geometry_line = False
    coordinates = []
    ctr=0
    for line in fobj:
        if is_geometry_line and ctr < n_sites:
            coordinates.append(np.fromstring(line,sep=" "))
            ctr += 1
            
        if "[Sites]" in line:
            n_sites = int(line.split("=")[1])
            is_geometry_line = True
            
    coordinates = np.array(coordinates)

    return Lattice(unitcell=unitcell, basiscoordinates=basiscoordinates,
                   coordinates=coordinates, simulation_torus=simulation_torus,
                   simulation_torus_matrix=simulation_torus_matrix,
                   sym_center=symcenter, dimension=dimension)



def get_ks(lattice):
    """
    Get the momenta and their names of a lattice ordered by
    the distance from (0,0).

    :type lattice: str/:class: Lattice
    :param lattice: Lattice to read momenta. If it is a string
                    it should be the path to the lattice file.
    :rtype: list of dict{'name','k'}
    :returns: Names and momenta of the lattice in sorted order.
    """

    if type(lattice) is str:
       lattice = read(lattice)

    ks = []
    names = []
    countnothighsym = 0
    for lg in lattice.little_groups:
        ks.append(lg['k'])
        if lg['high_sym_point'] is not None:
            names.append(lg['high_sym_point']+'.'+lg['little_group_name'])
        else:
            names.append(str(countnothighsym)+'.'+lg['little_group_name'])
            countnothighsym += 1

    ks = np.array(ks)
    names = np.array(names)
    knorms = np.sum(ks**2,axis=1)
    datasorted = []
    for kn in np.unique(knorms):
        idx = knorms==kn
        datasorted.append({'name':names[idx], 'k':ks[idx,:]})

    return datasorted




class Lattice:
    """
    :class: Lattice

    Class for describing lattices ocurring in Solid State Physics
    """

    def __init__ (self, **kwargs):
        """
        Initializer for the Lattice class.

        :type unitcell: numpy.ndarray
        :param unitcell: Vectors spanning the unit-cell of the lattice.
                         If basiscoordinates are given, the corresponding
                         infinite lattice is defined uniquely and created.
                         If no basiscoordinates are given one lattice-site
                         in the origin of each unitcell is assumed. If a
                         simulation-torus is given, a finite lattice is
                         created, otherwise the infinite one.

        :type basiscoordinates: numpy.ndarray
        :param basiscoordinates: Give the coordinates of the lattice
                                 points within a unit-cell
                                 (basis points of the lattice). **Optional**.

        :type simulation_torus: numpy.ndarray
        :param simulation_torus: Define the simulation-torus to create a
                                 finite-size lattice. **Optional**.

        :type simulation_torus_matrix: numpy.ndarray(int)
        :param simulation_torus_matrix: Define the simulation-torus as matrix
                                        :math:`$\\left( \\begin{smallmatrix}
                                        a & b \\\\ c & d \\end{smallmatrix}
                                        \\right)$`,
                                        such that the simulation torus vectors
                                        are given as multiples of the unit-cell
                                        vectors
                                        :math:`$\\mathbf{t}_1 = a
                                        \\mathbf{a}_1 + b \\mathbf{a}_2,
                                        \\mathbf{t}_2 = c \\mathbf{a}_1 + d
                                        \\mathbf{a}_2$`. **Optional**.

        :type trans_sym: Boolean
        :param trans_sym: If True, translational symmetry is considered.
                          **Optional**. Default: True

        :type sym_center: numpy.ndarray
        :param sym_center: Coordinates of the symmetry center for
                           point-group operations. Important to get
                           the maximum point-group for the lattice.
                           **Optional**. Default: (0,0)

        :type maxpg: list of str
        :param maxpg: Manually set the maximum point group operations
                      which should be used in the symmetry analysis. The
                      operations should be given as strings. The following
                      ones are possible:
                      Rotations: 'C1', 'C2', 'C3', 'C3^2', 'C6', 'C6^5',
                      Reflections: 'C1s', 'C2s', 'C3s', 'C3^2s', 'C6s', 'C6^5s'.
                      *Example*: if only translational symmetries should
                      be used set: maxpg=['C1']. **Optional**.

        :param dimension: The dimension of the lattice. At the moment only
                          dimension 2 is supported. **Optional**. Default: 2
        :type dimension: int

        Other possibilities to define the lattice without using the
        unitcell keyword are:

        :type coordinates: numpy.ndarray
        :param coordinates: Set finite lattice by coordinates. **Optional**.

        :type bravaiscoordinates: numpy.ndarray
        :param bravaiscoordinates: Set the Bravais-coordinates of the
                                   lattice. Together with basiscoordinates
                                   the lattice can be constructed. **Optional**
        """

        self._kwargs = kwargs
        self._opencluster = False

        # Create Lattice from unit cell and basiscoordinates
        # if no basiscoordinates are given a bravais lattice is assumed
        if 'dimension' in kwargs:
            self.dimension = kwargs['dimension']

        if 'unitcell' in kwargs and kwargs['unitcell'] is not None:
            self.unitcell = np.array(kwargs['unitcell']) #: Unit cell of the lattice

            #convert 1d
            if self.unitcell.size is 1:
                self.unitcell = self.unitcell.reshape((1,1))

            if not self.unitcell.shape[0] == self.unitcell.shape[1]:
                raise ValueError("Invalid unit cell given!")
            self.dimension = self.unitcell.shape[0] #: Dimension of the lattice
            self._unitcell_set = True
        else:
            self._unitcell_set = False


        if ('basiscoordinates' in kwargs and
            kwargs['basiscoordinates'] is not None):
            self.basiscoordinates = np.array(kwargs['basiscoordinates'])
            if self.basiscoordinates.shape[1] != self.dimension:
                raise ValueError("Invalid basiscoordinate dimension!")
            self._n_basiscoordinates = self.basiscoordinates.shape[0]
        else:
            self.basiscoordinates = np.zeros((1, self.dimension))
            self._n_basiscoordinates = 1


        # Create lattice from coordinates and simulation torus
        # unit cell is automatically determined
        if 'coordinates' in kwargs and kwargs['coordinates'] is not None:
            coordinates = kwargs['coordinates']

            if (not 'simulation_torus' in kwargs or
                kwargs['simulation_torus'] is None):
                self._opencluster = True
                
            self.dimension = kwargs['coordinates'].shape[1]
            self.n_sites = kwargs['coordinates'].shape[0]
            self.coordinates = kwargs['coordinates']
            if not self._opencluster:
                self.simulation_torus = kwargs['simulation_torus']
            else:
                self.simulation_torus = None
                self.unitcell = None
                self.basis_coordinates = None

            if not self._unitcell_set and not self._opencluster:
                # find unit cell using spglib algorithm
                if self.dimension == 2:
                    self.unitcell, basis_coordinates_frac, numbers = \
                        quantipy.spglib.spglib2d.find_primitive(
                            self.simulation_torus, self.coordinates)

                if self.dimension == 3:
                    self.unitcell, basis_coordinates_frac, numbers = \
                        quantipy.spglib.spglib.find_primitive(
                            self.simulation_torus, self.coordinates)

                if self.unitcell == None:
                    raise ValueError("Unable to find unit cell for given " +
                                     "simulation torus and coordinates!")

                self.basiscoordinates = np.dot(basis_coordinates_frac,
                                               self.unitcell)

        else:
            coordinates = None


        #Check if translations should be considered
        if 'trans_sym' in kwargs:
            self.trans_sym = kwargs['trans_sym']
        else:
            self.trans_sym = True

        if self._opencluster:
            self.trans_sym = False
            if 'refl_angle' in kwargs:
                self.refl_angle = kwargs['refl_angle']
            else:
                self.refl_angle = np.pi/2.


        # Set basis vectors and basis vectors of reciprocal lattice
        if not self._opencluster:
            if self.dimension is 1:
                self.a = self.unitcell[0]
                self.a_rec = 2*np.pi/self.a
                self.unitcell_rec = self.a_rec #: unitcell of reciprocal lattice
                self.unitcell_rec = self.unitcell_rec.reshape((1,1))
            elif self.dimension is 2:
                self.a1 = self.unitcell[0,:]
                self.a2 = self.unitcell[1,:]
                V = (self.a1[0]*self.a2[1] - self.a2[0]*self.a1[1])
                self.a1_rec = np.array([-2*np.pi*self.a2[1]/V,
                                        2*np.pi*self.a2[0]/V])
                self.a2_rec = np.array([2*np.pi*self.a1[1]/V,
                                        -2*np.pi*self.a1[0]/V])
                self.unitcell_rec = np.array([self.a1_rec, self.a2_rec])
            elif self.dimension is 3:
                self.a1 = self.unitcell[0,:]
                self.a2 = self.unitcell[1,:]
                self.a3 = self.unitcell[2,:]
                V = np.linalg.det(self.unitcell)
                self.a1_rec = 2*np.pi*np.cross(self.a2, self.a3)/V
                self.a2_rec = 2*np.pi*np.cross(self.a3, self.a1)/V
                self.a3_rec = 2*np.pi*np.cross(self.a1, self.a2)/V
                self.unitcell_rec = np.array([self.a1_rec, self.a2_rec,
                                              self.a3_rec])
            else:
                raise ValueError("Invalid dimension for lattice!")
        else:
            self.unitcell_rec = None


        # Calculate the Brillouin zone
        if not self._opencluster:
            if not self.unitcell.shape[0]==1:
                self.brillouin_zone_edges, self.brillouin_zone_faces = \
                    _wignerseitz(self.unitcell_rec)
            else:
                self.brillouin_zone_edges = None
                self.brillouin_zone_faces = None
        else:
            self.brillouin_zone_edges = None
            self.brillouin_zone_faces = None


        # Set maximum Point Group
        if 'maxpg' in kwargs and kwargs['maxpg'] is not None:
            self.maxpg = kwargs['maxpg']  #: Manually set maximal point group
        else:
            self.maxpg = None


        # sym_center only needed for 2d lattices
        # TODO automatic detection of symmetry center
        if 'sym_center' in kwargs and kwargs['sym_center'] is not None:
            self.sym_center = np.array(kwargs['sym_center']) #: Symmetry center for Point group symmetries
        else:
            self.sym_center = np.array([0.,0.])


        # Check if simulation torus is given
        if ('simulation_torus' in kwargs and
            kwargs['simulation_torus'] is not None):
            self._is_infinite = False
            self.set_simulation_torus(kwargs['simulation_torus'], coordinates)
            self._sim_tor_matrix = np.linalg.solve(self.unitcell.T,
                                                   self.simulation_torus.T).T
            self._sim_tor_matrix = np.array(self._sim_tor_matrix,dtype='int')

        elif ('simulation_torus_matrix' in kwargs and
              kwargs['simulation_torus_matrix'] is not None):
            self._is_infinite = False
            self.set_simulation_torus(np.dot(kwargs['simulation_torus_matrix'],
                                             self.unitcell), coordinates)
            self._sim_tor_matrix = kwargs['simulation_torus_matrix']
            self._sim_tor_matrix = np.round(self._sim_tor_matrix, decimals=6)
            if np.all(self._sim_tor_matrix==np.array(self._sim_tor_matrix,
                                                     dtype='int')):
                self._sim_tor_matrix = np.array(self._sim_tor_matrix,
                                                dtype='int')
            else:
                raise SystemExit("Simulation torus matrix has non-integer " +
                                 "entries. Abort!")

        else:
            self._is_infinite = True
            self.simulation_torus = self.unitcell
            self._sim_tor_matrix = None
            self.k_space = None

        if self._opencluster:
            self._is_infinite = False
            self.simulation_torus = None
            self._sim_tor_matrix = None
            self.k_space = None

        #Compute wigner seitz cell of simulation torus for finite lattices
        if not self._is_infinite and not self._opencluster:
            self.wigner_seitz_edges, self.wigner_seitz_faces = \
                _wignerseitz(self.simulation_torus)

            # Create Wigner Seitz Coordinates
            if self.dimension!=1:
                self.coordinates_wigner_seitz = np.zeros_like(self.coordinates)
                boundary_delaunay = scipy.spatial.Delaunay(
                    self.wigner_seitz_edges*1.00001)
                # Find transformed coordinate in wigner-seitz cell
                for idx, coord in enumerate(self.coordinates):
                    found = False
                    times_simulation_torus = 1
                    while not found:
                        for i in itertools.product(
                                range(-times_simulation_torus,
                                      times_simulation_torus),
                                repeat=self.dimension):
                            transformed_coord = coord + \
                                                np.dot(self.simulation_torus.T,
                                                       np.array(i))
                            if boundary_delaunay.find_simplex(
                                    transformed_coord) >= 0:
                                self.coordinates_wigner_seitz[idx,:] = \
                                    transformed_coord
                                found = True
                                break
                        times_simulation_torus += 1


        # Find the space group of the lattice
        if not self._opencluster:
            if self.dimension is 1:
                self.spacegroup = "C2"
                self.pointgroup = "C2"

            if self.dimension is 2:
                # TODO: Detect symmetry center in 2d automatically
                if 'sym_center' in kwargs and kwargs['sym_center'] is not None:
                    self.sym_center = np.array(kwargs['sym_center'])
                else:
                    self.sym_center = np.array([0., 0.])
                self.spacegroup = quantipy.spglib.spglib2d.get_spacegroup(
                    self.unitcell, self.basiscoordinates,
                    sym_center=self.sym_center, maxpg=self.maxpg)
                self.symmetries = quantipy.spglib.spglib2d.get_symmetry(
                    self.unitcell, self.basiscoordinates,
                    sym_center=self.sym_center, maxpg=self.maxpg)
                self.pointgroup = quantipy.spglib.spglib2d.get_pointgroup(
                    self.symmetries["rotations"])

            if self.dimension is 3:
                self.sym_center = None
                self.spacegroup = quantipy.spglib.spglib.get_spacegroup(
                    self.unitcell, self.basiscoordinates)
                self.symmetries = quantipy.spglib.spglib.get_symmetry(
                    self.unitcell, self.basiscoordinates)
                self.pointgroup = quantipy.spglib.spglib.get_pointgroup(
                    self.symmetries["rotations"])


            # Find symmetries of simulation torus
            if self._is_infinite:
                self.pointgroup_torus = self.pointgroup
                self.symmetries_torus = self.symmetries
                self.little_groups = None
                self.k_wedge = None
            else:
                assert (self.symmetries['rotations'].shape[0] ==
                        self.symmetries['translations'].shape[0])

                # Only use symmorphic symmetry elements (i.e. zero translation)
                # TODO: Think if we can keep non symmorphic stuff/
                # different symmetry centers
                symmorphic_symmetries = []
                for idx in range(self.symmetries['rotations'].shape[0]):
                    if np.count_nonzero(self.symmetries['translations'][idx]) == 0:
                        symmorphic_symmetries.append(
                            {'rot':self.symmetries['rotations'][idx],
                             'name':self.symmetries['names'][idx]})

                self._inv_unitcell = np.linalg.inv(self.unitcell)

                reduced_rotations = []
                reduced_translations = []
                reduced_names = []
                for sym in symmorphic_symmetries:
                    rot_matrix_nonfrac = np.dot(np.dot(self._inv_unitcell,
                                                       sym['rot']),
                                                self.unitcell)

                    A = np.dot(rot_matrix_nonfrac, self.simulation_torus.T)
                    c = np.linalg.solve(self.simulation_torus.T, A)

                    if np.allclose(c, np.around(c)):
                        reduced_rotations.append(sym['rot'])
                        reduced_translations.append(np.zeros(self.dimension))
                        reduced_names.append(sym['name'])

                self.symmetries_torus = {'rotations':
                                         np.array(reduced_rotations,
                                                  dtype='intc', order='C'),
                                         'translations':
                                         np.array(reduced_translations,
                                                  dtype='double', order='C'),
                                         'names': reduced_names}
                if self.dimension == 2:
                    self.pointgroup_torus = \
                        quantipy.spglib.spglib2d.get_pointgroup(
                            self.symmetries_torus["rotations"])
                elif self.dimension == 3:
                    self.pointgroup_torus = \
                        quantipy.spglib.spglib.get_pointgroup(
                            self.symmetries_torus["rotations"])


                # Get k wedge and little-groups
                self._get_little_groups(self.symmetries_torus)

        else:
            #TODO obtain symmetries for open cluster
            self.spacegroup = None
            self.symmetries = quantipy.spglib.spglib2d.get_symmetry_OBC(
                self.coordinates, sym_center=self.sym_center,
                refl_angle=self.refl_angle, maxpg=self.maxpg)
            self.pointgroup = quantipy.spglib.spglib2d.get_pointgroup(
                self.symmetries["rotations"])

            self.pointgroup_torus = self.pointgroup
            self.symmetries_torus = self.symmetries
            self._get_little_groups(self.symmetries)
            self.k_wedge = None


        # Set plot decorator
        if self.dimension==1 or self.dimension==2:
            self._plot_decorator = _axes_decorator
        elif self.dimension==3:
            self._plot_decorator = _axes_decorator_3d



    def _get_little_groups(self,symmetries):
            """
            Compute irreducible wedge and little groups of the lattice.
            """
            if self._opencluster:
                return [{'k':None, 'little_group_name':self.pointgroup,
                         'little_group':self.symmetries['rotations'],
                         'high_sym_point':"",
                         'rot_idx':np.arange(len(self.symmetries['rotations'])),
                         'rot_names':self.symmetries['names']}]


            # sort k_space to get compareable irreducible wedges for
            # different system sizes
            #sorting first according to x axis, then y, z
            sortidx = np.lexsort(self.k_space.T[::-1])
            self.k_space = self.k_space[sortidx[::-1]]

            #irreducible wedge
            self.k_wedge = np.array([self.k_space[0,:]])
            for kp in self.k_space:
                inkwedge = False
                for sym in symmetries['rotations']:
                    rot_matrix_nonfrac = np.dot(np.dot(self._inv_unitcell, sym),
                                                self.unitcell)
                    kp2 = np.dot(rot_matrix_nonfrac, kp)
                    if np.any(np.linalg.norm(self.k_wedge-kp2,axis=1)<1e-8):
                        inkwedge = True
                if not inkwedge:
                    self.k_wedge = np.vstack([self.k_wedge, kp])

            #Little-groups
            self.little_groups = []
            if self.dimension==2:
                highsympoints = self._get_high_symm_points()

            for kidx,kp in enumerate(self.k_wedge):
                little_group=[]
                rotidx = []
                rot_names =[]

                #reduced_rotations:
                for s,sym in enumerate(symmetries['rotations']):
                    rot_matrix_nonfrac = np.dot(np.dot(
                        np.linalg.inv(self.unitcell), sym), self.unitcell)
                    kp2 = np.dot(rot_matrix_nonfrac, kp)
                    if np.abs(_torusdistance(kp,kp2,self.unitcell_rec))<1e-8:
                        little_group.append(sym)
                        rotidx.append(s)
                        rot_names.append(symmetries['names'][s])

                if self.dimension == 2:
                    little_group_name = \
                        quantipy.spglib.spglib2d.get_pointgroup(little_group)
                    highsympoint = highsympoints[kidx]
                elif self.dimension == 3:
                    little_group_name = \
                        quantipy.spglib.spglib.get_pointgroup(little_group)
                    highsympoint = 'None'

                if not self.trans_sym:
                    highsympoint = 'None'

                self.little_groups.append(
                    {'k':kp, 'little_group_name':little_group_name,
                     'little_group':little_group, 'high_sym_point':highsympoint,
                    'rot_idx':rotidx, 'rot_names':rot_names})

            return self.little_groups



    def get_brillouin_zone_mesh(self, n_points):
        """
        Creates a mesh of points lying in Brillouin Zone. The number
        of points for a given direction in reciprocal space can be
        specified. This only works if basis vectors a1 and a2 are defined.

        :type n_points: int/array (dimension,)
        :param n_points: If int, number of points for every direction
                         of reciprocal lattice vectors. If array, each
                         element defines the number of points for the
                         corresponding reciprocal lattice vectors.
        :rtype: list of Numpy ndarrays
        :return: list of k points that lie in first Brillouin zone

        """
        if type(n_points)==np.ndarray or type(n_points)==list:
            n_points = np.array(n_points,dtype='int').reshape(self.dimension,1)
            if not n_points.shape[0]==self.dimension:
                raise ValueError("n_points must be int or array/list of " +
                                 "shape (self.dimension,)")
        else:
            n_points = int(n_points) * np.ones([self.dimension,1], dtype='int')

        mesh = []
        # print self.brillouin_zone_edges
        brillouin_zone_triangulation = \
            scipy.spatial.Delaunay(self.brillouin_zone_edges)

        #Create ranges
        ranges = [np.arange(-x, x+1) for x in n_points]

        # Check which points lie in first Brillouin zone
        for c in itertools.product(*ranges):
            k_tmp = np.dot(c,self.unitcell_rec/n_points)
            if brillouin_zone_triangulation.find_simplex(k_tmp) >= 0:
                mesh.append(k_tmp)
        for edge in self.brillouin_zone_edges:
            mesh.append(edge)

        return np.array(mesh)



    def set_simulation_torus(self, simulation_torus, coordinates=None):
        """
        Set the simulation torus for the lattice

        :param simulation_torus: Defines the vectors for the simulation
                                 torus, simmulation_torus[0,:] describes
                                 first vector of bounding box and
                                 simulation_torus[1,:] the second one
        :type simulation_torus: numpy.ndarray
        """

        if not isinstance(simulation_torus,np.ndarray):
            raise ValueError("Lattice.simulationtorus must be a NumPy array.")
        if not simulation_torus.shape == (self.dimension, self.dimension):
            raise ValueError("Lattice.simulationtorus must be a" +
                             " {0}x{0} NumPy array".format(self.dimension))

        self.simulation_torus = np.array(simulation_torus)

        self._is_infinite = False

        # Get reciprocal lattice of simulation torus
        if self.dimension is 1:
            self.t1 = simulation_torus[0,:]
            self.t_rec = 2*np.pi/self.t1
            self.simulation_torus_rec = self.t_rec #: Unit cell of reciprocal simulation_torus
        elif self.dimension is 2:
            self.t1 = simulation_torus[0,:]
            self.t2 = simulation_torus[1,:]
            V = (self.t1[0]*self.t2[1] - self.t2[0]*self.t1[1])
            self.t1_rec = np.array([-2*np.pi*self.t2[1]/V,
                                    2*np.pi*self.t2[0]/V])
            self.t2_rec = np.array([2*np.pi*self.t1[1]/V,
                                    -2*np.pi*self.t1[0]/V])
            self.simulation_torus_rec = np.array([self.t1_rec, self.t2_rec])
        elif self.dimension is 3:
            self.t1 = simulation_torus[0,:]
            self.t2 = simulation_torus[1,:]
            self.t3 = simulation_torus[2,:]
            V = np.linalg.det(self.simulation_torus)
            self.t1_rec = 2*np.pi*np.cross(self.t2, self.t3)/V
            self.t2_rec = 2*np.pi*np.cross(self.t3, self.t1)/V
            self.t3_rec = 2*np.pi*np.cross(self.t1, self.t2)/V
            self.simulation_torus_rec = np.array([self.t1_rec, self.t2_rec,
                                                  self.t3_rec])


        # Check if simulation torus is multiple of unit vector
        coeffs = np.linalg.solve(self.unitcell.T, self.simulation_torus.T)
        if not _validunitcell(self.unitcell, self.simulation_torus):
            raise ValueError("Lattice.simulationtorus is no multiple of " +
                             "unit cell vectors.")


        # Find coordinates of Bravais Lattice inside simulation torus
        self.bravaiscoordinates = []
        if self.dimension!=1:
            max_coeff = int(1.5*max(np.max(np.sum(coeffs,axis=0)),
                                    np.max(np.abs(np.diff(coeffs,axis=0)))))
        else:
            max_coeff = int(coeffs[0,0])

        for idx in itertools.product(range(-max_coeff-1,max_coeff+1),
                                     repeat=self.dimension):
            # check if bravais lattice point is within simulation torus
            c = np.linalg.solve(self.simulation_torus.T, np.dot(idx,
                                                                self.unitcell))
            if (c < 0.9999).all() and (c > -0.0001).all():
                self.bravaiscoordinates.append(np.dot(idx,self.unitcell))

        self.bravaiscoordinates = np.array(self.bravaiscoordinates)
        self._n_bravaiscoordinates = self.bravaiscoordinates[:,0].size
        if hasattr(self, 'basiscoordinates'):
            self._n_basiscoordinates = self.basiscoordinates.shape[0]
        self.n_sites = self._n_bravaiscoordinates * self._n_basiscoordinates

        # if coordinates are not explicitly given create all coordinates
        # from basis and bravaiscoordinates
        if coordinates == None:
            self.coordinates = np.zeros([self._n_bravaiscoordinates *
                                         self._n_basiscoordinates,
                                         self.dimension])
            for i in range(self._n_basiscoordinates):
                for j in range(self._n_bravaiscoordinates):
                    self.coordinates[i*self._n_bravaiscoordinates + j] = \
                        self.basiscoordinates[i] + self.bravaiscoordinates[j]


        # if coordinates are given check whether dimensions fit together
        else:
            if coordinates.shape != (self.n_sites, self.dimension):
                raise ValueError("Error in Lattice class: invalid coordinates given")
            self.coordinates = coordinates

        self._calc_k_points()

        #get relative indices for coordinates
        self._rel_indices = []
        for coord in self.coordinates:
            for bnum, base in enumerate(self.basiscoordinates):
                c = np.around(np.linalg.solve(self.unitcell.T,coord-base),
                              decimals=8)
                if np.allclose(c,np.around(c)):
                    self._rel_indices.append({'cell': map(int, np.around(c)),
                        'basis': bnum})

        # Compute reduced symmetries of simulation torus
        if self.dimension is 2:
            allsymmetries = quantipy.spglib.spglib2d.get_symmetry(
                self.unitcell, self.basiscoordinates,
                sym_center=self.sym_center,maxpg=self.maxpg)
        if self.dimension is 3:
            allsymmetries = quantipy.spglib.spglib.get_symmetry(
                self.unitcell, self.basiscoordinates)

        if hasattr(self, 'n_sites'):
            self._n_basiscoordinates = self.n_sites / self._n_bravaiscoordinates



    def _calc_k_points(self):
        """ Calculates the k points that lie in the Brillouin Zone"""

        if not hasattr(self,'brillouin_zone_edges'):
            #Calculate BZ
            self.brillouin_zone_edges, self.brillouin_zone_faces = _wignerseitz(self.unitcell_rec)


        if self.dimension!=1:
            if (not hasattr(self,'t1')) or (not hasattr(self,'t2')):
                raise ValueError("Cannot calculate k points: no simulation torus defined yet")
        else:
            if (not hasattr(self,'t1')):
                raise ValueError("Cannot calculate k points: no simulation torus defined yet")

        if self.dimension!=1:
            brillouin_zone_delaunay = scipy.spatial.Delaunay(self.brillouin_zone_edges*1.00001)
        else:
            brillouin_zone_delaunay = None


        if self.trans_sym:
            # Calculate k-points in First Brillouin zone given by Simulation Torus
            self.k_space = []
            if self.dimension!=1:
                coeffs = np.linalg.solve(self.simulation_torus_rec.T, self.unitcell_rec.T)


                max_coeff = int(np.around(1.5*max(np.max(np.sum(coeffs,axis=0)),
                                                  np.max(np.abs(np.diff(coeffs,axis=0))))))

                for idx in itertools.product(range(-max_coeff-1, max_coeff+1),
                                             repeat=self.dimension):

                    k_tmp = np.dot(idx, self.simulation_torus_rec)
                    if brillouin_zone_delaunay.find_simplex(k_tmp) >= 0:
                        # check if translated k point is not already registered
                        dist = lambda x: _torusdistance(k_tmp, x, self.unitcell_rec)
                        if not np.any(np.isclose(np.zeros(len(self.k_space)),  map(dist, self.k_space))):
                            self.k_space.append(k_tmp)

            else:
                coeff = int(self.unitcell_rec[0,0]/self.simulation_torus_rec[0])
                for j in range(0, coeff):
                    self.k_space.append([j*self.simulation_torus_rec[0]])

            self.k_space = np.array(self.k_space)
            assert(self.k_space.shape[0] == self._n_bravaiscoordinates)
        else:
            self.k_space = np.zeros((1,self.dimension))



    def write(self, filename, sublattice_structure=None, write_comments=True,
            eccentricity=False, write_sym_perms=False):
        """
        Write the Lattice object to a file.

        :type filename: str
        :param filename: Filename of the file where the Lattice is saved!
        :type sublattice_structure: numpy array of ints, size
                (number of sublattices)x(lattice points per sublattice)
        :param sublattice_structure: Defines the sublattice structure of the lattice, can be used for
                MPI sublattice codes
        :type write_comments: Bool
        :param write_comments: If True, comment lines with further information about the lattice are written. **Optional**. Default: True
        :type eccentricity: Bool
        :param eccentricity: If True, eccentricity of the lattice is computed and written to the file. **Optional**.
                Default: False
        :type write_sym_perms: Bool
        :param write_sym_perms: If True, permutations for all symmetry elements are written to the file. **Optional**.
                Default: False
        """
        np.set_printoptions(precision=16)
        with open(filename, 'w') as lattfile:
            lattfile.write("# This modelfile was created with the following properties:\n")

            if self._opencluster:
                lattfile.write("# Non-periodic cluster\n")

            if not self._opencluster:
                basiscoordsstring = "# Basis coordinates: " + \
                            ", ".join( ["("+", ".join(map(str,coord))+")"
                            for coord in self.basiscoordinates] ) + "\n"
                lattfile.write(basiscoordsstring)

                latticevecstring = "# Lattice vectors: " + \
                            ", ".join(["a%i=(%s)" %(i+1, ", ".join(map(str,vec)))
                            for i,vec in enumerate(self.unitcell)]) + "\n"
                lattfile.write(latticevecstring)

            if not self._is_infinite and not self._opencluster:
                simtorusstring = "# Simulation torus vectors: " + \
                        ", ".join(["t%i=(%s)" %(i+1, ", ".join(map(str,vec)))
                        for i,vec in enumerate(self.simulation_torus)]) + "\n"
                lattfile.write(simtorusstring)
                #simtorusmatrix
                coeffs = np.linalg.solve(self.unitcell.T, self.simulation_torus.T)
                simtormatrixstring = "# Simulation torus matrix: ((" + \
                        "), (".join([", ".join(["%i" %coeff for coeff in coeffs[i]])
                        for i in range(len(coeffs))]) + "))\n"
                lattfile.write(simtormatrixstring)

            if not self.sym_center is None:
                lattfile.write("# Symmetry center: (%s)\n" %(", ".join(map(str,self.sym_center))) )
            else:
                lattfile.write("# Symmetry center: --\n")
            lattfile.write("# Lattice Point Group: %s\n" %(self.pointgroup_torus))
            lattfile.write("# Lattice Space Group (infinite Lattice): %s\n" %self.spacegroup)
            if not self._opencluster:
                if not self.trans_sym:
                    lattfile.write("# Translational Symmetry NOT used!\n")
                else:
                    lattfile.write("# K points (K wedge marked with *): \n")
                    for k in self.k_space:
                        if np.any(np.all(k==self.k_wedge,axis=1)):
                            lattfile.write("# [" + " ".join(map(str,k)) +"]" +' *' + "\n")
                        else:
                            lattfile.write("# [" + " ".join(map(str,k)) +"]" + "\n")

                if self.dimension == 2:
                    lattfile.write("# High Symmetry Points: ")
                    for g in self.little_groups:
                        lattfile.write("{0}.{1}, ".format(g['high_sym_point'], g['little_group_name']))
                    lattfile.write("\n")

                if eccentricity:
                    ecc = self.eccentricity()
                    lattfile.write("# Eccentricity: %.3f\n" %ecc)
                else:
                    lattfile.write("# Eccentricity: --\n")

            lattfile.write("#\n")
            #lattfile.write("# Used Point Group: %s\n" [self.pointgroup_torus if self.maxpg==None else self.maxpg])
            #lattfile.write("#\n")

            #writing lattice file data
            if not self._is_infinite:
                lattfile.write("[Dimension]=%i\n" %self.dimension)
                lattfile.write("[Sites]=%i\n" %self.n_sites)
                if sublattice_structure is None:
                    for coord in self.coordinates:
                        lattfile.write(" ".join(["%.16f" %c for c in coord])+"\n")
                else:
                    # Get sublattice permutation
                    if sublattice_structure is not None:
                        if sublattice_structure.size != self.n_sites:
                            raise ValueError("Invalid Sublattice Structure")
                        n_sublattices = sublattice_structure.shape[0]
                        # print sublattice_structure.shape
                        sublattice_permutation = np.reshape(sublattice_structure,self.n_sites)
                        sublattice_permutation_inverse = np.zeros(self.n_sites, dtype=np.int)
                        for i in range(self.n_sites):
                            sublattice_permutation_inverse[sublattice_permutation[i]] = i
                            assert(i in sublattice_permutation)
                        # print sublattice_permutation
                        # print sublattice_permutation_inverse

                    for idx in range(len(self.coordinates)):
                        # print sublattice_permutation[idx]
                        lattfile.write(" ".join(["%.16f" %c for c in self.coordinates[sublattice_permutation[idx]]])
                                    +"\n")

                if write_sym_perms:
                    if not self.symmetries==None:
                        #compute permutations
                        perms = self._get_permutations()

                        lattfile.write("[SymmetryOps]=%i\n" %perms.shape[0])
                        for i, perm in enumerate(perms):
                            lattfile.write("[S%i] "%i + " ".join(map(str,perm)) + "\n")


                        irreps =  symmetries._get_irreps(self, self.symmetries, twod_to_oned=True)

                        lattfile.write("[Irreps]=%i\n" %len(irreps))
                        for irrepname, irrep in zip(irreps.keys(),irreps.values()):
                            lattfile.write("[Representation]=%s\n" %irrepname)
                            if not self._opencluster:
                                lattfile.write("[K=(%s)]\n" %(','.join(map(str,irrep['k']))))
                            else:
                                lattfile.write("[K=(None)]\n")
                            if sublattice_structure is None:
                                allowed_ops = irrep['allowed_ops']
                                phases = irrep['phases']
                            else:
                                # Convert allowed ops to new ordering of permutations
                                allowed_ops = np.zeros(len(irrep["allowed_ops"]),dtype=np.int)
                                for i in range(len(irrep["allowed_ops"])):
                                    allowed_ops[i] = symmetry_permutation[irrep["allowed_ops"][i]]
                                phases = irrep["phases"]

                                # sort phases and new allowed ops
                                allowed_ops, phases = (list(x) for x in zip(*sorted(zip(allowed_ops, phases))))
                                allowed_ops = np.array(allowed_ops)
                                phases = np.array(phases)

                            lattfile.write("[AllowedOps]=%i\n" %allowed_ops.shape[0])
                            lattfile.write("%s\n" %(" ".join(map(str,allowed_ops))))
                            lattfile.write("\n".join(["%.16f %.16f" %(np.real(x), np.imag(x))
                                                       for x in phases])+"\n")


    def _get_permutations(self):
        """
        Shortcut to compute permutations for lattice using symmetries module
        """
        if self.trans_sym:
            translations = self.bravaiscoordinates-self.bravaiscoordinates[0]
        else:
            translations = np.zeros((1,self.dimension))

        if not self._opencluster:
            perms = symmetries._get_permutations(self.coordinates, self.unitcell, self.simulation_torus,
                    translations, self.symmetries_torus['rotations'],
                    sym_center=self.sym_center)
        else:
            perms = symmetries._get_permutations_OBC(self.coordinates, self.symmetries['rotations'],
                    sym_center=self.sym_center)


        return perms


    def torusdistance(self, refpos):
        """
        Return the torus-distance of all sites of the lattice from a reference positions.

        :type refpos: int
        :param refpos: Reference position
        """
        refcoord = self.coordinates[refpos]

        dists = np.zeros(len(self.coordinates))
        for i,coord in enumerate(self.coordinates):
            dists[i] = _torusdistance(coord, refcoord,self.simulation_torus)

        return dists



    def eccentricity(self):
        """
        Returns the eccentricity of the lattice defined as quotient of number of bonds between two shortest
        not equivalent loops around the torus.

        :returns: Eccentricity
        :rtype: float
        """
        import networkx as nx

        if not self.dimension==2:
            raise ValueError('eccentricity only implemented for dim=2')

        allcoords = self.coordinates

        for i,j in itertools.product([0,1,-1],repeat=2):
            if not (i==0 and j==0):
                allcoords = np.vstack((allcoords, self.coordinates + i*self.t1 + j*self.t2))

        #find nearest neighbour distance
        vecs = allcoords[1:]-self.coordinates[0]
        dists = np.linalg.norm(vecs, axis=1)
        nndist = np.min(dists)

        #nn bonds
        bonds = []
        for i,j in itertools.combinations(range(len(allcoords)), r=2):
            dist = np.linalg.norm(allcoords[i]-allcoords[j])
            if np.abs(dist-nndist)<1e-8:
                bonds.append([i,j])

        G = nx.Graph()
        G.add_edges_from(bonds)
        pathlengths = []

        for c in range(1,9):
            try:
                if nx.has_path(G,0,c*self.n_sites):
                    pathlengths.append(nx.shortest_path_length(G,0,c*self.n_sites))
                else:
                    pathlengths.append(1000)
            except:
                print 'Problem computing eccentricity.'

        pathlengths = np.sort(pathlengths)

        return float(pathlengths[2])/pathlengths[0]



    def plot(self, periodic=False, boxlength=None, sym_center=True, coord_idx=False,
             plot_nearest_neighbours=True,
             nearest_neighbour_color=None, ax=None, **kwargs):
        """
        Creates a plot of the lattice

        :param periodic: If True and simulation Torus is defined the lattice is periodically contiuned
                         , optional. Default: False
        :type periodic: Boolean
        :param boxlength: Defines the length of the box in which the infinite lattice is plotted.
                           **Optional**, Default: 2 (for 3d lattices) or 4 (for 1d and 2d lattices)
        :type boxlength: float
        :param sym_center: If True, plot the used symmetry center of the lattice. **Optional**. Default: True
        :type sym_center: Boolean
        :type coord_idx: Boolean
        :param coord_idx: If True, the index of the coordinates are shown in the plot. **Optional**. Default: True
        :param plot_nearest_neighbours: If True, lines between nearest neighbours are plotted. **Optional**. Default: True
        :type plot_nearest_neighbours: Boolean
        :type wigner_seitz: Boolean
        :param wigner_seitz: If True, plot the lattice in it's Wigner-Seitz cell. **Optional**. Default: False
        :param ax: Axes for plotting, **optional**. Default: Create new figure and axes
        :type ax: Axes object
        :type kwargs: *keyword arguments*
        :param kwargs: The kwargs can be used to set plot properties.
        :returns: Handle to plot

        """
        # Handle legend kwargs
        kwargs, legkwargs = _kwtolegkw(kwargs)

        if self.dimension == 3:
            if boxlength is None:
                boxlength = 2
            wrapped_plot = _axes_decorator_3d(self._plot)
        else:
            if boxlength is None:
                boxlength = 4
            wrapped_plot = _axes_decorator(self._plot)
        wrapped_plot(periodic=periodic, boxlength=boxlength, sym_center=sym_center,
                     coord_idx=coord_idx, plot_nearest_neighbours=plot_nearest_neighbours,
                     nearest_neighbour_color=nearest_neighbour_color, ax=ax, **kwargs)


    def _plot(self, periodic=False, boxlength=2, sym_center=True, coord_idx=False, plot_nearest_neighbours=True,
              nearest_neighbour_color=None, wigner_seitz=False, plot_simulation_torus=True,
              ax=None, **kwargs):

        if StrictVersion(matplotlib.__version__) < StrictVersion('1.5.0'):
            colors = plt.rcParams['axes.color_cycle']
        else:
            colors = [x['color'] for x in plt.rcParams['axes.prop_cycle']]

        # create Torus boundaries
        if not self._opencluster:
            if wigner_seitz:
                unitcell_edges_to_plot = self.wigner_seitz_edges
                unitcell_faces_to_plot = self.wigner_seitz_faces
            else:
                unitcell_edges_to_plot = np.zeros((2**self.dimension, self.dimension))
                for idx, i in enumerate(itertools.product([0,1],repeat=self.dimension)):
                    unitcell_edges_to_plot[idx,:] = np.dot(self.simulation_torus.T, np.array(i))
                if self.dimension == 2:
                    unitcell_edges_to_plot = unitcell_edges_to_plot[[0,1,3,2]]
                    unitcell_faces_to_plot = [[0,1], [1,2], [2,3], [3,0]]
                if self.dimension == 3:
                    unitcell_faces_to_plot = [[0,2,6,4], [1,3,7,5], [0,1,5,4], [0,1,3,2], [2,3,7,6], [4,5,7,6]]


            # Plot unitcell boundary
            if plot_simulation_torus:
                if self.dimension is 2:
                    polygon = Polygon(np.array(unitcell_edges_to_plot), True)
                    p = PatchCollection([polygon], alpha=0.25)
                    p.set_facecolor((0.2,0.2,0.2, 1))
                    p.set_edgecolor((0,0,0, 1))
                    ax.add_collection(p)

                if self.dimension is 3:
                    for face in unitcell_faces_to_plot:
                        collection = Poly3DCollection([(unitcell_edges_to_plot[face]).tolist()])
                        collection.set_facecolor((0,1,0, 0.1))
                        ax.add_collection3d(collection)

        if self._is_infinite:
            repeat_inf = 0
            for i in itertools.product([0,1],repeat=self.dimension):
                repeat_inf = int(max(repeat_inf, np.max(np.abs(np.linalg.solve(self.unitcell,boxlength*np.array(i)))) ))

            coordinates = np.zeros(((repeat_inf*2+1)**self.dimension*self._n_basiscoordinates,self.dimension))
            ctr = 0
            for i in itertools.product(range(-repeat_inf,repeat_inf+1),repeat = self.dimension):
                for basiscoord in self.basiscoordinates:
                    coord = np.dot(i, self.unitcell) + basiscoord
                    if np.all(coord<=boxlength) and np.all(coord>=0):
                        coordinates[ctr] = coord
                        ctr += 1
            coordinates = coordinates[:ctr]

        else:
            if not wigner_seitz:
                coordinates = self.coordinates
            else:
                coordinates = self.coordinates_wigner_seitz

        # Plot periodic continuation
        if periodic:
            # Get shift vectors
            vecs = []
            if wigner_seitz:
                for face in unitcell_faces_to_plot:
                    vecs.append(2.*np.average(unitcell_edges_to_plot[face],axis=0))
            else:
                vecs = list(np.vstack((self.simulation_torus, -self.simulation_torus)))

            vecs_combinations = []
            for (v1, v2) in itertools.combinations(vecs, 2):
                vecs_combinations.append(v1 + v2)
            vecs = unique_rows(np.array(vecs + vecs_combinations))

            # Apply translations to coordinates and store
            newcoords = 1.*coordinates
            for vec in vecs:
                if not np.allclose(vec, np.zeros_like(vec)):
                    newcoords = np.vstack((newcoords, coordinates + vec))
            coordinates = newcoords

        # Plot nearest neighbours
        if plot_nearest_neighbours:
            distance_matrix = scipy.spatial.distance_matrix(coordinates, coordinates)
            nearest_distance = np.min(distance_matrix[distance_matrix>1e-6]) + 1e-6
            kdtree_coordinates = scipy.spatial.KDTree(coordinates)
            ball_tree = kdtree_coordinates.query_ball_tree(kdtree_coordinates, nearest_distance)

            if nearest_neighbour_color == None:
                nearest_neighbour_color = colors[1]

            for idx, neighbours in enumerate(ball_tree):
                neighbours = np.array(neighbours)
                for nb_idx in neighbours[neighbours>idx]:
                    if self.dimension is 1:
                        ax.plot(coordinates[idx], coordinates[nb_idx], "-",color=nearest_neighbour_color,
                                **kwargs)
                    if self.dimension is 2:
                        ax.plot([coordinates[idx,0], coordinates[nb_idx,0]],
                                [coordinates[idx,1], coordinates[nb_idx,1]], "-",color=nearest_neighbour_color,
                                **kwargs)
                    if self.dimension is 3:
                        ax.plot([coordinates[idx,0], coordinates[nb_idx,0]],
                                [coordinates[idx,1], coordinates[nb_idx,1]],
                                [coordinates[idx,2], coordinates[nb_idx,2]], "-",color=nearest_neighbour_color,
                                **kwargs)

        # Plot Points
        if self.dimension is 1:
            ax.plot(coordinates, np.zeros_like(coordinates),"o",color=colors[0], **kwargs)
        if self.dimension is 2:
            ax.plot(coordinates[:self.n_sites,0], coordinates[:self.n_sites,1],"o",color=colors[0], **kwargs)
            ax.plot(coordinates[self.n_sites:,0], coordinates[self.n_sites:,1],"o",color=[.8,.8,.8], **kwargs)
        if self.dimension is 3:
            ax.plot(coordinates[:self.n_sites,0], coordinates[:self.n_sites,1], coordinates[:self.n_sites,2],
                    "o", color=colors[0], **kwargs)
            ax.plot(coordinates[self.n_sites:,0], coordinates[self.n_sites:,1], coordinates[self.n_sites:,2],
                    "o", color=[.8,.8,.8], **kwargs)

        #Plot sym_center
        if self.dimension==2 and sym_center:
            ax.plot(self.sym_center[0], self.sym_center[1], 'xk')


        #Plot coordinates index
        if coord_idx==True:
            if self.dimension==1:
                for i,c in enumerate(coordinates):
                    ax.text(c,0,i)
            if self.dimension==2:
                for i,c in enumerate(coordinates):
                    ax.text(c[0],c[1],i)
            else:
                pass

        #limits
        ax.set_aspect('equal')
        if not self._opencluster:
            if self.dimension is 2:
                ydist = np.max(unitcell_edges_to_plot[:,1]) - np.min(unitcell_edges_to_plot[:,1])
                ax.set_ylim([np.min(unitcell_edges_to_plot[:,1]) - 0.05*ydist,
                             np.max(unitcell_edges_to_plot[:,1]) + 0.05*ydist])
            if self.dimension is 1 or 2:
                xdist = np.max(unitcell_edges_to_plot[:,0]) - np.min(unitcell_edges_to_plot[:,0])
                ax.set_xlim([np.min(unitcell_edges_to_plot[:,0]) - 0.05*xdist,
                             np.max(unitcell_edges_to_plot[:,0]) + 0.05*xdist])
        else:
            if self.dimension is 2:
                ydist = np.max(self.coordinates[:,1]) - np.min(self.coordinates[:,1])
                ax.set_ylim([np.min(self.coordinates[:,1]) - 0.05*ydist,
                             np.max(self.coordinates[:,1]) + 0.05*ydist])
            if self.dimension is 1 or 2:
                xdist = np.max(self.coordinates[:,0]) - np.min(self.coordinates[:,0])
                ax.set_xlim([np.min(self.coordinates[:,0]) - 0.05*xdist,
                             np.max(self.coordinates[:,0]) + 0.05*xdist])

        ax.set_xlabel(r'$x$')
        ax.set_ylabel(r'$y$')

        return ax



    def plot_brillouinzone(self, little_groups=True, shading_color=None, plot_reciprocal_vecs=False,
                           plot_reciprocal_lattice=False, legend=True, ax=None, **kwargs):
        """
        Creates a plot of the Brillouin zone of the lattice, if simulation torus is defined
        the k points resolved by this torus are plotted as well.

        High-symmetry points of the Brillouinzone are plotted together with their names. Until now only for Square, hexagonal and rectangular Brillouin zones.

        :type ax: Axes object
        :param ax: Axes for plotting, **optional**. Default: Create new figure and axes
        :type little_groups: bool
        :param little_groups: Plot the reduced k-points and the corresponding little groups. **Optional**.
        :type shading_color: string
        :param shading_color: defines the color in which the brillouin zone is shaded, optional, default: None
        :type plot_reciprocal_vecs: Bool
        :param plot_reciprocal_vecs: If True, reciprocal lattice vectors are plotted. **Optional**. Default: False
        :type plot_reciprocal_lattice: Bool
        :param plot_reciprocal_lattice: If True, the reciprocal lattice is plotted. **Optional**. Default: False
        :type legend: Bool
        :param legend: If True, a legend is shown indicating the little groups. **Optional**. Default: True
        :type kwargs: *keyword arguments*
        :param kwargs: The kwargs can be used to set plot properties.
        :returns: Handle to plot
        """
        if self._opencluster:
            raise ValueError('Cannot plot a Brillouin zone for a non-periodic cluster!')

        if self.dimension == 3:
            wrapped_plot = _axes_decorator_3d(self._plot_brillouinzone)
        else:
            wrapped_plot = _axes_decorator(self._plot_brillouinzone)
        wrapped_plot(little_groups=little_groups, shading_color=shading_color,
                     plot_reciprocal_vecs=plot_reciprocal_vecs,
                     plot_reciprocal_lattice=plot_reciprocal_lattice, plot_legend=legend, ax=ax, **kwargs)



    def _plot_brillouinzone(self, little_groups=True, shading_color=None,
                            plot_reciprocal_vecs=False, plot_reciprocal_lattice=False,
                            plot_legend=True, ax=None, plot_k_space=True, **kwargs):

        if StrictVersion(matplotlib.__version__) < StrictVersion('1.5.0'):
            colors = plt.rcParams['axes.color_cycle']
        else:
            colors = [x['color'] for x in plt.rcParams['axes.prop_cycle']]

        ax.set_aspect('equal')

        # Handle legend kwargs
        kwargs, legkwargs = _kwtolegkw(kwargs)

        # Plot BZ boundary
        if self.dimension is 2:
            for face in self.brillouin_zone_faces:
                ax.plot(self.brillouin_zone_edges[[face[0],face[1]],0]/np.pi,
                        self.brillouin_zone_edges[[face[0],face[1]],1]/np.pi, color=colors[0])

            polygon = Polygon(np.array(self.brillouin_zone_edges)/np.pi, True)

            p = PatchCollection([polygon], alpha=0.2)
            ax.add_collection(p)

        if self.dimension is 3:
            for face in self.brillouin_zone_faces:
                collection = Poly3DCollection([(self.brillouin_zone_edges[face]/np.pi).tolist()])
                collection.set_facecolor((0, 0, 1, 0.1))
                ax.add_collection3d(collection)

        newedges = np.zeros((1,self.dimension))
        for face in self.brillouin_zone_faces:
            newedges = np.vstack((newedges, self.brillouin_zone_edges[face]))
        plotwidths = np.max(np.abs(newedges), axis=0)*1.15/np.pi

        ax.set_xlabel(r"$k_x/\pi$")
        #ax.set_xlim(-plotwidths[0], plotwidths[0])
        if self.dimension is 2 or 3:
            ax.set_ylabel(r"$k_y/\pi$")
            #ax.set_ylim(-plotwidths[1], plotwidths[1])
        if self.dimension is 3:
            ax.set_zlabel(r"$k_z/\pi$")
            ax.set_zlim(-plotwidths[2], plotwidths[2])

        # Plot k points if simulation torus is defined
        if plot_k_space:
            if self.k_space is not None:
                if self.dimension is 2:
                    ax.plot(self.k_space[:,0]/np.pi, self.k_space[:,1]/np.pi,"*", c='.5', **kwargs)
                elif self.dimension is 3:
                    ax.plot(self.k_space[:,0]/np.pi, self.k_space[:,1]/np.pi, self.k_space[:,2]/np.pi, "*",
                            c='.5', **kwargs)

        #Plot irreps
            if self.little_groups is not None and self.dimension==2:
                #Plot fixed high-symm points for the infinite lattice_type
                if self.k_space is None:
                    for name in self._high_symm_points:
                        if 'Gamma' in name or 'Sigma' in name or 'Delta' in name:
                            highsym_text = '$\\' + name + '$'
                        else:
                            highsym_text = '$' + name + '$'

                        for k in self._high_symm_points[name]:
                            ax.plot(k[0], k[1], 'xk')
                            ax.text(k[0], k[1], highsym_text, fontsize=16, weight='bold')

                #Plot other high-sym points
                plotmarkers = {'C1': 'ob', 'C2':'db', 'C3':'^b', 'C4':'sb', 'C6':'Hb', 'D1': 'or',
                        'D2':'dr', 'D3':'^r', 'D4':'sr', 'D6':'Hr'}
                legs = []
                leglabels = []
                count_not_highsym = 0
                for lg in self.little_groups:
                    ploth = ax.plot(lg['k'][0]/np.pi, lg['k'][1]/np.pi, plotmarkers[lg['little_group_name']], ms=16)
                    if not lg['high_sym_point']==None:
                        #Make names latex style
                        if 'Gamma' in lg['high_sym_point'] or 'Sigma' in lg['high_sym_point'] or 'Delta' in lg['high_sym_point']:
                            highsym_text = '$\\' + lg['high_sym_point'] + '$'
                        else:
                            highsym_text = '$' + lg['high_sym_point'] + '$'

                        ax.text(lg['k'][0]/np.pi, lg['k'][1]/np.pi, highsym_text, fontsize=16, weight='bold')

                    else:
                        ax.text(lg['k'][0]/np.pi, lg['k'][1]/np.pi, '$'+str(count_not_highsym)+'$', fontsize=16, weight='bold')
                        count_not_highsym += 1

                    legs.append(ploth[0])
                    leglabels.append(lg['little_group_name'])

                #Unique legend
                if plot_legend:
                    leglabels,idx = np.unique(leglabels, return_index=True)
                    legs = np.array(legs)[idx]
                    ax.legend(legs, leglabels, **legkwargs)

                #ax.set_title(r'Symmetry center = $(%s,%s)$' %(self.sym_center[0], self.sym_center[1]))

            elif self.little_groups is not None and self.dimension==3:
                ax.plot(self.k_wedge[:,0]/np.pi, self.k_wedge[:,1]/np.pi, self.k_wedge[:,2]/np.pi, "o",
                                                    c='r', **kwargs)

            ax.set_xlabel(r"$k_x/\pi$")

            ax.set_xlim(-plotwidths[0], plotwidths[0])
            if self.dimension is 2 or 3:
                ax.set_ylabel(r"$k_y/\pi$")
                ax.set_ylim(-plotwidths[1], plotwidths[1])
            if self.dimension is 3:
                ax.set_zlabel(r"$k_z/\pi$")
                ax.set_zlim(-plotwidths[2], plotwidths[2])

        return ax



    def _get_high_symm_points(self, infinite=False):
        """
        Check which kpoints are high symmetry points in the given Brillouinzone and give their name.

        :type infinite: Bool
        :param infinite: If true, infinite lattice is assumed.
        """

        #Vertex coordinates
        coords = self.brillouin_zone_edges
        nedges = len(coords)

        #BZ edge vectors
        vecs = np.zeros([nedges,self.dimension])
        for i in range(nedges):
            vec = coords[(i+1)%nedges] - coords[i]
            vecs[i,:]=vec

        #Compute lengths of edge-vectors and cos(angles) between them
        lengs = np.zeros(nedges)
        cangles = np.zeros(nedges)
        for i in range(len(vecs)):
            lengs[i] = np.linalg.norm(vecs[i])
            cangles[(i+1)%nedges] = np.abs(np.dot(vecs[i]/np.linalg.norm(vecs[i]),\
                                                      vecs[(i+1)%nedges]/np.linalg.norm(vecs[(i+1)%nedges]) ))

        #Check if square
        if nedges==4 and np.all(np.abs(lengs-lengs[0])<1e-10) and np.all(np.abs(cangles)<1e-10):
            bzform = 'square'
        #Check if hexagon
        elif nedges==6 and np.all(np.abs(lengs-lengs[0])<1e-10) and np.all(np.abs(cangles-.5)<1e-10):
            bzform = 'hexagon'
        #Check if rectangular
        elif nedges==4 and (np.abs(lengs[2]-lengs[0])<1e-10 and np.abs(lengs[3]-lengs[1])<1e-10) and np.all(np.abs(cangles)<1e-10):
            bzform = 'rectangle'
        else:
            bzform = None


        #high-symmetry points with fixed locations -> they are also used for infinite lattices
        self._high_symm_points = {} #: coordinates and names of the high symmetry points of the lattice with fixed locations
        #Gamma-point
        self._high_symm_points['Gamma'] = np.array([[0,0]])

        if bzform=='square':
            self._high_symm_points['M'] = coords #Corners of BZ
            self._high_symm_points['X'] = coords + vecs/2. #centers of edges

        elif bzform=='rectangle':
            self._high_symm_points['M'] = coords #Corners of BZ
            #find short sites to distinguish X,X'
            shortpos = np.argmin(np.linalg.norm(vecs, axis=1))
            shortpos = np.array([shortpos, (shortpos+2)%4])
            longpos = (shortpos+1)%4
            self._high_symm_points['X'] = coords[shortpos] + vecs[shortpos]/2.
            self._high_symm_points["X'"] = coords[longpos] + vecs[longpos]/2.

        elif bzform=='hexagon':
            self._high_symm_points['K'] = coords  #Corners of BZ
            self._high_symm_points['M'] = coords + vecs/2. #centers of edges

        if not infinite:
            #Check the self.k_wedge if they are high-symmetry points
            high_symm_names = [None]*(len(self.k_wedge))
            for i, kpoint in enumerate(self.k_wedge):
                #Check fixed high-symm points
                high_symm_found = False
                for name in self._high_symm_points:
                    if np.any(np.linalg.norm(self._high_symm_points[name]-kpoint, axis=1)<1e-10):
                        high_symm_names[i] = name
                        high_symm_found = True
                        break

                #Other high_symm points which are not fixed on locations
                if not high_symm_found:
                    if bzform=='square':
                        #Check if kpoint vector is parallel to the vectors to the edges etc.
                        if np.any(np.abs(np.cross(self._high_symm_points['X'],kpoint, axisa=1))<1e-10):
                            high_symm_names[i] = 'Delta'
                        elif np.any(np.abs(np.cross(self._high_symm_points['M'],kpoint, axisa=1))<1e-10):
                            high_symm_names[i] = 'Sigma'
                        elif np.any(np.abs(np.cross(self._high_symm_points['M']-self._high_symm_points['X'], kpoint-self._high_symm_points['X'],axisa=1))<1e-10):
                            high_symm_names[i] = 'Z'

                    if bzform=='rectangle':
                        #Check if kpoint vector is parallel to the vectors to the edges etc.
                        if np.any(np.abs(np.cross(self._high_symm_points['X'],kpoint, axisa=1))<1e-10):
                            high_symm_names[i] = 'Delta'
                        elif np.any(np.abs(np.cross(self._high_symm_points["X'"],kpoint, axisa=1))<1e-10):
                            high_symm_names[i] = "Delta'"
                        elif np.any(np.abs(np.cross(self._high_symm_points['M'][shortpos]-self._high_symm_points['X'], kpoint-self._high_symm_points['X'],axisa=1))<1e-10):
                            high_symm_names[i] = 'Z'
                        elif np.any(np.abs(np.cross(self._high_symm_points['M'][longpos]-self._high_symm_points["X'"], kpoint-self._high_symm_points["X'"],axisa=1))<1e-10):
                            high_symm_names[i] = "Z'"

                    if bzform=='hexagon':
                        #Check if kpoint vector is parallel to the vectors to the edges etc.
                        if np.any(np.abs(np.cross(self._high_symm_points['K'],kpoint, axisa=1))<1e-10):
                            high_symm_names[i] = 'X'
                        elif np.any(np.abs(np.cross(self._high_symm_points['M'],kpoint, axisa=1))<1e-10):
                            high_symm_names[i] = 'Y'
                        elif np.any(np.abs(np.cross(self._high_symm_points['K']-self._high_symm_points['M'], kpoint-self._high_symm_points['M'],axisa=1))<1e-10):
                            high_symm_names[i] = 'Z'

            #Make high-symm-names unique by adding numbers
            names_unique = np.unique(high_symm_names)
            self.unique_high_symm_points = [name for name in names_unique if name is not None] #: Names of all high_symmetry points without indices. Each name is represented only once.

            for name in names_unique:
                if not name==None:
                    idx = np.argwhere(np.array(high_symm_names)==name)
                    if len(idx)>1:
                        for n,i in enumerate(idx):
                            high_symm_names[int(i)] += '_%i' %(n)

            return high_symm_names


#######################################################################
# Create all possible lattices with a defined shape and number of sites
#######################################################################
def get_finite_lattices(lattice_type, n_sites, lattice='None', showplots=True):
    """
    .. versionadded:: 1.0.x

    Create all distinct lattices with a defined shape and number of sites.

    :type lattice_type: str
    :param lattice_type: Define the shape of the lattice. The following shapes are implemented right now: 'Square', 'Triangular', 'Honeycomb', 'Kagome', 'Squagome', 'None'
    :type n_sites: int
    :param n_sites: Number of lattice sites
    :type lattice: :class:`quantipy.Lattice`
    :param lattice: If lattice_type is not given or 'None', this parameter is used to define an arbitrary lattice. A :class:`quantipy.Lattice` object must be given.
    :type showplots: Bool
    :param showplots: If True, the lattices are directly plotted. **Optional**. Default: True
    :rtype: List of :class:`quantipy.Lattice` objects
    :returns: All distinct lattices (up to rotations etc.) with given number of lattice sites. Sorted by their maximal point group symmetry. Highest symmetry first.
    """

    # Create the infinite lattice
    if lattice_type=='Square':
        lattfunc = Square
    elif lattice_type=='Triangular':
        lattfunc = Triangular
    elif lattice_type=='Honeycomb':
        lattfunc = Honeycomb
    elif lattice_type=='Kagome':
        lattfunc = Kagome
    elif lattice_type=='Squagome':
        lattfunc = Squagome
    else:
        if not lattice==None:
            latt = lattice
        else:
            raise ValueError('You have to use a suitable lattice_type or define a lattice instance')

    latt = lattfunc()

    a_array = np.array([latt.a1,latt.a2])
    n_basis = latt._n_basiscoordinates
    #Volume basiscell
    Vez = np.abs(np.linalg.det(a_array))
    Mused = []

    #loop through all possibilities in utlf form. M is the utlf matrix defining t1,t2
    for i,j in itertools.product(range(1,n_sites/n_basis+1),repeat=2):
        for k in range(j):
            M = np.array([[i,k],[0,j]])
            t1t2array = np.dot(M,a_array)
            Vsim = np.abs(np.linalg.det(t1t2array)) #Volume simulation cell
            #check if Vsim ok
            if np.abs(round(Vsim/Vez) - Vsim/Vez) < 1e-10:
                sites = round(Vsim/Vez)*n_basis #2 atoms in basiscell
            else:
                raise ValueError('Vsim is not an integer multiple of Vez')

            if sites==n_sites:
                if len(Mused)==0:
                    Mused.append(M)
                else:
                    #Check if point group operations create an already existing lattice
                    Mthere = False
                    for sym in latt.symmetries['rotations']:
                        sym_real = np.dot(np.dot(np.linalg.inv(latt.unitcell),sym),latt.unitcell)
                        for Mu in Mused:
                            #U = C'.inv(C P^T)
                            U = np.dot(np.dot(Mu,a_array),np.linalg.inv(np.dot(np.dot(M,a_array),sym_real.T)))
                            #Check if U is unimodular
                            if np.max(np.abs(U-np.round(U))) < 1e-12 and np.round(np.linalg.det(U),decimals=12) in [-1,1]:
                                Mthere = True
                                break

                        if Mthere:
                            break
                    if not Mthere:
                        Mused.append(M)

    #Compact form for M matrices -> try to find a better (mathematical) solution
    Mcompact = []
    for M in Mused:
        minnorm = 10000
        Umin = []
        Mmin = []
        for a,b,c in itertools.product(range(0,6)+range(-5,0), repeat=3):
            if not a==0:
                for d in [(1.+b*c)/a, (-1.+b*c)/a]:
                    if np.abs(d-round(d))<1e-12:
                        U = np.array([[a,b],[c,d]])
                        Mnew = np.dot(U,M)
                        newnorm = np.linalg.norm(Mnew[0,:]) + np.linalg.norm(Mnew[1,:])
                        if newnorm<minnorm:
                            minnorm=newnorm
                            Umin = U
                            Mmin = Mnew

        Mcompact.append(Mmin)


    #Create the lattices
    all_lattices = []
    for M in Mcompact:
        latt = lattfunc(simulation_torus_matrix=M)
        all_lattices.append(copy.deepcopy(latt))


    #Sort the lattices. Highest symmetries first.
    #get groupnames of max symmetry
    symgroupnames = [None]*len(all_lattices)
    for idx,lattice in enumerate(all_lattices):
        symgroupnames[idx] = lattice.pointgroup[::-1]  #Reverse the groupnames to sort them easily
    #sorting
    sortidx = np.argsort(symgroupnames)[::-1]
    symgroupnames = np.array(symgroupnames)[sortidx]
    symgroupnames = map(lambda x: x[::-1],symgroupnames) #Reverse the groupnames again properly
    all_lattices = np.array(all_lattices)[sortidx]

    # Plot the lattices
    if showplots==True:
        for lattplot in all_lattices:
            fig, (ax1,ax2) = plt.subplots(1,2)
            lattplot.plot(ax=ax1, periodic=False)
            ax1.plot([0,lattplot.t1[0]],[0,lattplot.t1[1]],'k')
            ax1.plot([0,lattplot.t2[0]],[0,lattplot.t2[1]],'k')
            lattplot.plot_brillouinzone(ax=ax2)
            ax2.set_title('')
            ax2.set_xlabel(r'$k_x$')
            ax2.set_ylabel(r'$k_y$')
            plt.suptitle(r'$N=%i$' %(lattplot.n_sites), fontsize=20)
            plt.tight_layout(rect=[0,0,1,.95])

    return all_lattices



def get_all_finite_lattices(lattice_type, max_sites, lattice=None):
    """
    .. versionadded:: 1.0.x

    Get the t1t2 arrays and their description in utlf form for all distinct lattices of a given type up to a maximum number of sites.

    :type lattice_type: str
    :param lattice_type: Define the shape of the lattice. The following shapes are implemented right now: 'Square', 'Triangular', 'Honeycomb', 'Kagome', 'Squagome', 'None'
    :type max_sites: int
    :param max_sites: Maximum number of lattice sites.
    :type lattice: :class:`quantipy.Lattice`
    :param lattice: If lattice_type is not given or 'None', this parameter is used to define an arbitrary lattice. A :class:`quantipy.Lattice` object must be given.
    :rtype: dicts
    :returns: Matrices in utlf form describing the simulation torii; matrices describing the same lattices with shortest possible simulation torus vectors; simulation torii building the lattices
    """

    # Create the infinite lattice
    if lattice_type=='Square':
        latt = Square()
    elif lattice_type=='Triangular':
        latt = Triangular()
    elif lattice_type=='Honeycomb':
        latt = Honeycomb()
    elif lattice_type=='Kagome':
        latt = Kagome()
    elif lattice_type=='Squagome':
        latt = Squagome()
    else:
        if not lattice==None:
            latt = lattice
        else:
            raise ValueError('You have to use a suitable lattice_type or define a lattice instance')


    a_array = np.array([latt.a1,latt.a2])
    n_basis = latt._n_basiscoordinates
    #Volume basiscell
    Vez = np.abs(np.linalg.det(a_array))

    #initialize Mused dictionary
    Mused = {}
    for i in range(max_sites/n_basis+1):
        Mused[i*n_basis]=[]

    #loop through all possibilities in utlf form. M is the utlf matrix defining t1,t2
    for i,j in itertools.product(range(1,max_sites/n_basis+1), repeat=2):
        for k in range(j):
            M = np.array([[i,k],[0,j]])
            t1t2array = np.dot(M,a_array)
            Vsim = np.abs(np.linalg.det(t1t2array)) #Volume simulation cell
            #check if Vsim ok
            if np.abs(round(Vsim/Vez) - Vsim/Vez) < 1e-10:
                sites = round(Vsim/Vez)*n_basis
            else:
                raise ValueError('Vsim is not an integer multiple of Vez')

            if sites <= max_sites: #otherwise not all possible lattices available
                if len(Mused[sites])==0:
                    Mused[sites].append(M)
                else:
                    #Check if point group operations create an already existing lattice
                    Mthere = False
                    for sym in latt.symmetries['rotations']:
                        sym_real = np.dot(np.dot(np.linalg.inv(latt.unitcell),sym),latt.unitcell)
                        for Mu in Mused[sites]:
                            #U = C'.inv(C P^T)
                            U = np.dot(np.dot(Mu,a_array),np.linalg.inv(np.dot(np.dot(M,a_array),sym_real.T)))
                            #Check if U is unimodular
                            if np.max(np.abs(U-np.round(U))) < 1e-12 and np.round(np.linalg.det(U),decimals=12) in [-1,1]:
                                Mthere = True
                                break

                        if Mthere:
                            break

                    if not Mthere:
                        Mused[sites].append(M)


    #Compact form for M matrices -> try to find a better (mathematical) solution
    Mcompact = {}
    t1t2arrays = {}
    for key in Mused:
        Mcompact[key] = []
        t1t2arrays[key] = []
        for M in Mused[key]:
            minnorm = 10000
            Umin = []
            Mmin = []
            for a,b,c in itertools.product(range(0,6)+range(-5,0), repeat=3):
                if not a==0:
                    for d in [(1.+b*c)/a, (-1.+b*c)/a]:
                        if np.abs(d-round(d))<1e-12:
                            U = np.array([[a,b],[c,d]])
                            Mnew = np.dot(U,M)
                            newnorm = np.linalg.norm(Mnew[0,:]) + np.linalg.norm(Mnew[1,:])
                            if newnorm<minnorm:
                                minnorm=newnorm
                                Umin = U
                                Mmin = Mnew

            Mcompact[key].append(Mmin)
            t1t2arrays[key].append(np.dot(Mmin,a_array))

    return Mused, Mcompact, t1t2arrays

###################################
# Shortcuts for often used lattices
###################################

def Chain(L, a=1, **kwargs):
    """
    Generate a periodic Chain

    :param L: Number of sites in the chain
    :type L: int
    :param a: unit cell spacing
    :type a: float
    """
    unit_cell = np.array([[a,0],[0,a*10]])
    simulation_torus = np.array([[L*a,0],[0,a*10]])
    lattice = Lattice(unitcell=unit_cell, simulation_torus=simulation_torus,
            sym_center=[L*a/2., 0], maxpg=['C1','C2'], **kwargs)
    return lattice


def Square(a=1.0, simulation_torus=None, **kwargs):
    """
    Generate a Square Lattice

    .. versionchanged:: 1.0.x

    The symmetry center is automatically set to obtain the maximum point-group.

    :param a: unit cell spacing
    :type a: float
    :param simulation_torus: Defines the vectors for the simulation torus, simulation_torus[0,:] describes
                             first vector of bounding box and simulation_torus[1,:] the second one
    :type simulation_torus: numpy.ndarray
    """
    unit_cell = np.array([[a,0.],[0.,a]])
    lattice = Lattice(unitcell=unit_cell, simulation_torus=simulation_torus, **kwargs)
    return lattice


def Triangular(a=1.0, simulation_torus=None, **kwargs):
    """
    Generate a Triangular Lattice

    .. versionchanged:: 1.0.x

    The symmetry center is automatically set to obtain the maximum point-group.

    :param a: unit cell spacing
    :type a: float
    :param simulation_torus: Defines the vectors for the simulation torus, simulation_torus[0,:] describes
                             first vector of bounding box and simulation_torus[1,:] the second one
    :type simulation_torus: numpy.ndarray
    """
    unit_cell = np.array([[a,0.],[0.5*a,a*np.sqrt(3.)/2.]])
    lattice = Lattice(unitcell=unit_cell, simulation_torus=simulation_torus, **kwargs)
    return lattice


def Honeycomb(a=2./np.sqrt(3), simulation_torus=None, **kwargs):
    """
    Generate a Honeycomb Lattice

    .. versionchanged:: 1.0.x

    The symmetry center is automatically set to obtain the maximum point-group.

    :param a: unit cell spacing
    :type a: float
    :param simulation_torus: Defines the vectors for the simulation torus, simulation_torus[0,:] describes
                             first vector of bounding box and simulation_torus[1,:] the second one
    :type simulation_torus: numpy.ndarray
    """
    unit_cell = np.array([[np.sqrt(3)*a/2., 3.*a/2.],[np.sqrt(3)*a,0.]])
    basis_coordinates = np.array([[0.,a],[0.,0.]])
    symmetry_center = np.array([np.sqrt(3)*a/2.,a/2.])
    lattice = Lattice(unitcell=unit_cell, basiscoordinates = basis_coordinates, simulation_torus=simulation_torus, sym_center=symmetry_center, **kwargs)
    return lattice


def Kagome(a=1.0, simulation_torus=None, **kwargs):
    """
    Generate a Kagome Lattice

    .. versionchanged:: 1.0.x

    The symmetry center is automatically set to obtain the maximum point-group.

    :param a: unit cell spacing
    :type a: float
    :param simulation_torus: Defines the vectors for the simulation torus, simulation_torus[0,:] describes
                             first vector of bounding box and simulation_torus[1,:] the second one
    :type simulation_torus: numpy.ndarray
    """
    unit_cell = np.array([[a,0.],[0.5*a,0.5*np.sqrt(3.)*a]])
    basis_coordinates = np.array([[0., 0.], [a*0.5,0.], [0.25*a, a*0.25*np.sqrt(3.)]])
    symmetry_center = np.array([3*a/4.,np.sqrt(3)*a/4.])
    lattice = Lattice(unitcell=unit_cell, basiscoordinates = basis_coordinates, simulation_torus=simulation_torus, sym_center=symmetry_center, **kwargs)
    return lattice


def Squagome(a=1.0, simulation_torus=None, **kwargs):
    """
    Generate a Squagome or Square Kagome Lattice

    .. versionchanged:: 1.0.x

    The symmetry center is automatically set to obtain the maximum point-group.

    :param a: unit cell spacing
    :type a: float
    :param simulation_torus: Defines the vectors for the simulation torus, simulation_torus[0,:] describes
                             first vector of bounding box and simulation_torus[1,:] the second one
    :type simulation_torus: numpy.ndarray
    """
    unit_cell = np.array([[a,0.],[0,a]])
    basis_coordinates = np.array([[0., 0.], [a*(1.0/(1.0 + np.sqrt(3))), 0.], [0., a*(1.0/(1.0 + np.sqrt(3)))],
                                  [a*(1.0/(1.0 + np.sqrt(3))), a*(1.0/(1.0 + np.sqrt(3)))],
                                  [a*((1.0 + np.sqrt(3)/2)/(1.0 + np.sqrt(3))), a*(0.5/(1.0 + np.sqrt(3)))],
                                  [a*(0.5/(1.0 + np.sqrt(3))), a*((1.0 + np.sqrt(3)/2)/(1.0 + np.sqrt(3)))]])
    symmetry_center = np.array([a*(1. + np.sqrt(3)/2.)/(1. + np.sqrt(3)), a*(1. + np.sqrt(3)/2.)/(1. + np.sqrt(3))])
    lattice = Lattice(unitcell=unit_cell, basiscoordinates = basis_coordinates, simulation_torus=simulation_torus, sym_center=symmetry_center, **kwargs)
    return lattice


def SquareOctagon(a=1.0, simulation_torus=None, **kwargs):
    """
    Generate a Square-Octagon Lattice

    .. versionchanged:: 1.1.x

    The symmetry center is automatically set to obtain the maximum point-group.

    :param a: unit cell spacing
    :type a: float
    :param simulation_torus: Defines the vectors for the simulation torus, simulation_torus[0,:] describes
                             first vector of bounding box and simulation_torus[1,:] the second one
    :type simulation_torus: numpy.ndarray
    """
    unit_cell = np.array([[a*(1+np.sqrt(2)),0],[0,a*(1+np.sqrt(2))]])
    basis_coordinates = np.array([[a/np.sqrt(2),0],[-a/np.sqrt(2),0],[0,a/np.sqrt(2)],[0, -a/np.sqrt(2)]])
    symmetry_center = np.array([0,0])
    lattice = Lattice(unitcell=unit_cell, basiscoordinates = basis_coordinates, simulation_torus=simulation_torus, sym_center=symmetry_center, **kwargs)
    return lattice


def Cubic(a=1.0, simulation_torus=None, **kwargs):
    """
    Generate a Cubic Lattice

    .. versionchanged:: 1.1.x

    The symmetry center is automatically set to obtain the maximum point-group.

    :param a: unit cell spacing
    :type a: float
    :param simulation_torus: Defines the vectors for the simulation torus, simulation_torus[0,:] describes
                             first vector of bounding box and simulation_torus[1,:] the second one,
                             simulation_torus[2,:] the third one
    :type simulation_torus: numpy.ndarray
    """
    unit_cell = np.array([[a, 0., 0.],[0., a, 0.],[0., 0., a]])
    lattice = Lattice(unitcell=unit_cell, simulation_torus=simulation_torus, **kwargs)
    return lattice


def FCC(a=1.0, simulation_torus=None, **kwargs):
    """
    Generate a Face centered cubic Lattice

    .. versionchanged:: 1.1.x

    The symmetry center is automatically set to obtain the maximum point-group.

    :param a: unit cell spacing
    :type a: float
    :param simulation_torus: Defines the vectors for the simulation torus, simulation_torus[0,:] describes
                             first vector of bounding box and simulation_torus[1,:] the second one,
                             simulation_torus[2,:] the third one
    :type simulation_torus: numpy.ndarray
    """
    unit_cell = a/2.*np.array([[1., 0., 1.],[1., 1., 0.],[0., 1., 1.]])
    lattice = Lattice(unitcell=unit_cell, simulation_torus=simulation_torus, **kwargs)
    return lattice


def BCC(a=1.0, simulation_torus=None, **kwargs):
    """
    Generate a Body centered cubic Lattice

    .. versionchanged:: 1.1.x

    The symmetry center is automatically set to obtain the maximum point-group.

    :param a: unit cell spacing
    :type a: float
    :param simulation_torus: Defines the vectors for the simulation torus, simulation_torus[0,:] describes
                             first vector of bounding box and simulation_torus[1,:] the second one,
                             simulation_torus[2,:] the third one
    :type simulation_torus: numpy.ndarray
    """
    unit_cell = a/2.*np.array([[1., 1., -1.],[1., -1., 1.],[-1., 1., 1.]])
    lattice = Lattice(unitcell=unit_cell, simulation_torus=simulation_torus, **kwargs)
    return lattice


def Diamond(a=1.0, simulation_torus=None, **kwargs):
    """
    Generate a Diamond Lattice

    .. versionchanged:: 1.1.x

    The symmetry center is automatically set to obtain the maximum point-group.

    :param a: unit cell spacing
    :type a: float
    :param simulation_torus: Defines the vectors for the simulation torus, simulation_torus[0,:] describes
                             first vector of bounding box and simulation_torus[1,:] the second one,
                             simulation_torus[2,:] the third one
    :type simulation_torus: numpy.ndarray
    """
    unit_cell = a/2.*np.array([[1., 0., 1.],[1., 1., 0.],[0., 1., 1.]])
    basis_coordinates = a/4.*np.array([[0., 0., 0.], [1., 1., 1.]])
    lattice = Lattice(unitcell=unit_cell, basiscoordinates=basis_coordinates,
                      simulation_torus=simulation_torus, **kwargs)
    return lattice


def Pyrochlore(a=1.0, simulation_torus=None, **kwargs):
    """
    Generate a Pyrochlore Lattice

    .. versionchanged:: 1.1.x

    The symmetry center is automatically set to obtain the maximum point-group.

    :param a: unit cell spacing
    :type a: float
    :param simulation_torus: Defines the vectors for the simulation torus, simulation_torus[0,:] describes
                             first vector of bounding box and simulation_torus[1,:] the second one,
                             simulation_torus[2,:] the third one
    :type simulation_torus: numpy.ndarray
    """
    unit_cell = a/2.*np.array([[1., 0., 1.],[1., 1., 0.],[0., 1., 1.]])
    basis_coordinates = a/4.*np.array([[2., 2., 2.], [1., 1., 2.], [2., 1., 1.], [1., 2., 1.]])
    lattice = Lattice(unitcell=unit_cell, basiscoordinates=basis_coordinates,
                      simulation_torus=simulation_torus, **kwargs)
    return lattice



def Hyperhoneycomb(a=1.0, simulation_torus=None, **kwargs):
    """
    Generate a Hyperhoneycomb Lattice

    .. versionchanged:: 1.1.x

    The symmetry center is automatically set to obtain the maximum point-group.

    :param a: unit cell spacing
    :type a: float
    :param simulation_torus: Defines the vectors for the simulation torus, simulation_torus[0,:] describes
                             first vector of bounding box and simulation_torus[1,:] the second one,
                             simulation_torus[2,:] the third one
    :type simulation_torus: numpy.ndarray
    """
    unit_cell = a*np.array([[2., 4., 0.],[3., 3., 2.],[-1., 1., 2.]])
    basis_coordinates = a*np.array([[0., 0., 0.], [1., 1., 0.], [1., 2., 1.], [2., 3., 1.]])
    lattice = Lattice(unitcell=unit_cell, basiscoordinates=basis_coordinates,
                      simulation_torus=simulation_torus, **kwargs)
    return lattice
