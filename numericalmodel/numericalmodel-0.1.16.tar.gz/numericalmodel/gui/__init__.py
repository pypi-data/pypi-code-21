#!/usr/bin/env python3
# system modules
import os, sys, time, re
import tempfile
import hashlib
import logging
import signal
import textwrap
import gettext
import webbrowser
import locale
from pkg_resources import resource_filename

# internal modules
from .. import utils
from ..numericalmodel import NumericalModel
from .. import __version__

# external modules
import numpy as np

logger = logging.getLogger(__name__)

# set up localization
GETTEXT_DOMAIN = 'numericalmodelgui'
LOCALEDIR = resource_filename(__name__,"locale")
locale.setlocale(locale.LC_ALL,'')
for mod in [locale,gettext]:
    mod.bindtextdomain(GETTEXT_DOMAIN,LOCALEDIR)
gettext.textdomain(GETTEXT_DOMAIN)
gettext.install(GETTEXT_DOMAIN,localedir=LOCALEDIR)

instructions = textwrap.dedent("""
To install the prerequisites, use your system's package manager and install
at least ``python3-gi`` (might also be called ``pygobject3``). You might also
need ``libffi``.

On Debian/Ubuntu:

.. code:: sh

    sudo apt-get install python3-gi libcffi6 libffi-dev

.. note:: If you don't have system privileges to install ``python3-gi`` , there
    is also the (experimental) :mod:`pgi` module on `PyPi
    <https://pypi.python.org/pypi/pgi/>`_ that you can install via::

        pip3 install --user pgi

    Theoretically, the :any:`NumericalModelGui` might work with this package as
    well, but no guarantees...

.. warning::

    If you are using `Anaconda <https://conda.io/docs/index.html>`_ you will
    **NOT** have fun trying to install Gtk. It seems to be pretty impossible
    unfortunately...

Then, install :mod:`numericalmodel` with the ``gui`` feature:

.. code:: sh

    pip3 install --user 'numericalmodel[gui]'

""")

__doc__ = \
"""
Graphical user interface for a NumericalModel. This module is only useful
if the system package ``python3-gi`` is installed to provide the :mod:`gi`
module.

""" + instructions

PGI = False
GTK_INSTALLED = False
try: # try real gi module
    import gi
    gi.require_version('Gtk','3.0')
    from gi.repository import Gtk,Gdk,GLib,GdkPixbuf
    GTK_INSTALLED = True # importing real gi worked
except Exception as e: # importing real gi didn't work
    logger.info("no 'gi' module found: {}".format(e))
    try: # try pgi package
        import pgi
        pgi.install_as_gi()
        import gi
        gi.require_version('Gtk','3.0')
        from gi.repository import Gtk
        from gi.repository import GLib
        PGI = True
        GTK_INSTALLED = True # importing pgi worked
        logger.warning("using 'pgi' module instead of 'gi'")
    except:
        logger.error("Neither 'pgi' nor 'gi' module found!"
            "The GUI will not work.")

class FigureCanvasFile(Gtk.EventBox):
    """
    Class to mimic a
    :class:`matplotlib.backends.backend_gtk3agg.FigureCanvasGTK3Agg` as a
    fallback solution with a primitive file-based approach.

    Args:
        figure (matplotlib.figure.Figure): the figure to show
        args,kwargs : further arguments passed to the :class:`Gtk.EventBox`
            constructor
    """
    def __init__(self, figure, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.figure = figure
        self.scrolledwindow.add_with_viewport(self.image)
        self.add(self.scrolledwindow)

    @property
    def scrolledwindow(self):
        """
        The underlying :class:`Gtk.ScrolledSindow`

        :type: :class:`Gtk.ScrolledSindow`
        """
        try:
            self._scrolledwindow
        except AttributeError:
            self._scrolledwindow = Gtk.ScrolledWindow()
        return self._scrolledwindow

    @property
    def image(self):
        """
        The underlying :class:`Gtk.Image`

        :type: :class:`Gtk.Image`
        """
        try:
            self._image
        except AttributeError:
            self._image = Gtk.Image()
        return self._image

    @property
    def figure(self):
        """
        The underlying figure

        :type: :class:`matplotlib.figure.Figure`
        :setter: sets the figure and calls :meth:`load`
        """
        try:
            self._figure
        except AttributeError:
            self._figure = Figure()
        return self._figure

    @figure.setter
    def figure(self, newfigure):
        assert isinstance(newfigure,Figure)
        if newfigure.canvas is None:
            newfigure.canvas = FigureCanvasAgg(newfigure)
        self._figure = newfigure

    @property
    def imagefile(self):
        """
        The path to the underlying image

        :type: :any:`str`
        :getter: Creates new temporary hidden file in the current folder if none
            was specified yet
        :setter: Sets the new path, removing the old file if necessary
        """
        try:
            self._imagefile
        except AttributeError:
            n,path = tempfile.mkstemp(
                dir=os.path.curdir,suffix=".png",prefix=".")
            logger.debug("Created new temporary file '{}'".format(path))
            self._imagefile = path
        return self._imagefile

    @imagefile.setter
    def imagefile(self, newimagefile):
        try:
            self._imagefile
            logger.debug("Removing old image '{}'".format(self._imagefile))
            os.remove(self._imagefile)
        except AttributeError:
            pass
        self._imagefile = str(newimagefile)

    ###############
    ### Methods ###
    ###############
    def save(self, width, height):
        """
        Save the current figure to :any:`imagefile`

        Args:
            width, height (int): width and height in pixels
        """
        DPI = self.figure.get_dpi()
        self.figure.set_size_inches(width/DPI,height/DPI)
        self.figure.savefig( self.imagefile )

    def load(self):
        """
        (Re)load the underlying :any:`imagefile`
        """
        logger.debug("Reading image '{}'".format(self.imagefile))
        self.image.set_from_file( self.imagefile )

    def display(self, width, height):
        """
        Get the content of the current figure displayed by calling :meth:`save`
        and :any:`load`.

        Args:
            width, height (int): width and height in pixels
        """
        self.save(width = width, height = height)
        self.load()

    def remove_imagefile(self):
        """
        Remove the :any:`imagefile`
        """
        try:
            self._imagefile
            logger.debug("Removing temporary image '{}'".format(
                self._imagefile))
            os.remove(self.imagefile)
        except AttributeError:
            pass

    #######################
    ### Special Methods ###
    #######################
    def __del__(self):
        """
        Class destructor. Deletes the :any:`imagefile`.
        """
        self.remove_imagefile()

from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
try:
    from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg \
        as FigureCanvas
except:
    FigureCanvas = FigureCanvasFile
    logger.error("matplotlib seems to not have a working Gtk3 backend. "
        "Falling back to file-based backend.")


MODEL_CONTENT = ["variables","forcing","parameters","observations"]

class NumericalModelGui(object):
    """
    class for a GTK gui to run a :any:`NumericalModel` interactively

    Args:
        numericalmodel (NumericalModel): the NumericalModel to run
        custom_plots (dict, optional): custom plots. This is a :any:`dict` like
            ``custom_plots[name]=function(model,figure,**gui_plot_options)``.
            The ``gui_plot_options`` will be set to :any:`plot_settings`. The
            function should just take the figure (a
            :any:`matplotlib.figure.Figure`) and add plots to it as if it was
            newly created. The data can be taken from the ``model`` argument,
            which will be set to :any:`NumericalModelGui.model`.
        use_fallback (bool, optional): use the file-based
            :class:`FigureCanvasFile` as file-based backend? This may help if
            there are problems with the GTK/matplotlib-interaction. Defaults
            to ``False`` .
    """
    def __init__(self, numericalmodel, custom_plots = None,
        use_fallback = False):
        if not GTK_INSTALLED:
            raise Exception(
                "Gtk3.0 bindings seem not installed.\n"+instructions)

        self.setup_signals(
            signals = [signal.SIGINT, signal.SIGTERM, signal.SIGHUP],
            handler = self.quit
        )

        self.dragtargets = Gtk.TargetList.new([])
        self.dragtargets.add_text_targets(80)

        self.use_fallback = use_fallback

        self.model = numericalmodel
        if not custom_plots is None:
            self.custom_plots = custom_plots

    ##################
    ### Properties ###
    ##################
    @property
    def model(self):
        """
        The :any:`NumericalModel` behind the gui

        :type: :any:`NumericalModel`
        """
        try:
            return self._model
        except AttributeError:
            self._model = NumericalModel()
        return self._model

    @model.setter
    def model(self, newmodel):
        assert isinstance(newmodel,NumericalModel)
        self._model = newmodel

    @property
    def builder(self):
        """
        The gui's :code:`GtkBuilder`. This is a read-only property.

        :getter: Return the :class:`GtkBuilder`, load the :any:`gladefile` if
            necessary.
        :type: :class:`GtkBuilder`
        """
        try:
            self._builder
        except AttributeError:
            builder = Gtk.Builder() # new builder
            # set translation domain
            builder.set_translation_domain(GETTEXT_DOMAIN)
            # load the gladefile
            builder.add_from_file( self.gladefile )
            # set internal attribute
            self._builder = builder
        return self._builder

    @property
    def gladefile(self):
        """
        The gui's Glade file. This is a read-only property.

        :type: :any:`str`
        """
        return resource_filename(__name__, "gui.glade")

    @property
    def figures(self):
        """
        The gui's :any:`matplotlib.figure.Figure` for plotting

        :type: :any:`dict` of :any:`matplotlib.figure.Figure`
        :getter: returns the gui's :any:`matplotlib.figure.Figure`, create one
            if necessary
        """
        try:
            self._figures
        except AttributeError:
            self._figures = {n:Figure(tight_layout=True) for n in MODEL_CONTENT}
            self._figures.update(
                {n:Figure(tight_layout=True) for n in self.custom_plots.keys()}
                )
        return self._figures

    @property
    def figures_content(self):
        """
        The :any:`figures` ' content as abstract dict

        :type: :any:`dict` of :any:`str`
        :getter: returns the :any:`figures` ' current content template, create
            new template if none was set yet
        :setter: sets the :any:`figures` ' content template and reloads the
            current plot. Resets the content template if set to ``None``.
        """
        try:
            self._figures_content
        except AttributeError:
            # default figure content
            self._figures_content = {}
            for tab in MODEL_CONTENT:
                self._figures_content[tab] = {}
                self._figures_content[tab][tab]= \
                    {k:v for k,v in sorted(getattr(self.model,tab).items())}
        return self._figures_content

    @figures_content.setter
    def figures_content(self, newcontent):
        if newcontent is None:
            del self._figures_content
        else:
            assert hasattr(newcontent,"items")
            self._figures_content = newcontent
        # changing the figures' content means replotting
        self.update_current_plot()

    @property
    def custom_plots(self):
        """
        Custom plots

        :type: :any:`dict`
        """
        try:
            self._custom_plots
        except AttributeError:
            self._custom_plots = {}
        return self._custom_plots

    @custom_plots.setter
    def custom_plots(self, newcustom_plots):
        assert hasattr(newcustom_plots,"items"), \
            "custom_plots have to be dict"
        self._custom_plots = newcustom_plots

    @property
    def logo_pixbuf(self):
        """
        The logo as :class:`GdkPixbuf.Pixbuf`

        :type: :class:`GdkPixbuf.Pixbuf`
        """
        try:
            self._logo_pixbuf
        except AttributeError:
            logo_path = resource_filename(__name__,"media/logo.png")
            logo_pixbuf = GdkPixbuf.Pixbuf.new_from_file(logo_path)
            self._logo_pixbuf = logo_pixbuf
        return self._logo_pixbuf

    @property
    def scales(self):
        """
        The :class:`GtkScale` used to manipulate model data

        :type: :any:`dict` of :class:`GtkScale`
        :getter: return the gui's :class:`GtkScale` s, create new if necessary
        """
        try:
            self._scales
        except AttributeError:
            self._scales = {}
            for attr in MODEL_CONTENT:
                self._scales[attr] = {}
                grid = Gtk.Grid()
                grid.props.hexpand = True
                grid.props.column_spacing = 10
                grid.props.row_spacing = 5
                i = 0
                for ivid,iv in sorted(getattr(self.model,attr).items()):
                    self._scales[attr][ivid] = {}
                    self._scales[attr][ivid]["initial"] = iv.value
                    lower, upper = iv.bounds
                    adj = self.adjustment_from_bounds(
                        value=iv.value,values=iv.values,lower=lower,upper=upper)
                    scale = Gtk.Scale(
                        orientation=Gtk.Orientation.HORIZONTAL,adjustment=adj)
                    scale.props.draw_value = False
                    scale.set_size_request(width = 100, height = -1)
                    digits = num_decimals(
                            scale.get_adjustment().get_step_increment())
                    scale.props.digits = digits
                    scale.props.hexpand = True
                    scale.add_mark(self._scales[attr][ivid]["initial"],
                        Gtk.PositionType.TOP,None)
                    spinbutton = Gtk.SpinButton.new(
                        scale.get_adjustment(),
                        climb_rate=scale.get_adjustment().get_step_increment(),
                        digits = scale.props.digits
                        )
                    spinbutton.set_tooltip_markup(_("The value used in "
                        "the model might have a higher accuracy.")+"\n"+_(
                        "The initial value when the GUI was launched "
                        "was <b>{}</b>.").format(iv.value)+"\n"+_(
                        "Drag'n'Drop the name <b>{}</b> onto the plot area "
                        "to see the actual value.").format(ivid)
                        )
                    eventbox = Gtk.EventBox()
                    namelabel = Gtk.Label()
                    namelabel.set_markup("<b>{}</b>".format(ivid))
                    namelabel.set_alignment(1,0.5)

                    eventbox.drag_source_set(
                        Gdk.ModifierType.BUTTON1_MASK,
                        [],
                        Gdk.DragAction.COPY
                        )
                    eventbox.drag_source_set_target_list(self.dragtargets)
                    def on_drag_get(widget, context, data,info,time,*args):
                        modelpart, ivid = args
                        string = "{}:::{}".format(modelpart,ivid)
                        data.set_text(string,len(string))
                    eventbox.connect("drag-data-get",on_drag_get,attr,ivid)
                    eventbox.add(namelabel)
                    unitlabel = Gtk.Label(iv.unit)
                    unitlabel.set_alignment(0,0.5)
                    for w in [unitlabel,scale]:
                        w.set_tooltip_markup("<b>{}</b>\n".format(iv.name)+_(
                            "Drag'n'Drop the name "
                            "<b>{}</b> onto the plot area to add it").format(
                            ivid))
                    for w in [namelabel]:
                        w.set_tooltip_markup("<b>{}</b>\n".format(iv.name)+_(
                            "Drag'n'Drop this onto the plot area to add it"))

                    grid.attach(scale,1,i,1,1)
                    grid.attach_next_to(
                        eventbox,scale,Gtk.PositionType.LEFT,1,1)
                    grid.attach_next_to(
                        spinbutton,scale,Gtk.PositionType.RIGHT,1,1)
                    grid.attach_next_to(
                        unitlabel,spinbutton,Gtk.PositionType.RIGHT,1,1)
                    self._scales[attr][ivid]["scale"] = scale
                    i += 1
                self._scales[attr]["grid"] = grid
        return self._scales

    @property
    def plot_settings(self):
        """
        Current settings from the plot settings page.

        :type: :any:`dict`
        """
        plot_settings = {}
        plot_settings["use_variable_time"] = \
            self["settings_plot_usevariabletime_checkbutton"].get_active()
        plot_settings["consistent_colors"] = \
            self["settings_plot_consistent_colors_checkbutton"].get_active()
        plot_settings["scatter"] = \
            self["settings_plot_scatterplot_checkbutton"].get_active()
        plot_settings["equal_axes"] = \
            self["settings_plot_equal_axes_checkbutton"].get_active()
        plot_settings["identity_line"] = \
            self["settings_plot_show_identity_checkbutton"].get_active()
        plot_settings["split_units"] = \
            self["settings_plot_split_units_checkbutton"].get_active()
        plot_settings["linear_fit"] = \
            self["settings_plot_linear_fit_checkbutton"].get_active()
        plot_settings["fit_intercept"] = \
            self["settings_plot_fit_intercept_checkbutton"].get_active()
        return plot_settings



    ###############
    ### Methods ###
    ###############
    @classmethod
    def adjustment_from_bounds(cls, value, values, lower, upper, nsteps = 1000):
        """
        Given upper and lower bounds of a range, set up a
        :class:`Gtk.Adjustment`.

        Args:
            value (float): the current value
            values (numpy.ndarray): all values
            lower, upper (float): lower and upper bounds. May be infinte.
            nsteps (int, optional): in how many steps to use. Defaults to
                ``1000``.
        """
        values = np.asarray(values)
        values = values[np.isfinite(values)]
        if np.isfinite([lower,upper]).all():
            pass
        elif np.isfinite(lower):
            upper = max(max(lower,value),1) * 2
        elif np.isfinite(upper):
            lower = - min(min(upper,value),1) * 2
        else:
            lower, upper = [-2*abs(min(values)),2*abs(max(values))]
        # now lower and upper are numbers
        # get accurate step width
        stepdiff = ( upper - lower ) / nsteps
        # count step width decimal places
        stepdiff_nice = 10**-pos_significant_decimal(stepdiff)
        return Gtk.Adjustment(
            value = value,lower = lower, upper = upper,
            step_increment = stepdiff_nice)

    def setup_signals(self, signals, handler):
        """
        This is a workaround to signal.signal(signal, handler)
        which does not work with a ``GLib.MainLoop`` for some reason.
        Thanks to: http://stackoverflow.com/a/26457317/5433146

        Args:
            signals (list): the signals (see :any:`signal` module) to
                connect to
            handler (callable): function to be executed on these signals
        """
        def install_glib_handler(sig): # add a unix signal handler
            GLib.unix_signal_add( GLib.PRIORITY_HIGH,
                sig, # for the given signal
                handler, # on this signal, run this function
                sig # with this argument
                )

        for sig in signals: # loop over all signals
            GLib.idle_add( # 'execute'
                install_glib_handler, sig, # add a handler for this signal
                priority = GLib.PRIORITY_HIGH  )

    def plot_interfacevalues(self, interfacevalues, figure, times = None,
        scatter = False, consistent_colors = False, equal_axes = False,
        identity_line = False, split_units = True, linear_fit = False,
        fit_intercept = True, **kwargs):
        """
        Plot an :any:`InterfaceValue` onto a given Figure

        Args:
            interfacevalues (list): the :any:`InterfaceValue` s to plot
            figure (matplotlib.figure.Figure): the
                :any:`matplotlib.figure.Figure` to plot onto
            times (numpy.ndarray, optional): Times to plot. If left unspecified,
                plot the times that are available.
            scatter (bool, optional): Use scatterplots where possible? Defaults
                to ``False``.
            consistent_colors (bool, optional): Use consistent colors for all
                plots, i.e. determine the color from the :any:`InterfaceValue`
                's metadata? Defaults to ``False``.
            identity_line (bool, optional): If ``scatter`` is ``True``, draw an
                identity line? Defaults to ``False``.
            equal_axes (bool, optional): If ``scatter`` is ``True``, use an
                aspect ratio of ``1:1`` for the x/y-axis? Defaults to ``False``.
            split_units (bool, optional): Put values of matching units into
                separate plots? Defaults to ``True``.
            linear_fit (bool, optional): If ``scatter=True``, display a linear
                fit? Defaults to ``False``.
            fit_intercept (bool, optional): If ``linear_fit=True``, fit an
                intercept? Defaults to ``True``.
        """
        units = {}
        if split_units:
            for interfacevalue in interfacevalues:
                try:
                    units[interfacevalue.unit].append(interfacevalue)
                except KeyError:
                    units[interfacevalue.unit] = [interfacevalue]
        else:
            units = {"] [".join(set([iv.unit for iv in interfacevalues])):
                interfacevalues}

        interp2drawstyle = {}
        if times is None:
            interp2drawstyle = {'linear':'default','nearest':'steps-mid',
                'zero':'steps-post',}
        i = 1
        axes = {}
        timeunit = "s"
        for unit,ivlist in sorted(units.items()):
            try:
                axes[unit]
            except KeyError:
                if scatter:
                    axes[unit] = figure.add_subplot(len(units),1,
                            len(units)-i+1)
                else:
                    try:
                        axes[unit] = figure.add_subplot(len(units),1,
                            len(units)-i+1, sharex=xaxis_shared)
                    except NameError:
                        axes[unit] = figure.add_subplot(len(units),1,
                            len(units)-i+1)
                        xaxis_shared = axes[unit]
            ax = axes[unit]
            plot_kwargs_all = { "linewidth":2, "zorder":5 }
            if scatter:
                if len(ivlist) == 1:
                    # 1-1 scatterplot
                    plot_kwargs = plot_kwargs_all.copy()
                    iv = ivlist[0]
                    plot_kwargs.update(
                        {"label":"{} ({}) {} {}".format(
                            iv.name,iv.id,_("vs."),_("itself"))})
                    if consistent_colors:
                        plot_kwargs.update(
                            {"color":string2color(iv.name+iv.id)})
                    if times is None:
                        times = iv.times
                    ax.scatter(iv(times),iv(times),**plot_kwargs)
                    ax.set_xlabel("{} [{}]".format(iv.id,iv.unit))
                    ax.set_ylabel("{} [{}]".format(iv.id,iv.unit))
                else:
                    if times is None:
                        times = np.array([])
                        for v in ivlist:
                            times = np.union1d(times,v.times)
                    multiscatter_units = []
                    for iv in ivlist:
                        plot_kwargs = plot_kwargs_all.copy()
                        if consistent_colors:
                            plot_kwargs.update(
                                {"color":string2color(iv.name+iv.id)})
                        # stacked scatterplot
                        try:
                            main_iv
                            multiscatter_units.append(iv.unit)
                            plot_kwargs.update({"label":"{} ({}) {} {} ({})"\
                                .format(iv.name,iv.id,_("vs."),main_iv.name,
                                main_iv.id)})
                            ax.scatter(main_iv(times),iv(times),**plot_kwargs)
                            # linear fit
                            if linear_fit:
                                a,b = linear_regression(
                                    main_iv(times),iv(times),
                                    fit_intercept=fit_intercept)
                                plot_kwargs.update({"label":
                                    r"{} = {:.4f} "
                                        "$\cdot$ {} {}".format(
                                    iv.id,a,main_iv.id,
                                    r"${}{:.4f}$".format("+ " if b>0 else "",b)\
                                        if fit_intercept else "",
                                    main_iv.id),
                                    "linestyle":":",
                                    "zorder":plot_kwargs["zorder"]+1,
                                    })
                                low,high = ax.get_xlim()
                                x = np.linspace(low,high,1000)
                                y = a*x+b
                                ax.plot(x,y,**plot_kwargs)
                        except NameError:
                            main_iv = iv
                        ax.set_xlabel("{} [{}]".format(main_iv.id,main_iv.unit))
                        ax.set_ylabel("["+"] [".join(
                            set(multiscatter_units))+"]")
                if equal_axes:
                    ax.set_aspect("equal","datalim")
                if identity_line:
                    xl,xu = ax.get_xlim()
                    yl,yu = ax.get_ylim()
                    plot_kwargs = plot_kwargs_all.copy()
                    plot_kwargs.update({"zorder":10,"c":"k","linestyle":"--",
                        "label":_("identity")})
                    low,high = min(xl,yl), max(xu,yu)
                    ax.plot([low,high],[low,high],**plot_kwargs)
            else: # no scatter plot
                for iv in ivlist:
                    plot_kwargs = plot_kwargs_all.copy()
                    if times is None:
                        x = iv.times
                        y = iv.values
                    else:
                        oneday = 24 * 60 * 60
                        onehour = 60 * 60
                        oneminute = 60
                        if max(times) > oneday:
                            x = times / oneday
                            timeunit = "d"
                        elif max(times) > onehour:
                            x = times / onehour
                            timeunit = "h"
                        elif max(times) > oneminute:
                            x = times / oneminute
                            timeunit = "min"
                        else:
                            x = times
                        y = iv(times)

                    plot_kwargs.update(
                        {"label":"{} ({})".format(iv.name,iv.id)})
                    if consistent_colors:
                        plot_kwargs.update(
                            {"color":string2color(iv.name+iv.id)})
                    if np.array(x).size > 1:
                        plot_kwargs.update({ "drawstyle":interp2drawstyle.get(
                                iv.interpolation,"steps-post"),})
                        ax.plot( x,y, **plot_kwargs)
                    else:
                        ax.scatter( x,y, **plot_kwargs)
                ax.set_ylabel("[{}]".format(unit))
            ax.tick_params(direction="in")
            ax.grid(zorder=0)
            ax.legend(fontsize="small")
            i += 1

        for unit,ax in axes.items():
            try:
                if ax == xaxis_shared:
                    ax.set_xlabel("{} [{}]".format(_("time"),timeunit))
                else:
                    ax.tick_params(bottom=True,left=True,top=True,
                        right=True,labelbottom=False,)
            except NameError:
                ax.tick_params(bottom=True,left=True,top=True,
                    right=True,labelbottom=True,)

    def apply_data_from_settings(self,*args,**kwargs):
        """
        Read the data from the settings and feed it into the model
        """
        self.add_status("settings",_("Applying new data settings..."))
        for what,d in self.scales.items():
            for ivid,widgets in sorted(d.items()):
                if ivid == "grid": continue
                iv = getattr(self.model,what)[ivid]
                value = widgets["scale"].get_adjustment().get_value()
                if iv.value != value:
                    try:
                        iv.next_time = iv.time + \
                            0.99 * (iv.time_function()-iv.time)
                        iv.value = iv.value
                        iv.next_time = None
                        iv.value = value
                    except Exception as e:
                        problem = _("Could not update {} from {} to {}")\
                            .format(iv.id,iv.value,value)
                        self.error(main=problem,secondary="<i>{}</i>".format(e))
                        self.add_status("settings",problem,important = True)
                        logger.warning(problem)
                        value = widgets["scale"].get_adjustment().set_value(
                            iv.value)

        self.add_status("settings",_("New data fed into model!"))

    def apply_model_data_to_settings(self,*args,**kwargs):
        """
        Read the data from the model and feed it into the settings
        """
        self.add_status("settings",_("Applying model data to settings..."))
        for what,d in self.scales.items():
            for ivid,widgets in sorted(d.items()):
                if ivid == "grid": continue
                iv = getattr(self.model,what)[ivid]
                adj = widgets["scale"].get_adjustment()
                modelvalue = iv.value
                lower, upper = adj.props.lower, adj.props.upper
                if modelvalue < lower:
                    adj.props.lower = modelvalue - abs(modelvalue-lower)
                elif modelvalue > upper:
                    adj.props.upper = modelvalue + abs(modelvalue-upper)
                adj.set_value(iv.value)
        self.add_status("settings",_("Model data fed into settings!"))

    def reset_scales(self, what=None):
        """
        Reset scales

        Args:
            what (list, optional): Reset what scales? Sublist of
                ``["variables","forcing","parameters","observations"]`` .
                Reset all if left unspecified.
        """
        if what is None:
            what = self.scales.keys()
        for whatscale in what:
            for ivid,widgets in self.scales[what].items():
                if ivid == "grid": continue
                widgets["scale"].set_value( widgets["initial"] )

    def update_current_plot(self, *args, **kwargs):
        """
        Update the current plot
        """
        plot_interfacevalues_kwargs = self.plot_settings
        if plot_interfacevalues_kwargs["use_variable_time"]:
            all_times = np.array([])
            for v in self.model.variables.elements:
                all_times = np.union1d(all_times,v.times)
            plot_interfacevalues_kwargs["times"] = all_times

        current_tab = self["plot_notebook"].get_current_page()
        current_box = self["plot_notebook"].get_nth_page(current_tab)
        current_canvas = current_box.get_children()[0]
        current_figure = current_canvas.figure
        for ax in current_figure.axes:
            current_figure.delaxes(ax)
        for title,plotter in self.custom_plots.items():
            if self.figures.get(title) == current_figure:
                try:
                    plotter(model=self.model,figure=current_figure,
                        **self.plot_settings)
                except Exception as e:
                    self.error(_("Plotting error"),str(e))

        for tab,content in self.figures_content.items():
            if self.figures.get(tab) == current_figure:
                self.add_status("plot",_("Plotting..."),important=True)
                interfacevalues = []
                for modelpart,ivs in content.items():
                    interfacevalues.extend(ivs.values())
                try:
                    self.plot_interfacevalues(
                        interfacevalues,
                        current_figure, # onto this figure
                        **plot_interfacevalues_kwargs
                        )
                except ValueError as e:
                    if str(e) == \
                        "Width and height specified must be non-negative":
                        self.error(_("Plot area is too small"),
                            _(
                            "This is a known plotting issue with the fallback "
                            "file-based backend that is used here because "
                            "something didn't work with the GTK/matplotlib "
                            "interaction."
                            "\n\n"
                            "To prevent this, next time you open this GUI, "
                            "make sure the window is big enough for the plots."
                            "\n\n"
                            "This plot seems to be broken from now on...")
                            )
                except Exception as e:
                    self.error(_("Plotting error"),str(e))

        current_figure.canvas.draw()

        # if this is a fallback file canvas, tell it to update
        if isinstance(current_canvas,FigureCanvasFile):
            width = current_canvas.get_allocation().width
            height = current_canvas.get_allocation().height
            current_canvas.display(width=width,height=height)
            self.wait_for_gui()

        self.add_status("plot",_("Plot updated!"),important=True)


    ###################
    ### Gui methods ###
    ###################
    def setup_gui(self):
        """
        Set up the GTK gui elements
        """
        def reset_variables(action,*args,**kwargs):
            self.reset_scales("variables")
        def reset_forcing(action,*args,**kwargs):
            self.reset_scales("forcing")
        def reset_params(action,*args,**kwargs):
            self.reset_scales("parameters")
        def reset_observations(action,*args,**kwargs):
            self.reset_scales("observations")
        def feedmodel(action,*args,**kwargs):
            self.apply_data_from_settings()
            self.update_current_plot()
        def reset_plots(action,*args,**kwargs):
            for attr in MODEL_CONTENT:
                label = self["plot_{}_notebook_label".format(attr)]
                italictext = re.sub(
                    string=label.get_text(),
                    pattern=r"^(?:<b><i>)?([^<]+)(?:</i></b>)?$",
                    repl=r"\1")
                label.set_markup(italictext)
            self.figures_content = None
        def show_about_dialog(action, *args, **kwargs):
            self.show_about_dialog()
        def show_hide_scatter_options(widget, *args, **kwargs):
            for e in [
                "settings_plot_show_identity_checkbutton",
                "settings_plot_equal_axes_checkbutton",
                "settings_plot_linear_fit_checkbutton",
                ]:
                self[e].set_sensitive(
                    self["settings_plot_scatterplot_checkbutton"].get_active())
                show_hide_linear_fit_options(widget, *args, **kwargs)
        def show_hide_linear_fit_options(widget, *args, **kwargs):
            for e in [
                "settings_plot_fit_intercept_checkbutton",
                ]:
                self[e].set_sensitive(
                    self["settings_plot_linear_fit_checkbutton"]\
                        .get_active() and
                    self["settings_plot_scatterplot_checkbutton"]\
                        .get_active()
                    )
        def online_help(action,*args,**kwargs):
            webbrowser.open("https://nobodyinperson.gitlab.io/"
                "python3-numericalmodel/gui.html")
        def save_plot(action,*args,**kwargs):
            filename = self.save_current_plot_dialog()
            if filename:
                nb = self["plot_notebook"]
                canvas=nb.get_nth_page(nb.get_current_page()).get_children()[0]
                self.add_status("plot",text=_(
                    "Saving the current plot to '{}'..."
                    ).format(filename),important=True)
                try:
                    canvas.figure.savefig(filename)
                except Exception as e:
                    self.error(main=_("Error saving plot"),secondary=str(e))
                self.add_status("plot",text=_("Current plot was saved to '{}'!"
                    ).format(filename),important=True)

        # connect signals
        self.handlers = {
            "CloseApplication": self.quit,
            "Integrate": self.integrate,
            "UpdatePlot": self.update_current_plot,
            "ShowAbout": show_about_dialog,
            "ShowHideScatterOptions": show_hide_scatter_options,
            "ShowHideLinearFitOptions": show_hide_linear_fit_options,
            "SavePlot": save_plot,
            "ResetParams": reset_params,
            "OnlineHelp": online_help,
            "ResetForcing": reset_forcing,
            "ResetVariables": reset_variables,
            "ResetObservations": reset_observations,
            "ResetPlots": reset_plots,
            "FeedModel": feedmodel,
            }
        self.builder.connect_signals(self.handlers)

        ### Plot ###
        # add the Figure to the plot box in the gui
        def on_drag_motion(widgt, context, x, y, time, *args):
            Gdk.drag_status(context, Gdk.DragAction.COPY, time)
            return True
        def on_drag_drop(widget, context, x, y, time, *args):
            widget.drag_get_data(context, context.list_targets()[-1], time)
            return True
        def on_drag_data_received(widget, context, x, y, data, info, time,
            user_data):
            try:
                attr,ivid = data.get_text().split(":::")
            except ValueError:
                self.error(main=_("Strange dropped content!"),
                    secondary=_("Whatever you dropped into here "
                        "doesn't work :-)"))
                Gtk.drag_finish(context,False,False,time)
                return False

            figures_content = self.figures_content.copy()
            newdict = {ivid:getattr(self.model,attr)[ivid]}
            try:
                figures_content[user_data]
            except KeyError:
                figures_content[user_data] = {}
            try:
                figures_content[user_data][attr].update(newdict)
            except KeyError:
                figures_content[user_data][attr] = newdict
            nb = self["plot_notebook"]
            label = nb.get_tab_label(nb.get_nth_page(nb.get_current_page()))
            italictext = re.sub(
                string=label.get_text(),
                pattern=r"^(?:<b><i>)?([^<]+)(?:</i></b>)?$",
                repl=r"<b><i>\1</i></b>")
            label.set_markup(italictext)
            self.figures_content = figures_content
            Gtk.drag_finish(context,True,False,time)
        def on_event(widget, event):
            if event.type == Gdk.EventType.BUTTON_PRESS \
                and event.button.button == 3:
                self["plot_menu"].popup(
                    None,None,None,None,event.button.button,event.time)

        # set up default figures
        for n,fig in self.figures.items():
            box = self["plot_{}_box".format(n)]
            if box:
                if self.use_fallback:
                    canvas = FigureCanvasFile(fig)
                else:
                    canvas = FigureCanvas(fig)
                canvas.drag_dest_set(0, [], Gdk.DragAction.COPY)
                canvas.drag_dest_set_target_list(self.dragtargets)
                canvas.connect("drag-motion",on_drag_motion)
                canvas.connect("drag-drop",on_drag_drop)
                canvas.connect("drag-data-received",on_drag_data_received,n)
                canvas.connect("event",on_event)
                box.pack_start(canvas,True,True,0)
        # set up custom figures
        for title,plotter in sorted(self.custom_plots.items()):
            fig = self.figures.get(title)
            if self.use_fallback:
                canvas = FigureCanvasFile(fig)
            else:
                canvas = FigureCanvas(fig)
            box = Gtk.Box.new(Gtk.Orientation.VERTICAL,0)
            box.pack_start(canvas,True,True,0)
            label = Gtk.Label(title)
            self["plot_notebook"].append_page(box,label)

        ### Fill the settings dialog ###
        for what,d in sorted(self.scales.items()):
            expander_box = self["{}_slider_box".format(what)]
            expander_box.pack_start(d["grid"],True,True,3)

        for value,text in zip(
            [60,10*60,30*60,60*60],
            [_("1 min"),_("10 min"),_("30 min"),_("1 hour")]
            ):
            self["time_scale"].add_mark(value,Gtk.PositionType.TOP,text)

        self.add_status("general",_("Running a NumericalModel interactively"))

        self["main_applicationwindow"].props.icon = self.logo_pixbuf
        # show everything
        self["main_applicationwindow"].set_title(self.model.name)
        self["main_applicationwindow"].show_all()

        self.update_current_plot()

    def error(self, main, secondary = None):
        """
        Display a error dialog

        Args:
            main (str): the main text to display
            secondary (str, optional): the secondary text to display
        """
        dialog = Gtk.MessageDialog(
            self["main_applicationwindow"],
            0,
            Gtk.MessageType.ERROR,
            Gtk.ButtonsType.OK,
            main
            )
        if not secondary is None:
            dialog.format_secondary_markup(secondary)
        dialog.run()
        dialog.destroy()

    def wait_for_gui(self):
        """
        Wait for the gui to process all pending events
        """
        while Gtk.events_pending():
            Gtk.main_iteration()

    def integrate(self, *args, **kwags):
        """
        Integrate the underlying model by the step defined in the
        ``time_adjustment``.
        """
        start_time = utils.utcnow()
        self.apply_data_from_settings()
        step = self["time_adjustment"].get_value()
        self.add_status("model",_("Integrating..."),important=True)
        integration_start_time = utils.utcnow()
        try:
            self.model.integrate(final_time = self.model.model_time + step)
            self.add_status("model",_("Integration was successful!"),
                important=True)
        except Exception as e:
            self.add_status("model",_("Integration FAILED!"),important=True)
            self.error(main=_("Integration failed!"),
                secondary="<i>{}</i>".format(e))
        integration_end_time = utils.utcnow()
        self.apply_model_data_to_settings()
        plot_start_time = utils.utcnow()
        self.update_current_plot()
        plot_end_time = utils.utcnow()
        end_time = utils.utcnow()
        self.add_status("model",_("Performance: integration ({:.3f} s), "
        " plotting ({:.3f} s), total ({:.3f} s)"
            ).format(integration_end_time-integration_start_time,
                plot_end_time-plot_start_time,end_time-start_time),
                important=True)


    def add_status(self, context, text, important = False):
        """
        Add a status to the statusbar

        Args:
            context (str): the context in which to display the text
            text (str): the text to display
            important (bool, optional): Make sure the text is **really**
                displayed by calling :any:`wait_for_gui`. Defaults to ``False``.
                Enabling this can slow down the gui.
        """
        context_id = self["statusbar"].get_context_id(context)
        self["statusbar"].push(context_id,text)
        if important:
            self.wait_for_gui()

    ###############
    ### Dialogs ###
    ###############
    def show_about_dialog(self):
        """
        Show the about dialog
        """
        dialog = self["aboutdialog"]
        logopixbuf = self.logo_pixbuf.scale_simple(
            200,200,GdkPixbuf.InterpType.BILINEAR)
        dialog.set_logo(logopixbuf)
        dialog.set_version(__version__)
        dialog.run()
        dialog.hide()

    def save_current_plot_dialog(self):
        """
        Display a dialog to select a plot saving destination

        Returns:
            :any:`str` or ``False``: the path to save to or ``False``
        """
        # create a dialog
        dialog = Gtk.FileChooserDialog(
            _("Please select a saving destination"), # title
            self["main_applicationwindow"], # parent
            Gtk.FileChooserAction.SAVE, # Action
            # Buttons (obviously not possible with glade!?)
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_SAVE, Gtk.ResponseType.OK)
            )

        # add the filter
        filters = {
            _("PDF files"):["application/pdf"],
            _("PNG files"):["image/png"]
            }
        plotmimetypes = []
        for name,mimetypes in filters.items():
            plotmimetypes.extend(mimetypes)
        allfilters = [(_("Plot files"),plotmimetypes)]
        allfilters.extend(sorted(filters.items()))
        for name,mimetypes in allfilters:
            filefilter = Gtk.FileFilter()
            filefilter.set_name(name)
            for mimetype in mimetypes:
                filefilter.add_mime_type(mimetype)
            dialog.add_filter(filefilter)

        response = dialog.run() # run the dialog
        if response == Gtk.ResponseType.OK: # file selected
            filename = dialog.get_filename()
            logger.debug("File '{}' selected".format(filename))
        elif response == Gtk.ResponseType.CANCEL: # cancelled
            filename = False
            logger.debug("File selection cancelled")
        else: # something else
            filename = False
            logger.debug("File selection dialog was closed")

        dialog.destroy() # destroy the dialog, we don't need it anymore
        return filename

    def run(self):
        """
        Run the gui
        """
        # set up the gui
        self.setup_gui()
        # run the gui
        logger.debug("starting mainloop")
        Gtk.main()
        logger.debug("mainloop is over")

    def quit(self, *args):
        """
        Stop the gui
        """
        logger.debug("received quitting signal")
        logger.debug("stopping mainloop...")
        Gtk.main_quit()
        logger.debug("mainloop stopped")


    #######################
    ### Special methods ###
    #######################
    def __getitem__(self, key):
        """
        When indexed, return the corresponding Glade gui element

        Args:
            key (str): the Glade gui element name
        """
        return self.builder.get_object( key )



def num_decimals(x):
    """
    Deterine the number of digits after the decimal point

    Args:
        x (float): the number of interest

    Returns:
        int : the number of digits after the decimal point or 0 there are none
    """
    string = str(x)
    match = re.match(string=string,pattern=r"^\de([+-]\d+)$")
    if match:
        decimals = -int(match.groups()[0])
    else:
        nonulls = re.sub(string=string,pattern=r"0+$",repl="")
        decimals = nonulls[::-1].find(".")
    return max(decimals,0)

def pos_significant_decimal(x):
    """
    Deterine the position of the most significant digit after the decimal point

    Args:
        x (float): the number of interest

    Returns:
        int : the position of the most significant digit after the decimal
            point or 0 there are none
    """
    string = "{:.30f}".format(x)
    match = re.match(string=string,pattern=r"^.*?\.(0*)[1-9]\d*$")
    if match is None:
        return 0
    else:
        return len(match.groups()[0]) + 1

def linear_regression(x,y,fit_intercept=True):
    """
    Fit :math:`y = a * x + b`

    Args:
        x (numpy.ndarray): the x values. Will be flattened.
        y (numpy.ndarray): the y values. Will be flattened.
        fit_intercept (bool, optional): Fit an intercept? Defaults to ``False``.

    Returns:
        float, float : :math:`a` and :math:`b`. If ``fit_intercept=False``,
            :math:`b` is ``None``.
    """
    A = x.reshape((x.size,1))
    if fit_intercept:
        A = np.hstack([A,np.ones_like(A)])
        a, b = np.linalg.lstsq(A, y)[0]
    else:
        a, b = np.linalg.lstsq(A, y)[0], 0
    return float(a),float(b)

def string2color(string):
    """
    Convert a string to a hex HTML color string

    Args:
        string (str): the string to use

    Returns:
        string : an HTML color string (e.g. #34df12)
    """
    return "#" + hashlib.md5(string.encode("utf-8")).hexdigest()[:6]
