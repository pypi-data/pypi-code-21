# -*- coding: utf-8 -*-
"""
.. _correlations-label:

correlations module
--------------------------------------

Module for handling correlations, such as Spin-Spin correlations, Dimer-Dimer correlations etc

**Overview:**
    * :ref:`correlations-usage-examples-label`
    * :ref:`correlations-function-reference-label`


.. _correlations-usage-examples-label:

Usage Examples
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. rubric:: Example / Plotting correlations on a lattice with :func:`Correlations.plot`

In the following example we show how to read correlations from a file, assign a lattice to the
correlations and plot them. There are implementations for plotting point-point, bond-bond
and triangle-triangle correlations. Also the structure factor like

.. math::
    \mathcal{S}(\mathbf{k}) = |N^{-1/2} \sum_{j=0}^{N-1} e^{-i \mathbf{k} \cdot (\mathbf{r}_j - \mathbf{r}_0)} S_0^z S_j^z |^2

can be plotted. The Fourier transform is internally computed. In this example we plot the
correlations for the groundstate of the Heisenberg nearest neighbour Spin 1/2 model on the
triangular lattice::

    import matplotlib.pyplot as plt
    import quantipy.lattice as lat
    import quantipy.correlations as corrs

    # Read the Lattice file on which the correlations where computed
    l = lat.read('../misc/lattice_files/triangular.36.j1j2jch.sublattices.fsl.lat')

    # Parse Correlations from file (here nearest neighbour HB model on triangular 36 site lattice)
    corrs = corrs.read_correlations('../misc/correlation_files/outfile.triangular.36.J1.1.J2.0.JCH.0.Sz..si.1.k.Gamma.C6.A')

    # Tell corrs on which lattice correlations should be plotted
    corrs.set_lattice(l)

    # Plot various point-point correlations on direct lattice
    corrs.plot(tags="SdotS",marker="o",ms=800, vmin=-0.15, vmax = 0.15)  # manually set plot range
    corrs.plot(tags="SzSz",marker="o",ms=800, vmin=-0.15, vmax = 0.15)
    corrs.plot(tags="SxSx+SySy",marker="o",ms=800, vmin=-0.15, vmax = 0.15)

    # Plot bond correlations and use SdotS to compute centralized correlations
    # (i.e. <(S_iS_j)(S_kS_l)> - <S_iS_j><S_kS_l>)
    corrs.plot(tags="DimerDimer", ms=800, vmin=-0.1, vmax = 0.1, centralizer_tag="SdotS")

    # Plot triangular corralations
    corrs.plot(tags="ScalarChiralityCorrelation")                        # automatically determine plot range

    # Plot Structure Factor for point-point correlation
    corrs.plot_structurefactor(tags="SdotS",marker="H",ms=1700, vmin=0, vmax = 0.1)

    # Display plots
    plt.show()

This produces the following plots

.. figure:: _static/test_correlations.sdots.corrs.svg
    :width: 600px
    :height: 375 px
    :align: center

.. figure:: _static/test_correlations.szsz.corrs.svg
    :width: 600 px
    :height: 375 px
    :align: center

.. figure:: _static/test_correlations.transverse.corrs.svg
    :width: 600 px
    :height: 375 px
    :align: center

.. figure:: _static/test_correlations.dimer.corrs.svg
    :width: 600 px
    :height: 375 px
    :align: center

.. figure:: _static/test_correlations.chirality.corrs.svg
    :width: 600 px
    :height: 375 px
    :align: center

.. figure:: _static/test_correlations.structurefactor.svg
    :width: 600 px
    :height: 375 px
    :align: center

    Sample plots of plot()

This example can also be found in the file tests/test_correlations.py. The lattice file
can be found under /misc/lattice_files/triangular.36.j1j2jch.sublattices.fsl.lat and the
correlation file under /misc/correlation_files/outfile.triangular.36.J1.1.J2.0.JCH.0.Sz..si.1.k.Gamma.C6.A
in the quantipy directory.

.. _correlations-function-reference-label:

Function and Class reference
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import linalg
from matplotlib.collections import LineCollection
import matplotlib.cm as cmx
import matplotlib.colors as cols
from mpl_toolkits.axes_grid1 import make_axes_locatable
import warnings
import itertools
from quantipy.utils import _axes_decorator, _axes_decorator_3d, _torusdistancevector, _kwtolegkw, unique_rows
import quantipy.lattice as latt
from quantipy.symmetries import _get_permutations

def read(filename, **kwargs):
    """
    Wrapper for read_correlations().
    """
    C = read_correlations(filename, **kwargs)

    return C


def read_correlations(filename, tags=None, tags_to_ignore=None):
    """
    Reads point/bond correlations, such as Spin-Spin correlations, currents, etc. from a file, e.g. from an output file of QMSpinDyn.
    Data must be listed in the file in the following way:

    **Name [pos1,pos2,...] = value**

    where *Name* is the name of the correlation (corresponding to the keyword tags), *value* is a floating
    point value giving the strength of the correlation,
    and *pos1,pos2,...* gives the positions of the correlation in the lattice. The positional arguments are
    simple integers and represent the number of a lattice site
    but **NOT** its coordinates. The mapping to coordinates is done by defining/loading a lattice
    (see :func:`set_lattice` or :func:`set_lattice_from_file`).

    **Examples:**

    * onsitepot[7] = 0.37
    * SzSz[0,1] = 0.25
    * current[3,5] = -4.58
    * bondbond[2,4,6,8] = 0.83

    :type filename: str
    :param filename: Filename of the input file.
    :type tags: str or list of str
    :param tags: Tags which identify the type of correlations to read from inputfile, **Optional**. Default is None which means every tag is loaded
    :rtype: :class:`Correlations` object
    :return: A :class:`Correlations` object which can be used to plot and evaluate correlations data.
    """
    with open(filename, 'r') as corrfile:

        # Read all tags
        if tags is None:
            tagstoload = []
            for line in corrfile:
                if "[" in line and "]" in line:
                    tag_read = line.split("[")[0]
                    if tag_read not in tagstoload and tag_read != "":
                        tagstoload.append(tag_read)

            corrfile.seek(0, 0)

        # Read only given tags
        elif isinstance(tags, str):
            tagstoload = [tags]
        else:
            tagstoload = list(tags)

        if tags_to_ignore != None:
            if type(tags_to_ignore) == str:
                tags_to_ignore = [tags_to_ignore]
            tagstoload = list(set(tagstoload) - set(tags_to_ignore))

        postag = {}
        valtag = {}
        for tag in tagstoload:
            postag[tag] = []
            valtag[tag] = np.array([])

        for line in corrfile:
            possplit = line.find('[')
            linetag = line[:possplit]
            for tag in tagstoload:
                #if tag in line:
                if tag == linetag:
                    dat = line.strip().split('=')
                    # read complex correlator
                    if "(" in dat[1] and ")" in dat[1]:
                        dat[1] = dat[1].split(") (")[0]  # Take first complex number
                        dat[1] = dat[1].replace("(", "").replace(")", "").\
                                 replace(", ", "+").replace(",", "+").\
                                 replace("+-", "-") + "j"
                        val = np.real(complex(dat[1]))

                    # read real correlator
                    else:
                        val = float(dat[1])

                    valtag[tag] = np.append(valtag[tag], val)

                    pos = dat[0].replace(']', '').split('[')
                    pos[1] = pos[1].replace('),', ')')
                    pos = pos[1].replace(')', '').split('(')
                    pos = [x for x in pos if x != '']
                    newpos = []
                    for x in pos:
                        newpos.append(np.array(map(int, x.split(','))))

                    newpos = np.array(newpos)
                    postag[tag].append(newpos)

    #check loaded data
    for tag in tagstoload:
        postag[tag] = np.array(postag[tag])
        try:
            nsites = postag[tag].shape[1]
        except IndexError:
            raise ValueError('Not all correlations with tag %s are defined with the same number of sites!' %tag)

    return Correlations(postag, valtag, filename)


class Correlations:
    """
    :class: Correlations

    Provides tools to analyze and visualize point and bond correlations from Exact Diagonalization code (QMSpinDyn).
    """

    def __init__(self, positions, values, filename=None):
        """
        Initialization:

        :type positions: :class: numpy.ndarray or dict of numpy.ndarrays
        :param positions: Positions of Correlations

        :type values: :class: numpy.ndarray or dict of numpy.npdarrays
        :param values: Values of Correlations

        :type filename: str
        :param filename: Filename of the correlations. **Optional**.
        """

        self._reference_set = False
        self._refpoint = None
        self._refvalue = None

        self._lattice_set = False
        self._k_space_set = False
        self._sf_calc = False

        self._isdict = False
        self.tags = None #: Dictionary tags of Correlation types
        self.filename = filename #: Filename of the Correlations file

        if isinstance(positions, dict) and isinstance(values, dict):
            if not len(positions) == len(values):
                raise ValueError('Dictionaries positions and values must have the same length!')

            tagspos = positions.keys()
            tagsval = values.keys()
            for i in range(len(tagspos)):
                if not tagspos[i] == tagsval[i]:
                    raise ValueError('Dictionary tags for positions and values must be identical!')

            self._isdict = True
            self.tags = tagspos

        elif isinstance(positions, np.ndarray) and isinstance(values, np.ndarray):
            pass

        else:
            raise ValueError('positions and values must be numpy.ndarrays or dictionaries of them!')

        self.pos = positions #: Position data of correlations
        self.val = values #: Values of correlations


    def __str__(self):
        """
        Returns a short summary of the class.
        """
        out = "Correlations class."
        if not self.tags == None:
            out += " Tags are: %s." %(self.tags)

        if self._lattice_set:
            out += " Lattice loaded."
        else:
            out += " Lattice NOT loaded!"

        if self._reference_set:
            out += " Reference point=%i and value=%g are set." %(self._refpoint, self._refvalue)
        else:
            out += " No Reference point and value set, default values (0, 0.0) are used!"

        return out


    def write(self, filename):
        """
        Writes the correlations to a file.

        :type filename: str
        :param filename: Filename for the correlations file.
        """
        with open(filename, 'w') as corrfile:
            for tag in self.tags:
                for pos, val in zip(self.pos[tag], self.val[tag]):
                    if pos.ndim==1:
                        posstring = ','.join(map(str, pos))
                    elif pos.shape[0]==1:
                        posstring = ','.join(map(str, pos[0]))
                    else:
                        pstrings = []
                        for p in pos:
                            posstring = ','.join(map(str, p))
                            pstrings.append(posstring)
                        posstring = '(' + ')('.join(pstrings) + ')'

                    corrfile.write('%s[%s] = %.20f\n' %(tag, posstring, val))


    def get(self, tags=None):
        """
        Return positions and values of loaded correlations.

        :type tags: str/list of str
        :param tags: If tags is set, return only data for given tags. **Optional**.
            Default: None - Return data for all tags in class instance.
        :rtype: (list, list)
        :returns: (list of positions, list of values) sorted like tags
        """
        if tags == None:
            tags = self.tags

        if isinstance(tags, str):
            tags = [tags]

        positions = []
        values = []
        for tag in tags:
            try:
                positions.append(self.pos[tag])
                values.append(self.val[tag])
            except KeyError:
                warnings.warn('Cannot find key %s. Ignoring it!' %tag, UserWarning)
                positions.append([])
                values.append([])

        return (positions, values)


    def set_reference(self, referencepoint, referencevalue):
        """
        Set reference point and value.

        :type referencepoint: int
        :param referencepoint: Reference point of lattice to which correlations are defined, **optional**. Default is 0.

        :type referencevalue: float
        :param referencevalue: Value for on-site correlation at reference point.
        """
        self._reference_set = True
        self._refpoint = referencepoint
        self._refvalue = referencevalue


    def set_lattice_from_file(self, filename):
        """
        Set lattice on which Correlations have been computed by reading from the corresponding lattice file.

        :type filename: str
        :param filename: The filename of the corresponding lattice file.
        """
        self._lattice_set = True
        self.lattice = latt.read(filename) #: Lattice (quantipy.lattice.Lattice instance)
        self.k_space = self.lattice.k_space
        self._k_space_set = True

    def set_lattice(self, lattice):
        """
        Set lattice on which Correlations have been computed from a lattice class object.

        :type lattice: quantipy.lattice.Lattice object
        :param lattice: Lattice object
        """
        self._lattice_set = True
        self.lattice = lattice #: Lattice (quantipy.lattice.Lattice instance)
        self.k_space = self.lattice.k_space
        self._k_space_set = True


    def extend_kspace(self, r=1):
        """
        Function to extend the k-space to further Brillouinzones.
        """
        if not self._k_space_set:
            raise ValueError('No k-space defined! Use set_lattice() to set a k-space via a lattice.')

        self._sf_calc = False
        unitcell = self.lattice.unitcell
        unitcell /= (r + 1.)
        simtorus = self.lattice.simulation_torus
        newlat = latt.Lattice(unitcell=unitcell, simulation_torus=simtorus)
        self.k_space = newlat.k_space
        self._k_space_set = True


    def calculate_structure_factor(self, reference_onsite_value=None, cfunc=None):
        """
        Calculate the structure factors (Fourier Transform of correlations).

        :type cfunc: function object
        :param cfunc: Apply the function on the correlations in the plot. **Optional**. Default: None
        """

        if not self._lattice_set or not self._k_space_set:
            raise ValueError('No lattice defined! Use set_lattice() to set a lattice.')

        if not self._k_space_set:
            raise ValueError('No k-space defined! Use set_lattice() to set a k-space via a lattice.')

        if reference_onsite_value is not None:
            self._refvalue = reference_onsite_value


        nsites = len(self.lattice.coordinates)

        if self._isdict:
            self.structurefactor = {} #: Structure factors of correlations
            for tag in self.tags:


                if np.all(self.pos[tag][:, 0, 0] == self.pos[tag][0, 0, 0]):
                    self._refpoint = self.pos[tag][0, 0, 0]
                else:
                    warnings.warn("Problem plotting {0} structurefactor: reference point not".format(tag)
                                  +" equal. {0} structurefactor is skipped".format(tag), UserWarning)
                    self.structurefactor[tag] = None
                    continue

                if reference_onsite_value is None:
                    if tag == "SdotS":
                        self._refvalue = 0.75
                    elif tag == "SzSz" or tag == "SxSx" or tag == "SySy":
                        self._refvalue = 0.25
                    elif tag == "SxSx+SySy":
                        self._refvalue = 0.5
                    else:
                        if not self._reference_set:
                            self._refvalue = 0
                            warnings.warn("Attention: Reference onsite value (e.g. <S1.S1>)" +
                                          " is not set for {0}. Assuming 0!".format(tag), UserWarning)

                refcoord = self.lattice.coordinates[self._refpoint]
                # print tag, self.pos[tag].shape
                if self.pos[tag].shape[1] == 1 and self.pos[tag].shape[2] == 2:
                    pos1 = np.array(self.pos[tag])[:, 0, 0]
                    pos2 = np.array(self.pos[tag])[:, 0, 1]

                    posavail = pos2[pos1 == self._refpoint]
                    posavail = np.append(posavail, self._refpoint)
                    coords = self.lattice.coordinates[posavail]

                    vals = np.array(self.val[tag])[pos1 == self._refpoint]
                    vals = np.append(vals, self._refvalue)

                elif self.pos[tag].shape[1] == 2 and self.pos[tag].shape[2] == 1:
                    pos1 = self.pos[tag][:, 0, 0]
                    pos2 = self.pos[tag][:, 1, 0]
                    posavail = pos2[pos1 == self._refpoint]
                    posavail = np.append(posavail, self._refpoint)
                    vals = np.array(self.val[tag])[pos1 == self._refpoint]
                    vals = np.append(vals, self._refvalue)

                elif self.pos[tag].shape[1] == 1 and self.pos[tag].shape[2] == 1:
                    posavail = self.pos[tag][:, 0, 0]
                    vals = self.val[tag]

                # Tag cannot give rise to a valid structure factor
                else:
                    self.structurefactor[tag] = None
                    continue

                if not len(vals) == nsites:
                    # raise ValueError('Number of correlations is not identical with number of sites of the lattice!')
                    self.structurefactor[tag] = None
                    continue
                # print tag, self._refvalue

                # apply cfunc
                if cfunc is not None:
                    vals = map(cfunc, vals)

                #Compute Fouriertrafo
                sfk = np.zeros(len(self.k_space))
                for nk, k in enumerate(self.k_space):
                    sf = 0
                    for i, r in enumerate(coords):
                        sf += vals[i] * np.exp(1j*np.dot(k, r-refcoord))
                    #sf = 1./nsites * np.abs(sf)**2     #normalization and absolute value squared
                    sf = np.real(sf) #proper definition of structure factor
                    sfk[nk] = sf

                self.structurefactor[tag] = sfk


        else:
            raise ValueError('Not yet implemented!')

        self._sf_calc = True


    def plot(self, tags=None, ms=700, msdyn=False, cfunc=None, factor=1, plot_lattice=True, colorbar=True, symmcb=False, centralizer_tag=None, plot_vals=False, ax=None, **kwargs):
        """
        Plot correlations  on the lattice.

        :type tag: str or list of str
        :param tag: Define the tags of the correlations which should be plotted. Use None or 'all' to plot all correlations. **Optional**. Default: None --> Plot all correlations.
        :type ms: float
        :param ms: Markersize of plotted symbols, **optional**.
        :type msdyn: Bool
        :param msdyn: If True, the markers are plotted proportional to the value. Markersize is scaled by
            the keyword ms. Minimal size is ms=10. For point-point correlations only! **Optional**. Default: False
        :type cfunc: function object
        :param cfunc: Apply the function on the correlations in the plot. **Optional**. Default: None
        :type factor: float
        :param factor: Factor for correlation values in plot. **Optional**. Default: 1
        :type colorbar: Bool
        :param colorbar: If True, a colorbar is shown. **Optional**. Default: True
        :type symmcb: Bool
        :param symmcb: If true, a symmetric color range is plotted. If no cmap is specified,
                    a diverging colormap is used. **Optional**, default: *False*.
        :type clabel: string
        :param clabel: Set the colorbar label. **Optional**. Default: None - No label is shown.
        :type centralizer_tag: str
        :param centralizer_tag: Tag to compute connected (centralized) correlation function. **Optional**.
                Default: Pure correlation function is plotted.
        :type plot_vals: Bool
        :param plot_vals: If True, the plotted values are shown as text in the plot. **Optional**. Default: False
        :type ax: Axes object
        :param ax: Axes for plotting, **optional**. Default: Create new figure and axes
        :type kwargs: *keyword arguments*
        :param kwargs: The kwargs can be used to set plot properties of a scatter plot.
        :returns: Handle(s) to plot
        """
        if not self._lattice_set:
            raise ValueError('A lattice must be set to use plot! Use set_lattice to set a lattice!')

        #Adapt kwargs
        kwargs['colorbar'] = colorbar
        if centralizer_tag is not None:
            kwargs['centralizer_tag'] = centralizer_tag

        if 'tag' in kwargs:
            tags = kwargs['tag']
            del kwargs['tag']

        if cfunc is not None:
            kwargs['cfunc'] = cfunc

        kwargs['factor'] = factor

        if tags == None or tags == 'None' or tags == 'none' or tags == 'all':
            if self._isdict:
                hplot = []
                for tag in self.tags:
                    if self._is_point_correlation(tag):
                        hp = self._singleplot(tag=tag, ms=ms, msdyn=msdyn, plot_lattice=plot_lattice, ax=ax, plot_vals=plot_vals, noref=True, **kwargs)
                    elif self._is_point_point_correlation(tag):
                        # print "pp ", tag
                        hp = self._singleplot(tag=tag, ms=ms, msdyn=msdyn, plot_lattice=plot_lattice, ax=ax, plot_vals=plot_vals, **kwargs)
                    elif self._is_bond_bond_correlation(tag):
                        hp = self.plot_bond_correlations(tag=tag, plot_lattice=plot_lattice, ax=ax, colored=True, **kwargs)
                        # print "bb ", tag
                    elif self._is_triangle_triangle_correlation(tag):
                        hp = self.plot_triangle_correlations(tag=tag, plot_lattice=plot_lattice, ax=ax, colored=True, **kwargs)
                        # print "tt ", tag
                    else:
                        hp = None
                    hplot.append(hp)
            else:
                hplot = self._singleplot(tag=None, ms=ms, msdyn=msdyn, plot_lattice=plot_lattice, ax=ax, plot_vals=plot_vals, **kwargs)
        else:
            hplot = []
            if isinstance(tags, str):
                tags = [tags]

            for k in tags:
                # print k
                if self._is_point_correlation(k):
                    hp = self._singleplot(tag=k, ms=ms, msdyn=msdyn, plot_lattice=plot_lattice, ax=ax, plot_vals=plot_vals, noref=True, **kwargs)
                elif self._is_point_point_correlation(k):
                    hp = self._singleplot(tag=k, ms=ms, msdyn=msdyn, plot_lattice=plot_lattice, ax=ax, plot_vals=plot_vals, **kwargs)
                elif self._is_bond_bond_correlation(k):
                    hp = self.plot_bond_correlations(tag=k, plot_lattice=plot_lattice, ax=ax, colored=True, **kwargs)
                elif self._is_triangle_triangle_correlation(k):
                    hp = self.plot_triangle_correlations(tag=k, plot_lattice=plot_lattice, ax=ax, **kwargs)
                else:
                    hp = None

                hplot.append(hp)

        return hplot

    def _is_point_correlation(self, tag):
        """
        Returns wheter a tag is a single point correlator
        """
        return self.pos[tag].shape[1] == 1 and self.pos[tag].shape[2] == 1

    def _is_point_point_correlation(self, tag):
        """
        Returns wheter a tag is a point-point-correlator
        """
        return (self.pos[tag].shape[1] == 1 and self.pos[tag].shape[2] == 2) or \
            (self.pos[tag].shape[1] == 2 and self.pos[tag].shape[2] == 1)

    def _is_bond_bond_correlation(self, tag):
        """
        Returns wheter a tag is bond-bond-correlator
        """
        posread = np.array(self.pos[tag])
        return (len(posread.shape) == 2 and (posread.shape[1] == 2 or posread.shape[1] == 4)) or\
                     (len(posread.shape) == 3 and (posread.shape[1] == 2 and posread.shape[2] == 2))

    def _is_triangle_triangle_correlation(self, tag):
        """
        Returns wheter a tag is triangle-triangle-correlator
        """
        posread = np.array(self.pos[tag])
        return ((len(posread.shape) == 2 and (posread.shape[1] == 3 or posread.shape[1] == 6)) or
                (len(posread.shape) == 3 and (posread.shape[1] == 2 and posread.shape[2] == 3)))



    @_axes_decorator
    def _singleplot(self, tag=None, ms=700, msdyn=False, plot_lattice=True, symmcb=False, ax=None, wigner_seitz=True,
                    periodic=False, plot_vals=False, noref=False, **kwargs):
        """
        Plot the correlations on the direct lattice for only one correlation type!
        """
        #handle legend keywords
        kwargs, legkwargs = _kwtolegkw(kwargs)

        if not noref:
            if not self._reference_set:
                if np.all(self.pos[tag][:, 0, 0] == self.pos[tag][0, 0, 0]):
                    self._refpoint = self.pos[tag][0, 0, 0]
                else:
                    raise ValueError("Error plotting {0} correlations: reference point not set and no equal value found!".format(tag))

        if wigner_seitz:
            coordinates = self.lattice.coordinates_wigner_seitz
        else:
            coordinates = self.lattice.coordinates

        if symmcb:
            kwargs['symmcb'] = True
        else:
            kwargs['symmcb'] = False

        if 'centralizer_tag' in kwargs:
            ctag = kwargs['centralizer_tag']
            del kwargs['centralizer_tag']
            if not self._is_point_correlation(ctag):
                raise ValueError('Cannot centralize Correlation with non-point correlation')
            centralize = True
        else:
            centralize = False

        if not tag == None:
            if self.pos[tag].shape[1] == 1 and self.pos[tag].shape[2] == 2:
                #handle reference point
                pos1 = self.pos[tag][:, 0, 0]
                pos2 = self.pos[tag][:, 0, 1]
                posplot = pos2[pos1 == self._refpoint]
                coords = coordinates[posplot, :]

                if centralize:
                    try:
                        centval = self.val[ctag][posplot] * self.val[ctag][self._refpoint]
                    except IndexError:
                        raise ValueError('Correlation structure not valid to centralize correlations!')
                    valplot = self.val[tag][pos1 == self._refpoint] - centval
                else:
                    valplot = self.val[tag][pos1 == self._refpoint]

            elif self.pos[tag].shape[1] == 2 and self.pos[tag].shape[2] == 1:
                pos1 = self.pos[tag][:, 0, 0]
                pos2 = self.pos[tag][:, 1, 0]
                posplot = pos2[pos1 == self._refpoint]
                coords = coordinates[posplot, :]

                if centralize:
                    try:
                        centval = self.val[ctag][posplot] * self.val[ctag][self._refpoint]
                    except IndexError:
                        raise ValueError('Correlation structure not valid to centralize correlations!')
                    valplot = self.val[tag][pos1 == self._refpoint] - centval
                else:
                    valplot = self.val[tag][pos1 == self._refpoint]

            elif self.pos[tag].shape[1] == 1 and self.pos[tag].shape[2] == 1:
                #onsite - data
                coords = coordinates[self.pos[tag][:, 0, 0]]
                valplot = self.val[tag]
            else:
                raise ValueError('Could not plot this position structure!')

        else:
            if self.pos.shape[1] == 1 and self.pos.shape[2] == 2:
                pos1 = self.pos[:, 0, 0]
                pos2 = self.pos[:, 0, 1]
                posplot = pos2[pos1 == self._refpoint]
                valplot = self.val[pos1 == self._refpoint]
                coords = coordinates[posplot, :]
            elif self.pos.shape[1] == 1 and self.pos.shape[2] == 1:
                coords = coordinates[np.array(self.pos)[:, 0, 0]]
                valplot = self.val[tag]
            else:
                raise ValueError('Could not plot this position structure!')

        if 'cfunc' in kwargs:
            valplot = kwargs['cfunc'](valplot)
            del kwargs['cfunc']

        valplot = kwargs['factor']*valplot
        del kwargs['factor']

        #colorbar handling
        plotcolorbar = kwargs['colorbar']
        del kwargs['colorbar']
        if 'clabel' in kwargs:
            clabel = kwargs['clabel']
            del kwargs['clabel']
        else:
            clabel = None

        #symmetric color bar handling
        if kwargs['symmcb']:
            maxval = np.max([np.abs(np.min(valplot)), np.abs(np.max(valplot))])
            kwargs['vmin'] = -maxval
            kwargs['vmax'] = maxval
            if not 'cmap' in kwargs:
                kwargs['cmap'] = 'coolwarm'
        del kwargs['symmcb']

        #plotting
        if plot_lattice:
            self.lattice.plot(ax=ax, nearest_neighbour_color="grey",
                              wigner_seitz=wigner_seitz, periodic=periodic)

        if msdyn:
            msscatter = np.maximum(np.abs(valplot)*ms, 10)
        else:
            msscatter = ms

        if periodic:
            for (i, j) in itertools.product([-1., 0., 1.], repeat=2):
                axplot = ax.scatter(coords[:, 0] + i*self.lattice.simulation_torus[0, :][0] +
                                    j*self.lattice.simulation_torus[1, :][0],
                                    coords[:, 1] + i*self.lattice.simulation_torus[0, :][1] +
                                    j*self.lattice.simulation_torus[1, :][1],
                                    s=msscatter, c=valplot, zorder=10, **kwargs)
        else:
            axplot = ax.scatter(coords[:, 0], coords[:, 1], s=msscatter, c=valplot, zorder=10, **kwargs)

        if not noref:
            ax.plot(coordinates[self._refpoint, 0], coordinates[self._refpoint, 1], 'xk', ms=20., mew=5)

        if plot_vals:
            for i in range(coords.shape[0]):
                val = valplot[i]
                if np.abs(val) > .9 * np.max(np.abs(valplot)):
                    color = 'k'
                else:
                    color = 'w'
                ax.text(coords[i,0], coords[i,1], '%.3f' %val, va='center', ha='center', color=color, zorder=1000)

        if plotcolorbar:
            divider = make_axes_locatable(ax) 
            cax = divider.append_axes("right", size=0.2, pad=0.05) 
            if clabel is not None:
                cb = plt.colorbar(axplot, cax, label=clabel)
            else:
                cb = plt.colorbar(axplot, cax)

        if not tag == None:
            ax.set_title(r'%s-Correlations' %tag)
        else:
            ax.set_title(r'Correlations')

        ax.set_xlabel(r'$x$')
        ax.set_ylabel(r'$y$')
        # ax.axis('equal')
        return axplot




    def plot_structurefactor(self, tags=None, ms=1000, msdyn=False,
                             colorbar=True, cfunc=None, plotBZ=True,
                             BZcolor='k', ax=None,
                             reference_onsite_value=None, **kwargs):
        """
        Plot the structurefactor of the 2-site correlations.

        :type ms: float
        :param ms: Markersize of plotted symbols, **optional**.
        :type msdyn: Bool
        :param msdyn: If True, the markers are plotted proportional to the value. Markersize is scaled by
            the keyword ms. Minimal size is ms=10. **Optional**. Default: False
        :type colorbar: Bool
        :param colorbar: If True, a colorbar is plotted. **Optional**. Default: True
        :type cfunc: function object
        :param cfunc: Apply the function on the correlations in the plot. **Optional**. Default: None
        :type plotBZ: Bool
        :param plotBZ: If true, Brillouin zone boundary is plotted.
        :type BZcolor: color specification
        :param BZcolor: Color for Brillouin zone boundary.
        :type ax: Axes object
        :param ax: Axes for plotting, **optional**. Default: Create new figure and axes
        :type kwargs: *keyword arguments*
        :param kwargs: The kwargs can be used to set plot properties of a scatter plot.
        :returns: Handle(s) to plot
        """

        self.calculate_structure_factor(reference_onsite_value=reference_onsite_value, cfunc=cfunc)

        #kwargs colorbar handling
        kwargs['colorbar'] = colorbar

        hplot = []
        if tags == None or tags == 'None' or tags == 'none' or tags == 'all':
            for tag in self.tags:
                if self.structurefactor[tag] is not None:
                    axp = self._plot_sf_single(tag=tag, ms=ms, msdyn=msdyn, plotBZ=plotBZ, BZcolor=BZcolor, ax=ax, **kwargs)
                    hplot.append(axp)

        else:
            if isinstance(tags, str):
                tags = [tags]
            for k in tags:
                hplot.append(self._plot_sf_single(tag=k, ms=ms, msdyn=msdyn, plotBZ=plotBZ, BZcolor=BZcolor, ax=ax,
                                                  **kwargs))

        return hplot


    @_axes_decorator
    def _plot_sf_single(self, tag=None, ms=1000, msdyn=False, plotBZ=True,
                        BZcolor='k', ax=None, **kwargs):
        """
        Plots structure factor for a single tag. Only loaded by plot_structurefactor.
        """
        #handle legend keywords
        kwargs, legkwargs = _kwtolegkw(kwargs)

        #colorbar handling
        plotcolorbar = kwargs['colorbar']
        del kwargs['colorbar']

        if 'clabel' in kwargs:
            clabel = kwargs['clabel']
            del kwargs['clabel']
        else:
            clabel = None


        if tag == None:
            raise ValueError('No tag given in _plot_sf_single()')


        kx = self.k_space[:, 0]/np.pi
        ky = self.k_space[:, 1]/np.pi
        sf = self.structurefactor[tag]

        # for i, s in enumerate(self.structurefactor[tag]):
        #     print kx[i], ky[i], s

        if msdyn:
            ms = np.maximum(np.abs(sf)*ms, 10)

        axplot = ax.scatter(kx, ky, s=ms, c=sf, zorder=10, **kwargs)

        if plotcolorbar:
            divider = make_axes_locatable(ax) 
            cax = divider.append_axes("right", size=0.2, pad=0.05) 
            if clabel is not None:
                cb = plt.colorbar(axplot, cax, label=clabel)
            else:
                cb = plt.colorbar(axplot, cax)

        ax.set_xlabel(r'$k_x/\pi$')
        ax.set_ylabel(r'$k_y\pi$')
        ax.set_title('%s Structure factor' %tag)
        ax.axis('equal')

        if plotBZ:
            self.lattice.plot_brillouinzone(ax=ax, plot_k_space=False, legend=False, **kwargs)

        return axplot


    @_axes_decorator
    def plot_bond_correlations(self, tag='bondcorrs', lwrange=[1, 15], minplotval=1e-10, posnegcolor=['r', 'b'],
                               colored=True, reference_bond=[0, 1], ax=None, wigner_seitz=True,
                               plot_lattice=True,
                               periodic=False, directed=False, **kwargs):
        """
        .. versionadded:: 1.0.x

        Plot correlations between sites or bond-bond correlations with a reference bond as bonds of different
        width. Positive and negative values are plotted in different colors.

        :type tag: string
        :param tag: Name of the correlations which you want to plot. Default: 'bondcorrs'
        :type lwrange: list/array (1x2)
        :param lwrange: The range for the linewidths. The correlation values are linearly mapped into this
                        range. **Optional**. Default: [1,10]
        :type minplotval: float
        :param minplotval: Correlation values smaller than this value are not plotted. **Optional**.
                           Default: 1e-10
        :type colored: Bool
        :param colored: If true, the bonds are colored according to their values using a colormap.
                        **Optional**. Default: False
        :type posnegcolor: list (1x2) of colors
        :param posnegcolor: Colors to plot positive/negative correlation values. Only if 'colored' option
                            is False. **Optional**. Default: ['r','b'] --> Positive red, negative blue
        :type reference_bond: np.ndarray/list (1x2) of int
        :param reference_bond: If bond-bond correlations are plotted, set the reference bond with lattice
                               positions. **Optional**. Default: [0,1]
        :type ax: Axes object
        :param ax: Axes for plotting, **optional**. Default: Create new figure and axes

        :rtype: tuple
        :returns: (Handle to lattice, Handle to correlations, Scalar mappable for manually creating a colorbar)
        """
        if not self._lattice_set:
            raise ValueError('A lattice must be set to use plot! Use set_lattice to set a lattice!')

        #handle legend keywords
        kwargs, legkwargs = _kwtolegkw(kwargs)

        #colorbar handling
        plotcolorbar = kwargs['colorbar']
        del kwargs['colorbar']

        #Positions and values
        posread = np.array(self.pos[tag])
        if not ((len(posread.shape) == 2 and (posread.shape[1] == 2 or posread.shape[1] == 4)) or
                (len(posread.shape) == 3 and (posread.shape[1] == 2 and posread.shape[2] == 2))):
            raise ValueError('Plot bond correlations works only for correlations with two/four'+
                             ' positional arguments!')

        values = np.array(self.val[tag])

        if wigner_seitz:
            coordinates = self.lattice.coordinates_wigner_seitz
        else:
            coordinates = self.lattice.coordinates


        #proceed bond-bond corrs with reference bond value
        if len(posread.shape) == 2:

            if posread.shape[1] == 4:
                bondpos1 = posread[:, :2]
                bondpos2 = posread[:, 2:]
                refidx = np.all(bondpos1 == reference_bond, axis=1)
                bondstoplot = bondpos2[refidx, :]
                valstoplot = values[refidx]
                #append reference bond and value
                bondstoplot = np.vstack((bondstoplot, reference_bond))
                valstoplot = np.append(valstoplot, np.min(valstoplot))
                lineshapes = ['-']*(len(valstoplot)-1)+['--'] #different linestyle for reference bond
            else:
                bondstoplot = posread
                valstoplot = values
                lineshapes = '-'
        elif  len(posread.shape) == 3:
            if posread.shape[1] == 2 and posread.shape[2] == 2:

                bondpos1 = posread[:, 0, :]
                bondpos2 = posread[:, 1, :]
                if np.all(bondpos1 == bondpos1[0, :]):
                    reference_bond = bondpos1[0, :]
                else:
                    raise ValueError("Error plotting {0} correlations: reference bonds not equal").format(tag)


                refidx = np.all(bondpos1 == reference_bond, axis=1)
                bondstoplot = bondpos2[refidx, :]
                valstoplot = values

                #append reference bond and value
                # print valstoplot

                bondstoplot = np.vstack((bondstoplot, reference_bond))
                valstoplot = np.append(valstoplot, np.min(valstoplot))
                lineshapes = ['-']*(len(valstoplot)-1)+['--'] #different linestyle for reference bond

        # for bond,val in zip(bondstoplot, valstoplot):
        #     print reference_bond, bond, val

        # subtract centralizing part if defined in kwargs
        if 'centralizer_tag' in kwargs:
            ctag = kwargs['centralizer_tag']
            if not self._is_point_point_correlation(kwargs['centralizer_tag']):
                raise ValueError('Cannot cetralize Correlation with non-point-point correlation')

            if self.pos[ctag].shape[1] == 1 and self.pos[ctag].shape[2] == 2:
                pos1 = self.pos[ctag][:, 0, 0]
                pos2 = self.pos[ctag][:, 0, 1]
            elif self.pos[ctag].shape[1] == 2 and self.pos[ctag].shape[2] == 1:
                pos1 = self.pos[ctag][:, 0, 0]
                pos2 = self.pos[ctag][:, 1, 0]
            else:
                raise ValueError('Invalid bond structure for centralization!')
            cbonds = np.array([pos1, pos2]).T

            #compute translational invariant bonds using permutations
            allperms = _get_permutations(coordinates, self.lattice.unitcell,
                                         self.lattice.simulation_torus,
                                         self.lattice.bravaiscoordinates -
                                         self.lattice.bravaiscoordinates[0],
                                         [np.eye(self.lattice.dimension)],
                                         self.lattice.sym_center)

            allrefbonds = np.array([perm[reference_bond] for perm in allperms])

            # search reference centralization
            crefidx = -1
            for idx, bond in enumerate(cbonds):
                whichrefbond = np.all(bond == allrefbonds, axis=1)
                if np.any(whichrefbond):
                    crefidx = idx
                    refperm = allperms[np.argwhere(whichrefbond)[0]][0]
                    break

            if crefidx == -1:
                raise ValueError('No reference centralizer found')
            reference_corr = self.val[ctag][crefidx]

            # search for corresponding point-point correlation to centralize
            for bondcorridx, bondcorr in enumerate(bondstoplot):
                # check if correlation is directly given ...
                crefidx = -1
                for idx, cbond in enumerate(cbonds):
                    if (cbond == refperm[bondcorr]).all():
                        crefidx = idx
                        break

                # .. otherwise assume translation invariance and find bond which can be translated
                if crefidx == -1:
                    # warnings.warn("Warning: No Correct Centralizer for correlation {0} {1} found.".\
                    #                   format(reference_bond,bondcorr) + "Assuming translation invariace")
                    bondcorrvec = _torusdistancevector(coordinates[bondcorr[0]], coordinates[bondcorr[1]],
                                                       self.lattice.simulation_torus)
                    for idx, cbond in enumerate(cbonds):
                        cbondvec = _torusdistancevector(coordinates[cbond[0]], coordinates[cbond[1]],
                                                        self.lattice.simulation_torus)
                        if np.allclose(cbondvec, bondcorrvec) or np.allclose(cbondvec, -bondcorrvec):
                            crefidx = idx
                            break

                # if still no centralizer is found raise error
                if crefidx == -1:
                    raise ValueError('No reference centralizer found')

                # print bondcorr, cbonds[crefidx], valstoplot[bondcorridx], \
                #     valstoplot[bondcorridx] - reference_corr*self.val[ctag][crefidx]

                valstoplot[bondcorridx] -= reference_corr*self.val[ctag][crefidx]

                # print bondcorr, self.lattice.coordinates[bondcorr[0]], self.lattice.coordinates[bondcorr[1]]

        #check if lwrange is okay
        if lwrange[0] < 0 or lwrange[1] < 0:
            raise ValueError('You have to use positive values for lwrange!')
        lwrange = np.sort(lwrange)

        #Coordinates of bonds in lattice
        bonds = coordinates[bondstoplot]

        # calculate shortest distance bonds for tori
        for idx, bond in enumerate(bonds):
            mindist = 100000
            for u, v in itertools.product([0, 1, -1], repeat=2):
                coord = bond[1, :] + u * self.lattice.t1 + v * self.lattice.t2
                dist = linalg.norm(coord-bond[0, :])
                # print coord, dist, u, v
                # print dist
                if dist < mindist:
                    mindist = dist
                    mincoord = coord
            bonds[idx, 1, :] = mincoord


        # Choose uniform orientation for bonds to plot
        if directed:
            for idx, bond in enumerate(bonds):
                vec = bond[1, :] - bond[0, :]
                if np.abs(np.arctan2(vec[1], vec[0]) - np.pi/3.) < 1e-6 or \
                        np.abs(np.arctan2(vec[1], vec[0]) + np.pi/3.) < 1e-6 or \
                        np.abs(np.arctan2(vec[1], vec[0]) - np.pi) < 1e-6:
                # if np.arctan2(vec[1], vec[0]) < -1e-6 or  np.arctan2(vec[1], vec[0]) > np.pi - 1e-6:
                    bonds[idx] = bond[[1, 0]]
                    valstoplot[idx] = -valstoplot[idx]
                # valstoplot[idx] = np.log(valstoplot[idx])

        #handle cfunc and factor
        if 'cfunc' in kwargs:
            valstoplot = kwargs['cfunc'](valstoplot)
            del kwargs['cfunc']

        valstoplot = kwargs['factor']*valstoplot
        del kwargs['factor']

        #Map absolute values to lwrange (default:[1,10]) for plotting as linewidths
        absvalues = np.abs(valstoplot)

        if 'vmax' in kwargs:
            vmax = kwargs['vmax']
        else:
            vmax = np.max(valstoplot)

        if 'vmin' in kwargs:
            vmin = kwargs['vmin']
        else:
            vmin = np.min(valstoplot)


        valrange = vmax - vmin
        lws = 6*np.sqrt((absvalues-np.min(absvalues))/valrange*np.diff(lwrange) + lwrange[0])

        #find small values which shouldnt be plotted
        idxsmall = absvalues < minplotval
        lws[idxsmall] = 0.


        if not colored:
            #check which values are positive/negative and give the corresponding color
            colors = [(posnegcolor[0] if val > 0 else posnegcolor[1]) for val in valstoplot]
        else:
            #check if there are pos and negative values
            if np.sign(vmin) == -np.sign(vmax):
                if 'cmap' in kwargs and kwargs['cmap'] is not None:
                    cm = plt.get_cmap(kwargs['cmap'])
                else:
                    cm = plt.get_cmap('coolwarm')
                cNorm = cols.Normalize(vmin=vmin, vmax=vmax)
            else:
                if 'cmap' in kwargs and kwargs['cmap'] is not None:
                    cm = plt.get_cmap(kwargs['cmap'])
                else:
                    cm = plt.get_cmap()
                cNorm = cols.Normalize(vmin=vmin, vmax=vmax)

            scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cm)
            colors = scalarMap.to_rgba(valstoplot)

        #Change color, linewidth of reference bond for bond-bond corrs
        if posread.shape[1] == 4 or (len(posread.shape) == 3 and posread.shape[1] == 2 and posread.shape[2] == 2):
            colors[-1] = [0, 0, 0, 1]
            lws[-1] = 8.
        # print "bonds\n" , bonds , lws

        #Line Collection
        lines = LineCollection(bonds, linewidths=lws, color=colors, linestyles=lineshapes)

        #Plotting
        if plot_lattice:
            axlatt = self.lattice.plot(periodic=periodic, wigner_seitz=wigner_seitz, sym_center=False,
                                       nearest_neighbour_color="grey", ax=ax, zorder=0)
            axplot = ax.add_collection(lines)

        ax.set_title("{0} correlations".format(tag))
        #colorbar
        scalarMap.set_array(valstoplot)
        if colored and plotcolorbar:
            #plt.colorbar(scalarMap)
            divider = make_axes_locatable(ax) 
            cax = divider.append_axes("right", size=0.2, pad=0.05) 
            cb = plt.colorbar(scalarMap, cax)


        # add arrows if directed
        if directed:
            for bond in bonds:
                p = (bond[0, :] + bond[1, :])/2.
                pdiff = (bond[1, :] - p)/2.
                ax.arrow(p[0], p[1], pdiff[0], pdiff[1], fc="black", width=0,
                         head_width=np.linalg.norm(pdiff)/4., length_includes_head=True, zorder=200)


        return (axlatt, axplot, scalarMap)


    @_axes_decorator
    def plot_triangle_correlations(self, tag='trianglecorrs', lwrange=[1, 10], minplotval=1e-10,
                                   posnegcolor=['r', 'b'], colored=True, reference_triangle=None, ax=None,
                                   plot_lattice=True,
                                   wigner_seitz=True, periodic=False, **kwargs):
        """
        Plot triangle correlations. Positive and negative values are plotted in different colors.

        :type tag: string
        :param tag: Name of the correlations which you want to plot. Default: 'trianglecorrs'
        :type lwrange: list/array (1x2)
        :param lwrange: The range for the linewidths. The correlation values are linearly mapped into this
                        range. **Optional**. Default: [1,10]
        :type minplotval: float
        :param minplotval: Correlation values smaller than this value are not plotted. **Optional**.
                           Default: 1e-10
        :type colored: Bool
        :param colored: If true, the trianles are colored according to their values using a colormap.
                        **Optional**. Default: False
        :type posnegcolor: list (1x2) of colors
        :param posnegcolor: Colors to plot positive/negative correlation values. Only if 'colored' option
                            is False. **Optional**. Default: ['r','b'] --> Positive red, negative blue
        :type reference_triangle: np.ndarray/list (1x2) of int
        :param reference_triangle: If triangle-triangle correlations are plotted, set the reference triangle
                                   with lattice positions. **Optional**. Default: [0,1]
        :type ax: Axes object
        :param ax: Axes for plotting, **optional**. Default: Create new figure and axes
        """

        if not self._lattice_set:
            raise ValueError('A lattice must be set to use plot! Use set_lattice to set a lattice!')

        #handle legend keywords
        kwargs, legkwargs = _kwtolegkw(kwargs)

        #colorbar handling
        plotcolorbar = kwargs['colorbar']
        del kwargs['colorbar']

        #Positions and values
        posread = np.array(self.pos[tag])
        if not ((len(posread.shape) == 2 and (posread.shape[1] == 3 or posread.shape[1] == 6)) or
                (len(posread.shape) == 3 and (posread.shape[1] == 2 and posread.shape[2] == 3))):
            raise ValueError('Plot triangle correlations works only for correlations with two/four'+
                             ' positional arguments!')

        values = np.array(self.val[tag])

        if wigner_seitz:
            coordinates = self.lattice.coordinates_wigner_seitz
        else:
            coordinates = self.lattice.coordinates

        # check wheter all first positions are the same and use this as reference triangle
        if reference_triangle == None:
            trianglepos1 = posread[:, 0, :]
            if np.all(np.all(trianglepos1 == trianglepos1[0, :])):
                reference_triangle = trianglepos1[0, :]
            else:
                raise ValueError('Unable to detect reference triangle for triangle-triangle correlations')

        #proceed triangle-triangle corrs with reference triangle value
        # Input like [1,2,3,4,5,6]
        if len(posread.shape) == 2:
            if posread.shape[1] == 4:
                trianglepos1 = posread[:, :3]
                trianglepos2 = posread[:, 3:]
                refidx = np.all(trianglepos1 == reference_triangle, axis=1)
                trianglestoplot = trianglepos2[refidx, :]
                valstoplot = values[refidx]
                #append reference triangle and value
                trianglestoplot = np.vstack((trianglestoplot, reference_triangle))
                valstoplot = np.append(valstoplot, np.min(valstoplot))
                lineshapes = ['-']*(len(valstoplot)-1)+['--'] #different linestyle for reference triangle
            else:
                trianglestoplot = posread
                valstoplot = values
                lineshapes = '-'

        # Input like [(1,2,3)(4,5,6)]
        elif  len(posread.shape) == 3:
            if posread.shape[1] == 2 and posread.shape[2] == 3:
                trianglepos1 = posread[:, 0, :]
                trianglepos2 = posread[:, 1, :]
                refidx = np.all(trianglepos1 == reference_triangle, axis=1)
                trianglestoplot = trianglepos2[refidx, :]
                valstoplot = values[refidx]

                #append reference triangle and value
                trianglestoplot = np.vstack((trianglestoplot, reference_triangle))
                valstoplot = np.append(valstoplot, np.min(valstoplot))
                lineshapes = ['-']*(len(valstoplot)-1)+['--'] #different linestyle for reference triangle

        #check if lwrange is okay
        if lwrange[0] < 0 or lwrange[1] < 0:
            raise ValueError('You have to use positive values for lwrange!')
        lwrange = np.sort(lwrange)

        #Coordinates of triangles in lattice
        triangles = coordinates[trianglestoplot]

        # calculate shortest distance triangles for tori
        for idx, triangle in enumerate(triangles):
            # print triangle
            # Set first bond minimal
            mindist = 100000
            for u, v in itertools.product([0, 1, -1], repeat=2):
                coord = triangle[1, :] + u * self.lattice.t1 + v * self.lattice.t2
                dist = linalg.norm(coord-triangle[0, :])
                if dist < mindist:
                    mindist = dist
                    mincoord = coord
            triangles[idx, 1, :] = mincoord

            # print mincoord

            # Set second bond minimal
            mindist = 100000
            for u, v in itertools.product([0, 1, -1], repeat=2):
                coord = triangle[2, :] + u * self.lattice.t1 + v * self.lattice.t2
                dist = linalg.norm(coord-triangle[1, :])
                if dist < mindist:
                    mindist = dist
                    mincoord = coord
            triangles[idx, 2, :] = mincoord
            # print mincoord

        #handle cfunc and factor
        if 'cfunc' in kwargs:
            valstoplot = kwargs['cfunc'](valstoplot)
            del kwargs['cfunc']

        valstoplot = kwargs['factor']*valstoplot
        del kwargs['factor']

        #Map absolute values to lwrange (default:[1,10]) for plotting as linewidths
        absvalues = np.abs(valstoplot)
        valrange = np.max(absvalues)-np.min(absvalues)
        lws = (absvalues-np.min(absvalues))/valrange*np.diff(lwrange) + lwrange[0]
        #find small values which shouldnt be plotted
        idxsmall = absvalues < minplotval
        lws[idxsmall] = 0.


        if 'vmax' in kwargs:
            vmax = kwargs['vmax']
        else:
            vmax = np.max(valstoplot)


        if 'vmin' in kwargs:
            vmin = kwargs['vmin']
        else:
            vmin = np.min(valstoplot)


        if not colored:
            #check which values are positive/negative and give the corresponding color
            cm = plt.get_cmap('coolwarm')
            cNorm = cols.Normalize(vmin=vmin, vmax=vmax)
            scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cm)
            colors = [(posnegcolor[0] if val > 0 else posnegcolor[1]) for val in valstoplot]
        else:
            cm = plt.get_cmap('coolwarm')
            cNorm = cols.Normalize(vmin=vmin, vmax=vmax)
            scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cm)
            colors = scalarMap.to_rgba(valstoplot)

        #Change color, linewidth of reference bond for bond-bond corrs
        if posread.shape[1] == 6 or (len(posread.shape) == 3 and posread.shape[1] == 2 and posread.shape[2] == 3):
            if colored:
                colors[-1] = [0., 0., 0., 1.]
            else:
                colors[-1] = 'k'
            lws[-1] = 2.

        #triple the colors and linewidths for plotting bonds
        colors = [[color, color, color] for color in colors]
        colors = np.array([c  for threec in colors for c in threec])
        lws = [[lw, lw, lw] for lw in lws]
        lws = np.array([l  for threel in lws for l in threel])
        lineshapes = [[l, l, l] for l in lineshapes]
        lineshapes = np.array([l  for threel in lineshapes for l in threel])

        #create lines
        bonds = []
        for triangle in triangles:
            bonds.append(np.array([triangle[0, :], triangle[1, :]]))
            bonds.append(np.array([triangle[1, :], triangle[2, :]]))
            bonds.append(np.array([triangle[2, :], triangle[0, :]]))
        bonds = np.array(bonds)


        #Line Collection
        lines = LineCollection(bonds, linewidths=lws, color=colors, linestyles=lineshapes)

        #Plotting
        if plot_lattice:
            axlatt = self.lattice.plot(periodic=periodic, wigner_seitz=wigner_seitz,
                                       sym_center=False, ax=ax)
            axplot = ax.add_collection(lines)

        ax.set_title("{0} correlations".format(tag))

        if plotcolorbar:
            scalarMap.set_array(valstoplot)
            #plt.colorbar(scalarMap)

            divider = make_axes_locatable(ax) 
            cax = divider.append_axes("right", size=0.2, pad=0.05) 
            cb = plt.colorbar(scalarMap, cax)

        return (axlatt, axplot)


    def g2_correlation(self, tag, centralizer_tag, connected=False, symmetrize=False, debug=False):
        """
        Plot the g2 correlation function. Only for open clusters in the moment!

        :type tag: str
        :param tag: 2-body correlation tag
        :type centralizer_tag: str
        :param centralizer_tag: 1-body correlation tag to normalize g2
        :type connected: Bool
        :param connected: If True plot the connected correlation function instead. **Optional**. Default: False
        :type symmetrize: Bool
        :param symmetrize: If True, the correlations are symmetrized. This may be used for experimental, noisy data. **Optional**. Default: False
        """

        if not self._lattice_set:
            raise ValueError('No lattice defined! Use set_lattice() to set a lattice.')

        if not self.lattice._opencluster:
            raise ValueError('g2_correlation is currently only implemented for open clusters!')

        if tag == None or centralizer_tag == None:
            raise ValueError('You must give a tag and a centralizer tag. Abort!')

        ## compute g^2 (k,l)
        #get centralizer correlations
        pos, valuesni = self.get(centralizer_tag)
        pos = np.ravel(pos[0])
        valuesni = valuesni[0]
        coords = self.lattice.coordinates[pos]

        #get correlations
        posninj, valuesninj = self.get(tag)
        posninj = np.squeeze(posninj[0])
        valuesninj = valuesninj[0]
        #both directions of correlations
        posninj = np.vstack((posninj, posninj[:, [1, 0]]))
        valuesninj = np.hstack((valuesninj, valuesninj))

        #print lattice distance (has to be changed for PBC)
        coordsninj = self.lattice.coordinates[posninj]
        diffninj = np.squeeze(np.diff(coordsninj, axis=1))
        diffninj = np.around(diffninj, decimals=4)

        #compute ninj/ni*nj or ninj-ni*nj
        g2corr = np.zeros_like(valuesninj)
        for i, p in enumerate(posninj):
            ni = valuesni[pos == p[0]]
            nj = valuesni[pos == p[1]]
            if not connected:
                g2corr[i] = valuesninj[i]/(ni*nj)
            else:
                g2corr[i] = valuesninj[i]-(ni*nj)

        kls = unique_rows(diffninj)
        g2kl = np.zeros(kls.shape[0])
        nkl = np.zeros(kls.shape[0], dtype=int)
        for i, kl in enumerate(kls):
            g2s = g2corr[np.all(diffninj == kl, axis=1)]
            g2kl[i] = np.sum(g2s)/g2s.shape[0]
            nkl[i] = g2s.shape[0]

        if symmetrize:
            klsunique = unique_rows(np.abs(kls))
            factors = [np.array([1,1]), np.array([1,-1])]

            for kl in klsunique:
                g2sym = 0.
                idxs = []
                for factor in factors:
                    idx = np.all(kls==(kl*factor), axis=1)
                    negidx = np.all(kls==-(kl*factor), axis=1)
                    idxs.append(idx)
                    idxs.append(negidx)
                    g2sym += g2kl[idx]

                g2sym /= 2.
                
                #write the symmetrized g2
                for idx in idxs:
                    g2kl[idx] = g2sym

        if debug:
            return kls, nkl
        else:
            return kls, g2kl

    @_axes_decorator
    def plot_g2(self, tag, centralizer_tag, connected=False, symmetrize=False, factor=1., ms=700,
                colorbar=True, plot_vals=False, ax=None, debug=False, **kwargs):
        """
        Plot the g2 correlation function. Only for open clusters in the moment!

        :type tag: str
        :param tag: 2-body correlation tag
        :type centralizer_tag: str
        :param centralizer_tag: 1-body correlation tag to normalize g2
        :type connected: Bool
        :param connected: If True plot the connected correlation function instead. **Optional**. Default: False
        :type symmetrize: Bool
        :param symmetrize: If True, the correlations are symmetrized. This may be used for experimental, noisy data. **Optional**. Default: False
        :type factor: float
        :param factor: Multiply the correlations with this factor. **Optional**. Default: 1.0
        :type ms: float
        :param ms: marker size. **Optional**
        :type colorbar: bool
        :param colorbar: If True, a colorbar is plotted. **Optional**. Default: True
        :type plot_vals: bool
        :param plot_vals: If True, the plotted values are shown as text in the plot. **Optional**. Default: False
        """

        kls, g2kl = self.g2_correlation(tag, centralizer_tag, connected=connected, symmetrize=symmetrize, debug=debug)

        #kwargs handling
        if 'marker' in kwargs:
            marker = kwargs['marker']
            del kwargs['marker']
        else:
            marker = 'o'

        if 'clabel' in kwargs:
            clabel = kwargs['clabel']
            del kwargs['clabel']
        else:
            clabel = None

        g2ax = ax.scatter(kls[:, 0], kls[:, 1], c=g2kl*factor, s=ms, marker=marker, **kwargs)

        if plot_vals:
            for i in range(kls.shape[0]):
                val = g2kl[i]*factor
                if np.abs(val) > .9 * factor * np.max(np.abs(g2kl)):
                    color = 'w'
                else:
                    color = 'k'
                ax.text(kls[i,0], kls[i,1], '%.3f' %val, va='center', ha='center', color=color, zorder=1000)

        if debug:
            for co, v in zip(kls, g2kl):
                ax.text(co[0], co[1], '%d' %v, va='center', ha='center')

        #colorbar handling
        if colorbar:
            #plt.colorbar(g2ax)
            divider = make_axes_locatable(ax) 
            cax = divider.append_axes("right", size=0.2, pad=0.05) 
            cb = plt.colorbar(g2ax, cax, label=clabel)

        ax.axis('equal')
        ax.set_xlabel('k')
        ax.set_ylabel('l')
        ax.set_title(r'$g^{(2)}(k,l)$')

        return g2ax
