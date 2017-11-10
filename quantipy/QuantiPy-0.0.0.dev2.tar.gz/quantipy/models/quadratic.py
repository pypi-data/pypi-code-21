# -*- coding: utf-8 -*-
""" 
.. _quadratic-label:

Quadratic bosonic models
=========================

:author: Andreas Parteli


 Methods to analyse two-dimensional quadratic bosonic models on arbitrary lattices. This module
 can be used to calculate bandstructures. 

 **Overview:**
   * :ref:`quadratic-usage-examples-label`
   * :ref:`quadratic-function-reference-label`

.. _quadratic-usage-examples-label:

Usage Examples
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 .. rubric:: Hamiltonian terms of square lattices

 Examples of quadratic terms in the Hamiltonian with according amplitudes (if only one site per unit cell
 exists, e.g. in the case of square lattices):

   * :math:`\sum_\mathbf{x} t\  a_\mathbf{x}^\dagger a_\mathbf{x}` \
   ,where :math:`t` is real (inversion symmetry), converts to :code:`model.set_onsite_potential(t, 0)`

   * :math:`\sum_\mathbf{x} p\  a_{\mathbf{x}+\mathbf{d}}^\dagger a_\mathbf{x}^\dagger + p^*\  a_{\mathbf{x}+\mathbf{d}} a_\mathbf{x}` \
   ,where :math:`p` is complex, converts to :code:`model.set_hopping(p, 0, 0, cell_shift_1=d)`

   * :math:`\sum_\mathbf{x} s\  a_\mathbf{x}^\dagger a_\mathbf{x}^\dagger + s^*\  a_\mathbf{x} a_\mathbf{x}`  \
   ,where :math:`s` is complex, converts to :code:`model.set_pairing(s, 0, 0)`

   * :math:`\sum_\mathbf{x} u\  a_{\mathbf{x}+\mathbf{d}}^\dagger a_\mathbf{x} + u\  a_{\mathbf{x}+\mathbf{d}} a_\mathbf{x}^\dagger` \
   ,where :math:`u` is real (inversion symmetry), converts to :code:`model.set_hopping(u, 0, 0, cell_shift_1=d)`


 .. rubric:: One-site (per unit cell) bosonic Hamiltonian with nearest neighbour hopping

 Let us consider an example of a quadratic bosonic Hamiltonian on a square lattice with nearest neighbor hopping and pairing in both directions. 
 The system consists of harmonic oscillators coupled to the neighbours via the square of the difference of the oscillator amplitude.
 The Hamiltonian then is

  .. math::

     H &= \\sum_{l,m} \\left[ \\left( \\omega_0 + \\frac{1}{\omega_0} \\right) a_{l,m}^\\dagger a_{l,m} + \
      \\frac{1}{\\omega_0} \\left( a_{l,m} a_{l,m} + a_{l,m}^\\dagger a_{l,m}^\\dagger \\right) \\right] + \\\\
     &+ \\frac{1}{2} \\sum_{l,m} [ \\frac{1}{\\omega_0} \\left( a_{l,m} a_{l,m} + a_{l,m}^\\dagger a_{l,m}^\\dagger \\right)  - \\\\
     &- \\frac{1}{\\omega_0} \\left( a_{l,m} a_{l+1,m} + a_{l,m}^\\dagger a_{l+1,m}^\\dagger + \
      a_{l,m} a_{l,m+1} + a_{l,m}^\\dagger a_{l,m+1}^\\dagger \\right) - \\\\
     &- \\frac{1}{\\omega_0} \\left( a_{l,m} a_{l+1,m}^\\dagger + a_{l,m}^\\dagger a_{l+1,m} + \
      a_{l,m} a_{l,m+1}^\\dagger + a_{l,m}^\\dagger a_{l,m+1} \\right) ],

 can be diagonalized analytically and has the dispersion

 .. math::

     E \\left( k_x,k_y \\right) = \\sqrt{ \\omega_0^2 + 4 \\sin^2 \\left( \\frac{k_x}{2} \\right) + 4 \\sin^2 \\left( \\frac{k_y}{2} \\right)}.

 It may be implemented as follows.::

    import numpy as np
    import matplotlib.pyplot as plt

    import quantipy.lattice
    import quantipy.models

    # Create a default honeycomb lattice
    square = quantipy.lattice.Square()
    # Create nearest neighbour model on Honeycomb lattice
    model = quantipy.models.Quadratic(square)

    w0 = 1.
    #onsite 
    model.set_onsite_potential((w0+2./w0), 0)
    model.set_pairing(1./w0, 0, 0)
    #first dimension
    model.set_pairing(-1./w0/2., 0, 0, cell_shift_2=[1,0])
    model.set_hopping(-1./w0/2., 0, 0, cell_shift_2=[1,0])
    #second dimension
    model.set_pairing(-1./w0/2., 0, 0, cell_shift_2=[0,1])
    model.set_hopping(-1./w0/2., 0, 0, cell_shift_2=[0,1])

    kvals=[[0,np.pi]] #k values you want to compute the spectrum at
    eig=model.get_bands(kvals) #set get_eigenvectors=true if needed

 .. rubric:: Linear spin wave theory for a Heisenberg model in a magnetic field on a honeycomb lattice

 A honeycomb lattice has two lattice sites per minimal unit cell. When implementing the Hamiltonian

  .. math ::

     H &=  3 J S \\ \\cos \\left( 2 \\theta \\right) \\left(  \\sum_i a_i^\\dagger a_i + \\sum_i b_j^\\dagger b_j  \\right) + \\\\
       &+ J S \\sum_{i,j} \\left[ - \\frac{1}{2} \\left(1 + cos \\left( 2 \\theta \\right) \\right) \\left( a_i^\\dagger b_j^\\dagger + a_i b_j \\right) \
           - \\frac{1}{2} \\left(cos \\left( 2 \\theta \\right) - 1 \\right) \\left( a_i^\\dagger b_j + a_i b_j^\\dagger \\right) \\right] + \\\\
       &+ 4 \\sin \\left( \\theta \\right) \\left( \\sum_i a_i^\\dagger a_i + \sum_j b_j^\\dagger b_j \\right)

 one has to take care of both sublattices like this:::

    import numpy as np
    import matplotlib.pyplot as plt

    import quantipy.lattice
    import quantipy.models

    # Create a default honeycomb lattice
    honeycomb = quantipy.lattice.Honeycomb()
    # Create nearest neighbour model on Honeycomb lattice
    model = quantipy.models.Quadratic(honeycomb)

    J=1.
    S=1./2.
    theta=np.pi/4
    #onsite for both sublattices
    model.set_onsite_potential(3*J*S*np.cos(2.*theta), 0)
    model.set_onsite_potential(3*J*S*np.cos(2.*theta), 1)

    model.set_pairing(-J*S/2.*(1+np.cos(2*theta)), 0, 1)
    model.set_pairing(-J*S/2.*(1+np.cos(2*theta)), 0, 1, cell_shift_1=[-1,0])
    model.set_pairing(-J*S/2.*(1+np.cos(2*theta)), 0, 1, cell_shift_1=[-1,1])
                    
    model.set_hopping(-J*S/2.*(np.cos(2*theta)-1), 0, 1)
    model.set_hopping(-J*S/2 *(np.cos(2*theta)-1), 0, 1, cell_shift_1=[-1,0])
    model.set_hopping(-J*S/2.*(np.cos(2*theta)-1), 0, 1, cell_shift_1=[-1,1])
                    
    model.set_onsite_potential(4.*np.sin(theta), 0)
    model.set_onsite_potential(4.*np.sin(theta), 1)

    kvals=[[0,np.pi]] #k values you want to compute the spectrum at
    eig=model.get_bands(kvals) #set get_eigenvectors=true if needed
    

.. _quadratic-function-reference-label:

Function and Class reference
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


"""

import numpy as np
import warnings

from quantipy.lattice import Lattice

__all__ = ['Quadratic']


class Quadratic:
    """
    :class: Quadratic

    Class for describing quadratic models

    """

    def __init__(self, lattice, statistics="bosonic"):
        """ 
        Initializer of a quadratic bosonic hamiltonian for a given Lattice instance

        :type lattice: QuantiPy Lattice object
        :param lattice: the lattice on which to define the tight binding model, must have Bravais unit 
            cell defined
        """
        if not isinstance(lattice, Lattice):
            raise ValueError("Quadratic.lattice must be a QuantiPy Lattice class object")
        if lattice.a1 is None or lattice.a2 is None:
            raise ValueError("Quadratic.lattice must have Bravais unit cell defined")
     
        
        self._lattice = lattice     
        self._statistics = statistics 
        if statistics == "bosonic":
            self._stat_sign = 1.
        elif statistics == "fermionic":
            self._stat_sign = -1.  
        else:
            raise ValueError("Statistics must be either bosonic or fermionic!")

        self._dimension = lattice.dimension
        self._n_orbitals = lattice._n_basiscoordinates 
        self._hoppings = []
        self._pairings = []
        self._onsite_potentials = [] 

    def set_onsite_potential(self, amplitude, site1):
        """ 
        Set a number operator term on a site (on-site potential). 'amplitude' is the coefficient of the
        term: creation(site1)-annihilation(site1).

        :param amplitude: the onsite potential for site1
        :type amplitude: real
        :param site1: the site of the term
        :type site1: int
         """     
        if isinstance(amplitude, complex):
            raise ValueError("Amplitude for on-site potential has to be real")
        no_cell_shift = [0,0]

        self._hoppings.append([amplitude/2., site1, site1, no_cell_shift, no_cell_shift])

    def set_hopping(self, amplitude, site1, site2, cell_shift_1 = None, cell_shift_2 = None):
        """ 
        Set a hopping term between two sites. 'amplitude' is the coefficient of the 
        creation(site2)-annihilation(site1) term while its complex conjugate belongs to the 
        annihilation(site2)-creation(site1) term.

        site1 and site2 have to be different if there is no cell_shift. For terms with site1==site2
        and both in the same unit cell the method set_onsite_potential() has to be used.

        :param amplitude: the hopping amplitude from site 1 to site 2 (remark: in this order if not real)
        :type amplitude: complex
        :param site1: the first site of the hopping term
        :type site1: int
        :param site2: the second site of the hopping term
        :type site2: int
        :param cell_shift1: defines by how many bravais unit cells the first site is shifted, optional, 
                            defaults to [0,0]
        :typehoppings cell_shift1: list of int
        :param cell_shift2: defines by how many bravais unit cells the second site is shifted, optional, 
                            defaults to [0,0]
        :type cell_shift2: list of int
         """     
        (site1, site2, cell_shift_1, cell_shift_2) = self._check_term_params(site1,site2,cell_shift_1,cell_shift_2) 

        no_cell_shift = [0,0]
        if site1 == site2 and cell_shift_1==no_cell_shift and cell_shift_2==no_cell_shift:
            raise ValueError("site1 can't be equal to site2 (no cell shifts). use set_onsite_potential() instead")

        self._hoppings.append([amplitude, site1, site2, cell_shift_1, cell_shift_2])     

    def set_pairing(self, amplitude, site1, site2, cell_shift_1 = None, cell_shift_2 = None):
        """ 
        Set a pairing term between two sites. 'amplitude' is the coefficient of the pair creation
        term while its complex conjugate is the one of the pair annihilation term.

        :param amplitude: the pair creation term amplitude of site 1 and site 2 (remark: order of site 1 and 2 arbitrary)
        :type amplitude: complex
        :param site1: the first site of the pairing term
        :type site1: int
        :param site2: the second site of the pairing term
        :type site2: int
        :param cell_shift1: defines by how many bravais unit cells the first site is shifted, optional, 
                            defaults to [0,0]
        :type cell_shift1: list of int
        :param cell_shift2: defines by how many bravais unit cells the second site is shifted, optional, 
                            defaults to [0,0]
        :type cell_shift2: list of int
         """
        (site1, site2, cell_shift_1, cell_shift_2) = self._check_term_params(site1,site2,cell_shift_1,cell_shift_2)                    

        self._pairings.append([amplitude, site1, site2, cell_shift_1, cell_shift_2])     

    def _check_term_params(self, site1, site2, cell_shift_1 = None, cell_shift_2 = None):

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

        return site1, site2, cell_shift_1, cell_shift_2
    


    def _get_hamiltonian(self, k_point):
        """ Calculates the Hamiltonian for a given k point """
        k_point = np.array(k_point)
        if k_point.shape != (self._dimension,):
            raise ValueError("Wrong shape of k_point!")
 
        #create a 2n*2n matrix of a special form to get the eigenvalues for k and -k (both have the same!)
        hamiltonian = np.zeros((2*self._n_orbitals,2*self._n_orbitals),dtype=complex)
        
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

            hamiltonian[site1,site2] += hopping[0]*phase
            hamiltonian[site2,site1] += np.conjugate(hopping[0]*phase)
            hamiltonian[self._n_orbitals+site1,self._n_orbitals+site2] += self._stat_sign*np.conj(hopping[0]*phase) 
            hamiltonian[self._n_orbitals+site2,self._n_orbitals+site1] += self._stat_sign*hopping[0]*phase
  



        # Set the pairing terms
        for pairing in self._pairings:
            site1 = pairing[1]
            site2 = pairing[2]
            cell_shift_1 = pairing[3]
            cell_shift_2 = pairing[4]

            # calculate connection vector 
            vec = ( self._lattice.basiscoordinates[site2,:] + cell_shift_2[0]*self._lattice.a1 + \
                        cell_shift_2[1]*self._lattice.a2 )   -   ( self._lattice.basiscoordinates[site1,:] + \
                        cell_shift_1[0]*self._lattice.a1 + cell_shift_1[1]*self._lattice.a2 )

            # Entry in Hamiltonian is hopping amplitude times phase factor
            phase = np.exp(1.0j*np.dot(vec,k_point))
            
            if (site1 != site2):
                hamiltonian[site1,self._n_orbitals+site2] += pairing[0]*phase
                hamiltonian[site2,self._n_orbitals+site1] -= pairing[0]*phase
                if self._statistics == "fermionic":
                    hamiltonian[self._n_orbitals + site1, site2] -= np.conj(pairing[0]*phase)
                    hamiltonian[self._n_orbitals + site2, site1] += np.conj(pairing[0]*phase)
            else:
                hamiltonian[site1, self._n_orbitals + site2] += pairing[0]*phase
                hamiltonian[self._n_orbitals + site1, site2] += np.conj(pairing[0]*phase)
                
            
        # D = -At
        assert np.allclose(hamiltonian[0:self._n_orbitals,0:self._n_orbitals] , \
                               -hamiltonian[self._n_orbitals:,self._n_orbitals:].T)

       
        # # B = -Bt
        # assert np.allclose(hamiltonian[0:self._n_orbitals,self._n_orbitals:] , \
        #                        -hamiltonian[0:self._n_orbitals,self._n_orbitals:].T)


        # # C = -Ct
        # assert np.allclose(hamiltonian[self._n_orbitals:, 0:self._n_orbitals] , \
        #                        -hamiltonian[self._n_orbitals:, 0:self._n_orbitals].T)

        # A = Ah
        assert np.allclose(hamiltonian[0:self._n_orbitals,0:self._n_orbitals] , \
                                np.conj(hamiltonian[0:self._n_orbitals,0:self._n_orbitals].T))

        # Bh = -C
        # assert np.allclose(hamiltonian[0:self._n_orbitals,self._n_orbitals:] , \
        #                         -np.conj(hamiltonian[self._n_orbitals:,0:self._n_orbitals].T))


        # Add Hermitian conjugate
        # hamiltonian += np.conjugate(np.transpose(hamiltonian))
                

        return hamiltonian

        
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
        eigenvectors = []

        for k in range(len(k_points)):
            #get hamiltonian matrix for this k_point
            h = np.matrix(self._get_hamiltonian(k_points[k]))
            # print h
            ##create commutation matrix
            #l=len(h)
            #g=np.matrix(np.diag([1]*(l/2)+[-1]*(l/2)))
            
            ##Cholesky decomposition h=K.H*K
            ##note numpy LA: y=cholesky(x) -> x=y*y.H
            ##If function not positive definite try to add a little diagonal element eta
            #try:
                #K=np.linalg.cholesky(h) 
                
            #except np.linalg.LinAlgError:
                ##TODO!!
                ##eta=0.001
                ##K=np.linalg.cholesky(h+np.matrix(np.diag([eta]*l)))
                #eva = np.real(np.linalg.eig(np.dot(g,h))[0])
                #eva.sort()
                #spectra.append(eva[l/2:l][::-1].tolist())
                ##spectra.append(eva.tolist())
                
                #print "eva k=(" + ",".join(map(str,k_points[k])) + ")"
                #if get_eigenvectors:
                    #eigenvectors.append([])
                #continue
            
            #K=K.H   #to have h=K.H*K
            
            ##Bogoliubov trafo steps start here
            #K2=K*g*K.H

            #D,U=np.linalg.eigh(K2)

            ##sort eigenvalues and vectors in descending order
            #idx=np.argsort(D)[::-1]
            #D=D[idx]
            #U=U[:,idx]
            
            ##Energies & Transformation matrix
            #E=g*np.diag(D)
            #T=np.linalg.inv(K)*U*np.sqrt(E)

            #spectra.append(E.diagonal().tolist()[0][0:l/2])
            np.set_printoptions(precision=3,linewidth=400)
            # print "+++++++++++++++++++"
            # print np.real(h)
            l = h.shape[0]/2
            # print np.real(h[l:,:l]) 
            # print np.abs(h[l:,:l] + np.transpose(h[l:,:l])) < 1e-10

            assert np.allclose(h[:l,:l],h[:l,:l].H) #A.H = A.H
            assert np.allclose(h[l:,l:],h[l:,l:].H) #D.H = D.H
            assert np.allclose(h[l:,l:], -np.conj(h[:l,:l])) # D = -A.C 
            assert np.allclose(h[:l,l:],-np.transpose(h[:l,l:])) # B = -B.T
            assert np.allclose(h[l:,:l],-np.transpose(h[l:,:l])) # C = -C.T
            assert np.allclose(h[l:,:l],h[:l,l:].H) # C = B.H

            print np.linalg.det(h[:l,:l])

            print "-------------------"
            if not get_eigenvectors:
                E = _bogoliubov(h, statistics=self._statistics)
            else:
                E,T = _bogoliubov(h, statistics=self._statistics, get_eigenvectors=True)

            spectra.append(E)
            if get_eigenvectors:
                eigenvectors.append(T)

        if get_eigenvectors:
            return (spectra, eigenvectors)
        else:
            return spectra



def _bogoliubov(h, statistics="bosonic", get_eigenvectors=False):
    """
    Compute the bosonic bogoliubov transformation of a Matrix h.
    """
    h = np.matrix(h)
    l=len(h)

    if statistics == "fermionic":
        g=np.matrix(np.diag([1]*(l/2)+[-1]*(l/2)))
        E,T = np.linalg.eigh(h)
        #sort eigenvalues and vectors in descending order
        # idx=np.argsort(E)[::-1]
        # E=E[idx]
        # T=T[:,idx]

    elif statistics == "bosonic":
        #create commutation matrix
        g=np.matrix(np.diag([1]*(l/2)+[-1]*(l/2)))

        #Cholesky decomposition h=K.H*K
        #note numpy LA: y=cholesky(x) -> x=y*y.H
        #If function not positive definite try to add a little diagonal element eta
        try:
            K=np.linalg.cholesky(h) 

        except np.linalg.LinAlgError:
            warnings.warn('Matrix to diagonalize is not positive definite')
            eva = np.real(np.linalg.eigvals(np.dot(g,h)))
            # eva.sort()
            E = eva[0:l/2]

            #print "eva k=(" + ",".join(map(str,k_points[k])) + ")"
            if get_eigenvectors:
                return (E,[])
            else:
                return E

        K=K.H   #to have h=K.H*K

        #Bogoliubov trafo steps start here
        K2=K*g*K.H

        D,U=np.linalg.eigh(K2)

        #sort eigenvalues and vectors in descending order
        idx=np.argsort(D)[::-1]
        D=D[idx]
        U=U[:,idx]

        #Energies & Transformation matrix
        E= g*np.diag(D)
        T=np.linalg.inv(K)*U*np.sqrt(E)

    #E = E.diagonal().tolist()[0][0:l/2]

        E = np.diag(E)[0:l/2]

    if get_eigenvectors:
        return (E,T)
    else:
        return E

