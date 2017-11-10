# -*- coding: utf-8 -*-
"""
 Module for handling QuantiPy Spectrum objects

 :author: Alexander Wietek, Michael Schuler
"""

__all__ = ["read", "read_re", "Spectrum", "Spectrum_Collection"]

import numpy as np
import matplotlib
import matplotlib as mpl
import matplotlib.pyplot as plt
from scipy import linalg
import scipy.optimize as opt
import os
import re
import warnings
import itertools
import copy

from quantipy.utils import _axes_decorator, unique_rows, find_rows, _kwtolegkw
from distutils.version import StrictVersion

def read(filename_or_dir_or_list, **kwargs):
    """
    Reads (a) spectrum(a) from an output file(s) of QMSpinDyn

    :type filename_or_dir_or_list: str / list of str
    :param filename: filename of the output file or directory with
                     multiple outfiles or list of filenames/directories
    :type eigenvaluename: str
    :param eigenvaluename: Name of the variable from which the energy
                           data is read. **Optional**.
    :rtype: :class:`Spectrum` if single file is given,
            :class:`Spectrum_Collection` if directory or list of
            files is given (with more than one file).
    :return: Exact Diagonalization Spectrum(a) read from input file(s).
    """
    if not 'eigenvaluename' in kwargs:
        kwargs['eigenvaluename'] = 'Eigenvalue['

    if isinstance(filename_or_dir_or_list, list):
        spectras = []
        for file_or_dir in filename_or_dir_or_list:
            spectras.extend(_read_file_or_dir(file_or_dir,**kwargs) )
    else:
        spectras =  _read_file_or_dir(filename_or_dir_or_list,**kwargs)

    if len(spectras)>1:
        return Spectrum_Collection(spectras)
    else:
        return spectras[0]


def _read_file_or_dir(filename_or_dir,**kwargs):
    """
    Reads a spectrum from a file or directory
    """
    if os.path.isfile(filename_or_dir):
        return [_read_single_file(filename_or_dir,**kwargs)]

    if os.path.isdir(filename_or_dir):
        files = [f for f in os.listdir(filename_or_dir)
                 if os.path.isfile(os.path.join(filename_or_dir,f))]
        spectra = []
        for f in files:
            spectra.append(_read_single_file(os.path.join(filename_or_dir,f),
                                             **kwargs))

        return spectra
    else:
        return []


def _read_single_file(filename,**kwargs):
    """
    Reads a spectrum from an output file of QMSpinDyn (auxillary to read())

    :type filename_or_dir: str
    :param filename: filename of the output file or directory with
                     multiple outfiles
    :rtype: QuantiPySpectrum
    :return: Exact diagonalization spectrum read from the input file
    """
    fobj = open(filename,"r")
    eigenvalues_tmp = []
    properties_tmp = dict()
    alphas_tmp = []
    betas_tmp = []
    is_parameter_line = False

    for line in fobj:
        entries = line.split("=")

        if "0 1 2 3 4 5" in line:
            is_parameter_line = True
        if "threads =" in line:
            is_parameter_line = False


        if is_parameter_line and len(entries) is 2:
            properties_tmp[str(entries[0].strip())] = \
                entries[1].replace(";","").replace("\"","").strip()
        if kwargs['eigenvaluename'] in entries[0]:
            value = float(entries[1])
            eigenvalues_tmp.append(value)
        if "alpha[" in entries[0]:
            value = float(entries[1])
            alphas_tmp.append(value)
        if "beta[" in entries[0]:
            value = float(entries[1])
            betas_tmp.append(value)

    eigenvalues = np.array(eigenvalues_tmp)
    if alphas_tmp is not []:
        alphas = np.array(alphas_tmp)
    if betas_tmp is not []:
        betas = np.array(betas_tmp)


    if alphas_tmp is not [] and betas_tmp is not []:
        return Spectrum(eigenvalues, properties_tmp, alphas, betas)
    else:
        return Spectrum(eigenvalues)


def read_re(dirpath, regexp, rep_pos=-1, spinflip_pos=None, sz_pos=None,
            **kwargs):
    """
    .. versionadded:: 1.0.x

    Reads all files in a directory matching a regular expression and
    groups them according to a representation name.

    :type dirpath: str
    :param dirpath: Path to the directory in which a regular expression
                    search is performed.
    :type regexp: str
    :param regexp: Python regular expression string to identify the
                   files which should be loaded. If groups are in the
                   regular expression string, these groups are used to
                   identify parameters and the representation.
    :type rep_pos: int/np.ndarray(int)
    :param rep_pos: Position(s) of the representation index in the groups
                    of the regular expression string. All other positions
                    are accounted as parameters. **Optional**.
                    Default: representation is last group.
    :type spinflip_pos: int / 'even','odd' / 'e','o'
    :param spinflip_pos: Position of a spinflip like quantum number in
                         the groups of the regular expression string.
                         This position is not taken into account as a
                         parameter but more like a further representation
                         index, but will be identified with different symbol
                         styles or in a different plot. Ground-state
                         energies etc. will be computed within all this
                         quantum number sectors. **Optional**.
                         Default: No such index.
    :type sz_pos: int
    :param sz_pos: Position of the Sz quantum number (or an Sz like number)
                   in the groups of the regular expression string. This
                   position is not taken into account as a parameter
                   but more like a further representation index, but
                   will be identified with symbols of different size.
                   **Optional**. Default: No such index.
    :type eigenvaluename: str
    :param eigenvaluename: Name of the variable from which the energy
                           data is read. **Optional**.
    """
    if not 'eigenvaluename' in kwargs:
        kwargs['eigenvaluename'] = 'Eigenvalue['

    #Get number of groups in searchexp
    n_groups = re.compile(regexp).groups

    #Handle rep_pos int/array
    if type(rep_pos)==int:
        rep_pos = np.array([rep_pos])

    #Handle negative indices
    for i,rp in enumerate(rep_pos):
        if rp<0:
            rep_pos[i] += n_groups
    if not spinflip_pos is None and spinflip_pos<0:
        spinflip_pos += n_groups
    if not sz_pos is None and sz_pos<0:
        sz_pos += n_groups

    #check if rep_pos and spinflip_pos,sz_pos are different
    if np.any(rep_pos==spinflip_pos) and rep_pos is not None:
        raise ValueError('rep_pos and spinflip_pos must be different!')
    if np.any(rep_pos==sz_pos) and rep_pos is not None:
        raise ValueError('rep_pos and sz_pos must be different!')
    if np.any(spinflip_pos==sz_pos) and sz_pos is not None:
        raise ValueError('spinflip_pos and sz_pos must be different!')

    #parameter positions in the groups
    param_pos = np.setdiff1d(np.arange(n_groups),
                             np.hstack([rep_pos,spinflip_pos,sz_pos]))

    allfiles = os.listdir(dirpath)

    files = []
    params = []
    reps = []   #Representations
    sis = []    #spin-flip like quantum numbers
    szs = []    #Sz quantum numbers

    for fi in allfiles:
        match = re.search(regexp, fi)
        if match:
            #filenames
            files.append(dirpath+match.string)
            if len(match.groups()):
                parameters = np.array(match.groups())
                #Representations
                reps.append('.'.join(map(str,parameters[rep_pos])))
                #Spinflipnumbers
                if not spinflip_pos is None:
                    mapfunc = {'1': 1, '-1': -1, 'even': 1, 'odd': -1,
                               'e': 1, 'o':-1, '0':0, 'None':0}
                    sis.append(mapfunc[parameters[spinflip_pos]])
                #Sz
                if not sz_pos is None:
                    #szs.append(map(float,parameters[sz_pos])[0])
                    szs.append(float(parameters[sz_pos]))
                #Parameters
                params.append(map(float,parameters[param_pos]))

    params = np.array(params)
    sis = np.array(sis)
    szs = np.array(szs)
    reps = np.array(reps)
    files = np.array(files)

    #read files
    spectras = []
    for filename in files:
        spectras.extend(_read_file_or_dir(filename,**kwargs))

    #Check if params and reps where found
    if params.size==0:
        params = None
    if len(reps)==0:
        reps = None
    if sis.size==0:
        sis = None
    if szs.size==0:
        szs = None

    if len(spectras):
        return Spectrum_Collection(spectras, representations=reps,
                                   parameters=params, spinflips=sis, szs=szs)
    else:
        raise ValueError('Could not find any files matching the ' +
                         'regular expression regexp!')



class Spectrum:
    """
    :class: Spectrum

    Provides means to analyse Spectra of Hermitian Operators as given
    by Exact Diagonalization techniques.
    """
    def __init__(self, eigenvalues, properties=dict(),
                 alphas=np.array([]), betas=np.array([])):
        """
        Constructor of Spectrum class

        :type eigenvalues: :class: numpy.ndarray
        :param eigenvalues:  Eigenvalues of an hermitian operator
        :type properties: Python dictionary
        :param properties:  properties of the spectrum, optional.
                            Default is empty dictionary.
        :type alphas: :class: numpy.ndarray
        :param alphas:  Diagonal elements of the T-matrix, optional.
                        Default is empty list.
        :type betas: :class: numpy.ndarray
        :param betas:  Subdiagonal elements of the T-matrix , optional.
                       Default is empty list.

        """

        # make sure eigenvalues, alphas, betas are initialized as a numpy array
        if not isinstance(eigenvalues,np.ndarray):
            raise ValueError("Spectrum.eigenvalues must be a NumPy array.")
        if not isinstance(eigenvalues,np.ndarray):
            raise ValueError("Spectrum.alphas must be a NumPy array.")
        if not isinstance(eigenvalues,np.ndarray):
            raise ValueError("Spectrum.betas must be a NumPy array.")

        self.eigenvalues = eigenvalues

        self._properties = properties
        if not alphas == []:
            self.alphas = alphas

        if not betas == []:
            self.betas = betas

        if alphas is not [] and betas is not []:
            self._tmatrix_defined = True
        else:
            self._tmatrix_defined = False

        if self._tmatrix_defined:
            if self.eigenvalues.size==0 and self.alphas.size>0 \
               and self.betas.size>0:
                warnings.warn("Eigenvalues are empty. T-matrix can be " +
                              "constructed nevertheless", UserWarning)
            elif eigenvalues.size != alphas.size or (alphas.size!=betas.size \
                 and alphas.size!=(betas.size+1) ):
                warnings.warn("Eigenvalues, alphas and betas arrays do " +
                              "not have same size", UserWarning)
                self._tmatrix_defined = False

        self._convergence_computed = False

    def __getitem__(self,key):
        """
        Returns the value in the properties for a given key

        :type key: str
        :param key: Key of an entry in properties
        :rtype: str
        :return: Value of the properity for the key

        """
        return self._properties[key]

    def __setitem__(self,key,value):
        """
        Sets the value for a property for a given key

        :type key: str
        :param key: Key of an entry in properties
        :type key: str
        :param key: Value of an entry in properies
        """
        self._properties[key] = value



    def __contains__(self, item):
        """
        Checks if a key is contained in the properties

        :type item: str
        :param item: Key of an entry in properties
        :rtype: boolean
        :return: True is item is in properties dictionary
        """
        return item in self._properties


    def __str__(self):
        """
        Returns a short summary of the Spectrum

        :rtype: str
        :return:  Short summary of the spectrum with number of
                  eigenvalues, extremal eigenvalues and information
                  whether T-matrix is defined
        """
        out = "Spectrum class: # eigenvalues: " + str(self.eigenvalues.size) + \
            " , extremal eigenvalues: [ "  + str(np.min(self.eigenvalues)) + \
            ", " + str(np.max(self.eigenvalues)) + "]"
        if self._tmatrix_defined:
            out += " , T-Matrix defined \n"
        else:
            out += " , T-Matrix not defined \n"

        return out + str(self._properties)


    @_axes_decorator
    def plot(self, pos=0.0, excitation_energies=False, num_excitations=None,
             ax=None, yscale=1., **kwargs):
        """
        Plots the spectrum at a given position

        :type pos: float
        :param pos: position on x axis where to plot the spectrum
        :type num_excitations: int
        :param num_excitations: Number of excitation energies to plot,
                                **optional**. Default *all*.
        :type yscale: float
        :param yscale: Scales the y-data (energies) by this factor..
                       **Optional**.
        :param kwargs: The kwargs can be used to set line properties.
        :return: Handle to axes with plot
        """
        #handle legend keywords
        kwargs, legkwargs = _kwtolegkw(kwargs)

        if num_excitations:
            numplot = num_excitations
        else:
            numplot = len(self.eigenvalues)

        xes = np.ones(self.eigenvalues.shape)*pos
        if excitation_energies:
            return ax.plot(xes[:numplot], (self.eigenvalues[:numplot] -
                                           np.min(self.eigenvalues))*yscale,
                           "*", **kwargs)
        else:
            return ax.plot(xes[:numplot], self.eigenvalues[:numplot]*yscale,
                           "*", **kwargs)


    def compute_convergence(self, stepsize=1):
        """
        Plots convergence pattern of the Lanczos algorithm

        :type stepsize: int
        :param stepsize: Stepsize for evaluation of Eigenvalues of 
                         the T-Matrix, **optional**.
        """
        if not self._tmatrix_defined:
            raise ValueError("T-matrix not defined.")

        # make sure that full T-matrix is always diagonalized, independent
        # of stepsize
        iterarray = range(1,self.alphas.size-1,stepsize)
        if not iterarray[-1]==self.alphas.size-1:
            iterarray.extend([self.alphas.size-1])

        X = np.array([])
        E = np.array([])
        
        #faster than linalg.eigvalsh
        for iteration in iterarray:
            evals = linalg.eigvals_banded((self.alphas[:iteration],
                                           self.betas[:iteration]), lower=True)
            x_coords = iteration*np.ones(evals.size)
            X = np.append(X, x_coords)
            E = np.append(E, evals)

        self.convergence_data = np.array([X,E])  #data for plotting convergence
        self._convergence_computed = True
        self._convergence_stepsize = stepsize


    @_axes_decorator
    def plot_convergence(self, stepsize=None, ax=None, **kwargs):
        """
        Plots convergence pattern of the Lanczos algorithm

        :type stepsize: int
        :param stepsize: Stepsize for evaluation of Eigenvalues of 
                         the T-Matrix, **optional**.
        :type ax: Axes object
        :param type: Axes for plotting, **optional**. Default: Create new 
                     figure with axes.
        :param kwargs: The kwargs can be used to set line properties.
        :return: Handle to axes with plot
        """
        #handle legend keywords
        kwargs, legkwargs = _kwtolegkw(kwargs)

        if stepsize is None:
            if not self._convergence_computed:
                self.compute_convergence(stepsize=1)
        else:
            if not self._convergence_computed or \
               not self._convergence_stepsize==stepsize:
                self.compute_convergence(stepsize=stepsize)

        ax.plot(self.convergence_data[0,:], self.convergence_data[1,:], "*",
                **kwargs)

        ax.set_xlabel('Iteration')
        ax.set_ylabel('Eigenvalues of T-matrix')
        return ax

    def write(self, filename, **kwargs):
        np.set_printoptions(precision=20)
        with open(filename, 'w') as the_file:
            for idx, value in enumerate(self.eigenvalues):
                print idx, value
                the_file.write('Eigenvalue[{0}]={1:.20f}\n'.format(idx, value))
    


class Spectrum_Collection:
    """
    :class: Spectrum_Collection

    Provides tools to visualize and evaluate multiple :class:`Spectrum` 
    objects simultaneously.
    """
    def __init__(self, speclist, representations=None, parameters=None,
                 spinflips=None, szs=None):
        """
        Initialization:

        :type speclist: list
        :param speclist: List of :class:`DynSpecFunc` objects.
        :type representations: list
        :param representations: List of representation names for 
                                speclist. Representations are used to 
                                group the speclist. **Optional**. 
                                Default is None.
        :type parameters: numpy.ndarray (len(speclist)xn)
        :param parameters: List of parameters for speclist. A single 
                           speclist can have n parameter values. Parameters 
                           are used to set an order for e.g. plotting. 
                           **Optional**. Default is None.
        :type spinflips: list
        :param spinflips: List of spinflip-like quantum numbers for 
                          speclist to further group the speclist. 
                          Similar to representations. **Optional**. 
                          Default is None.
        :type szs: list
        :param szs: List of Sz quantum numbers for speclist to further 
                    group the speclist. Similar to representations. 
                    **Optional**. Default is None.
        """

        #check if dsflist is in correct form
        if not isinstance(speclist, list):
            raise ValueError("Input must be a Python list of Spectrum objects.")

        #initialize speclist and num ....
        self.speclist = []              #: List of :class:`Spectrum` objects in this Collection
        self.rep_list = []              #: List of representation names corresponding to :class:`Spectrum` objects in this Collection
        self.par_list = []              #: List of parameters corresponding to :class:`Spectrum` objects in this Collection
        self.spinflip_list = []         #: List of spinflip-like quantum numbers corresponding to :class:`Spectrum` objects in this Collection
        self.sz_list = []               #: List of sz quantum numbers corresponding to :class:`Spectrum` objects in this Collection

        #Only take spectrum objects with eigenvalues
        for i,spec in enumerate(speclist):
            if len(spec.eigenvalues)>0:
                self.speclist.append(spec)
                if not representations is None:
                    self.rep_list.append(representations[i])
                if not parameters is None:
                    self.par_list.append(parameters[i])
                else:
                    self.par_list.append([0])

                if not spinflips is None:
                    self.spinflip_list.append(spinflips[i])
                if not szs is None:
                    self.sz_list.append(szs[i])

        self.par_list = np.array(self.par_list)
        self.num = len(speclist)        #: Number of :class:`Spectrum` objects in this Collection

        #sort representations (Gamma first, ...)
        if len(self.rep_list):
            self.representations = sorted(np.unique(self.rep_list), key=self._sortfunc) #: Representations in the Collection (sorted)
        else:
            self.representations = []

        if self.par_list.size:
            self.parameters = unique_rows(self.par_list)                #: Parameters in the Collection
            self.parameters = self.parameters[self.parameters[:,0].argsort()] #sort parameters according to first row
        else:
            self.parameters = []
        if len(self.spinflip_list):
            self.spinflips = np.unique(self.spinflip_list)              #: Spinflip values in the Collection
        else:
            self.spinflips = []
        if len(self.sz_list):
            self.szs = np.unique(self.sz_list)          #: Sz values in the Collection
            if np.all(np.abs(self.szs - np.round(self.szs))<1e-8):
                self.szs = np.array(self.szs, dtype='int')
        else:
            self.szs = []

    def _sortfunc(self,x):
        """
        Sorts the representations beginning with Gamma, numbers last
        """
        if 'Gamma' in x or '0-0' in x:
            return '0'+x
        elif 'M' in x or 'K' in x or 'X' in x or 'Y' in x or 'Sigma' in x or \
          'Delta' in x or 'Z' in x:
            return '1'+x
        else:
            return '2'+x

    def __str__(self):
        """
        Returns a short summary of the class.
        """
        out="Spectrum_Collection class. # Spectrum objects = " + str(self.num)
        return out

    def __len__(self):
        """
        Returns the number of :class:`Spectrum` objects in the collection.
        """
        return self.num


    def rename_reps(self, oldnames, newnames):
        """
        Rename the representations in the Spectrum_Collection!

        :type oldnames: list/np.ndarray of regexp strings
        :param oldnames: A list of representations to be renamed. 
                         Regular expressions are used.
        :type newnames: list/np.ndarray of strings
        :param newnames: A list of new names. The first entry in oldnames
            is renamed according to the first entry in newnames and so on.
        """
        for oldname,newname in zip(oldnames,newnames):
            for i,r in enumerate(self.rep_list):
                if re.match(oldname,r):
                    self.rep_list[i] = newname

            for i,r in enumerate(self.representations):
                if re.match(oldname,r):
                    self.representations[i] = newname

        self.representations = np.unique(self.representations)


    def get_parameters_gs_energy(self, return_rep=False):
        """
        Get the UNIQUE parameters of the Spectrum objects and the 
        corresponding ground-state energies as arrays.

        :type return_rep: Bool
        :param return_rep: If True, an array with the corresponding 
                           representations is also returned. 
                           **Optional**. Default: False

        :returns: parameter array, energy array, [representations array]
        """
        if not self.par_list is None and not self.par_list.size==0:
            gs_energies = np.zeros(len(self.parameters))
            if return_rep:
                gs_reps = np.zeros(len(self.parameters),dtype='object')

            for i, param in enumerate(self.parameters):
                idx = find_rows(param, self.par_list)
                Emin = 10000000
                jmin = 0
                for j,spec in enumerate(np.array(self.speclist)[idx]):
                    if spec.eigenvalues[0]<Emin:
                        Emin = spec.eigenvalues[0]
                        jmin = j
                gs_energies[i] = Emin
                if return_rep:
                    gs_reps[i] = np.array(self.rep_list)[idx][jmin]

            if return_rep:
                return self.parameters, gs_energies, gs_reps
            else:
                return self.parameters, gs_energies

        elif self.par_list.size==0:
            Emin = 10000000
            jmin = 0
            for j,spec in enumerate(self.speclist):
                Emin = min(Emin,spec.eigenvalues[0])
                if spec.eigenvalues[0]<Emin:
                    Emin = spec.eigenvalues
                    if return_rep:
                        jmin = j
            if return_rep:
                gs_rep = self.rep_list[jmin]

            if return_rep:
                return [], Emin, gs_rep
            else:
                return [], Emin

        else:
            raise ValueError('Could not find parameters in the class!')


    def _get_params_gs_energy(self):
        """
        Get gs energy of all representations for each parameter. 
        Returns gs_energies as list corresponding to speclist!
        """
        if not self.par_list is None:
            uniqueparams, gs_energies = self.get_parameters_gs_energy()
            #GS energy for each Spectrum object
            all_gs_energies = np.zeros(len(self.par_list))
            for i,param in enumerate(self.par_list):
                idx = find_rows(param, uniqueparams)
                all_gs_energies[i] = gs_energies[idx[0][0]]

            return all_gs_energies

        else:
            warnings.warn('Could not find parameters in the class!')


    def get_parameters_excitations(self, return_rep=False,
                                   return_spinflip=False, return_sz=False):
        """
        Get the UNIQUE parameters of the Spectrum objects and the 
        corresponding excitation energies as arrays.

        :type return_rep: Bool
        :param return_rep: If True, an array with the corresponding 
                           representations is also returned. 
                           **Optional**. Default: False
        :type return_spinflip: Bool
        :param return_spinflip: If True, an array with the corresponding 
                                spinflip number is also returned. 
                                **Optional**. Default: False
        :type return_sz: Bool
        :param return_sz: If True, an array with the corresponding 
                          Sz number is also returned. 
                          **Optional**. Default: False
        :rtype: np.array, list(np.array), [list(np.array)] ,[list(np.array)]
        :returns: parameters, excitation energies for each parameter, 
                  [representations for each parameter if return_rep=True], 
                  [spinflip numbers for each parameter if return_spinflip=True],
                  [spinflip numbers for each parameter if return_spinflip=True]
        """
        if return_rep and self.rep_list is None:
            raise ValueError('No representations are found in the class ' +
                             'object. Switch off return_rep option.')
        if return_spinflip and self.spinflip_list is None:
            raise ValueError('No spinflip are found in the class object.' +
                             ' Switch off return_spinflip option.')
        if return_sz and self.sz_list is None:
            raise ValueError('No Sz are found in the class object. Switch ' +
                             'off return_sz option.')

        if not self.par_list is None:

            excitations = []
            if return_rep:
                reps = []
            if return_spinflip:
                spflips = []
            if return_sz:
                szs = []

            if not self.par_list.size==0:
                pars = self.parameters
            else:
                pars = [0]

            for i, param in enumerate(pars):
                if not self.par_list.size==0:
                    idx = find_rows(param, self.par_list)
                else:
                    idx = np.arange(len(self.par_list))

                allenergies = np.array([])
                if return_rep:
                    allreps = []
                    repsavail = np.array(self.rep_list)[idx]
                if return_spinflip:
                    allspflips = []
                    spflipsavail = np.array(self.spinflip_list)[idx]
                if return_sz:
                    allszs = []
                    szsavail = np.array(self.sz_list)[idx]

                for i,spec in enumerate(np.array(self.speclist)[idx]):
                    allenergies = np.append(allenergies, spec.eigenvalues)
                    if return_rep:
                        allreps.extend([repsavail[i]]*len(spec.eigenvalues))
                    if return_spinflip:
                        allspflips.extend([spflipsavail[i]] * \
                                           len(spec.eigenvalues))
                    if return_sz:
                        allszs.extend([szsavail[i]]*len(spec.eigenvalues))

                #sort allenergies
                idxsort = np.argsort(allenergies)
                allenergies = allenergies[idxsort]
                excitations.append(allenergies-allenergies[0])
                if return_rep:
                    reps.append( np.array(allreps)[idxsort] )
                if return_spinflip:
                    spflips.append(np.array(allspflips)[idxsort])
                if return_sz:
                    szs.append(np.array(allszs)[idxsort])

            #return data
            returnlist = [self.parameters, excitations]
            if return_rep:
                returnlist.append(reps)
            if return_spinflip:
                returnlist.append(spflips)
            if return_sz:
                returnlist.append(szs)

            return returnlist

        else:
            raise ValueError('Could not find parameters in the class!')


    def plot(self, which_spinflip=None, singleplot=True, which_sz=None,
             legend=True, figlegend=False, return_leg=False, **kwargs):
        """
        Plot energies of loaded spectral data (:class:`Spectrum` objects) 
        depending on parameters.

        .. versionchanged:: 1.0.x

        If representations and parameters are defined in the 
        :class:`SpectrumCollection` class, they are plotted 
        automatically with different symbols for different representations
        and the x-position corresponds to the parameters 
        (see plot_parameter_idx variable)

        :type plot_parameter_idx: int
        :param plot_parameter_idx:  Choose, which column of the parameter 
                                    array is used for the x-axis of the plot. 
                                    **Optional**. Default: 0, the first
                                    column is used!
        :type which_parameters: list/np.ndarray
        :param which_parameters: Choose which parameters should be plotted. 
                                 Input must be similar to specs.parameters 
                                 list. **Optional**. Default: All is plotted
        :type xpos: int/float/numpy.ndarray
        :param xpos: x-positions to plot :class:`Spectrum` objects. When 
                     parameters are defined in the Collection, xpos must 
                     be of the length of the number of different parameters! 
                     **Optional**. Default is linear spacing with unit distance.

        :type excitatation_energies: Bool
        :param excitation_energies: If True, set lowest energy to zero, 
                                    **optional**. Default *True*.
        :type num_excitations: int
        :param num_excitations: Number of excitation energies to plot, 
                                **optional**. Default *all*.
        :type yscale: float/list/numpy.ndarray
        :param yscale: Scales the y-data (energies) by this factor if it 
                       is a float. If a list/array is given, the spectrum 
                       is scaled for each parameter separately according 
                       to the list. **Optional**.
        :type xscale: float
        :param xscale: Scales the x-data (parameters) by this factor. 
                       **Optional**.
        :type representations: list of strings
        :param representations: Choose which representations should be 
                                plotted. A regexp-search in 
                                self.representations is performed for 
                                each string. Works only if representations 
                                are initialized! **Optional**. 
                                Default: None, Plot all representations.
        :type emptymarkers: Bool
        :param emptymarkers: If True, markers are not filled. 
                             **Optional**. Default: False, plotting filled 
                             markers.
        :type symbols: list
        :param symbols: Define a list of symbols which are cycled for 
                        the different representations. **Optional**. 
                        Default: ['o','^','x','*','s','>','<','D','v']
        :type colors: list
        :param colors: Define a list of colors to use cycled for the 
                       different representations. **Optional**. Default 
                       from mpl.rcParams.
        :type which_spinflip: int
        :param which_spinflip: Position of the spinflip sector to plot 
                               in the spinflip array. **Optional**. 
                               Default: None, plot all sectors.
        :type singleplot: Bool/list
        :param singleplot: Only if spininversion position is defined. 
                           If True, all spininversion sectors are plotted 
                           in the same plot with empty and full markers 
                           alternating. If singleplot is a list, only 
                           these spininversion sectors are plotted in a 
                           single plot. The 'mew' kwarg can be used with 
                           a list as argument to define the individual 
                           markeredgewidth of the different spininversion 
                           sectors. Only recommended if there are TWO 
                           spinflip sectors. **Optional**. Default: True

        :type which_sz: int/float/list/np.array
        :param which_sz: Choose which Sz sector(s) should be included 
                         in the plot. **Optional**. Default: All sectors 
                         are plotted.
        :type fixedsymbols: Bool
        :param fixedsymbols: If True, symbols are fixed for all 
                             representations in Spectrum_Collection. 
                             **Optional**. Default: False.
        :type msdiffsz: float/int
        :param msdiffsz: Set the difference of markersizes for Sz sectors. 
                         **Optional**. Default: The standard value of 
                         markersize/2 is used.
        :type legend: Bool
        :param legend: If True, a legend is created automatically. 
                       **Optional**. Default: True
        :type figlegend: Bool
        :param figlegend: If True, a figure legend is created automatically. 
                          **Optional**. Default: False
        :type return_leg: Bool
        :param return_leg: If True, legend handles and labels are return, 
                           but no legend is plotted. Default: False
        :type ax: matplotlib.axes
        :param ax: Axes where the plot is plotted. **Optional**. 
                   Default: Create new figure.
        :type sortfuncreps: function
        :param sortfuncreps: Define how to sort the representations 
                             in the plot. **Optional**. Default = None, 
                             automatically sorted!
        :type showallreps: Bool
        :param showallreps: If True, representations without data to 
                            plot are also shown in legend and used to set 
                            the marker styles. Use this to plot several 
                            instances of the same SpectrumCollection but 
                            with different parameter sets with the same 
                            symbols. **Optional**. Default: False
        :type kwargs: *keyword arguments*
        :param kwargs: The kwargs can be used to set plot properties and 
                       most legend properties.
        :returns:  Handles to plots (Legend handles/labels if return_leg)

        .. rubric:: Example

        Load ED spectras from different symmetry sectors and plot in 
        different style::

            # Import modules
            import quantipy.edspectra as spec
            import matplotlib.pyplot as plt

            # Use read_re to read all files matching a Python regular 
            # expression from a directory
            directory_path = 'tests/files_energy/'
            regexp = 'Energies.*.Sz.(.?.?).rep.(.*)$'
            spectras = spec.read_re(directory_path, regexp)

            # Use the plot function of the Spectrum_Collection class to 
            # plot the data
            spectras.plot(num_excitations=10)

            # set plot properties
            plt.xlabel(r'$S_z$')
            plt.ylabel(r'Energy')
            plt.tight_layout()
            plt.show()


        .. figure:: img_edspectra_collection_plot.png
           :align: center
           :width: 400px
           :height: 300px

           Sample plot of :func:`plot`
        """
        #handle legend keywords
        kwargs, legkwargs = _kwtolegkw(kwargs)

        #handle plotparameters
        if not 'plot_parameter_idx' in kwargs or \
           kwargs['plot_parameter_idx'] is None:
            plot_parameter_idx = 0
        else:
            plot_parameter_idx = kwargs['plot_parameter_idx']
        plotparameters = np.array(self.parameters)

        if 'which_parameters' in kwargs and \
           not kwargs['which_parameters'] is None:
            plotparameters = np.array(kwargs['which_parameters'])
            del kwargs['which_parameters']
            if not self.parameters.shape[1:]==plotparameters.shape[1:]:
                raise ValueError('The shape of which_parameters must be' +
                                 ' identical to self.parameters, except' +
                                 'for the first entry!')
            allparameters=False
        else:
            allparameters=True

        #handle singleplot list/bool values
        if type(singleplot)==list or type(singleplot)==np.ndarray:
            if len(singleplot)>0:
                sfidx=np.array(singleplot)
                sfidx = np.array([np.argwhere(self.spinflips==x)[0,0]
                                  for x in singleplot if x in self.spinflips])
                singleplot=True
        elif singleplot==True:
            sfidx = np.array([True]*len(self.spinflips),dtype=bool)

        #handle which_sz types
        if which_sz is None:
            if len(self.szs):
                which_sz = np.array(self.szs) #plot all
            else:
                which_sz = [None]
        elif type(which_sz)==float or type(which_sz)==int:
            which_sz = np.array([which_sz])
        elif type(which_sz)==list or type(which_sz)==np.ndarray:
            which_sz = np.array(which_sz)
        else:
            raise ValueError('Keyword which_sz must either be None, an int, ' +
                             'a float, a list or a np.ndarray!')


        #Plotting
        if len(self.spinflips)>0 and which_spinflip is None:
            if singleplot==False:
                axes = []
                #Handle creation of new plots and ax keyword
                if 'ax' in kwargs and kwargs['ax'] is not None:
                    ax = kwargs['ax']
                    del kwargs['ax']
                    newfig = False
                else:
                    newfig = True

                #Spinflip loop
                for i in range(len(self.spinflips)):
                    if newfig:
                        fig = plt.figure()
                        ax = fig.gca()
                    axarrs = []
                    leglabels = []
                    #Loop through sz sectors
                    szax = []
                    szlabels = []
                    for wsz in which_sz:
                        axarr = self._plot(which_spinflip=i,
                                           plotparameters=plotparameters,
                                           allparameters=allparameters,
                                           which_sz=wsz, ax=ax, **kwargs)
                        axarrs.extend(axarr)
                        leglabels.extend(self._repstoplot)
                        if wsz is not None:
                            szax.extend([axarr[0]])
                            szlabels.extend(['Sz=%s' %wsz])

                    axes.append(axarr)
                    ax.set_title('spininversion = %s' %self.spinflips[i])
                    if (legend or figlegend or return_leg) and \
                       not self.representations is None:
                        legaxes = axarrs
                        ax_lab = np.array([x for x in zip(legaxes,leglabels)
                                           if x[0]])
                        _, unique_idx = np.unique(ax_lab[:,1],
                                                  return_index=True)
                        ax_lab = ax_lab[unique_idx,:]

                        if len(ax_lab):
                            legaxes = list(ax_lab[:,0])
                            leglabels = list(ax_lab[:,1])
                            if not return_leg:
                                if figlegend:
                                    plt.figlegend(szax+legaxes,
                                                  szlabels+leglabels,
                                                  **legkwargs)
                                elif legend:
                                    ax.legend(szax+legaxes, szlabels+leglabels,
                                              **legkwargs)

            else: #singleplot==True
                if not 'ax' in kwargs:
                    fig = plt.figure()
                    ax = fig.gca()
                    kwargs['ax']=ax
                if not 'emptymarkers' in kwargs or \
                   kwargs['emptymarkers'] is None or \
                   kwargs['emptymarkers']==False:
                    emptymarkercycle = itertools.cycle([True,False])
                    mewcycle = np.tile([2,.5], len(self.spinflips)/2+1)
                    if 'emptymarkers' in kwargs:
                        del kwargs['emptymarkers']
                    if 'mec' in kwargs:
                        del kwargs['mec']
                    if 'markeredgecolor' in kwargs:
                        del kwargs['markeredgecolor']
                else:
                    emptymarkercycle = itertools.cycle([kwargs['emptymarkers']])
                    if kwargs['emptymarkers']==True:
                        mewcycle = np.array([2]*len(self.spinflips))
                    else:
                        mewcycle = np.array([.5]*len(self.spinflips))
                    del kwargs['emptymarkers']

                if 'mew' in kwargs:
                    if isinstance(kwargs['mew'],float) or \
                       isinstance(kwargs['mew'],int):
                        mewcycle = np.array([kwargs['mew']]*len(self.spinflips))
                    elif isinstance(kwargs['mew'],list) or \
                         isinstance(kwargs['mew'],np.ndarray):
                        mewcycle = np.tile(kwargs['mew'], len(self.spinflips) /\
                                           len(kwargs['mew'])+1)
                    else:
                        raise ValueError('kwarg mew must be of the types int,' +
                                         ' float, list or np.ndarray!')
                    del kwargs['mew']
                if 'markeredgewidth' in kwargs:
                    if isinstance(kwargs['markeredgewidth'],float) or \
                       isinstance(kwargs['markeredgewidth'],int):
                        mewcycle = np.array([kwargs['markeredgewidth']] * \
                                            len(self.spinflips))
                    elif isinstance(kwargs['markeredgewidth'],list) or \
                    isinstance(kwargs['markeredgewidth'],np.ndarray):
                        mewcycle = np.tile(kwargs['markeredgewidth'],
                                           len(self.spinflips) / \
                                           len(kwargs['markeredgewidth'])+1)
                    else:
                        raise ValueError('kwarg markeredgewidth must be of ' +
                                         'the types int, float, list or ' +
                                         'np.ndarray!')
                    del kwargs['markeredgewidth']

                axes = []
                silegendaxes = []
                silegend = []
                szlegendaxes = []
                szlabels = []
                axarrplot = []
                repslabel = []
                #Loop through spinflip sectors
                for i,s in enumerate(self.spinflips[sfidx]):
                    emptymarker = next(emptymarkercycle)
                    if emptymarker:
                        if 'c' in kwargs:
                            kwargs['mec']=kwargs['c']
                        if 'color' in kwargs:
                            kwargs['mec']=kwargs['color']
                    else:
                        if 'mec' in kwargs:
                            del kwargs['mec']

                    # Loop through sz sectors
                    # axarrs = []
                    # replabels = []
                    for wsz in which_sz:
                        axarr = self._plot(which_spinflip = \
                                           np.where(self.spinflips==s),
                                           emptymarkers=emptymarker,
                                           plotparameters=plotparameters,
                                           mew=mewcycle[i],
                                           allparameters=allparameters,
                                           which_sz=wsz, **kwargs)
                        #axarrs.extend(axarr)
                        axes.append(axarr)
                        if wsz is not None and len(axarr):
                            szlegendaxes.extend([axarr[0]])
                            szlabels.extend(['Sz=%s' %wsz])

                    try:

                        idxnotempty = int(np.argwhere([a!=[] for a in axarr])[0])
                        silegendaxes.append(axarr[idxnotempty])
                        silegend.append('si = %s' %s)
                        #axarrplot.extend(axarrs)
                        axarrplot.extend(axarr)
                        repslabel.extend(list(self._repstoplot))
                    except IndexError:
                        warnings.warn('Cannot plot for si=%s!' %s)

                if (legend or figlegend or return_leg) and \
                   not self.representations is None:
                    if len(self.sz_list)>0:
                        sz_lab = np.array([x for x in zip(szlegendaxes,szlabels)
                                           if x[0]])
                        if len(sz_lab):
                            _, szidx = np.unique(sz_lab[:,1], return_index=True)
                            sz_lab = sz_lab[szidx]
                            sz_ax = list(sz_lab[:,0])
                            sz_labels = list(sz_lab[:,1])
                        else:
                            sz_ax = []
                            sz_labels = []
                    else:
                        sz_ax = []
                        sz_labels = []

                    #unique representations for legend
                    repslabel = np.array(repslabel)[np.where(axarrplot)]
                    axarrplot = np.array(axarrplot)[np.where(axarrplot)]
                    repslabel, unique_idx = np.unique(repslabel,
                                                      return_index=True)
                    axarrplot = np.array(axarrplot)[unique_idx]
                    #sort representations again
                    if not 'sortfuncreps' in kwargs:
                        axarrplot_repslabel = \
                            np.array(sorted(zip(axarrplot,repslabel),
                                            key=lambda x: self._sortfunc(x[1])))
                    else:
                        axarrplot_repslabel = \
                            np.array(sorted(zip(axarrplot,repslabel),
                                            key=lambda x: kwargs['sortfuncreps'](x[1])))

                    if len(axarrplot_repslabel):
                        repslabel = list(axarrplot_repslabel[:,1])
                        axarrplot = list(axarrplot_repslabel[:,0])
                    else:
                        repslabel =[]
                        axarrplot = []

                    legaxes = silegendaxes+sz_ax+axarrplot
                    leglabels = silegend+sz_labels+repslabel
                    ax_lab = np.array([x for x in zip(legaxes,leglabels) if x[0]])
                    if len(ax_lab):
                        legaxes = list(ax_lab[:,0])
                        leglabels = list(ax_lab[:,1])
                    else:
                        legaxes = []
                        leglabels = []

                    if not return_leg:
                        if figlegend:
                            lgnd = plt.figlegend(legaxes, leglabels, **legkwargs)
                        elif legend:
                            lgnd = plt.legend(legaxes, leglabels, **legkwargs)

                    #change markersize of representation entries in legend to sz=0 size
                    if 'ms' in kwargs:
                        markersize = kwargs['ms']
                    else:
                        markersize = plt.rcParams['lines.markersize']
                    # for i in range(len(axarrplot)):
                    #     lgnd.legendHandles[-(1+i)]._legmarker.set_markersize(markersize)

        else: #len(self.spinflips)==0 or which_spinflip is set
            if not 'ax' in kwargs:
                fig = plt.figure()
                ax = fig.gca()
                kwargs['ax'] = ax

            if 'mew' in kwargs:
                if isinstance(kwargs['mew'],float) or \
                   isinstance(kwargs['mew'],int):
                    mewcycle = np.array([kwargs['mew']] * len(which_sz))
                elif isinstance(kwargs['mew'],list) or \
                     isinstance(kwargs['mew'],np.ndarray):
                    mewcycle = np.tile(kwargs['mew'],
                                       len(which_sz)/len(kwargs['mew'])+1)
                else:
                    raise ValueError('kwarg mew must be of the types int, ' +
                                     'float, list or np.ndarray!')
                del kwargs['mew']
            elif 'markeredgewidth' in kwargs:
                if isinstance(kwargs['markeredgewidth'],float) or \
                   isinstance(kwargs['markeredgewidth'],int):
                    mewcycle = np.array([kwargs['markeredgewidth']] *
                                        len(which_sz))
                elif isinstance(kwargs['markeredgewidth'],list) or \
                     isinstance(kwargs['markeredgewidth'],np.ndarray):
                    mewcycle = np.tile(kwargs['markeredgewidth'],
                                       len(which_sz) / \
                                       len(kwargs['markeredgewidth'])+1)
                else:
                    raise ValueError('kwarg markeredgewidth must be of the ' +
                                     'types int, float, list or np.ndarray!')
                del kwargs['markeredgewidth']
            else:
                mewcycle = [.5]*len(which_sz)

            axes = []
            leglabels = []
            szaxes = []
            szlabels = []
            for j, wsz in enumerate(which_sz):
                axret = self._plot(which_spinflip=which_spinflip,
                                   plotparameters=plotparameters,
                        allparameters=allparameters, which_sz=wsz,
                                   mew=mewcycle[j], **kwargs)
                axes.extend(axret)
                leglabels.extend(list(self._repstoplot))
                if len(axret):
                    szaxes.extend([axret[0]])
                    szlabels.extend(['Sz=%s' %wsz])

            if len(self.spinflips):
                plt.title('spininversion = %s' %self.spinflips[which_spinflip])
            if (legend or figlegend or return_leg) and \
               len(self.representations):
                legaxes = axes
                ax_lab = np.array([x for x in zip(legaxes,leglabels) if x[0]])

                if len(ax_lab):
                    _, unique_idx = np.unique(ax_lab[:,1], return_index=True)
                    ax_lab = ax_lab[unique_idx,:]
                    legaxes = list(ax_lab[:,0])
                    leglabels = list(ax_lab[:,1])
                else:
                    legaxes = []
                    leglabels = []

                #sort representations
                if not 'sortfuncreps' in kwargs:
                    axarrplot_repslabel = \
                        np.array(sorted(zip(legaxes,leglabels),
                                        key=lambda x: self._sortfunc(x[1])))
                else:
                    axarrplot_repslabel = \
                        np.array(sorted(zip(legaxes,leglabels),
                                        key=lambda x: kwargs['sortfuncreps'](x[1])))

                leglabels = list(axarrplot_repslabel[:,1])
                legaxes = list(axarrplot_repslabel[:,0])

                if len(self.sz_list)>0:
                    legaxes = szaxes + legaxes
                    leglabels = szlabels + leglabels

                if not return_leg:
                    if figlegend:
                        plt.figlegend(legaxes, leglabels, **legkwargs)
                    elif legend:
                        plt.legend(legaxes, leglabels, **legkwargs)

        if return_leg==True:
            return axes, legaxes, leglabels
        else:
            return axes


    def plot_tos(self, parameter=None, szmax=None, showline=True,
                 Smultiplets=False, tol=1e-2, **kwargs):
        """
        Plot Tower of States as function of Sz(Sz+1) for a given parameter

        :type parameter: (N,)-array
        :param parameter: Choose which parameter of Spectrum_Collection 
                          should be plotted. **Optional**.
                          Default: Plot first parameter of Spectrum_Collection.
        :type szmax: int
        :param szmax: Maximum sz to plot. **Optional**. Default: Plot all sz.
        :type showline: Bool
        :param showline: If True, a line connecting the TOS levels is 
                         plotted and their slope is returned. 
                         **Optional**. Default: True
        :type Smultiplets: Bool
        :param Smultiplets: If True, Smultiplets are identified from Sz. 
                            **Optional**. Default: False
        :type tol: float
        :param tol: Accepted Energy difference for identification of 
                    Smultiplets. **Optional**. Default: 1e-2
        :type kwargs: dictionary
        :param kwargs: Can be used to set the properties of 
                       :class:`Spectrum_Collection` plot function. **Optional**.
        """

        if not len(self.szs):
            raise ValueError('Cannot use plot_TOS for Spectrum_Collection ' +
                             'without Sz numbers!')

        if szmax==None:
            szmax = max(self.szs)
        szmax = min(max(self.szs),szmax)
        szplot = self.szs[self.szs<=szmax]

        #Parameter handling
        if parameter is None:
            which_parameter = self.parameters[0]
        else:
            which_parameter = parameter

        kwargs['which_parameters'] = np.array([which_parameter])

        #Handle kwargs arguments
        if 'which_sz' in kwargs:
            del kwargs['which_sz']
            warnings.warn('kwarg which_sz cannot be used for ' +
                          'plot_tos(). Maybe you want to use szmax instead.',
                          UserWarning)
        if not 'ax' in kwargs:
            fig = plt.figure()
            ax = fig.gca()
            kwargs['ax']=ax
        if 'xpos' in kwargs:
            del kwargs['xpos']
            warnings.warn('kwarg xpos cannot be used for plot_tos().',
                          UserWarning)
        if 'emptymarkers' not in kwargs or kwargs['emptymarkers'] is None:
            kwargs['emptymarkers'] = False
            kwargs['szemptymarkers'] = False

        kwargs['msdiffsz']=0
        kwargs['return_leg']=True

        #handle legend keywords
        kwargs, legkwargs = _kwtolegkw(kwargs)

        #Smultiplet identification
        if Smultiplets:
            #Copy original speclist for reset after operation
            orig_speclist = copy.deepcopy(self.speclist)

            #Filter parameter and szs needed
            paridx = np.all(self.par_list==which_parameter,axis=1)
            szlist = np.ravel(self.sz_list)[paridx]
            szidx = szlist<=szmax
            szlist = szlist[szidx]
            replist = np.array(self.rep_list)[paridx][szidx]
            #Filter repstoplot
            if 'representations' in kwargs:
                repidx = self._filter_reps(replist, kwargs['representations'],
                                           return_idx=True)
                repstoplot = self._filter_reps(self.representations,
                                               kwargs['representations'])
            else:
                repidx = np.ones_like(replist, dtype='Bool')
                repstoplot = self.representations
            replist = replist[repidx]
            szlist = szlist[repidx]
            speclist = np.array(self.speclist)[paridx][szidx][repidx]

            #Lex-sort
            ind = np.lexsort((szlist,replist))[::-1]
            replist = replist[ind]
            szlist = szlist[ind]
            speclist = speclist[ind]

            #Go through all reps individually
            idx = 0
            while idx<len(replist):
                #last index with same rep
                repidx = len(replist)-np.searchsorted(replist[::-1],
                                                      replist[idx])

                minlength = min([len(x.eigenvalues)
                                 for x in speclist[idx:repidx]])
                evlist = np.array([x.eigenvalues[:minlength]
                                   for x in speclist[idx:repidx]])
                #print len(replist[idx:repidx])

                #check if sz=0 sector is here in different si-sectors
                num_sz_0 = np.sum(szlist[idx:repidx]==0)
                if num_sz_0>2:
                    raise ValueError('Works only for maximally 2 si ' +
                                     'sectors per sz')

                remove_idx = np.zeros_like(evlist, dtype='Bool')
                for i in range(len(evlist)):
                    sz = szlist[idx:repidx][i]
                    if sz==0:
                        break
                    restlist = evlist[i+1:,:]

                    for ev in evlist[i]:
                        #check if elements exist in every lower sz sector
                        if num_sz_0<=1:
                            rem_idx = np.abs(restlist-ev)<tol
                            check = np.all(np.any(rem_idx, axis=1))
                        elif num_sz_0==2:
                            rem_idx = np.abs(restlist-ev)<tol
                            check = np.any(rem_idx, axis=1)
                            check1 = np.all(check[:-1])
                            check2 = np.all(np.delete(check,-2))
                            check = np.logical_or(check1,check2)

                        #if check is ok, add indices to remove_idx
                        if check:
                            remove_idx[i+1:,:] = \
                                np.logical_or(remove_idx[i+1:,:],rem_idx)

                #remove elements
                evlist[remove_idx] = np.nan
                for i in range(len(evlist)):
                    speclist[idx:repidx][i].eigenvalues = evlist[i,:]


                #start next representation
                idx = repidx


        #Plot the TOS
        legaxes = 0
        leglabel = 0
        for sz in szplot:
            axes,legax,leglab = self.plot(which_sz=int(sz), xpos=[sz*(sz+1)],
                    singleplot=[-1,1,0], **kwargs)
            if sz==szplot[0]:
                legaxes = legax
                leglabel = leglab

        #Plot line along tower
        if showline:
            pars,excs,szs = self.get_parameters_excitations(return_sz=True)
            paridx = np.argwhere(np.all(pars==which_parameter,axis=1))
            paridx = int(paridx)
            excs = excs[paridx]
            szs = szs[paridx]
            toslevels = np.zeros(szmax+1, dtype='float')
            for i,s in enumerate(range(szmax+1)):
                szidx = np.ravel(szs)==s
                val = min(excs[szidx])
                toslevels[i] = val

            def fitfunc(x,a):
                return a*x
            popt, pcov = opt.curve_fit(fitfunc,self.szs[:szmax+1] *
                                       (self.szs[:szmax+1]+1),toslevels)
            plt.plot([0,szmax*(szmax+1)], fitfunc([0,szmax*(szmax+1)],popt),
                     '--k', zorder=-1)

        #Legend
        if len(leglabel):
            leglabel[0] += r'/0'
        for idx,lab in enumerate(leglabel):
            if 'Sz' in lab:
                leglabel = np.delete(leglabel,idx)
                legaxes = np.delete(legaxes,idx)
                break

        if 'figlegend' in kwargs and kwargs['figlegend']==True:
            plt.figlegend(legaxes, leglabel, **legkwargs)
        elif 'legend' in kwargs and kwargs['legend']==True:
            plt.legend(legaxes, leglabel, **legkwargs)


        if Smultiplets:
            plt.xlabel(r'$S(S+1)$')
        else:
            plt.xlabel(r'$S^z(S^z+1)$')
        plt.ylabel(r'$\Delta$')
        plt.xlim(-.5, szmax*(szmax+1)+.5)
        plt.xticks(self.szs[:szmax+1]*(self.szs[:szmax+1]+1))


        #Reset spectrum_collection
        if Smultiplets:
            self.speclist = orig_speclist

        if showline:
            return popt,pcov

    def write(self, directory, prefix):

        for spec, rep, pars, sf, sz in zip(self.speclist, self.rep_list,
                                           self.par_list, self.spinflip_list,
                                           self.sz_list):
            filename = os.path.join(directory, prefix)
            for par_idx, par in enumerate(pars):
                filename += ".J{0}.{1}".format(par_idx+1, par)
            filename += ".Sz.{0}".format(sz)
            filename += ".si.{0}".format(sf)
            filename += ".k.{0}".format(rep)
            spec.write(filename)
            print "wrote spectrum:", filename 
            

    @_axes_decorator
    def _plot(self, xpos=None, plot_parameter_idx=0, excitation_energies=True,
              num_excitations=None, yscale=1., xscale=1., representations=None,
              emptymarkers=False, symbols=None, colors=None, params_gs=None,
              which_spinflip=0, ax=None, sortfuncreps=None, plotparameters=None,
              allparameters=True, showallreps=False, which_sz=None,
              fixedsymbols=False, **kwargs):
        """
        Plot energies of loaded spectral data (:class:`Spectrum` objects).
        """
        if num_excitations is None:
            #plot all energies
            num_excitations = -1

        #set colors
        if colors is None:
            if StrictVersion(matplotlib.__version__) < StrictVersion('1.5.0'):
                colors = mpl.rcParams['axes.color_cycle']
            else:
                colors = [x['color'] for x in mpl.rcParams['axes.prop_cycle']]
        #colorcycle = itertools.cycle(colors)

        if emptymarkers:
            kwargs['mfc'] = 'None'
            if not ('mec' in kwargs or 'markeredgecolor' in kwargs):
                meccycle = True
            else:
                meccycle = False
        else:
            meccycle = True

        if 'szemptymarkers' in kwargs:
            szemptymarkers = kwargs['szemptymarkers']
            del kwargs['szemptymarkers']
        else:
            szemptymarkers = True

        #Define symbols
        if symbols is None:
            symbols = ['o','^','p','*','s','>','<','D','v']
        #symbolcycle = itertools.cycle(symbols)

        #Sort representations
        if sortfuncreps is None:
            def sortreps(x):
                if 'Gamma' in x or '0-0' in x:
                    return '0'+x
                elif 'M' in x or 'K' in x or 'X' in x or 'Y' in x \
                  or 'Sigma' in x or 'Delta' in x or 'Z' in x:
                    return '1'+x
                else:
                    return '2'+x
        else:
            sortreps = sortfuncreps
            self._sortfunc = sortreps
        repssorted = sorted(self.representations, key=sortreps)

        if fixedsymbols:
            #Apply symbols for repstoplot
            symbols = list(symbols)*(len(repssorted)/len(symbols)+1)
            symbols = symbols[:len(repssorted)]
            symbols = dict(zip(repssorted, symbols))
            #Apply colors for repstoplot
            colors = list(colors)*(len(repssorted)/len(colors)+1)
            colors = colors[:len(repssorted)]
            colors = dict(zip(repssorted, colors))

        #Define markersize
        if 'ms' in kwargs and kwargs['ms'] is not None:
            markersize = kwargs['ms']
            del kwargs['ms']
        elif 'markersize' in kwargs and kwargs['markersize'] is not None:
            markersize = kwargs['markersize']
            del kwargs['markersize']
        else:
            markersize = plt.rcParams['lines.markersize']

        #Define markersize difference for sz sectors
        if 'msdiffsz' in kwargs:
            msdiff = kwargs['msdiffsz']
            del kwargs['msdiffsz']
        else:
            msdiff = markersize/2.

        if not self.rep_list==[]:
            #Ground state energy
            if excitation_energies:
                if params_gs is None:
                    gs_energies = self._get_params_gs_energy()
                else:
                    gs_energies = np.zeros(len(self.par_list))
                    for i,param in enumerate(self.par_list):
                        idx = find_rows(param, params_gs[0])
                        gs_energies[i] = params_gs[1][idx]

            #check which reps to plot
            if representations is None:
                self._repstoplot = self.representations
            else:
               self._repstoplot = self._filter_reps(self.representations,
                                                    representations)

            #Sort repstoplot
            if sortfuncreps is None:
                def sortreps(x):
                    if 'Gamma' in x or '0-0' in x:
                        return '0'+x
                    elif 'M' in x or 'K' in x or 'X' in x or 'Y' in x \
                      or 'Sigma' in x or 'Delta' in x or 'Z' in x:
                        return '1'+x
                    else:
                        return '2'+x
            else:
                sortreps = sortfuncreps
                self._sortfunc = sortreps
            self._repstoplot = sorted(self._repstoplot, key=sortreps)

            if not fixedsymbols:
                #Apply symbols for repstoplot
                symbols = list(symbols)*(len(self._repstoplot)/len(symbols)+1)
                symbols = symbols[:len(self._repstoplot)]
                symbols = dict(zip(self._repstoplot, symbols))
                #Apply colors for repstoplot
                colors = list(colors)*(len(self._repstoplot)/len(colors)+1)
                colors = colors[:len(self._repstoplot)]
                colors = dict(zip(self._repstoplot, colors))

            #check yscale
            if isinstance(yscale,np.ndarray) or isinstance(yscale,list):
                if not len(yscale)==plotparameters.shape[0]:
                    raise ValueError('yscale must be a float or a ' +
                                     'list/np.ndarray with same length ' +
                                     'as plotparameters')
            elif isinstance(yscale,float) or isinstance(yscale,int):
                yscale = yscale * np.ones(plotparameters.shape[0],dtype=float)
            #dict for yscale
            yscale = dict(zip(plotparameters[:,plot_parameter_idx],yscale))

            #check xpos
            if not xpos is None:
                if type(xpos)==int or type(xpos)==float \
                   or isinstance(xpos, np.float64):
                    xpos = xpos*np.ones(len(plotparameters))
                xpos = np.array(xpos)
                if not len(xpos)==len(plotparameters):
                    raise ValueError('xpos array must be of the same length ' +
                                     'as plotparameters')
                #dict for xpos
                xposdict = dict(zip(plotparameters[:,plot_parameter_idx],xpos))
                xscale=1.

            #which representations to plot
            if not allparameters:
                idxrep = np.array([False]*len(self.par_list),dtype='bool')
                for p in plotparameters:
                    idxrep = np.logical_or(idxrep,np.all(self.par_list==p,
                                                         axis=1))
                #print 'partoplot=',self.par_list[idxrep]
            else:
                idxrep = np.array([True]*len(self.par_list),dtype='bool')

            axplotarray = []
            for rep in self._repstoplot:
                idx = np.array(self.rep_list)==rep
                idx = np.logical_and(idx,idxrep)

                #which spinflips to plot
                if len(self.spinflip_list)>0:
                    #check where spinflip fits
                    spinflipstoplot = np.array(self.spinflip_list)[idx]
                    spfidx = (spinflipstoplot==self.spinflips[which_spinflip])
                else:
                    #dont check a spinflip
                    spfidx = np.array([True]*np.sum(idx))

                #which szs to plot
                if len(self.sz_list)>0:
                    #check where sz fits
                    szforrep = np.array(self.sz_list)[idx]
                    szidx = (szforrep==which_sz).flatten()
                    sztoplot = szforrep[szidx]
                else:
                    #dont check a sz
                    szidx = np.array([True]*np.sum(idx))

                spidx = np.logical_and(spfidx,szidx)

                specstoplot = (np.array(self.speclist)[idx])[spidx]
                paramstoplot = (self.par_list[idx,plot_parameter_idx])[spidx]

                if not xpos is None:
                    xtoplot = np.array([xposdict[param]
                                        for param in paramstoplot])
                else:
                    xtoplot = paramstoplot

                if excitation_energies:
                    gstoplot = (gs_energies[idx])[spidx]

                #x,y-data
                yarr = np.array([])
                xarr = np.array([])
                for i in range(len(specstoplot)):
                    if excitation_energies:
                        yarr = np.append(yarr,
                                (specstoplot[i].eigenvalues[:num_excitations] -
                                 gstoplot[i])*yscale[paramstoplot[i]])
                    else:
                        yarr = np.append(yarr,
                                specstoplot[i].eigenvalues[:num_excitations] *
                                yscale[paramstoplot[i]])

                    xarr = np.append(xarr, xtoplot[i]*xscale*
                        np.ones_like(specstoplot[i].eigenvalues[:num_excitations]))

                if not xarr.size==0 or showallreps==True:
                    #Plotting
                    #symbol = next(symbolcycle)
                    symbol = symbols[rep]

                    #ms determined by sz (if sz available)
                    if len(self.sz_list):
                        ms = markersize + sztoplot[i] * msdiff
                        kwargs['ms'] = ms
                        kwargs['zorder'] = -sztoplot[i]
                        if sztoplot[i]!=0 and szemptymarkers is not False:
                            emptymarkers = True
                    else:
                        kwargs['ms'] = markersize

                    if not emptymarkers:
                        #kwargs['color'] = next(colorcycle)
                        kwargs['color'] = colors[rep]
                    elif emptymarkers and meccycle:
                        #kwargs['mec'] = next(colorcycle)
                        kwargs['mec'] = colors[rep]
                        kwargs['mfc'] = 'None'

                    axplot = ax.plot(xarr, yarr, symbol, **kwargs)
                    axplotarray.append(axplot[0])
                else:
                    axplotarray.append([])

        else:
            #xpos definition
            if xpos is None:
                self._xpos=np.arange(self.num)
            elif not len(xpos)==self.num:
                warnings.warn("Size of xpos is not identical to size of " +
                              "self.dsflist! Default values used!",
                              RuntimeWarning)
                self._xpos=np.arange(self.num)
                xscale=1.
            else:
                self._xpos=xpos
                xscale=1.

            #check yscale
            if isinstance(yscale,np.ndarray) or isinstance(yscale,list):
                if not len(yscale)==self.num:
                    raise ValueError('yscale must be a float or a ' +
                                     'list/np.ndarray with length self.num')
            elif isinstance(yscale,float) or isinstance(yscale,int):
                yscale = yscale * np.ones(self.num,dtype=float)

            axplotarray=[]
            for i,spec in enumerate(self.speclist):
                xarr = self._xpos[i]*np.ones_like(spec.eigenvalues)
                if excitation_energies:
                    yarr = spec.eigenvalues - np.min(spec.eigenvalues)
                else:
                    yarr = spec.eigenvalues

                if num_excitations:
                    xarr = xarr[:num_excitations]
                    yarr = yarr[:num_excitations]

                if not xarr.size==0 or showallreps==True:
                    axplot = ax.plot(xarr*xscale,yarr*yscale[i], '*', **kwargs)
                    axplotarray.append(axplot)
                else:
                    axplotarray.append([])

        return axplotarray



    def _filter_reps(self, representations, re_reps, return_idx=False):
        #Find which representations match re_reps
        idxmatch = np.array([False]*len(representations))
        for rep in re_reps:
            if not rep[-1]=='$':
                a = re.compile('.*'+rep+'.*')
            else:
                a = re.compile('.*'+rep)
            idx = [a.match(reptocheck)!=None for reptocheck in representations]
            idxmatch = np.logical_or(idxmatch,idx)
        if not return_idx:
            return np.array(representations)[idxmatch]
        if return_idx:
            return idxmatch




