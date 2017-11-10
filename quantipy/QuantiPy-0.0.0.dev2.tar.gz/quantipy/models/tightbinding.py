# -*- coding: utf-8 -*-
""" 
.. _tight-binding-label:

Tight Binding models
=========================

:author: Alexander Wietek

 Methods to analyse tight binding models on arbitrary lattices. This module
 can be used to calculate bandstructures and Chern numbers. 

 **Overview:**
   * :ref:`tight-binding-usage-examples-label`
   * :ref:`tight-binding-function-reference-label`



 .. _tight-binding-usage-examples-label:

 Usage Examples
 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  .. rubric:: Example / Simple tight-binding model on Graphene

  Create a Honeycomb lattice, define nearest neighbour hoppings, calculate the bandstructure 
  and plot it.::


      import numpy as np
      import matplotlib.pyplot as plt
      from mpl_toolkits.mplot3d import Axes3D
      import quantipy.lattice
      import quantipy.models

      # Create a default honeycomb lattice
      honeycomb = quantipy.lattice.Honeycomb()

      # Create nearest neighbour model on Honeycomb lattice
      model = quantipy.models.TightBinding(honeycomb)
      t = 1.0
      model.set_hopping(t, 0, 1)
      model.set_hopping(t, 1, 0, cell_shift_2=[1,0])
      model.set_hopping(t, 1, 0, cell_shift_2=[0,1])


      # Create a mesh in reciprocal space with 
      n_discretizing_points = 50
      k_mesh = []
      for i in np.linspace(-2*np.pi,2*np.pi,n_discretizing_points):
          for j in np.linspace(-2*np.pi,2*np.pi,n_discretizing_points):
              k_mesh.append( i*np.array([1., 0.]) + j*np.array([0., 1.]))


      # Calculate bandstructure  
      bands = model.get_bands(k_mesh)

      k_mesh = np.array(k_mesh)
      bands = np.array(bands)

      # Plot the band structure
      fig = plt.figure()
      ax = fig.gca(projection='3d')

      for i in range(honeycomb.n_basiscoordinates):
          ax.plot_trisurf(k_mesh[:,0],k_mesh[:,1],bands[:,i])


      ax.set_xlabel('X')
      ax.set_ylabel('Y')
      ax.set_zlabel('Z')
      ax.set_title(r"Band structure")
      plt.show()

 This produces the following plot:

 .. figure:: img_honeycomb_tb_nearest_neighbour.png
    :width:  500px
    :height: 400px
    :align:  center



 .. rubric:: Example / Spinliquid on the Kagome lattice

 Create a tight binding model on a six site unit cell Kagome lattice with 0 flux through
 the hexagons and :math:`\pi/2` flux through the hexagons, plot the 3d bandstructure and 
 calculate the Chern numbers of the bands::
 
     import numpy as np
     import matplotlib.pyplot as plt
     from mpl_toolkits.mplot3d import Axes3D
     import quantipy.lattice
     import quantipy.models 

     # Create six site unit cell Kagome lattice
     unit_cell = np.array([[4.,0.],[-1.,np.sqrt(3.)]])
     basis_coordinates = np.array([[0., 0.], [1.,0.], [0.5, np.sqrt(3.)/2.], [2., 0.], [3.,0.], [2.5, np.sqrt(3.)/2.]])
     kagome = quantipy.lattice.Lattice(unitcell = unit_cell, basiscoordinates = basis_coordinates)
     
     # Create tight binding model on Kagome lattice
     model = quantipy.models.TightBinding(kagome)
     
     # Set the hoppings that yield zero flux through hexagons and 
     # pi/2 flux through triangles
     model.set_hopping(np.exp(-1j*np.pi/6), 0, 1)
     model.set_hopping(np.exp(7j*np.pi/6) , 1, 3)
     model.set_hopping(np.exp(-1j*np.pi/6), 3, 4)
     model.set_hopping(np.exp(1j*np.pi/6) , 4, 0, cell_shift_2 = [1,0])
     model.set_hopping(np.exp(1j*np.pi/6) , 0, 2)
     model.set_hopping(np.exp(1j*np.pi/6) , 2, 1)
     model.set_hopping(np.exp(1j*np.pi/6) , 3, 5)
     model.set_hopping(np.exp(1j*np.pi/6) , 5, 4)
     model.set_hopping(np.exp(5j*np.pi/6) , 4, 2, cell_shift_1 = [-1, 1])
     model.set_hopping(np.exp(5j*np.pi/6) , 2, 0, cell_shift_2 = [0, 1])
     model.set_hopping(np.exp(5j*np.pi/6) , 1, 5, cell_shift_1 = [0, 1])
     model.set_hopping(np.exp(-1j*np.pi/6), 5, 3, cell_shift_2 = [0, 1]) 
     
     
     # Create a mesh in reciprocal space with boundaries of Brillouin zone
     bzedges = kagome.brillouin_zone_edges
     v1 = bzedges[0] - bzedges[1]
     v2 = bzedges[2] - bzedges[1]
     basis = bzedges[1]
     
     k_mesh = []
     for i in np.linspace(0,1,20):
         for j in np.linspace(0,1,10):
             k_mesh.append(basis + i*v1 + j*v2)
     
     # Calculate bandstructure and eigenvectors 
     (bands, evecs) = model.get_bands(k_mesh, get_eigenvectors = True)
     
     k_mesh = np.array(k_mesh)
     bands = np.array(bands)


     # Plot the band structure
     fig = plt.figure()
     ax = fig.gca(projection='3d')

     for i in range(6):
         ax.plot_trisurf(k_mesh[:,0],k_mesh[:,1],bands[:,i])


     ax.set_xlabel('X')
     ax.set_ylabel('Y')
     ax.set_zlabel('Z')
     ax.set_title(r"Band structure")
     plt.show()

     # Make finer grid for plotting Berry curvature
     k_mesh = []
     for i in np.linspace(0,1,50):
         for j in np.linspace(0,1,50):
             k_mesh.append(basis + i*v1 + j*v2)
     
     # Calculate bandstructure and eigenvectors again
     (bands, evecs) = model.get_bands(k_mesh, get_eigenvectors = True)
     
     k_mesh = np.array(k_mesh)
     bands = np.array(bands)

     # Calculate Chern numbers
     cns = quantipy.models.calc_chern_numbers(k_mesh,evecs)
     print "Chern numbers: ", cns

     # Plot berry curvature
     f, axarr = plt.subplots(3, 2)
     quantipy.models.plot_berry_curvature(k_mesh, evecs, band_index=0, vmin=-0.017, vmax = 0.017, ax=axarr[0,0])
     axarr[0,0].set_title("Band #1, CN: {0}".format(cns[0]))
     quantipy.models.plot_berry_curvature(k_mesh, evecs, band_index=1, vmin=-0.017, vmax = 0.017, ax=axarr[0,1])
     axarr[0,1].set_title("Band #2, CN: {0}".format(cns[1]))
     quantipy.models.plot_berry_curvature(k_mesh, evecs, band_index=2, vmin=-0.017, vmax = 0.017, ax=axarr[1,0])
     axarr[1,0].set_title("Band #3, CN: {0}".format(cns[2]))
     quantipy.models.plot_berry_curvature(k_mesh, evecs, band_index=3, vmin=-0.017, vmax = 0.017, ax=axarr[1,1])
     axarr[1,1].set_title("Band #4, CN: {0}".format(cns[3]))
     quantipy.models.plot_berry_curvature(k_mesh, evecs, band_index=4, vmin=-0.017, vmax = 0.017, ax=axarr[2,0])
     axarr[2,0].set_title("Band #5, CN: {0}".format(cns[4]))
     im = quantipy.models.plot_berry_curvature(k_mesh, evecs, band_index=5, vmin=-0.017, vmax = 0.017, ax=axarr[2,1])
     axarr[2,1].set_title("Band #6, CN: {0}".format(cns[5]))

     f.suptitle("Berry Curvature for six bands from lowest to highest")
     f.subplots_adjust(right=0.8)
     cax = f.add_axes([0.85, 0.1, 0.03, 0.8])
     f.colorbar(im, cax=cax)
     plt.show()



 The Chern numbers are evaluated as::

    Chern numbers:  [-1. -1.  1. -1.  1.  1.]

 and the following plots are produced

 .. figure:: img_kagome_sixsiteuc_spinliquid_pihalf_zero.png
    :width:  500px
    :height: 400px
    :align:  center

 .. figure:: img_berrycurv.png
    :width:  700px
    :height: 400px
    :align:  center


 .. _tight-binding-function-reference-label:

 Function and Class reference
 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


"""

import numpy as np
from scipy import linalg
from scipy.spatial import Delaunay
from scipy.interpolate import griddata
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from matplotlib.mlab import griddata
from quantipy.lattice import Lattice, read
from quantipy.utils import _axes_decorator, _axes_decorator_3d, _kwtolegkw

__all__ = ['TightBinding', 'calc_chern_numbers']


class TightBinding:
    """
    :class: TightBinding

    Class for describing tight binding models

    """

    def __init__(self, lattice):
        """ 
        Initializer of a tight binding model for a given Lattice instance

        :type lattice: QuantiPy Lattice object
        :param lattice: the lattice on which to define the tight binding model, must have Bravais unit 
            cell defined
        """
        if not isinstance(lattice, Lattice):
            raise ValueError("TightBinding.lattice must be a QuantiPy Lattice class object")
        if lattice.a1 is None or lattice.a2 is None:
            raise ValueError("TightBinding.lattice must have Bravais unit cell defined")
     
        
        self._lattice = lattice     
        self._dimension = lattice.dimension
        self._n_orbitals = lattice._n_basiscoordinates 
        self._hoppings = []
        self._onsite_potentials = [] 
        

    def set_hopping(self, amplitude, site1, site2, cell_shift_1 = None, cell_shift_2 = None):
        """ 
        Set a hopping term between two sites

        :param amplitude: the hopping amplitude from site 1 to site 2 (remark: in this order if not real)
        :type amplitude: complex
        :param site1: the first site of the hopping term
        :type site1: int
        :param site2: the second site of the hopping term
        :type site2: int
        :param cell_shift1: defines by how many bravais unit cells the first site is shifted, optional, 
                            defaults to [0,0]
        :type cell_shift1: list of int
        :param cell_shift2: defines by how many bravais unit cells the second site is shifted, optional, 
                            defaults to [0,0]
        :type cell_shift2: list of int
         """
        site1 = int(site1)
        site2 = int(site2)
        
        if (not site1 in range(self._n_orbitals)) or (not site2 in range(self._n_orbitals)):
            raise ValueError("Invalid orbital index given")
       
        # Check if shifts have right dimension
        if cell_shift_1 is None:
            cell_shift_1 = [0,0]
        else:
            if len(cell_shift_1) != self._dimension:
                raise ValueError("Length of cell_shift_1 must be equal to dimension of lattice")
                    
        if cell_shift_2 is None:
            cell_shift_2 = [0,0]
        else:
            if len(cell_shift_2) != self._dimension:
                raise ValueError("Length of cell_shift_2 must be equal to dimension of lattice")
                    
        self._hoppings.append([amplitude, site1, site2, cell_shift_1, cell_shift_2])     
    


    def _get_hamiltonian(self, k_point):
        """ Calculates the Hamiltonian for a given k point """
        k_point = np.array(k_point)
        if k_point.shape != (self._dimension,):
            raise ValueError("Wrong shape of k_point!")
 
        hamiltonian = np.zeros((self._n_orbitals,self._n_orbitals),dtype=complex)
        
        # Set the hopping terms
        for hopping in self._hoppings:
            site1 = hopping[1]
            site2 = hopping[2]
            cell_shift_1 = hopping[3]
            cell_shift_2 = hopping[4]

            # calculate connection vector 
            vec = ( self._lattice.basiscoordinates[site2,:] + cell_shift_2[0]*self._lattice.a1 + \
                        cell_shift_2[1]*self._lattice.a2 )   -   ( self._lattice.basiscoordinates[site1,:] + \
                        cell_shift_1[0]*self._lattice.a1 + cell_shift_1[1]*self._lattice.a2 )

            # Entry in Hamiltonian is hopping amplitude time s phase factor
            phase = np.exp(1.0j*np.dot(vec,k_point))
            entry = hopping[0]*phase

            hamiltonian[site1,site2] += entry
           
        # Add Hermitian conjugate
        hamiltonian += np.conjugate(np.transpose(hamiltonian))
        return -hamiltonian

        
    def get_bands(self, k_points, get_eigenvectors = False):
        """ 
        Calculates the Band structure for the tight binding model. The k points 
        for which to calculate the spectrum and eigenvectors (if specified) have to be 
        handed to this function. 

        :type k_points: list of numpy.ndarrays
        :param k_points: the k points for which to calculate the bandstructure
        :type get_eigenvectors: boolean
        :param get_eigenvectors: flag whether or not eigenvectors for the Hamiltonians are calculated 
                                 and returned
        :rtype: list of Numpy ndarrays, (list of Numpy ndarrays if  get_eigenvectors = True) 
        :return: Spectrum of Hamiltonian for each k-point, (Eigenvectors of Hamiltonian for each k-point)
        """
        
        spectra = []
        if get_eigenvectors:
            eigenvectors = []
        for k in k_points:
            H = self._get_hamiltonian(k)
            if get_eigenvectors:
                (eigs, eigvecs) = linalg.eigh(H)
                eigenvectors.append(eigvecs)
            else:
                eigs = linalg.eigvalsh(H)

            spectra.append(eigs)                

        if get_eigenvectors:
            return (spectra, eigenvectors)
        else:
            return spectra

    def eval_onebody_wavefunction(self, band_index, k_point, x, sublattice_index):
        """ 
        Evaluates the one-body wavefunction for a given band index and k-point. 

        :type band_index: int
        :param band_index: defines the band index in ascending order (i.e. 0 is the lowest band)
        :type k_point: numpy.ndarray
        :param k_point: the k point for which to evaluate the wavefunction
        :type x: numpy.ndarray
        :param x: the point in real space where to evaluate the wavefunction
        :type sublattice_index: int 
        :param sublattice_index: sublattice which x belongs to 
        :rtype: complex
        :return: the wavefunction with specified k, bandindex evaluated at x, normalized if simulation torus
                 is given, else unnormalized
        """

        k = [k_point]
        (eigs, evecs) = self.get_bands(k, get_eigenvectors=True)
        eig = eigs[0][band_index]
        evec = evecs[0][:,band_index]
        if hasattr(self._lattice,'_n_bravaiscoordinates'):
            return np.exp(1j*np.dot(k_point,x))*evec[sublattice_index]/ \
                np.sqrt(float(self._lattice._n_bravaiscoordinates))
        
        else:
            return np.exp(1j*np.dot(k_point,x))*evec[sublattice_index]

    @_axes_decorator_3d
    def plot_bandstructure(self, n_discretizing_points=15, ax=None, **kwargs):
        """ 
        generates a plot of the Band structure of the model

        :type n_discretizing_points: int 
        :param n_discretizing_points: number of linear points for discretizing BZ
        :param ax: Axes for plotting, **optional**. Default: Create new figure and axes
        :type ax: Axes object
        :type kwargs: *keyword arguments*
        :param kwargs: The kwargs can be used to set plot properties.
        :returns: Handles to plots    
        """

        k_mesh = self._lattice.get_brillouin_zone_mesh(n_discretizing_points)

        # Calculate bandstructure  
        (bands, evecs) = self.get_bands(k_mesh, get_eigenvectors = True)

        k_mesh = np.array(k_mesh)
        bands = np.array(bands)
        k_mesh = np.array(k_mesh)

        #Plot the band structure
        # fig = plt.figure()
        # ax = fig.gca(projection='3d')

        for i in range(self._lattice._n_basiscoordinates):
            ax.plot_trisurf(k_mesh[:,0],k_mesh[:,1],bands[:,i])

        ax.set_xlabel(r"$k_x$")
        ax.set_ylabel(r"$k_y$")
        ax.set_zlabel(r'$E$')

        return ax

def calc_chern_numbers(k_mesh,band_eigenvectors):
    """ 
    Numerically calculates the Chern numbers out of eigenvectors of a given Band structure
    
    .. warning:: k_mesh must contain boundary of Brillouin zone

    :type k_mesh: list of numpy.ndarrays
    :param k_mesh: a mesh in k space discretizing the Brillouin zone 
    :type band_eigenvectors: list of numpy.ndarrays
    :param band_eigenvectors: list of eigenvectors 
    :rtype: numpy.ndarray
    :return: Chern numbers for the given Bands
    """
    
    # Calculate a Delaunay Triangulation of the Brillouin zone
    triangulation = Delaunay(k_mesh)

    if band_eigenvectors[0].ndim is not 2:
        raise ValueError("Invalid band_eigenvectors given")
    if band_eigenvectors[0].shape[0] != band_eigenvectors[0].shape[1]:
        raise ValueError("Invalid band_eigenvectors given")

    n_orbitals = band_eigenvectors[0].shape[0]
    chern_numbers = np.zeros(n_orbitals)

    # Go through triangles and calculate gauge independent links
    for triangle in triangulation.simplices:
        for i in range(n_orbitals):
            v0 = (band_eigenvectors[triangle[0]])[:,i]
            v1 = (band_eigenvectors[triangle[1]])[:,i]
            v2 = (band_eigenvectors[triangle[2]])[:,i]

            U1 = np.vdot(v0,v1)/np.abs(np.vdot(v0,v1))
            U2 = np.vdot(v1,v2)/np.abs(np.vdot(v1,v2))
            U3 = np.vdot(v2,v0)/np.abs(np.vdot(v2,v0))
            
            chern_numbers[i] += np.angle(U1*U2*U3)
    
    chern_numbers /= 2*np.pi
    return chern_numbers



def plot_berry_curvature(k_mesh, band_eigenvectors, band_index, num_x_pts=200, num_y_pts=200, \
                         vmin=None, vmax= None, ax=None, **kwargs):
    """ 
    Plots the Berry curvature for a given k space mesh and corresponding eigenvectors of 
    the Hamilonian

    :type k_mesh: list of numpy.ndarrays
    :param k_mesh: a mesh in k space discretizing the Brillouin zone 
    :type band_eigenvectors: list of numpy.ndarrays
    :param band_eigenvectors: list of eigenvectors 
    :type band_index: list of numpy.ndarrays
    :param band_index: list of eigenvectors 
    :type num_x_pts: int
    :param num_x_pts: Number of discretization points used in x direction, optional, default is 200 
    :type num_y_pts: int
    :param num_y_pts: Number of discretization points used in y direction, optional, default is 200
    :type vmin: float
    :param vmin: minimum for normalization of luminance data in matplotlib pcolor plot, optional, default None  
    :type vmax: float
    :param vmax: maximum for normalization of luminance data in matplotlib pcolor plot, optional, default None  
    :return: matplotlib.collections.Collection instance. 
    """
    #handle legend keywords
    kwargs, legkwargs = _kwtolegkw(kwargs)
    
    # Calculate a Delaunay Triangulation of the Brillouin zone
    triangulation = Delaunay(k_mesh)
    
    if band_eigenvectors[0].ndim is not 2:
        raise ValueError("Invalid band_eigenvectors given")
    if band_eigenvectors[0].shape[0] != band_eigenvectors[0].shape[1]:
        raise ValueError("Invalid band_eigenvectors given")

    n_orbitals = band_eigenvectors[0].shape[0]
    chern_numbers = np.zeros(n_orbitals)

    xes = []
    yes = []
    berrycurv = []

    # Go through triangles and calculate gauge independent links
    for triangle in triangulation.simplices:
        v0 = (band_eigenvectors[triangle[0]])[:,band_index]
        v1 = (band_eigenvectors[triangle[1]])[:,band_index]
        v2 = (band_eigenvectors[triangle[2]])[:,band_index]

        U1 = np.vdot(v0,v1)/np.abs(np.vdot(v0,v1))
        U2 = np.vdot(v1,v2)/np.abs(np.vdot(v1,v2))
        U3 = np.vdot(v2,v0)/np.abs(np.vdot(v2,v0))
        
        xes.append(((k_mesh[triangle[0]] + k_mesh[triangle[1]] + k_mesh[triangle[2]])/3)[0])
        yes.append(((k_mesh[triangle[0]] + k_mesh[triangle[1]] + k_mesh[triangle[2]])/3)[1])
        berrycurv.append(np.angle(U1*U2*U3))


    xes = np.array(xes)
    yes = np.array(yes)
    berrycurv = np.array(berrycurv)

    xi = np.linspace(min(xes), max(xes), num_x_pts)
    yi = np.linspace(min(yes), max(yes), num_y_pts)

    X, Y = np.meshgrid(xi, yi)
    Z = griddata(xes, yes, berrycurv, xi, yi)
    if vmin is not None and vmax is not None:
        surf = plt.pcolor(X, Y, Z, vmin=vmin, vmax=vmax, **kwargs)
    else :
        surf = plt.pcolor(X, Y, Z, **kwargs)
    # surf = ax.imshow(Z)
    plt.axis("equal")
    # print "min berry curv: {0}  max berry curv: {1}".format(min(berrycurv),max(berrycurv))
    return surf
