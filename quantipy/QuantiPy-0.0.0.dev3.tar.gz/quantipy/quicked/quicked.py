# -*- coding: utf-8 -*-
"""
QuickED Exact Diagonalization Code for QuantiPy

:author: Alexander Wietek
"""
import numpy as np
import scipy as sp
import itertools

import _quicked
import quantipy.spectra.spectra as spec
import quantipy.operators.heisenberg as heis
import quantipy.correlations.correlations as corr


def raw_dimension(n_sites, hilbert_space="spinhalf", qn=0):
    """
    Return raw dimension without symmetries of Hilbert space
    with a given quantum number

    :param n_sites: number of sites
    :type n_sites: int
    :param hilbert_space: type of the Hilbert space **optional**
                          Default: "spinhalf"
    :type hilbert_space: string
    :param qn: quantum number of conserved quantity in Hilbert space
    :type qn: quicked.quantumnumber
    """
    return _quicked._raw_dimension(n_sites, hilbert_space, qn)

def basis_state_string(state, n_sites, hilbert_space="spinhalf", revert=True):
    """
    Return a string of a basis state in a human readable format

    :param state: state to be printed
    :type state: numpy.uint64
    :param n_sites: number of sites of the basis state
    :type n_sites: int
    :param hilbert_space: type of the Hilbert space **optional**
                          Default: "spinhalf"
    :type hilbert_space: string
    :param revert: flag whether MSB is left (True) or right (False)
    :type revert: boolean

    :returns: string of a basis state in a human readable format
    :rtype: string
    """
    if revert:
        return _quicked._basis_state_string(state, n_sites, hilbert_space)[::-1]
    else:
        return _quicked._basis_state_string(state, n_sites, hilbert_space)


def get_basis_states(n_sites, hilbert_space="spinhalf", qn=0):
    """
    Return all basis states of raw (unsymmetrized) Hilbert space

    :param n_sites: number of sites
    :type n_sites: int
    :param hilbert_space: type of the Hilbert space **optional**
                          Default: "spinhalf"
    :type hilbert_space: string
    :param qn: quantum number of conserved quantity in Hilbert space
    :type qn: quicked.quantumnumber

    :returns: array containing all basis states
    :rtype: np.array(dtype=uint64)
    """
    return _quicked._get_basis_states(n_sites, hilbert_space, qn)


def get_basis_states_symmetrized(n_sites, lattice_symmetries, bloch_factors,
                                 hilbert_space="spinhalf", qn=0):
    """
    Return all basis states and normalization constants
    of symmetrized Hilbert space block in an ordered array

    :param n_sites: number of sites
    :type n_sites: int
    :param lattice_symmetries: permutations of lattice sites defining
                               the lattice symmetries
    :type lattice_symmetries: np.array, shape (#symmetries x #n_sites)
    :param bloch_factors: complex bloch factors corresponding to the
                          characters of the irreducible representation
    :type bloch_factors: np.array, shape (#symmetries)
    :param hilbert_space: type of the Hilbert space **optional**
                          Default: "spinhalf"
    :type hilbert_space: string
    :param qn: quantum number of conserved quantity in Hilbert space
    :type qn: quicked.quantumnumber

    :returns: (basis_states, norms), basis_states contains all basis
              states in an ordered way norms are the corresponding
              normalization factors
    :rtype: (np.array(dtype=uint64), np.array(dtype=double))
    """
    # TODO: Check lattice_symmetries for numpy array
    if lattice_symmetries.shape[1] != n_sites:
        raise ValueError("Invalid shape for symmetries")
    if lattice_symmetries.shape[0] != bloch_factors.shape[0]:
        raise ValueError("Dimension mismatch for lattice_symmetries " +
                         "and bloch_factors")

    # TODO: Check whether symmetries are permutations
    return _quicked._get_basis_states_symmetrized(n_sites, lattice_symmetries,
                                                  bloch_factors, hilbert_space,
                                                  qn)

def get_bonds_from_model(model, type_matrices, couplings):
    """
    Get a list of bonds with corresponding bondmatrices from a model by
    specifying type_matrices and couplings

    :param model: model defining interactions
    :type model: quantipy.models.GenericModel instance
    :param type_matrices: bond matrices for interaction type like
                          {'HB': np.array(...), ...}
    :type type_matrices: Python dictionary
    :param couplings: coupling strengths for coupling constant like
                          {'J': 0.5, ...}
    :type couplings: Python dictionary

    :returns: list of dictionaries of form
              [{'sites': [0, 1], 'matrix': np.array(...)}, ...]
    :rtype: list of Python dictionaries
    """
    types = type_matrices.keys()
    coupling_names = couplings.keys()
    model._get_finite_lattice_bonds(model.lattice)
    finite_lattice_bonds = model._finite_lattice_bonds

    bonds = []
    for interaction in finite_lattice_bonds:
        type_name = interaction['int_type']
        coupling_name = interaction['coupling']

        if coupling_name in coupling_names and type_name in types:
            for sites in interaction['bonds']:
                bonds.append({"sites": sites,
                              "matrix": couplings[coupling_name] *
                                        type_matrices[type_name]})
    return bonds



def get_operator(n_sites, bonds, hilbert_space="spinhalf", qn=0,
                 basis_states=None):
    """
    Get Hamiltonian in raw basis

    :param n_sites: number of sites
    :type n_sites: int
    :param bonds: list of dictionaries of form
                  [{'sites': [0, 1], 'matrix': np.array(...)}, ...]
    :type bonds: list of Python dictionaries
    :param hilbert_space: type of the Hilbert space **optional**
                          Default: "spinhalf"
    :type hilbert_space: string
    :param qn: quantum number of conserved quantity in Hilbert space
    :type qn: quicked.quantumnumber
    :param basis_states: array that contains the basis states,
                         if argument is None the basis states are
                         computed anew. **optional**, Default: None
    :type basis_states: numpy.array

    :returns: tuple containing (rows, cols, data), in the sense
              that A[rows[i],cols[i]] = data[i] if data[i] is non-zero
    :rtype: rows: np.array(dtype=uint64), cols: np.array(dtype=uint64),
            data: np.array(dtype=complex128)
    """
    (bond_sites, bond_matrices_flat) = _prepare_bond_matrices(bonds)
    if basis_states == None:
        basis_states = np.array([])

    return _quicked._get_operator(n_sites, hilbert_space, qn, bond_sites,
                                  bond_matrices_flat, basis_states)



def get_operator_symmetrized(n_sites, lattice_symmetries, bloch_factors, bonds,
                             hilbert_space="spinhalf", qn=0, basis_states=None,
                             norms=None):
    """
    Get Hamiltonian in symmetrized basis

    :param n_sites: number of sites
    :type n_sites: int
    :param lattice_symmetries: permutations of lattice sites defining
                               the lattice symmetries
    :type lattice_symmetries: np.array, shape (#symmetries x #n_sites)
    :param bloch_factors: complex bloch factors corresponding to the
                          characters of the irreducible representation
    :type bloch_factors: np.array, shape (#symmetries)
    :param bonds: list of dictionaries of form
                  [{'sites': [0, 1], 'matrix': np.array(...)}, ...]
    :type bonds: list of Python dictionaries
    :param hilbert_space: type of the Hilbert space **optional**
                          Default: "spinhalf"
    :type hilbert_space: string
    :param qn: quantum number of conserved quantity in Hilbert space
    :type qn: quicked.quantumnumber
    :param basis_states: array that contains the basis states,
                         if argument is None the basis states are
                         computed anew. **optional**, Default: None
    :type basis_states: numpy.array
    :param norms: array that contains the norms of the basis states, if
                  argument is None the basis states are computed anew.
                  **optional**, Default: None
    :type norms: numpy.array

    :returns: tuple containing (rows, cols, data), in the sense
              that A[rows[i],cols[i]] = data[i] if data[i] is non-zero
    :rtype: rows: np.array(dtype=uint64), cols: np.array(dtype=uint64),
            data: np.array(dtype=complex128)

    """
    (bond_sites, bond_matrices_flat) = _prepare_bond_matrices(bonds)
    if basis_states == None:
        basis_states = np.array([])
    if norms == None:
        norms = np.array([])
    return _quicked._get_operator_symmetrized(n_sites, lattice_symmetries,
                                              bloch_factors, hilbert_space, qn,
                                              bond_sites, bond_matrices_flat,
                                              basis_states, norms)


def get_spectra(model, type_matrices, couplings, qns,
                hilbert_space="spinhalf", representations=None,
                n_eigenvalues=10, verbose=True):
    """
    Compute the spectrum of a model for given parameters

    :param model: model defining interactions
    :type model: quantipy.models.GenericModel instance
    :param type_matrices: bond matrices for interaction type like
                          {'HB': np.array(...), ...}
    :type type_matrices: Python dictionary
    :param couplings: coupling strengths for coupling constant like
                          {'J': [1.], 'J2': [0, 0.1, 0.2, 0.3]}
    :type couplings: Python dictionary
    :param qns: quantumnumbers, e.g. Sz values like qn=[0, 1, 2, 4]
    :type qns: list of quicked.quantumnumber
    :param hilbert_space: type of the Hilbert space **optional**
                          Default: "spinhalf"
    :type hilbert_space: string
    :param representations: list of names of representations of
                            the model. **Optional**. default: None
                            (all representations are computed)
    :type representations: list of strings
    :param n_eigenvalues: number of eigenvalues to be computed
                          in each spectrum
    :type n_eigenvalues: int
    :param verbose: flag whether current progress is printed
    :type verbose: boolean

    :return: Exact Diagonalization Spectra
    :rtype: QuantiPy :class:`Spectrum_Collection`
    """
    if representations == None:
        representations = model.irrep_names()

    spectra = []
    parameters = []
    reps = []
    szs = []
    sis = []

    for rep in representations:
        perms, phases = model.symmetries(irrep_name=rep)
        for qn in qns:
            basis_states, norms = get_basis_states_symmetrized(
                model.n_sites, perms, phases, hilbert_space=hilbert_space,
                qn=qn)
            dim = len(basis_states)
            params = couplings.values()
            for coupl in itertools.product(*params):
                # rebuild couplings
                coupl_dict = dict()
                if verbose:
                    print "Computing spectrum:", rep, ", qn =", qn, ", ",

                for c_idx, c_val in enumerate(coupl):
                    if verbose:
                        print couplings.keys()[c_idx], c_val, ", ",
                    coupl_dict[couplings.keys()[c_idx]] = c_val

                if verbose:
                    print "\n",

                bonds = get_bonds_from_model(model, type_matrices, coupl_dict)
                (rows, cols, data) = get_operator_symmetrized(model.n_sites,
                                                              perms,
                                                              phases, bonds,
                                                              basis_states=\
                                                              basis_states,
                                                              norms=norms,
                                                              hilbert_space=\
                                                              hilbert_space,
                                                              qn=0)
                if dim == 0:
                    eigs = np.array([])
                else:
                    hamiltonian = sp.sparse.csr_matrix((data, (rows, cols)),
                                                       shape=(dim, dim))

                    if dim <= n_eigenvalues:
                        eigs = sp.linalg.eigh(hamiltonian.todense(),
                                              eigvals_only=True)
                    else:
                        eigs = sp.sparse.linalg.eigsh(hamiltonian,
                                                      k=n_eigenvalues,
                                                      which='SA',
                                                      return_eigenvectors=False,
                                                      maxiter=1000)

                eigs = np.sort(eigs)
                spectra.append(spec.Spectrum(eigs))
                parameters.append(coupl)
                reps.append(rep)
                szs.append(qn)
                sis.append(0)
                if verbose:
                    print eigs

    return spec.Spectrum_Collection(spectra, representations=reps,
                                    parameters=parameters, spinflips=sis,
                                    szs=szs)


def get_spin_correlations(model, type_matrices, couplings, representation,
                          hilbert_space="spinhalf", qn=0, diagonal=True,
                          verbose=True):
    """
    Compute static spin correlations of the groundstate

    :param model: model defining interactions
    :type model: quantipy.models.GenericModel instance
    :param type_matrices: bond matrices for interaction type like
                          {'HB': np.array(...), ...}
    :type type_matrices: Python dictionary
    :param couplings: coupling strengths for coupling constant like
                          {'J': 1., ...}
    :type couplings: Python dictionary
    :param representation: name of representations of the model.
    :type representation: string
    :param hilbert_space: type of the Hilbert space **optional**
                          Default: "spinhalf"
    :type hilbert_space: string
    :param qn: quantum number of conserved quantity in Hilbert space
    :type qn: quicked.quantumnumber
    :param diagonal: flag whether diagonal SzSz or full SdotS
                     correlations are computed
    :type diagonal: boolean
    :param verbose: flag whether current progress is printed
    :type verbose: boolean
    """
    # Compute ground state of model
    if verbose:
        print "Computing groundstate"
    perms, phases = model.symmetries(irrep_name=representation)
    basis_states, norms = get_basis_states_symmetrized(
        model.n_sites, perms, phases, hilbert_space=hilbert_space, qn=qn)
    dim = len(basis_states)

    bonds = get_bonds_from_model(model, type_matrices, couplings)
    (rows, cols, data) = get_operator_symmetrized(
        model.n_sites, perms, phases, bonds, hilbert_space=hilbert_space,
        qn=qn, basis_states=basis_states, norms=norms)
    hamiltonian = sp.sparse.csr_matrix((data, (rows, cols)), shape=(dim,dim))
    eig, evec = sp.sparse.linalg.eigsh(hamiltonian, k=1, which='SA',
                                       return_eigenvectors=True, maxiter=1000)

    # Compute all correlations
    if diagonal:
        corrtag = "SzSz"
    else:
        corrtag = "SdotS"

    positions = dict()
    positions[corrtag] = []
    values = dict()
    values[corrtag] = []

    for site in range(1, model.n_sites):
        if hilbert_space == "spinhalf":
            hb_matrix = heis.heisenberg_bond(spin=2)
        elif hilbert_space == "spinone":
            hb_matrix = heis.heisenberg_bond(spin=3)
        elif hilbert_space == "spinthreehalf":
            hb_matrix = heis.heisenberg_bond(spin=4)
        elif hilbert_space == "spintwo":
            hb_matrix = heis.heisenberg_bond(spin=5)

        if diagonal:
            if verbose:
                print "Computing SzSz correlator [{0},{1}] =".format(0, site),
            hb_matrix = np.diag(np.diag(hb_matrix))
        else:
            if verbose:
                print "Computing SdotS correlator [{0},{1}] =".format(0, site),

        # symmetrize bonds
        bonds = []
        for perm in perms:
            bonds.append({"sites": [perm[0], perm[site]],
                          "matrix": hb_matrix})

        (rows, cols, data) = get_operator_symmetrized(
            model.n_sites, perms, phases, bonds, hilbert_space=hilbert_space,
            qn=qn, basis_states=basis_states, norms=norms)

        corr_matrix = sp.sparse.csr_matrix((data, (rows, cols)),
                                           shape=(dim,dim))
        corrval = np.real(np.dot(np.conj(evec[:,0]),
                                 corr_matrix.dot(evec[:,0]))) / \
            (float(perms.shape[0]))

        if verbose:
            print corrval

        positions[corrtag].append(np.array([[0, site]]))
        values[corrtag].append(np.real(corrval))

    positions[corrtag] = np.array(positions[corrtag])
    values[corrtag] = np.array(values[corrtag])

    corrs = corr.Correlations(positions, values)
    corrs.set_lattice(model.lattice)
    return corrs


def _prepare_bond_matrices(bonds):
    """
    Prepare bonds in a format that can be passed to the C interface
    """
    n_bonds = len(bonds)

    # Construct bond data structures
    max_bond_sites = max([len(bond["sites"]) for bond in bonds])
    bond_sites = -np.ones((n_bonds, max_bond_sites+1), dtype=np.intc, order='C')
    bond_matrices_flat = np.array([], dtype=np.complex128)
    for bond_idx, bond in enumerate(bonds):
        bond_sites[bond_idx, 0:len(bond["sites"])] = np.array(bond["sites"],
                                                              dtype=np.intc)
        bond_matrices_flat = np.hstack((bond_matrices_flat,
                                        bond["matrix"].flatten()))

    return (bond_sites, bond_matrices_flat)
