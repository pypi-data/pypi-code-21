# -*- coding: utf-8 -*-
"""
 .. _dynspecfunc-label:

 dynspecfunc module
 ------------------

 Module for handling Dynamical correlation functions in QuantiPy
 
"""
import numpy as np
from scipy import linalg as LA
import matplotlib.pyplot as plt
import re #regular expressions
import warnings
import sys
from quantipy.utils import _axes_decorator, _axes_decorator_3d, _kwtolegkw
import quantipy.edspectra as spec

import numpy.ma as ma

##----------------------------------------------------------------------------------------------------------
##----------------------------------------------------------------------------------------------------------
##----------------------------------------------------------------------------------------------------------
def read_dyn_spec(file_or_list, tag="ofQ"):
    """
    Reads dynamical spectral functions from an output file or list of files of QMSpinDyn.
    
    :type file_or_list: str / list of str
    :param file_or_list: Filename of the input file or list of filenames.

    :type tag: str
    :param tag: Tag which identifies time integrated value of dyn spectral functions in input file(s), optional. Default is *"ofQ"*.
    
    :rtype: :class: DynSpecFunc / DSF_Collection
    :return: Quantipy :class:`DynSpecFunc` Object if input is a single file, Quantipy :class:`DSF_Collection` Object if input is a list of files. 
    """
    if (isinstance(file_or_list, list) and len(file_or_list)==0) or file_or_list==None:
        raise ValueError('Cannot read from an empty list!')
        
    elif isinstance(file_or_list, list) and len(file_or_list)>1:
        dsflist = np.array([],dtype=object)
        for filename in file_or_list:
            try:
                dsf = _read_dyn_spec_single(filename,tag=tag)
            except ValueError:
                dsf = -1
            dsflist = np.append(dsflist,dsf)

        #number of good dsf objects
        ngoodobjs = len(dsflist[dsflist!=-1])

        if ngoodobjs>1:
            return DSF_Collection(dsflist)
        elif ngoodobjs==1:
            return dsflist[dsflist!=-1]
        else:
            raise ValueError('Cannot read any of the files in the list!')

    else:
        if isinstance(file_or_list, list) and len(file_or_list)==1:
            file_or_list = file_or_list[0]

        dsflist =  _read_dyn_spec_single(file_or_list, tag=tag)
        return dsflist

def _read_dyn_spec_single(filename, tag):
    """
    Reads dynamical spectral functions from an output file of QMSpinDyn.
    
    :type filename: str
    :param filename: Filename of the input file.

    :type tag: str
    :param tag: Tag which identifies time integrated value of dyn spectral functions in input file, optional. Default is *"ofQ"*.
    
    :rtype: :class: DynSpecFunc
    :return: Quantipy :class:`DynSpecFunc` Object
    """
        
    # open file
    alphas_tmp=[]
    betas_tmp=[]
    energies_tmp=[]
    sofqs_tmp=[]
    tagfound = False    

    with open(filename, 'rb' ) as sofqfile:
        for line in sofqfile:
            entries = line.split(" = ")
            if "Energy" in entries[0]:
                value = float(entries[1])
                energies_tmp.append(value)
            if tag in entries[0]:
                value = float(entries[1])
                sofqs_tmp.append(value)     
                tagfound = True
            if "alpha[" in entries[0]:
                value = float(entries[1])
                alphas_tmp.append(value)
            if "beta[" in entries[0]:
                value = float(entries[1])
                betas_tmp.append(value)
    
    if not tagfound:
        raise ValueError("The specified tag '%s' cannot be found in the file!" %tag)
    if len(energies_tmp)>1:
        raise ValueError('More than one Energy value in file.')
    if len(sofqs_tmp)>1:
        raise ValueError('More than one spectral function value in file.')
    
    return DynSpecFunc(np.array(alphas_tmp), np.array(betas_tmp), energies_tmp[0], sofqs_tmp[0])

##----------------------------------------------------------------------------------------------------------
##----------------------------------------------------------------------------------------------------------
##----------------------------------------------------------------------------------------------------------
class DynSpecFunc:
    """
    :class: DynSpecFunc
    
    Provides tools to evaluate and visualize data for Dynamical Spectral functions (e.g. S(q,omega)) 
    from Exact Diagonalization techniques.
    """
    
    def __init__(self, alphas, betas, gsenergy=0., totalvalue=1.):
        """
        Constructor of DynSpecFunc class
        
        :type alphas: :class: numpy.ndarray
        :param alphas: Diagonal elements of the T-matrix which arise in the 
            Lanczos Algorithm when computing Dynamical Spectral Functions.
        
        :type betas: :class: numpy.ndarray
        :param betas: Subdiagonal elements of the T-matrix which arise in the 
            Lanczos Algorithm when computing Dynamical Spectral Functions.
        
        :type gsenergy: float
        :param gsenergy: Ground state Energy, optional. Default is 0.
        
        :type totalvalue: float
        :param totalvalue: Expectation value of the total (time-integrated) Spectral function, optional. Default is 1.
        """

        if isinstance(alphas,np.ndarray):
            self.alphas = alphas #:alpha values from Lanczos
        else:
            self.alphas = np.array(alphas)
        #check if alphas not empty   
        if not self.alphas.size:
            raise ValueError("DynSpecFunc.alphas must not be empty.")
            
        if isinstance(betas,np.ndarray):
            self.betas = betas #: beta values from Lanczos
        else:
            self.betas = np.array(betas)
        #check if betas not empty   
        if not self.betas.size:
            raise ValueError("DynSpecFunc.betas must not be empty.")
        
        #check if alphas and betas have same size
        if not (self.alphas.size==self.betas.size):
            raise ValueError("DynSpecFunc.alphas and DynSpecFunc.betas must have same size.")
        
        #check if gsenergy,totalvalue are floats
        if not isinstance(gsenergy,float):
            raise ValueError("DynSpecFunc.gsenergy must be a floating point number.")
        if not isinstance(totalvalue,float):
            raise ValueError("DynSpecFunc.totalvalue must be a floating point number.")
            
        self.gsenergy=gsenergy #: groundstate energy
        self.totalvalue=totalvalue #: Expectation value of time-integrated spectral function
        
        self._broad_spec_computed = False
        self.w=[] #: Values of energy/frequency to compute broadened spectral function
        self.eta=[] #: Broadening to compute broadened spectral function
        
        # Compute poles and weights
        self._dynpw=self._computepw()
               
        
    def __str__(self):
        """
        Returns a short summary of the Dynamical Spectral Function.
        
        :rtype: str
        :return:  Short summary of the Dynamical Spectral Function with length of alphas/betas,
            values of Ground state energy and time-integrated Spectral function
        """
        
        out=("DynSpecFunc class: # alphas/betas = " + str(self.alphas.size) + 
             ", gsenergy = " + str(self.gsenergy) + ", time-integrated Spectral weight (totalvalue) = " + str(self.totalvalue) )
        
        if not self._broad_spec_computed:
            out += ", Broadened spectral function not computed!"
        else:
            out += ", Broadened spectral function computed for w in range [" + str(np.min(self.w)) + "," + str(np.max(self.w)) + "] and eta = " + str(self.eta) + "."
        
        return out
    
    ## --------------------------------------------------------------------------
    ## Functions to compute poles and weights following
    def _computepw(self):
        """
        (Non-public) Compute poles and weights from input parameters.
        """
        #Construct T-Matrix
        #T=np.diag(self.alphas,0) + np.diag(self.betas[:-1],-1) + np.diag(self.betas[:-1],1)

        #Compute Eigensystem
        #w,v=LA.eigh(T)
        w,v=LA.eig_banded((self.alphas,self.betas),lower=True)  #faster than eigh

        #Poles & Weight
        poles=w-self.gsenergy
        weight=abs(v[0,:])**2 * self.totalvalue

        #Combine close poles
        polesnew=[poles[0]]
        weightnew=[weight[0]]
        for j in range(len(poles)-1):
            if (poles[j+1]-poles[j]) > 1e-4:
                polesnew.append(poles[j+1])
                weightnew.append(weight[j+1])
            else:
                weightnew[-1]+=weight[j+1]
        
        dynpw={'pol': np.array(polesnew),
                    'wei': np.array(weightnew)}
        
        return dynpw
    
    
    def polesweight(self):
        """
        Returns poles and weights of Dynamical Spectral Function.
        
        :rtype: Python dictionary {'pol', 'wei'}
        :return: Dictionary with poles ('pol') and weights('wei') of the computed Dynamical Spectral Function.
        """
        return self._dynpw
    
    ## --------------------------------------------------------------------------
    ## Functions to compute broadened spectral function following
    def compute_broad_spec(self,w=[],eta=0.1):
        """
        Compute broadened dynamical spectral function.
 
        :type w: :class: numpy.ndarray
        :param w: The domain of excitation energies above which the broadened structure factor
            is computed, optional. Default is the range *(0,1)*.
        
        :type eta: float
        :param eta: Strength of the broadening (width of Lorentzian), optional.
            Default is *0.1*. 
        """

        #Check recursion limit ok?
        maxrec = sys.getrecursionlimit()
        if len(self.alphas)>=maxrec:
            raise ValueError('Set maximum recursion depth larger then number of iterations (length of alphas). Use sys.setrecursionlimit() to do so!')

        if w==[]:
            self.w=np.linspace(0,1)
        else:
            self.w=np.array(w)
        self.eta=eta

        zall=np.array(self.w)+self.gsenergy+self.eta*1.j
        dyns=np.zeros_like(self.w)
        
        for z in xrange(len(zall)):
            cf=self._contfrac(zall[z])
            dyn=-1./np.pi * cf.imag * self.totalvalue
            dyns[z]=dyn
        
        self._broadspec=dyns
        self._broad_spec_computed = True


    def _contfrac(self,z,pos=0):
        """ 
        (Non-public) Continued fraction for complex number z(=omega+E0+i*epsilon).
        
        :type z: :class: numpy.ndarray
        :param z: Values for which continued fraction should be evaluated. Typically: z=omega+E0+i*epsilon.
        
        :rtype: :class: numpy.ndarray
        :return: Continued fraction for all values in z. 
        """
        if (pos==len(self.alphas)):
            return 0
        elif pos==0:   
            return 1./(z-self.alphas[pos]-self._contfrac(z,pos+1) )
        else:
            return self.betas[pos-1]**2/(z-self.alphas[pos]-self._contfrac(z,pos+1) )

    
    def return_broad_spec(self):
        """
        Returns broadened dynamical spectral function.
        Broadened spectral function must be previously computed with :func:`DynSpecFunc.compute_broad_spec`!
        
        :rtype: :class: numpy ndarray
        :return: * Evaluation points w.
                 * Broadened dynamical spectral function evaluated at points in w, broadened with eta.
        """
        if self._broad_spec_computed:
            return self.w, self._broadspec
        else:
            raise ValueError("Broadened Spectral function has not yet been computed. Use compute_broad_spec(w,eta) to compute it!")
    
    ## --------------------------------------------------------------------------
    ## Plotting functions following

    @_axes_decorator
    def plot(self, ax=None, xscale=1., yscale=1., **kwargs):
        """
        Plot the raw poles and weights of the spectral function.

        :type ax: Axes object
        :param ax: Axes for plotting, **optional**. Default: Create new figure and axes
        :type xscale: float
        :param xscale: Scale the x-axis (energies) by this factor. **Optional**.
        :type yscale: float
        :param yscale: Scale the y-axis (weight) by this factor. **Optional**.
        :type kwargs: *keyword arguments*
        :param kwargs: The kwargs can be used to set plot properties.
        :returns: Handle to plot
        """
        #handle legend keywords
        kwargs, legkwargs = _kwtolegkw(kwargs)
        
        axplot = ax.plot(self._dynpw['pol']*xscale, self._dynpw['wei']*yscale, 'o', **kwargs)
        ax.set_xlabel(r'$\omega$', fontsize=16)
        ax.set_ylabel(r'Weight', fontsize=16)
        return axplot


    @_axes_decorator
    def plot_broad_spec(self, filled=False, ax=None, xscale=1., yscale=1., **kwargs):
        """
        Plots the broadened spectral function against the excitation energies w. 
        Broadened spectral function must be previously computed with :func:`DynSpecFunc.compute_broad_spec`!
        
        :type filled: Boolean
        :param filled: If True plot is filled, optional. Default: False
        :type ax: Axes object
        :param ax: Axes for plotting, **optional**. Default: Create new figure and axes
        :type xscale: float
        :param xscale: Scale the x-axis (energies) by this factor. **Optional**.
        :type yscale: float
        :param yscale: Scale the y-axis (weight) by this factor. **Optional**.
        :type kwargs: *keyword arguments*
        :param kwargs: The kwargs can be used to set plot properties.
        :returns: Handle to plot
        
        .. rubric:: Example

        >>> import quantipy.correlations as corrs
        >>> import numpy as np
        >>> dsf=corrs.read_dyn_spec("tests/files_dynsofq/DynamicalSofQ.Sz.k.0.q.0.Honeycomb.tJ.32.t.0.JHB.0.00.JK.-1.00.Np.32.NoSz.GS.rep.0")
        >>> dsf.compute_broad_spec(w=np.linspace(0,1.6,100), eta=.1)
        >>> dsf.plot_broad_spec(filled=True, lw=2, ls ='--')
        <matplotlib.axes.AxesSubplot object at 0x40bca90>
        
        .. figure::  img_plot_broad_spec_func.png
           :width:  500px
           :height: 400px
           :align:  center

           Sample plot of plot_broad_spec()
        """
        #handle legend keywords
        kwargs, legkwargs = _kwtolegkw(kwargs)
        
        if self._broad_spec_computed:
        
            axplot = ax.plot(self.w*xscale, self._broadspec*yscale, **kwargs)
            if filled:
                #get color of line
                col = plt.getp(axplot[0],'c')
                axplot = ax.fill_between(self.w*xscale, 0, self._broadspec*yscale, alpha=.3, color=col)
        
            ax.set_ylim([0,1.1*np.max(self._broadspec*yscale)])
            ax.set_xlim([np.min(self.w*xscale), np.max(self.w*xscale)]) 
            ax.set_xlabel(r'$\omega$', fontsize=16)
            ax.set_ylabel(r'Weight', fontsize=16)
            ax.set_title(r'Broadening $\eta = %g$' %(self.eta), fontsize=16)
        
            return axplot

        else:
            raise ValueError("Broadened Spectral function has not yet been computed. Use compute_broad_spec(w,eta) to compute it!")
        


    def plot_poles_convergence(self, log=False, **kwargs):
        """
        Compare poles with Lanczos convergence.

        :type log: Boolean
        :param log: If true, plot weight of poles logarithmically. **Optional**.
        :type kwargs: *keyword arguments*
        :param kwargs: The kwargs can be used to set plot properties of the poles-weight plot.
        :returns: Figure; Both axes in figure; Handles to convergence plot, poles, horizontal lines in poles plot.


        .. rubric:: Example

        >>> import quantipy.correlations as corrs
        >>> import numpy as np
        >>> dsf=corrs.read_dyn_spec("tests/files_dynsofq/DynamicalSofQ.Sz.k.0.q.0.Honeycomb.tJ.32.t.0.JHB.0.00.JK.-1.00.Np.32.NoSz.GS.rep.0")
        >>> fig, axes, handles = dsf.plot_poles_convergence()
        >>> plt.ylim(-6.5,-4.5)
        >>> # Adjust subplots
        >>> fig.subplots_adjust(wspace=0.05)
        >>> plt.show()
        
        .. figure::  img_correlations_plot_poles_convergence.png
           :width:  500px
           :height: 333px
           :align:  center

           Sample plot of :func:`plot_poles_convergence`
        """
        #handle legend keywords
        kwargs, legkwargs = _kwtolegkw(kwargs)
        
        # Compute spectrum
        spectrum = spec.Spectrum(eigenvalues=np.array([]), alphas=self.alphas, betas=self.betas)
        
        # Plotting
        fig = plt.figure()
        ax1 = fig.add_subplot(121)
        axspec = spectrum.plot_convergence(ax=ax1, marker='o', c='k', ms=1)

        ax2 = fig.add_subplot(122, sharey=ax1)
        axpoles = ax2.plot(self._dynpw['wei'], self._dynpw['pol']+self.gsenergy, 'o', **kwargs)
        axlines = ax2.hlines(self._dynpw['pol']+self.gsenergy, 0, self._dynpw['wei'])
        
        if log:
            plt.xscale('log')
            plt.xlim(1e-6, 1e2)

        ax2.yaxis.tick_right()
        ax2.yaxis.set_label_position('right')
        plt.xlabel(r'Weight')
        plt.ylabel(r'Energy')
    
        return fig, [ax1,ax2], [axspec,axpoles,axlines]






##----------------------------------------------------------------------------------------------------------
##----------------------------------------------------------------------------------------------------------
##----------------------------------------------------------------------------------------------------------
class DSF_Collection:
    """
    :class: DSF_Collection
    
    Provides tools to visualize (and evaluate) multiple :class:`DynSpecFunc` objects simultaneously.
    """

    def __init__(self,dsflist):
        """
        Constructor of :class:`DSF_Collection`.
        
        :type dsflist: python list
        :param dsflist: List of :class:`DynSpecFunc` objects.
        """
        
        #check if dsflist is in correct form
        if not (isinstance(dsflist, np.ndarray) or isinstance(dsflist,list)):
            raise ValueError("Input must be a np.ndarray or list of DynSpecFunc objects.")
        
        #initialize dsflist,num ....
        self.dsflist = np.array(dsflist)
        self._gooddsfidx = self.dsflist!=-1
        self.num = len(dsflist)
        self._num_good = np.sum(self._gooddsfidx)
        self._broad_spec_computed = False

    def __str__(self):
        """
        Returns a short summary of the class.
        """
        out="DSF_Collection class. # DynSpecFunc objects = " + str(self.num)

        if not self.num==self._num_good:
            out += ", # good objects = " + str(self._num_good)

        if not self._broad_spec_computed:
            out += ", Broadened spectral functions not computed!"
        else:
            out += ", Broadened spectral functions computed for w in range [" + str(np.min(self.w)) + "," + str(np.max(self.w)) + "] and eta = " + str(self.eta) + "."
        return out


    def __len__(self):
        """
        Returns the number of :class:`DynSpecFunc` objects in the collection.
        """
        return self.num
    

    def compute_broad_spec(self,w=[],eta=0.1):
        """
        Compute broadened dynamical spectral function for all :class:`DynSpecFunc` objects in :class:`DSF_Collection`.
 
        :type w: :class: numpy.ndarray
        :param w: The domain of excitation energies above which the broadened structure factors
            are computed, optional. Default is the range *(0,1)*.
        
        :type eta: float
        :param eta: Strength of the broadening (width of Lorentzian), optional.
            Default is *0.1*. 
        """
        #Initialize Parameters
        if w==[]:
            self.w=np.linspace(0,1)
        else:
            self.w=np.array(w)
        self.eta=eta
        
        #Compute broadened spectral functions
        for dsf in self.dsflist[self._gooddsfidx]:
            dsf.compute_broad_spec(self.w, self.eta)
        
        self._broad_spec_computed = True


    @_axes_decorator
    def plot(self, ax=None, **kwargs):
        """
        Plot the raw poles and weights of the spectral functions (See :func:`DynSpecFunc.plot`).

        :type ax: Axes object
        :param ax: Axes for plotting, **optional**. Default: Create new figure and axes
        :type kwargs: *keyword arguments*
        :param kwargs: The kwargs can be used to set plot properties.
        :returns: Handles to plot
        """
        hpall = []
        for dsf in self.dsflist[self._gooddsfidx]:
            hp = dsf.plot(ax=ax, **kwargs)
            hpall.append(hp)
        return hpall


    @_axes_decorator
    def plot_broad_spec_pcolor(self, xpos=[], ax=None, **kwargs):
        """
        Create pcolor-plot of broadened spectral functions of :class:`DynSpecFunc` objects in :class:`DSF_Collection`. 

        :type xpos: :class: numpy.ndarray
        :param xpos: x-positions to plot poles/weights of :class:`DynSpecFunc` objects, **optional**.
                     Default is linear spacing with unit distance.
        
        :type ax: Axes object
        :param ax: Axes for plotting, **optional**. Default: Create new figure and axes

        :type kwargs: *keyword arguments*
        :param kwargs: The kwargs can be used to set plot properties of a pcolor.
        
        :return: Handle to plot

        .. rubric:: Example

        >>> import quantipy.correlations as corrs
        >>> import numpy as np
        >>> import matplotlib.pyplot as plt

        >>> Szall=np.arange(0,15)
        >>> dsfall=[]
        >>> for i in Szall:
        ...     name="tests/files_dynsofq/DynamicalSofQ.Sz.k.11.q.30.Honeycomb.tJ.30.t.0.JHB.1.00.JK.0.00.Np.30.Sz.%i.si.0.Sznew.%i.sinew.0.GS.rep.0" %(i, i)
        ...     dsfall.append(corrs.read_dyn_spec(name))

        >>> dsfcoll=corrs.DSF_Collection(dsfall)
        >>> dsfcoll.compute_broad_spec(w=np.linspace(0,4,100), eta=.05)
            
        >>> fig, axbroad, axplot=dsfcoll.plot_broad_spec_pcolor(cmap='gist_earth_r')
        >>> cb=fig.colorbar(axplot)
        >>> cb.set_label(r'weight', fontsize=16)
        >>> axbroad.set_xlabel(r'$S^z$', fontsize=16)
        >>> axbroad.set_ylabel(r'$\omega$', fontsize=16)
        >>> axbroad.set_xlim([0,15])
        >>> plt.show()
        
        .. figure:: img_DSF_Collection_plot_broad_spec_pcolor.png
           :width:  500px
           :height: 400px
           :align:  center

           Sample plot of :func:`plot_broad_spec_pcolor` for :class:`DSF_Collection` objects

        """
        #handle legend keywords
        kwargs, legkwargs = _kwtolegkw(kwargs)
        
        #Values should be sorted ?
        mustsort = False

        #Initialize xpos
        if xpos==[]:
            _xpos=np.arange(self.num)
        elif not len(xpos)==self.num:
            warnings.warn("Size of xpos is not identical to size of self.dsflist! Default values used!", RuntimeWarning)
            _xpos=np.arange(self.num)
        else:
            _xpos=np.array(xpos)
            mustsort = True

        #Sort xpos and data if necessary
        if mustsort:
            idxsort = np.argsort(_xpos)
            _xpos = _xpos[idxsort]
            dsflist_ordered = np.array(self.dsflist)[idxsort]
        else:
            dsflist_ordered = self.dsflist

        #make xpos one larger to plot all data in pcolor
        _xpos=np.append(_xpos,2*_xpos[-1]-_xpos[-2])

        #Create meshgrid for pcolor
        X,Y = np.meshgrid(_xpos, self.w)

        #Data as 2d-array
        broadsofqarray = np.zeros_like(X, dtype=float)
        for i in xrange(self.num):
            dsf = dsflist_ordered[i]
            if not dsf==-1:
                _, broads = dsf.return_broad_spec()
                broadsofqarray[:,i] = broads

        #Plotting
        axplot=ax.pcolormesh(X,Y, broadsofqarray, **kwargs)
        ax.set_xlim(_xpos[0],_xpos[-1])

        return axplot


    @_axes_decorator
    def plot_broad_spec(self, dist=None, values=None, valuepos=.9, valuelabels=True, valuetitle=None, ax=None, **kwargs):
        """
        Create plot of broadened spectral functions of :class:`DynSpecFunc` objects in :class:`DSF_Collection`. 

        :type dist: float
        :param dist: Vertical distance between single lines. **Optional**.

        :type values: np.ndarray
        :param values: external values describing the dsflist. The plot is ordered corresponding to the values and the distances between individual lines is proportional to the difference of the values.
                        **Optional**. Default: None

        :type valuepos: float
        :param valuepos: Position for the labelling in x-direction. Value must be between 0 and 1, where 0. corresonds to the left side and 1. to the right side of the frame. **Optional**. Default: 0.9.
        
        :type valuelabels: bool
        :param valuelabels: If true and values are given, the values are showed within the plot. **Optional**. Default: True

        :type valuetitle: string
        :param valuetitle: A title to the valuelabels. **Optional**. Default: None
        
        :type ax: Axes object
        :param ax: Axes for plotting, **optional**. Default: Create new figure and axes

        :type kwargs: *keyword arguments*
        :param kwargs: The kwargs can be used to set plot properties of plot().
        
        :return: Handles to plot

        .. rubric:: Example

        >>> import quantipy.correlations as corrs
        >>> import numpy as np
        >>> import matplotlib.pyplot as plt

        >>> Szall=np.arange(0,15)
        >>> dsfall=[]
        >>> for i in Szall:
        ...     name="tests/files_dynsofq/DynamicalSofQ.Sz.k.11.q.30.Honeycomb.tJ.30.t.0.JHB.1.00.JK.0.00.Np.30.Sz.%i.si.0.Sznew.%i.sinew.0.GS.rep.0" %(i, i)
        ...     dsfall.append(corrs.read_dyn_spec(name))

        >>> dsfcoll=corrs.DSF_Collection(dsfall)
        >>> dsfcoll.compute_broad_spec(w=np.linspace(0,4,100), eta=.05)
            
        >>> axplot=dsfcoll.plot_broad_spec(values=Szall)
        >>> plt.xlabel(r'$\omega$')
        >>> plt.ylabel(r'$Weight$')
        >>> plt.show()
        
        .. figure:: img_DSF_Collection_plot_broad_spec.png
           :width:  500px
           :height: 400px
           :align:  center

           Sample plot of :func:`plot_broad_spec` for :class:`DSF_Collection` objects

        """
        #handle legend keywords
        kwargs, legkwargs = _kwtolegkw(kwargs)
        
        if not values==None:
            #Check if size ok
            if not len(values)==len(self.dsflist):
                raise ValueError('values must have the same number of elements as self.dsflist!')

            idxsort = np.argsort(values)
            vals = np.array(values)[idxsort]
            dsflist_ordered = np.array(self.dsflist)[idxsort]
        else:
            dsflist_ordered = self.dsflist

        if dist==None:
            #Mean distance
            ymax = np.zeros(len(dsflist_ordered))
            for i,dsf in enumerate(dsflist_ordered):
                if not dsf==-1:
                    x,y = dsf.return_broad_spec()
                    ymax[i] = np.max(y)
                else:
                    ymax[i] = ymax[i-1]
            ymaxmean = 0.8*np.sum(ymax[:-1])/(len(ymax)-1)
            if not values==None:
                deltas = np.diff(vals)/np.mean(np.diff(vals))
                deltay = ymaxmean*deltas
                deltay = np.append(np.array([0]),deltay)
            else:
                deltay = np.append(np.array([0]), ymaxmean*np.ones(len(self.dsflist)-1))
        else:
            ymaxmean = dist
            deltay = np.append(np.array([0]), ymaxmean*np.ones(len(self.dsflist)-1))

        if dist==None and values!=None:
            #round deltay to steps 1,2 or 5 *10**x and arbitrary exponent x
            mostcommondist = max(set(list(deltay)), key=list(deltay).count)
            valpos = np.ceil(np.log10(np.abs(mostcommondist)))
            mostcommondistnew = np.round(mostcommondist,decimals=int(-valpos+1))
            firstval = int(mostcommondistnew*10**(-valpos+1))
            if not firstval in [1,2,5]:
                goodvals = np.array([1,2,5,10])
                idx = np.argmin(np.abs(firstval-goodvals))
                newfirstval = goodvals[idx]
                mostcommondistnew = newfirstval*10**(valpos-1)
            deltay = deltay/mostcommondist*mostcommondistnew

        #Plotting
        axplot = []
        
        #maxy, maxx
        if not values==None and valuelabels==True:
            ymax = 0.
            for i,dsf in enumerate(dsflist_ordered):
                if not dsf==-1:
                    x,y = dsf.return_broad_spec()
                    #ymax = max(ymax, np.max(y+i*ymaxmean))
                    ymax = max(ymax, np.max(y+np.sum(deltay[:i+1])))
            xmax = x[-1]
        
        for i,dsf in enumerate(dsflist_ordered):
            if not dsf==-1:
                x,y = dsf.return_broad_spec()
                #axp = ax.plot(x,y+i*ymaxmean, **kwargs)
                axp = ax.plot(x,y+np.sum(deltay[:i+1]), **kwargs)
                axplot.append(axp)
                if not values==None and valuelabels==True:
                    if not (valuepos>=0. and valuepos<1):
                        warnings.warn('valuepos must be a value between 0 and 1. Standard value .9 used!')
                        valuepos = .9
                    posidx = int(len(x)*valuepos)
                    dy = (y[posidx+1]-y[posidx])/ymax
                    dx = (x[posidx+1]-x[posidx])/xmax
                    angle = np.round(np.rad2deg(np.arctan2(dy, dx)), decimals=-1) #Angle in steps of 10 degrees
                    ax.text(x[posidx], y[posidx]+np.sum(deltay[:i+1]), str(vals[i]), rotation=angle, color = axp[0].get_color(), ha='center', va='center', bbox=dict(ec='1',fc='1'))
        if not valuetitle==None:
            ax.text(x[posidx], y[posidx]+np.sum(deltay)+np.mean(deltay), valuetitle, color='k', ha='center', va='center', bbox=dict(ec='1',fc='1'))

        ax.set_xlabel(r'$\omega$')

        #set yticks properly
        if dist==None and values!=None:
            autoylim = ax.get_ylim()
            nticks = np.abs(autoylim[1]-autoylim[0])/mostcommondistnew + 1
            ticks = np.arange(autoylim[0],autoylim[1]+1e-6,mostcommondistnew)
            ax.set_yticks(np.arange(autoylim[0],autoylim[1]+1e-6,mostcommondistnew))
            if nticks>11:
                #check if ints
                if np.all(ticks - map(int,ticks)==0):
                    ticks = map(int,ticks)
                ticklabels = [('$'+str(ticks[i])+'$' if i%2==0 else '') for i in range(len(ticks))]
                print ticks, ticklabels
                ax.set_yticklabels(ticklabels)

        return axplot


    @_axes_decorator
    def scatter_pw(self,xpos=[], factor=1., yscales=None, ylim=None, ax=None, **kwargs):
        """
        Create scatter plot of poles and weights of :class:`DynSpecFunc` objects.
        
        :type xpos: :class: numpy.ndarray
        :param xpos: x-positions to plot poles/weights of :class:`DynSpecFunc` objects, **optional**.
                     Default is linear spacing with unit distance.
        
        :type factor: float
        :param factor: Factor to magnify weights of :class:`DynSpecFunc` objects, **optional**. Default is 1.
        
        :type yscales: :class: numpy.ndarray
        :param yscales: Scale factors for y-axis. Individual for each x-datapoint. **Optional**.
        
        :type ylim: :class: numpy.ndarray
        :param ylim: Set plot limits in y-direction. Only data within ylim is plotted. Very useful to avoid large files when saving as pdf/svg! **Optional**.

        :type ax: Axes object
        :param ax: Axes for plotting, **optional**. Default: Create new figure and axes
 
        :type kwargs: *keyword arguments*
        :param kwargs: The kwargs can be used to set plot properties of a scatter plot.
        
        :returns:  Handle to plot

        .. rubric:: Example
        
        >>> import quantipy.correlations as corrs
        >>> import numpy as np
        >>> import matplotlib.pyplot as plt

        >>> Szall=np.arange(0,15)
        >>> dsfall=[]
        >>> for i in Szall:
        ...     name="tests/files_dynsofq/DynamicalSofQ.Sz.k.11.q.30.Honeycomb.tJ.30.t.0.JHB.1.00.JK.0.00.Np.30.Sz.%i.si.0.Sznew.%i.sinew.0.GS.rep.0" %(i, i)
        ...     dsfall.append(corrs.read_dyn_spec(name))

        >>> dsfcoll=corrs.DSF_Collection(dsfall)
        >>> print dsfcoll
            DSF_Collection class. # DynSpecFunc objects = 6.

        >>> axplot=dsfcoll.scatter_pw(xpos=Szall,factor=200, alpha=.3)
        >>> plt.xlabel(r'$S^z$', fontsize=16)
        >>> plt.ylabel(r'$\omega$', fontsize=16)
        >>> plt.ylim([0,4])
        >>> plt.show()

        .. figure:: img_DSF_Collection_scatter_pw.png
           :width:  500px
           :height: 400px
           :align:  center
  
           Sample plot of :func:`scatter_pw` for :class:`DSF_Collection` objects
        """
        if xpos==[]:
            self._xpos=np.arange(self.num)
        elif not len(xpos)==self.num:
            warnings.warn("Size of xpos is not identical to size of self.dsflist! Default values used!", RuntimeWarning)
            self._xpos=np.arange(self.num)
        else:
            self._xpos=xpos

        yscal=np.ones(self.num)
        if yscales is not None:
            if not len(yscales)==self.num:
                warnings.warn("Size of yscales is not identical to size of self.dsflist! Default used!", RuntimeWarning)
            else:
                yscal=yscales

        if ylim is not None:
            ylim = np.sort(ylim)
            if not ylim.size==2:
                warnings.warn("ylim must have exactly 2 entries! ylim not used!", RuntimeWarning)
                ylim_set = False
            else:
                ylim_set = True
        else:
            ylim_set = False

        #Combine poles and weights for plotting
        poles=np.array([])
        weights=np.array([])
        x=np.array([])

        for i, dsf in enumerate(self.dsflist):
            if not dsf==-1:
                pw=dsf.polesweight()
                pol = pw['pol']*yscal[i]
                #Find pol within ylim
                if ylim_set:
                    delta = 1e-6
                    idx = np.logical_and(pol>=ylim[0]-delta, pol<=ylim[1]+delta)
                else:
                    idx = np.array([True]*len(pol))

                pol = pol[idx]
                #Append data
                poles=np.append(poles,pol)
                weights = np.append(weights, pw['wei'][idx])
                x=np.append(x,self._xpos[i]*np.ones_like(pol))
        

        #Get color from color cycle or kwargs
        if not('c' in kwargs or 'color' in kwargs):
            colorcycle = ax._get_lines.color_cycle
            kwargs['c'] = next(colorcycle)

        #Plotting
        axplot = ax.scatter(x,poles, s=weights*factor, **kwargs)
        ax.set_ylabel(r'$\omega$', fontsize=16)
        ax.set_xlabel(r'$x$', fontsize=16)
        if ylim_set:
            ax.set_ylim(ylim)
        
        return axplot



