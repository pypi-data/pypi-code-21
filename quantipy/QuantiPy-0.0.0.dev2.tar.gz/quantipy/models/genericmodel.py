# -*- coding: utf-8 -*-
"""
:file: genericmodel.py
:synopsis: module for defining and creating generic models on lattices
"""

import numpy as np
from scipy import linalg
import matplotlib
from matplotlib import rcParams
import itertools

from quantipy.lattice import Lattice
from quantipy.utils import _axes_decorator, _axes_decorator_3d, \
    unique_rows, _kwtolegkw, _map_to_simtorus
import quantipy.spglib.spglib
import quantipy.spglib.spglib2d
import quantipy.symmetries as symmetries
from distutils.version import StrictVersion


class GenericModel:
    """
    :class: GenericModel

    Class for describing generic models.
    """

    def __init__(self, lattice, OBC=False, maxpg=None):
        """
        :type lattice: QuantiPy Lattice object
        :param lattice: the lattice on which to define the tight binding model,
                        must have Bravais unit cell defined
        :type OBC: Boolean
        :param OBC: If True, open boundary conditions are used instead of PBC.
                    **Optional**. Default: False - Periodic boundary conditions
        :param maxpg: define the maximum point group elements as a list,
                      e.g. ["C1", "C4", "C2", "C4^3"]
        :type maxpg: list of strings
        """
        if not isinstance(lattice, Lattice):
            raise ValueError("GenericModel.lattice must be a "
                             + "QuantiPy Lattice class object")

        if maxpg != None and not all(isinstance(elem, basestring)
                                     for elem in maxpg):
            raise ValueError("GenericModel.maxpg must be a list of strings")

        self.lattice = lattice

        self.OBC = OBC
        if self.OBC and self.lattice.trans_sym:
            # Redo lattice
            lattkwargs = self.lattice._kwargs
            lattkwargs['trans_sym'] = False
            self.lattice = Lattice(**lattkwargs)

        if self.lattice._is_infinite:
            self.n_sites = None
        else:
            self.n_sites = lattice.n_sites
        self.dimension = lattice.dimension

        self._couplings_set = False
        self._couplings = []

        self._syms_computed = False  # allperms, irreps already computed?
        self.maxpg = maxpg

        self._allperms = None
        self._irreps = None
        self._irreps_computed = False
        
        self._modelfilename = None  # name of modelfile

        self._pointgroup = None
        self._finite_lattice_bonds = None
        self.little_groups = None

    def set_nb_interaction(self, nbdist, int_type='HB', coupling='J',
                           couplingvalue=1.):
        """
        Set interactions for nearest neighbours etc. on the lattice.
        These interactions are not directed.

        :type nbdist: int
        :param nbdist: neighbour distance - 0 for on-site potentials,
                       1 for nearest neighbour interactions, etc.
        :type int_type: string
        :param int_type: Interaction type recognized by QMSpinDyn. **Optional**.
        :type coupling: string
        :param coupling: Name of the coupling constant. **Optional**.
        :type couplingvalue: float
        :param couplingvalue: Value of the coupling, if a Dofile should
                              be created. **Optional**. Default: 1.0
        """
        if self.OBC:
            finite_lattice = self.lattice
        else:
            finite_lattice = \
                Lattice(unitcell=self.lattice.unitcell,
                        basiscoordinates=self.lattice.basiscoordinates,
                        simulation_torus_matrix=(nbdist + 1) *
                        np.eye(self.dimension))

        # compute different distances on lattice
        latticedist = np.array([])
        for coord in finite_lattice.coordinates:
            for bcoord in finite_lattice.basiscoordinates:
                latticedist = np.append(latticedist,
                                        np.linalg.norm(coord - bcoord))
        latticedist = np.unique(np.round(latticedist, decimals=8))

        bonddata = []
        if nbdist == 0:
            for b in range(len(self.lattice.basiscoordinates)):
                self._couplings.append({'cellshift':
                                        np.array([[0] * self.dimension]),
                                        'basis_sites': [b],
                                        'int_type': int_type,
                                        'coupling': coupling,
                                        'value': couplingvalue,
                                        'directed': False,
                                        'allowed_perms': None,
                                        'trans_repeat': True})
        else:
            for i, j in itertools.combinations(xrange(finite_lattice.n_sites),
                                               r=2):
                dist = np.linalg.norm(finite_lattice.coordinates[i] -
                                      finite_lattice.coordinates[j])
                if np.abs(dist - latticedist[nbdist]) < 1e-8:
                    if (finite_lattice._rel_indices[i]['basis'] <=
                            finite_lattice._rel_indices[j]['basis']):
                        order = [i, j]
                    else:
                        order = [j, i]

                    bondtmp = np.hstack(
                        [np.array(
                            finite_lattice._rel_indices[order[1]]['cell']) -
                         np.array(
                             finite_lattice._rel_indices[order[0]]['cell']),
                         finite_lattice._rel_indices[order[0]]['basis'],
                         finite_lattice._rel_indices[order[1]]['basis']])
                    bonddata.append(bondtmp)
            bonddata = unique_rows(np.array(bonddata))

            for b in bonddata:
                cellshift = np.array([np.zeros(self.dimension),
                                      b[:self.dimension]], dtype=int)
                basissites = b[self.dimension:]
                self._couplings.append({'cellshift': cellshift,
                                        'basis_sites': basissites,
                                        'int_type': int_type,
                                        'coupling': coupling,
                                        'value': couplingvalue,
                                        'directed': False,
                                        'allowed_perms': None,
                                        'trans_repeat': True})

        self._couplings_set = True
        self._syms_computed = False  # Recomputation of symmetries needed

    def set_long_range_interaction(self, function, max_nb_dist=None,
                                   int_type='HB', coupling='J'):
        """
        Set long-range 2-body interactions. The coupling values for the
        start-file are generated by the function!

        :type function: function
        :param function: Function f(r) depending on distance r which
                         describes the long-range couplings
                         (typically decaying)
        :type max_nb_dist: int
        :param max_nb_dist: Maximum distance in units of neighbours.
                            **Optional**. Default is infinity.
        :type int_type: string
        :param int_type: Interaction type recognized by QMSpinDyn.
                         **Optional**. :type coupling: string
        :param coupling: Name of the coupling constant. In the lattice
                         file 'lr' and the distance in units of neighbours
                         is added. **Optional**.
        """
        # Check if function is callable
        if not callable(function):
            raise ValueError('function must be a callable object!')

        if self.OBC:
            finite_lattice = self.lattice
        else:
            finite_lattice = Lattice(unitcell=self.lattice.unitcell,
                                     basiscoordinates=\
                                     self.lattice.basiscoordinates,
                                     simulation_torus_matrix=(nbdist + 1) *
                                     np.eye(self.dimension))

        # compute different distances on lattice
        latticedist = np.array([])
        for coord in finite_lattice.coordinates:
            for bcoord in finite_lattice.basiscoordinates:
                latticedist = np.append(
                    latticedist, np.linalg.norm(coord - bcoord))
        latticedist = np.unique(np.round(latticedist, decimals=8))

        # Remove value zero from latticedist
        latticedist = latticedist[1:]
        if max_nb_dist is not None:
            latticedist = latticedist[:max_nb_dist]

        # Compute coupling strengths
        couplings = np.zeros_like(latticedist)
        for i, r in enumerate(latticedist):
            couplings[i] = function(r)
        # print couplings

        for j, c in enumerate(couplings):
            self.set_nb_interaction(j + 1, int_type=int_type,
                                    coupling='%s%d' % (coupling, j),
                                    couplingvalue=c)

        self._couplings_set = True
        self._syms_computed = False  # Recomputation of symmetries needed
        
    def set_interaction(self, positions=None, basis_sites=None, cellshifts=None,
                        int_type='HB', coupling='J', directed=False,
                        allowed_perms=None, couplingvalue=1.,
                        trans_repeat=True):
        """
        Set general interactions on the lattice which are
        periodically continued throughout the lattice.

        :type positions: numpy.ndarray
        :param positions: Reference positions where the couplings should act on.
                          Specified as numpy array with each entry as:
                          [n_a1, n_a2, n_basis]. n_a1/2 define the unit-cell
                          position as :math:`$n_{a1} \mathbf{a_1} + n_{a2}
                          \mathbf{a_2}$`. :math:`$n_{basis}$` gives the number
                          of the basiscoordinate within the unit-cell.
        :type int_type: string
        :param int_type: Interaction type recognized by QMSpinDyn.
                         **Optional**. Default: 'HB'
        :type coupling: string
        :param coupling: Name of the coupling constant.
                         **Optional**. Default: 'J'
        :type directed: bool
        :param directed: If True, the bonds are directed from positions[0]
                         to positions[1] and so on. Take care of the correct
                         ordering of the positions array!
                         **Optional**. Default: False
        :type allowed_perms: np.ndarray
        :param allowed_perms: List of allowed permutations for the bonds
                              if they are directed and longer than 2.
                              **Optional**. Default: None
        :type couplingvalue: float
        :param couplingvalue: Value of the coupling, if a Dofile should
                              be created. **Optional**. Default: 1.0
        """

        if basis_sites is None and positions is None:
            raise ValueError("You must either set basis_sites or positions!")
        elif basis_sites is not None and positions is not None:
            raise ValueError("You must only set either basis_sites " +
                             "or positions!")
        elif positions is not None:
            positions = np.array(positions)
            if not positions.shape[1] == self.dimension + 1:
                raise ValueError("positions must be of shape (n,dimension+1)!")
            cellshifts = positions[:, :self.dimension]
            basis_sites = positions[:, -1]
        else:
            basis_sites = np.array(basis_sites)
            if cellshifts is not None:
                cellshifts = np.array(cellshifts)
                if (not cellshifts.shape[1] == self.dimension or
                        not cellshifts.shape[0] == len(basis_sites)):
                    raise ValueError("cellshifts must be of shape " +
                                     "(len(basis_sites),dimension)!")
            else:
                cellshifts = np.zeros([len(basis_sites), self.dimension])

        if not allowed_perms is None:
            if not allowed_perms.shape[1] == len(basis_sites):
                raise ValueError("Shape of allowed_perms not consistent " +
                                 "with bond size!")

        self._couplings.append({'cellshift': cellshifts,
                                'basis_sites': basis_sites,
                                'int_type': int_type,
                                'coupling': coupling,
                                'value': couplingvalue,
                                'directed': directed,
                                'allowed_perms': allowed_perms,
                                'trans_repeat': trans_repeat})
        self._couplings_set = True
        self._syms_computed = False  # Recomputation of symmetries needed

    def pointgroup(self):
        """
        Get the point group of the model

        :returns: the pointgroup of the model
        :rtype: string
        """
        if self._syms_computed:
            return self._pointgroup
        else:
            self._get_allowed_symmetries()
            return self._pointgroup

    def irreps(self):
        """
        Get irreducible representations of the model

        :returns: All Irreps, characters and allowed operations of 
                  the symmetry group.
        :rtype: OrderedDict
        """
        # get allowed syms and little groups for model
        if not self._syms_computed:
            self._get_allowed_symmetries()

        if not self._irreps_computed:
            self._irreps = symmetries._get_irreps(self.lattice, self._symmetries,
                                                  twod_to_oned=True)
            self._irreps_computed = True
            
        return self._irreps

    def irrep_names(self):
        """
        Get names of all irreducible representations of the model

        :returns: names of all irreps, characters and allowed operations 
                  of the symmetry group.
        :rtype: list of strings
        """
        irreps = self.irreps()
        return irreps.keys()

    def symmetries(self, irrep_name=None, return_bloch_factors=True):
        """
        Compute the lattice symmetries 

        :param irrep_name: name of the irreducible representation for which 
                           the symmetries are returned. **optional**.
                           Default: None (all symmetries are returned)
        :type irrep_name: string
        :param return_bloch_factors: flag whether also bloch factors of the
                                     irreducible representations are returned
        :type return_bloch_factors: boolean
        :returns: permutations of lattice sites defining the lattice symmetries,
                  if keyword return_bloch_factors is set True, also the 
                  blochfactors of the symmetry are returned
        :rtype: np.array, shape (#symmetries x #n_sites)
        """
        if not self._syms_computed:
            self._get_allowed_symmetries()

        translations = self.lattice.bravaiscoordinates - \
                       self.lattice.bravaiscoordinates[0]
        perms = symmetries._get_permutations(self.lattice.coordinates,
                                             self.lattice.unitcell,
                                             self.lattice.simulation_torus,
                                             translations,
                                             self._symmetries['rotations'],
                                             sym_center=self.lattice.sym_center)
        if irrep_name == None:
            return np.ascontiguousarray(perms, dtype = np.intc)
        else:
            irreps = self.irreps()
            if not irrep_name in irreps:
                raise ValueError("irrep_name not found aa irrep of the model." +
                                 " Use irrep_names to get a list of irreps")
            perms = np.ascontiguousarray(
                perms[irreps[irrep_name]["allowed_ops"]], dtype = np.intc)
            if return_bloch_factors:
                blochs = np.ascontiguousarray(
                    irreps[irrep_name]["phases"], dtype = np.complex128)
                return (perms, blochs)
            else:
                return perms
            
    
    
    def plot(self, closed_loops=False, interactions=None, rep_inf=4, ax=None,
             **kwargs):
        """
        Plots the lattice with specified interaction bonds.

        :type interactions: list of str
        :param interactions: int_types of interactions which should be plotted.
                             **Optional**. Default: Plot all interactions
        :type closed_loops: bool
        :param closed_loops: Close loops for interactions on more than
                             two bonds. **Optional**. Default: False
        :type rep_inf: int
        :param rep_inf: Repeat unit_cell of infinite lattice rep_inf
                        times to plot. **Optional**. Default=4.
        :param ax: Axes for plotting, **Optional**.
                   Default: Create new figure and axes
        :type ax: Axes object
        :type kwargs: *keyword arguments*
        :param kwargs: The kwargs can be used to set plot properties.
        :returns: Handles to plots
        """
        if self.dimension == 3:
            wrapped_plot = _axes_decorator_3d(self._plot)
        else:
            wrapped_plot = _axes_decorator(self._plot)

        wrapped_plot(closed_loops=closed_loops, interactions=interactions,
                     rep_inf=rep_inf, ax=ax, **kwargs)


    def plot_brillouinzone(self, **kwargs):
        """
        Creates a plot of the Brillouin zone of the model, if the
        model is finite the k points resolved by this torus are
        plotted as well.

        High-symmetry points of the Brillouinzone are plotted
        together with their names. Until now only for Square,
        hexagonal and rectangular Brillouin zones.

        :type ax: Axes object
        :param ax: Axes for plotting,
                   **optional**. Default: Create new figure and axes
        :type little_groups: bool
        :param little_groups: Plot the reduced k-points and the
                              corresponding little groups. **Optional**.
        :type shading_color: string
        :param shading_color: defines the color in which the brillouin
                              zone is shaded, optional, default: None
        :type plot_reciprocal_vecs: Bool
        :param plot_reciprocal_vecs: If True, reciprocal lattice vectors
                                     are plotted. **Optional**. Default: False
        :type plot_reciprocal_lattice: Bool
        :param plot_reciprocal_lattice: If True, the reciprocal
                                        lattice is plotted. **Optional**.
                                        Default: False
        :type legend: Bool
        :param legend: If True, a legend is shown indicating the
                       little groups. **Optional**. Default: True
        :type kwargs: *keyword arguments*
        :param kwargs: The kwargs can be used to set plot properties.
        :returns: Handle to plot
        """
        if not self._syms_computed:
            self._get_allowed_symmetries()

        self.lattice.plot_brillouinzone(**kwargs)

        
    def write(self, filename, sublattice_structure=None, write_comments=True,
              eccentricity=False, write_symmetry_info=True):
        """
        Write the model object to a file.

        :type filename: str
        :param filename: Filename of the file where the Lattice is saved!
        :type sublattice_structure: numpy array of ints, size
                (number of sublattices)x(lattice points per sublattice)
        :param sublattice_structure: Defines the sublattice structure
                                     of the lattice, can be used for MPI
                                     sublattice codes
        :type write_comments: Bool
        :param write_comments: If True, comment lines with further information
                               about the lattice are written.
                               **Optional**. Default: True
        :type write_symmetry_info: Bool
        :param write_symmetry_info: If True, little groups, symmetry
                                    permutations and phases are written to
                                    the file. **Optional**. Default: True
        :type eccentricity: Bool
        :param eccentricity: If True, eccentricity of the lattice is
                             computed and written to the file. **Optional**.
                             Default: False
        """
        np.set_printoptions(precision=16)

        if self.lattice._is_infinite:
            raise ValueError("Cannot write the model for an infinite " +
                             "lattice yet!")
        else:
            writelattice = self.lattice

        # Compute symmetry stuff
        if write_symmetry_info:
            irreps = self.irreps()
        else:
            # recompute symmetries if needed
            if not self._syms_computed:
                self._get_allowed_symmetries()

        writelattice.write(filename, sublattice_structure, write_comments,
                           eccentricity, write_sym_perms=False)

        # compute the couplings for the finite lattice
        self._get_finite_lattice_bonds(writelattice)

        # Get sublattice permutation and inverse
        if sublattice_structure is not None:
            if sublattice_structure.size != self.lattice.n_sites:
                raise ValueError("Invalid Sublattice Structure")
            n_sublattices = sublattice_structure.shape[0]
            sublattice_permutation = np.reshape(sublattice_structure,
                                                self.lattice.n_sites)
            sublattice_permutation_inverse = np.zeros(self.lattice.n_sites,
                                                      dtype=np.int)
            for i in range(self.lattice.n_sites):
                sublattice_permutation_inverse[sublattice_permutation[i]] = i
                assert i in sublattice_permutation

        # interaction bonds
        bondstrings = []
        for coupl in self._finite_lattice_bonds:
            bonds = coupl['bonds']
            if sublattice_structure is None:
                for b in bonds:
                    if isinstance(b, int):
                        bondstrings.append(("%s %s %i" % (coupl['int_type'],
                                                          coupl['coupling'],
                                                          b)))
                    else:
                        bondstrings.append(("%s %s " % (coupl['int_type'],
                                                        coupl['coupling'])) +
                                           " ".join(map(str, b)))
            else:
                for b in bonds:
                    if isinstance(b, int):
                        bondstrings.append(
                            ("%s %s %i" % (coupl['int_type'],
                                           coupl['coupling'],
                                           sublattice_permutation_inverse[b])))
                    else:
                        newb = np.zeros(b.shape, dtype=np.int)
                        for idx, i in enumerate(b):
                            newb[idx] = sublattice_permutation_inverse[i]

                        bondstrings.append(("%s %s " % (coupl['int_type'],
                                                        coupl['coupling'])) +
                                           " ".join(map(str, newb)))

        num_bonds = len(bondstrings)

        # Create all permutations
        if write_symmetry_info:
            if self.lattice.trans_sym == False:
                translations = np.zeros((1, self.dimension))
            else:
                translations = writelattice.bravaiscoordinates - \
                    writelattice.bravaiscoordinates[0]

            perms = symmetries._get_permutations(writelattice.coordinates,
                                                 writelattice.unitcell,
                                                 writelattice.simulation_torus,
                                                 translations,
                                                 self._symmetries['rotations'],
                                                 sym_center=\
                                                 writelattice.sym_center)

            # Convert symmetries in sublattice stable way
            if sublattice_structure is not None:

                fixed_sublattice_permutations = []
                symmetry_permutation_inv = []
                for i in range(n_sublattices):
                    fixed_sublattice_permutations.append([])
                    symmetry_permutation_inv.append([])

                for perm_idx, perm in enumerate(perms):
                    # Convert permutation
                    newperm = np.zeros(writelattice.n_sites, dtype=np.int)
                    for j in range(len(perm)):
                        newperm[j] = \
                            sublattice_permutation_inverse[
                                perm[sublattice_permutation[j]]]

                    # Find out which sublattice symmetry sector newperm
                    # might belong to ...
                    sublattice_idx = int(np.where(newperm == 0)[0][0]) // \
                        (writelattice.n_sites / n_sublattices)

                    # ... and check whether perm is sublattice stable
                    for j in range(sublattice_idx * writelattice.n_sites /
                                   n_sublattices,
                                   (sublattice_idx + 1) * writelattice.n_sites /
                                   n_sublattices):
                        if not newperm[j] < writelattice.n_sites / n_sublattices:
                            raise ValueError("Sublattice structure does not " +
                                             "yield stable symmetries")

                    fixed_sublattice_permutations[sublattice_idx].\
                        append(newperm)
                    symmetry_permutation_inv[sublattice_idx].append(perm_idx)

                # Glue symmetries together in sublattice ordered way and
                # determine this permutation
                perms = np.array(
                    [item for sublist in fixed_sublattice_permutations
                     for item in sublist])
                symmetry_permutation_inv = \
                    [item for sublist in symmetry_permutation_inv
                     for item in sublist]
                symmetry_permutation = np.zeros(len(symmetry_permutation_inv),
                                                dtype=np.int)
                for i in range(len(symmetry_permutation_inv)):
                    symmetry_permutation[symmetry_permutation_inv[i]] = i

        # Open model file
        with open(filename, 'a') as modelfile:
            modelfile.write("[Interactions]=%i\n" % num_bonds)
            for i in range(num_bonds):
                modelfile.write("%s\n" % bondstrings[i])

            if write_symmetry_info:
                modelfile.write("[SymmetryOps]=%i\n" % perms.shape[0])
                for i, perm in enumerate(perms):
                    modelfile.write("[S%i] " %
                                    i + " ".join(map(str, perm)) + "\n")

                modelfile.write("[Irreps]=%i\n" % len(irreps))
                for irrepname, irrep in zip(irreps.keys(), irreps.values()):
                    modelfile.write("[Representation]=%s\n" % irrepname)
                    modelfile.write(
                        "[K=(%s)]\n" % (','.join(map(str, irrep['k']))))
                    if sublattice_structure is None:
                        allowed_ops = irrep['allowed_ops']
                        phases = irrep['phases']
                    else:
                        # Convert allowed ops to new ordering of permutations
                        allowed_ops = np.zeros(len(irrep["allowed_ops"]),
                                               dtype=np.int)
                        for i in range(len(irrep["allowed_ops"])):
                            allowed_ops[i] = \
                                symmetry_permutation[irrep["allowed_ops"][i]]
                        phases = irrep["phases"]

                        # sort phases and new allowed ops
                        allowed_ops, phases = \
                            (list(x) for x in zip(*sorted(zip(allowed_ops,
                                                              phases))))
                        allowed_ops = np.array(allowed_ops)
                        phases = np.array(phases)

                    modelfile.write("[AllowedOps]=%i\n" % allowed_ops.shape[0])
                    modelfile.write("%s\n" % (" ".join(map(str, allowed_ops))))
                    modelfile.write("\n".join(["%.16f %.16f" % (np.real(x),
                                                                np.imag(x))
                                               for x in phases]) + "\n")

        self._modelfilename = filename
        print 'Modelfile %s written!' % filename


        
    def _get_allowed_symmetries(self):
        """
        Compute the allowed symmetries of the model, taking all bonds
        into account.
        """
        inv_unitcell = np.linalg.inv(self.lattice.unitcell)

        reduced_rotations = []
        rot_names = []

        # loop through all allowed symmetry elements of the lattice
        for idx, sym in enumerate(self.lattice.symmetries_torus['rotations']):
            rot_matrix_nonfrac = np.dot(np.dot(inv_unitcell, sym),
                                        self.lattice.unitcell)
            symok = True

            for bond in self._couplings:
                # Compute allowed perms
                if bond['directed']:
                    if bond['allowed_perms'] is None:
                        allowedperms = np.arange(
                            bond['cellshift'].shape[0]).reshape(1, -1)
                    else:
                        allowedperms = bond['allowed_perms']
                else:
                    if bond['cellshift'].shape[0] > 1:
                        allowedperms = list(itertools.permutations(
                            range(bond['cellshift'].shape[0])))
                    else:
                        allowedperms = np.array([[0]])

                cellshift = bond['cellshift']
                cellshift = cellshift - np.min(cellshift, axis=0)
                cellcoords = np.dot(cellshift, self.lattice.unitcell)

                basis = bond['basis_sites']
                basiscoords = self.lattice.basiscoordinates[basis]
                bondcoords = cellcoords + basiscoords

                newcoords = np.dot(rot_matrix_nonfrac,
                                   (bondcoords - self.lattice.sym_center).T).T\
                    + self.lattice.sym_center

                newbasiscoords = _map_to_simtorus(newcoords,
                                                  self.lattice.unitcell)
                newcellshift = np.linalg.solve(self.lattice.unitcell.T,
                                               newcoords.T).T
                newcellshift = np.floor(np.round(newcellshift, decimals=6))
                newcellshift = newcellshift - np.min(newcellshift, axis=0)

                symforbond = False
                for checkbond in self._couplings:
                    if (checkbond['int_type'] == bond['int_type'] and
                        checkbond['coupling'] == bond['coupling'] and
                        checkbond['directed'] == bond['directed']):

                        # map bonds to unitcell to compare to
                        # rotated coordinates
                        checkcellshift = checkbond['cellshift']
                        checkcellshift = checkcellshift - np.min(checkcellshift,
                                                                 axis=0)
                        checkcellcoords = np.dot(checkcellshift,
                                                 self.lattice.unitcell)

                        checkbasiscoords = self.lattice.basiscoordinates[
                            checkbond['basis_sites']]
                        checkbondcoords = checkcellcoords + checkbasiscoords

                        checkbasiscoords = _map_to_simtorus(
                            checkbondcoords, self.lattice.unitcell)
                        checkcellshift = np.linalg.solve(
                            self.lattice.unitcell.T, checkbondcoords.T).T
                        checkcellshift = np.floor(np.round(checkcellshift,
                                                           decimals=6))
                        checkcellshift = checkcellshift - np.min(checkcellshift,
                                                                 axis=0)

                        for perm in allowedperms:
                            cellshiftperm = newcellshift[np.array(perm)]
                            diffshifts = cellshiftperm - checkcellshift
                            cellok = np.all(np.abs(diffshifts) < 1e-6)
                            basisok = np.all(
                                np.abs(newbasiscoords[np.array(perm)]
                                       - checkbasiscoords) < 1e-6)
                            if cellok and basisok:
                                symforbond = True
                                break
                    if symforbond:
                        break

                symok = symok and symforbond

            if symok:
                if ((self.maxpg == None) or
                    (self.lattice.symmetries_torus['names'][idx] in self.maxpg)):

                    reduced_rotations.append(sym)
                    rot_names.append(
                        self.lattice.symmetries_torus['names'][idx])

        self._symmetries = {'rotations': np.array(reduced_rotations,
                                                 dtype='intc', order='C'),
                            'translations': np.zeros_like(reduced_rotations,
                                                          dtype='intc',
                                                          order='C'),
                            'names': rot_names}

        if self.dimension == 2:
            self._pointgroup = quantipy.spglib.spglib2d.get_pointgroup(
                self._symmetries["rotations"])  # Pointgroup of the lattice
        elif self.dimension == 3:
            self._pointgroup = quantipy.spglib.spglib.get_pointgroup(
                self._symmetries["rotations"])  # Pointgroup of the lattice

        # Recompute little groups
        self.little_groups = self.lattice._get_little_groups(self._symmetries)

        # Set syms computed
        self._syms_computed = True


    def _plot(self, closed_loops=False, interactions=None, rep_inf=4,
              ax=None, **kwargs):
        if self.lattice._is_infinite:
            plotlattice = Lattice(unitcell=self.lattice.unitcell,
                                  basiscoordinates=\
                                  self.lattice.basiscoordinates,
                                  simulation_torus_matrix=rep_inf *
                                  np.eye(self.dimension))
        else:
            plotlattice = self.lattice

        # handle legend keywords
        kwargs, legkwargs = _kwtolegkw(kwargs)

        # compute the couplings for the finite lattice
        self._get_finite_lattice_bonds(plotlattice)

        # Plot the lattice
        plotlattice.plot(periodic=False, ax=ax, ms=8, mfc='none', **kwargs)

        # Legend axes and labels
        legaxes = [0] * len(self._finite_lattice_bonds)
        leglabels = [0] * len(self._finite_lattice_bonds)

        # Color cycle
        if StrictVersion(matplotlib.__version__) < StrictVersion('1.5.0'):
            clist = rcParams['axes.color_cycle']
        else:
            clist = [x['color'] for x in rcParams['axes.prop_cycle']]

        color_cycle = itertools.cycle(clist)

        allaxes = []

        for n, coupl in enumerate(self._finite_lattice_bonds):
            color = next(color_cycle)
            directed = coupl['directed']
            leglabels[n] = ', '.join([coupl['int_type'], coupl['coupling']])

            if coupl['bonds'].shape[1] == 1:
                coords = plotlattice.coordinates[coupl['bonds']]
                if self.dimension == 1:
                    axplot = ax.plot(coords[:, 0, 0], '*', c=color, ms=14)
                elif self.dimension == 2:
                    axplot = ax.plot(coords[:, 0, 0], coords[:, 0, 1], '*',
                                     c=color, ms=14)
                elif self.dimension == 3:
                    axplot = ax.plot(coords[:, 0, 0],
                                     coords[:, 0, 1],
                                     coords[:, 0, 2],
                                     '*', c=color, ms=14)

            else:
                for b in coupl['bonds']:
                    coords = np.zeros([len(b), self.dimension])
                    for i, pos in enumerate(b):
                        # Handle periodic boundary bonds
                        if i == 0:
                            coord = plotlattice.coordinates[pos]
                            coords[i, :] = coord
                        else:
                            mindist = 100000
                            for uvw in itertools.product([0, 1, -1],
                                                         repeat=self.dimension):
                                coord = plotlattice.coordinates[pos] + \
                                    np.dot(uvw, plotlattice.simulation_torus)
                                dist = linalg.norm(coord - coords[i - 1, :])
                                if dist < mindist:
                                    mindist = dist
                                    mincoord = coord
                            coords[i, :] = mincoord

                    # Sort by angle ##TODO: 3D
                    if self.dimension == 2:
                        coords_com = np.sum(coords, axis=0) / coords.shape[0]
                        rel_coords = coords - coords_com
                        sortidx = np.argsort(np.arctan2(rel_coords[:, 1],
                                                        rel_coords[:, 0]))
                        coords = coords[sortidx]

                    # close the  loops
                    if closed_loops and len(b) > 2:
                        coords = np.vstack((coords, coords[0, :]))

                    if self.dimension == 1:
                        axplot = ax.plot(coords[:, 0], c=color, lw=1.5)
                    elif self.dimension == 2:
                        axplot = ax.plot(coords[:, 0], coords[:, 1],
                                         c=color, lw=1.5)
                    elif self.dimension == 3:
                        axplot = ax.plot(coords[:, 0], coords[:, 1],
                                         coords[:, 2], c=color, lw=1.5)
                    if directed:
                        ax.quiver(coords[:-1, 0], coords[:-1, 1],
                                  np.diff(coords, axis=0)[:, 0],
                                  np.diff(coords, axis=0)[:, 1], color=color)

            legaxes[n] = axplot[0]
            allaxes.append(axplot)

        ax.legend(legaxes, leglabels, **legkwargs)

        return allaxes


    def _get_finite_lattice_bonds(self, lattice):
        # Rebuild couplings on finite lattices for Modelfiles and plotting
        self._finite_lattice_bonds = []

        # first get different bond-types
        param_dicts = []
        for coupl in self._couplings:
            # copy dictionary info without positions
            newdict = dict(coupl)

            del newdict['cellshift']
            del newdict['basis_sites']
            del newdict['allowed_perms']

            if newdict not in param_dicts:
                param_dicts.append(newdict)
                coupl_dict = dict(newdict)
                coupl_dict['bonds'] = []
                self._finite_lattice_bonds.append(coupl_dict)

        # get bonds
        for coupl in self._couplings:
            pdict = dict(coupl)
            del pdict['cellshift']
            del pdict['basis_sites']
            del pdict['allowed_perms']
            param_pos = np.argwhere(pdict == np.array(param_dicts))

            if coupl['trans_repeat'] is False:
                bond = np.zeros(len(coupl['basis_sites']))
                for i in range(len(coupl['basis_sites'])):
                    index = {'cell': list(coupl['cellshift'][i]),
                             'basis': coupl['basis_sites'][i]}
                    pos = np.argwhere(index ==
                                      np.array(lattice._rel_indices))[0, 0]
                    bond[i] = pos
                # Put bond to finite_lattice_bonds
                self._finite_lattice_bonds[param_pos]['bonds'].extend([bond])
            else:
                # Shift to first unit-cell
                bonds = []
                cellshifts = coupl['cellshift'] - coupl['cellshift'][0]
                bravaisshifts = \
                    unique_rows(np.array([x['cell']
                                          for x in lattice._rel_indices]))

                for bravaisshift in bravaisshifts:
                    # Get bond
                    bond = np.zeros(len(coupl['basis_sites']))

                    for i in range(len(coupl['basis_sites'])):
                        index = {'cell': list(cellshifts[i] + bravaisshift),
                                 'basis': coupl['basis_sites'][i]}
                        pos = np.argwhere(
                            index == np.array(lattice._rel_indices))
                        if pos.size:
                            bond[i] = pos[0, 0]
                        else:
                            cell = _map_to_simtorus(
                                (cellshifts[i] + bravaisshift).reshape(1, -1),
                                lattice._sim_tor_matrix).reshape(-1,)

                            index = {'cell': map(int, list(np.around(cell))),
                                     'basis': coupl['basis_sites'][i]}
                            pos = np.argwhere(index ==
                                              np.array(lattice._rel_indices))
                            if pos.size:
                                bond[i] = pos[0, 0]
                            else:
                                raise ValueError("Problem computing finite " +
                                                 "lattice bonds.")

                    bonds.append(map(int, bond))
                # print int(param_pos)
                self._finite_lattice_bonds[int(
                    param_pos)]['bonds'].extend(bonds)

        # make bonds to np array
        for coupl in self._finite_lattice_bonds:
            coupl['bonds'] = np.array(coupl['bonds'])

            if self.OBC:
                if coupl['bonds'].shape[1] == 2:
                    dist = np.linalg.norm(
                        self.lattice.coordinates[coupl['bonds'][:, 0]] -
                        self.lattice.coordinates[coupl['bonds'][:, 1]], axis=1)
                    mindist = np.min(dist)
                    idx = dist == mindist
                    coupl['bonds'] = coupl['bonds'][idx, :]
                    coupl['bonds'] = np.sort(coupl['bonds'], axis=1)
                    coupl['bonds'] = unique_rows(coupl['bonds'])

                elif coupl['bonds'].shape[1] > 2:
                    raise ValueError("OBC not yet implemented for more " +
                                     "than 2-spin interactions!")
