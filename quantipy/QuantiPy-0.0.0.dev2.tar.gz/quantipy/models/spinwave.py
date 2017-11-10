# -*- coding: utf-8 -*-
"""
.. _spinwave-label:

LSWT module
===========

:author: Michael Schuler
"""

import numpy as np
import matplotlib.pyplot as plt
import itertools

import quantipy.lattice as latt
from quantipy.models.quadratic import _bogoliubov
from quantipy.utils import _axes_decorator, find_rows, _kwtolegkw

__all__ = ['SpinWave']


class SpinWave:
    """
    :class: SpinWave

    Class for performing Linear Spin Wave Theory calculations.
    """

    def __init__(self, lattice):
        """
        Initialization:

        :type lattice: QuantiPy Lattice class
        :param lattice: The lattice to define the Spin model. Must contain Bravais-vectors and unit-cell.
        """
        if not isinstance(lattice, latt.Lattice):
            raise ValueError("SpinWave.lattice must be a QuantiPy Lattice class object")
        if lattice.a1 is None or lattice.a2 is None:
            raise ValueError("SpinWave.lattice must have Bravais unit cell defined")


        self.lattice = lattice  #: Initialized lattice object
        self._dimension = lattice.dimension
        self._n_orbitals = lattice._n_basiscoordinates
        self._n_mag_sublattices = lattice._n_basiscoordinates  # This is the minimal number of magnetic sublattices

        self._spin_interactions = []
        self._magnetic_fields = []

        self._magnetic_structure = []
        self._spin_value = 0

        self._Es = []
        self._Ts = []
        

    def set_spin_interaction(self, interaction_matrix, position1, position2, J=1.):
        """
        Set general two-body spin interaction between sites position1 (i) and position2 (j) with an
        interaction_matrix H_ij of the following form:

        :math:`(S_i^x \\; S_i^y \\; S_i^z) \\; H_{ij} \\; \\begin{pmatrix}S_j^x \\\\ S_j^y \\\\ S_j^z \\end{pmatrix}`

        position1 and position2 may be identical. The interaction is set for all unit-cells automatically.

        :type interaction_matrix: numpy.ndarray(3x3)
        :param interaction_matrix: The spin interaction matrix H_ij to be set.
        :type position1: numpy.ndarray(3x1)
        :param position1: Position 1 of the coupling 
                Specified as numpy array of the form: [n_a1, n_a2, n_basis].
                n_a1/2 define the unit-cell position as :math:`$n_{a1} \mathbf{a_1} + n_{a2} \mathbf{a_2}$`. 
                :math:`$n_{basis}$` gives the number of the basiscoordinate within the unit-cell.
        :type position2: numpy.ndarray(3x1)
        :param position2: Position 2 of the coupling. Specified equivalent to position1.
        :type J: float
        :param J: Coupling value of the interaction. **Optional**. Default: 1.
        """

        if not (isinstance(interaction_matrix,np.ndarray) and interaction_matrix.shape==(3,3)):
            raise ValueError('interaction_matrix must be a np.ndarray of shape (3,3)')

        self._check_position_parameters(position1)
        self._check_position_parameters(position2)

        self._spin_interactions.append([interaction_matrix,position1,position2, J])


    def set_magnetic_field(self, interaction_vector, J=1.):
        """
        Set a uniform magnetic field of the following form:
        
        :math:`\\sum_i J (h^x \\; h^y \\; h^z) \\cdot \\begin{pmatrix}S_i^x \\\\ S_i^y \\\\ S_i^z \\end{pmatrix}`

        with the interaction vector h and strength J. The interaction is set for all sites automatically.

        :type interaction_vector: numpy.ndarray(3x1)
        :param interaction_vector: The spin interaction vector h_i to be set. It is normalized to a unit vector.
        :type J: float
        :param J: Strength of the magnetic field. **Optional**. Default: 1.
        """

        if len(self._magnetic_fields)>0:
            warnings.warn('A magnetic field was already set before. Multiple magnetic fields are now used!')

        if not (isinstance(interaction_vector,np.ndarray) and (interaction_vector.shape==(3,1) or interaction_vector.shape==(1,3) or interaction_vector.shape==(3,))):
            raise ValueError('interaction_vector must be a np.ndarray of shape (3,) or (3,1) or (1,3)')

        self._magnetic_fields.append([interaction_vector/np.linalg.norm(interaction_vector),J])


    def _check_position_parameters(self,position):
        """
        Check if position parameter arguments are in correct form.
        """
        if not (isinstance(position,np.ndarray) and (position.shape==(3,1) or position.shape==(1,3) or position.shape==(3,))):
            raise ValueError('position argument must be a np.ndarray of shape (3,) or (3,1) or (1,3)')

        if not (position[2] in range(self._n_orbitals)):
            raise ValueError('Invalid orbital index given in position arguments')

        return 0
        

    def set_magnetic_structure(self, positions, spin_directions, S=1./2., ext_unit_cell=None):
        """
        Define the magnetic structure explicitely by giving the spin-directions on lattice positions.
        The smallest possible magnetic unit-cell should be given!

        :type positions: np.ndarray(Nx3)
        :param positions: Array of positions of the spins to be set. Each entry has the form [n_a1, n_a2, n_basis].
                        For further details see :func:`set_spin_interaction`.
        :type spin_directions: np.ndarray(Nx3)
        :param spin_directions: Array of the directions where the classical spin at the corresponding position points to (in cartesian coordinates). The vectors are normalized to unit-vectors.
        :type S: float
        :param S: Spin value of the spins. **Optional**. Default = 1/2.
        :type ext_unit_cell: list/np.array(2x1)
        :param ext_unit_cell: [a,b] enlarges the bravais-vectors of the lattice as a*a1, b*a2.
                        Must be set if magnetic structure extends basis cell of the lattice.
        """
        for position in positions:
            self._check_position_parameters(position)

        if not (isinstance(spin_directions,np.ndarray) and spin_directions.shape[1]==3):
            raise ValueError('spin_directions must be a numpy.ndarray of the shape Nx3')

        if not positions.shape[0]==spin_directions.shape[0]:
            raise ValueError('positions and spin_directions arrays must be of the same length')

        #Check if spin is not a zero vector
        if np.any(np.all(spin_directions==0,axis=1)):
            raise ValueError('spin_directions must not contain a zero-vector')

        #Check if a spin is set on all basis-coordinates
        if not np.all(np.unique(positions[:,2])==np.arange(self._n_orbitals)):
            raise ValueError('Spins must be set on each basiscoordinate of the lattice at least!')

        #Normalize spins
        spin_directions = (spin_directions.T/np.linalg.norm(spin_directions, axis=1)).T

        #Number of magnetic sublattices is number of positions
        self._n_mag_sublattices = len(positions)

        self._magnetic_structure = [positions,spin_directions]
        self._spin_value = S

        #check extended magnetic structure
        if self._n_mag_sublattices==self._n_orbitals:
            self._unit_cell_factor = np.array([1,1])
        else:
            #AUTOMATIC DETERMINATION OF THE MAGNETIC UNIT_CELL WOULD BE GREAT
            if ext_unit_cell==None:
                raise ValueError('An extended unit cell ext_unit_cell must be defined when the magnetic structure is largen than the lattice basis_cell!')
            elif not len(ext_unit_cell)==2:
                raise ValueError('ext_unit_cell must be a list/numpy.ndarray with 2 entries')
            else:
                self._unit_cell_factor = np.array(ext_unit_cell)

        #Compute local coordinate system from magnetic structure
        self._local_coordinates()


    #def set_magnetic_structure_from_ordering_vector(self, Q, axis):
        #"""
        #TO DO !!
        #BETTER AS OPTION IN set_magnetic_structure ??
        #"""


    def plot_magnetic_structure(self, **kwargs):
        """
        Plot the magnetic structure on the lattice.
        
        :type kwargs: dict
        :param kwargs: kwargs for a 3d-quiver plot. **Optional**.
        """
        #handle legend keywords
        kwargs, legkwargs = _kwtolegkw(kwargs)
        
        from mpl_toolkits.mplot3d import Axes3D
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        if len(self._magnetic_structure)==0:
            raise ValueError('The magnetic structure must be defined before it can be plotted')

        #self.lattice.plot(ax=ax)
        
        #Compute coordinates
        coords = np.zeros((len(self._magnetic_structure[0])*25,3),dtype='float')
        directions = np.zeros_like(coords)
        count = 0
        for i,j in itertools.product([0,1,2,-1,-2],repeat=2):
            for k,pos in enumerate(self._magnetic_structure[0]):
                coords[count,:2] = pos[0]*self.lattice.a1 + pos[1]*self.lattice.a2 + self.lattice.basiscoordinates[pos[2]] + i*self._unit_cell_factor[0]*self.lattice.a1 + j*self._unit_cell_factor[1]*self.lattice.a2
                directions[count,:] = self._magnetic_structure[1][k]
                count += 1

        ax.quiver(coords[:,0],coords[:,1],coords[:,2],directions[:,0],directions[:,1],directions[:,2])
        ax.plot(coords[:,0],coords[:,1],np.zeros(len(coords)), 'o')
        ax.set_zlim3d([-3,3])

        #TO DO: shift vectors that centers are at points; better visualization; colors?


    def _local_coordinates(self):
        """
        Create us and vs for the local coordinate system
        """
        #Rs = [] #Rotation matrices are built by the vectors of the local coordinate system
        uvs = []
        for spin in self._magnetic_structure[1]:
            e3 = spin/np.linalg.norm(spin)
            e2 = np.cross(e3,np.array([1,0,0]))
            if np.linalg.norm(e2)<1e-10: #if spin parallel to [1,0,0]
                e2 = np.array([0,0,1])
            else:
                e2 = e2/np.linalg.norm(e2)
            e1 = np.cross(e2,e3)
            e1 = e1/np.linalg.norm(e1)
            #Rs.append(np.array([e1/np.linalg.norm(e1),e2/np.linalg.norm(e2),e3]))
            #define u and v vectors
            u = e1 + 1j*e2
            v = e3
            uvs.append([u,v])
        self._uvs = uvs
        

    def _quadratic_hamiltonians(self,karray):
        """
        Create quadratic Hamiltonian.
        
        :type karray: np.ndarray(n x 2)
        :param karray: Array of k-values for which the quadratic Hamiltonian should be computed
        """
        karray = np.array(karray)
        try:
            if not karray.shape[1]==2:
                raise ValueError('karray must be a np.ndarray of shape (nx2)')
        except IndexError:
            raise ValueError('karray must be a np.ndarray of shape (nx2)')

        Harray = []

        for k in karray:
            H = np.zeros([2*self._n_mag_sublattices, 2*self._n_mag_sublattices],dtype='complex')
            #A = np.zeros([self._n_mag_sublattices, self._n_mag_sublattices],dtype='complex')
            #B = np.zeros([self._n_mag_sublattices, self._n_mag_sublattices],dtype='complex')
            #C = np.zeros([self._n_mag_sublattices, self._n_mag_sublattices],dtype='complex')

            #loop through magnetic structure and determine which Hamiltonian connects to which other position
            for i,spin in enumerate(self._magnetic_structure[0]):
                #interactions between spins
                for ham in self._spin_interactions:
                    #check if Hamiltonian connects spin in both directions (-> check basisindex)
                    newbase_deltabrav = []
                    if spin[2]==ham[1][2]:
                        newbasis = ham[2][2]
                        deltabravais = ham[2][:2]-ham[1][:2]
                        newbase_deltabrav.append([newbasis,deltabravais])
                    if spin[2]==ham[2][2]:
                        newbasis = ham[1][2]
                        deltabravais = ham[1][:2]-ham[2][:2]
                        newbase_deltabrav.append([newbasis,deltabravais])

                    for nbase_deltab in newbase_deltabrav:
                        newbasis = nbase_deltab[0]
                        deltabravais = nbase_deltab[1]
                        #Compute newspin in basis_cell
                        newspin = np.zeros_like(spin)
                        newspin[:2] = (spin[:2]+deltabravais)%self._unit_cell_factor
                        newspin[2] = newbasis
                        #print 'spin, deltabravais, newspin = ', spin, deltabravais, newspin

                        #Compute index of newspin
                        newspinidx = find_rows(newspin, self._magnetic_structure[0])[0]
                        if len(newspinidx)==0:
                            raise ValueError('Could not find the new spin position')
                        elif len(newspinidx)>1:
                            raise ValueError('New spin position is not unique')
                        else:
                            newspinidx = newspinidx[0]

                        #distance vector
                        #print 'pos,newpos = ', spin,newpos
                        rij = deltabravais[0]*self.lattice.a1 + deltabravais[1]*self.lattice.a2 + self.lattice.basiscoordinates[newbasis] -self.lattice.basiscoordinates[spin[2]]
                        #print 'i, j, rij = ', i, newspinidx, rij

                        #Build Hamiltonian matrix
                        #Aij terms
                        #print 'gammapart = ',np.exp(1j*np.dot(k,rij))
                        #print 'uHu* = ', ham[3] * np.dot(self._uvs[i][0].T, np.dot(ham[0],np.conjugate(self._uvs[newspinidx][0])))
                        if i==newspinidx:
                            #print 'is this needed?'
                            H[i,newspinidx] += np.real(self._spin_value/2. * ham[3] * np.dot(self._uvs[i][0].T, np.dot(ham[0],np.conjugate(self._uvs[newspinidx][0]))) * np.exp(1j*np.dot(k,rij)))
                            H[i+self._n_mag_sublattices, newspinidx+self._n_mag_sublattices] += np.real( self._spin_value/2.* ham[3] * np.dot(self._uvs[i][0].T, np.dot(ham[0],np.conjugate(self._uvs[newspinidx][0]))) * np.exp(1j*np.dot(-k,rij)) )
                            #A[i,newspinidx] += np.real(self._spin_value/2. * ham[3] * np.dot(self._uvs[i][0].T, np.dot(ham[0],np.conjugate(self._uvs[newspinidx][0]))) * np.exp(1j*np.dot(k,rij)))
                        else:
                            H[i,newspinidx] += self._spin_value/2. * ham[3] * np.dot(self._uvs[i][0].T, np.dot(ham[0],np.conjugate(self._uvs[newspinidx][0]))) * np.exp(1j*np.dot(k,rij))
                            H[i+self._n_mag_sublattices, newspinidx+self._n_mag_sublattices] += np.conjugate( self._spin_value/2.* ham[3] * np.dot(self._uvs[i][0].T, np.dot(ham[0],np.conjugate(self._uvs[newspinidx][0]))) * np.exp(1j*np.dot(-k,rij)) )
                            #A[i,newspinidx] += self._spin_value/2. * ham[3] * np.dot(self._uvs[i][0].T, np.dot(ham[0],np.conjugate(self._uvs[newspinidx][0]))) * np.exp(1j*np.dot(k,rij))
                        #Bij terms
                        if i==newspinidx:
                            #print 'must be checked 1/2 oder 1/1 and if needed'
                            H[i,newspinidx+self._n_mag_sublattices] += 1./1.*np.real( self._spin_value/2. * ham[3] * np.dot(self._uvs[i][0].T, np.dot(ham[0],self._uvs[newspinidx][0])) * np.exp(1j*np.dot(k,rij)) )
                            H[newspinidx+self._n_mag_sublattices, i] += 1./1.*np.real( self._spin_value/2. * ham[3] * np.dot(self._uvs[i][0].T, np.dot(ham[0],self._uvs[newspinidx][0])) * np.exp(1j*np.dot(k,rij)) )
                            #B[i,newspinidx] += 1./1.*np.real( self._spin_value/2. * ham[3] * np.dot(self._uvs[i][0].T, np.dot(ham[0],self._uvs[newspinidx][0])) * np.exp(1j*np.dot(k,rij)) )
                        else:
                            H[i,newspinidx+self._n_mag_sublattices] += self._spin_value/2. * ham[3] * np.dot(self._uvs[i][0].T, np.dot(ham[0],self._uvs[newspinidx][0])) * np.exp(1j*np.dot(k,rij))
                            H[newspinidx+self._n_mag_sublattices, i] += np.conjugate( self._spin_value/2. * ham[3] * np.dot(self._uvs[i][0].T, np.dot(ham[0],self._uvs[newspinidx][0])) * np.exp(1j*np.dot(k,rij)) )
                            #B[i,newspinidx] += self._spin_value/2. * ham[3] * np.dot(self._uvs[i][0].T, np.dot(ham[0],self._uvs[newspinidx][0])) * np.exp(1j*np.dot(k,rij))
                        #Cii terms
                        H[i,i] += -self._spin_value * ham[3] * np.dot(self._uvs[i][1].T, np.dot(ham[0],self._uvs[newspinidx][1]))
                        H[i+self._n_mag_sublattices, i+self._n_mag_sublattices] += -self._spin_value * ham[3]* np.dot(self._uvs[i][1].T, np.dot(ham[0],self._uvs[newspinidx][1]))
                        #C[i,i] += -self._spin_value * ham[3] * np.dot(self._uvs[i][1].T, np.dot(ham[0],self._uvs[newspinidx][1]))

                #magnetic fields
                for hvec,J in self._magnetic_fields:
                    H[i,i] += -J*np.dot(hvec,self._uvs[i][1])
                    H[i+self._n_mag_sublattices,i+self._n_mag_sublattices] += -J*np.dot(hvec,self._uvs[i][1])

            Harray.append(H)
            #print 'A,B,C = ', A, B, C
        return Harray


    def get_dispersion(self, karray, get_T_matrix=False):
        """
        Get the dispersion relation (band energies) for points in k-space.

        :type karray: np.ndarray(n x 2)
        :param karray: Array of k-values for which the dispersion relation should be computed.
        :type get_T_matrix: Bool
        :param get_T_matrix: If True, the transformation matrices are also returned. **Optional**. Default: False
        :rtype: np.ndarray(len(karray) x n_mag_sublattices), [list(np.matrix) if get_T_matrix=True]
        :returns: Dispersion (energy bands) for each kpoint in k-array, [List of transformation matrices if get_T_matrix=True]
        """
        karray = np.array(karray)
        try:
            if not karray.shape[1]==2:
                raise ValueError('karray must be a np.ndarray of shape (nx2)')
        except IndexError:
            raise ValueError('karray must be a np.ndarray of shape (nx2)')

        
        Hs = self._quadratic_hamiltonians(karray)
        Es = np.zeros([len(Hs),len(Hs[0])/2])
        if get_T_matrix:
            Ts = []

        for i,H in enumerate(Hs):
            if not get_T_matrix:
                E = _bogoliubov(H)
            else:
                E,T = _bogoliubov(H, get_eigenvectors=True)
            
            Es[i,:] = E
            if get_T_matrix:
                Ts.append(T)

        self._Es = Es

        if not get_T_matrix:
            return Es
        else:
            self._Ts = Ts
            return (Es,Ts)


    @_axes_decorator
    def plot_dispersion(self, karray=None, xpos=None, ax=None, **kwargs):
        """
        Plot the dispersion relation along a path in k-space.
        
        :type karray: np.ndarray(n x 2)
        :param karray: Array of k-values for which the dispersion relation should be computed. **Optional**. Default: Take values from a previous call of :func:`get_dispersion`.
        :type xpos: np.ndarray(n x 1)
        :param xpos: Position on the x-axis to plot the energy data. **Optional**. Default. Unit spacing for each point in karray.
        :type ax: Axes object
        :param ax: Axes for plotting. **Optional**. Default: Create new figure and axes
        :param kwargs: Keywort arguments for a 2d plot.
        :returns: Handle to plot
        """
        #handle legend keywords
        kwargs, legkwargs = _kwtolegkw(kwargs)
        
        if not (len(self._Es) and karray==None):
            E = self.get_dispersion(karray)

        #Plotting
        if xpos==None:
            xpos = np.arange(len(self._Es))

        ax.plot(xpos, self._Es, **kwargs)
            
                #TO DO: get_gs_energy; compute spin-structure factor; implement set_nb_interaction() function
                    
#    def get_spin_structure_factor(self):
#        """
#        Get the Spin-Structure factor.
#        """
#        Y = np.zeros([3,3,self._n_mag_sublattices,self._n_mag_sublattices], dtype='complex')
        

