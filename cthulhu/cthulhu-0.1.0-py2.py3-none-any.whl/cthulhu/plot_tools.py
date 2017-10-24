# Python 2 and 3 compatibility
from __future__ import print_function, division
from builtins import range

import os
import sys

import numpy as np
from scipy.fftpack import fftshift
from astropy.time import Time

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt

plt.rc("font", family="serif")
CMAP = plt.cm.hsv
COLOURS = CMAP(np.linspace(0, 1, 360))
FONTSIZE = mpl.rcParams["font.size"] + 2


def setup_subplot(axis, title=None, xlabel=None, ylabel=None, grid=True):
    if title is not None:
        axis.set_title(title, fontsize=FONTSIZE)
    if xlabel is not None:
        axis.set_xlabel(xlabel, fontsize=FONTSIZE)
    else:
        axis.set_xlabel("RA [deg]", fontsize=FONTSIZE)
    if ylabel is not None:
        axis.set_ylabel(ylabel, fontsize=FONTSIZE)
    else:
        axis.set_ylabel("Dec [deg]", fontsize=FONTSIZE)
    if grid:
        axis.grid(grid)
    axis.set_aspect("equal")
    axis.set_facecolor("#3f3f3f")


def plot_vector_arrows(axis, ra=None, dec=None, ra_shifts=None, dec_shifts=None, obsid=None, norm=False, scale=None):
    # If the source positions and shifts are all "None", then assume we're unpacking the obsid object.
    if ra is None and dec is None and ra_shifts is None and dec_shifts is None:
        ra = obsid.ra
        dec = obsid.dec
        ra_shifts = obsid.ra_shifts
        dec_shifts = obsid.dec_shifts

    # If specified, we can normalise the size of the arrows.
    if norm:
        mag = np.sqrt(ra_shifts**2 + dec_shifts**2)
        mmag = mag.max()
    elif scale is not None:
        mmag = 1/scale
    else:
        mmag = 1
    # Unfortunately, matplotlib's arrow function does not work with vectors.
    # For every source...
    for i in np.arange(len(ra)):
        # ... determine the angle of the vector to use as a colour ...
        angle = np.arctan2(dec_shifts[i], ra_shifts[i])
        colour = COLOURS[np.rint(np.rad2deg(angle)).astype(int)]
        # ... and plot the arrow.
        axis.arrow(ra[i], dec[i],
                   ra_shifts[i]/mmag+1e-6, dec_shifts[i]/mmag+1e-6,
                   width=np.sqrt(ra_shifts[i]**2 + ra_shifts[i]**2)/(30*mmag),
                   head_width=np.sqrt(ra_shifts[i]**2 + dec_shifts[i]**2)/(3*mmag),
                   color=colour, length_includes_head=True)
    axis.set_xlim(ra.max(), ra.min())
    axis.set_ylim(dec.min(), dec.max())


def plot_source_dots(obsid, axis, size=1, colour="mag", colourbar=True, cmap="Greys"):
    if colour == "mag":
        mag = np.sqrt(obsid.ra_shifts**2 + obsid.dec_shifts**2)
        mag /= mag.max()
        image = axis.scatter(obsid.ra, obsid.dec, c=mag,
                             s=size, edgecolors="face", cmap=cmap)
    elif colour == "phase":
        angles = np.arctan2(obsid.dec_shifts, obsid.ra_shifts)
        colours = COLOURS[np.rint(np.rad2deg(angles)).astype(int)]
        image = axis.scatter(obsid.ra, obsid.dec, c=colours,
                             s=size, edgecolors="face", cmap=CMAP)
    else:
        raise ValueError("Must be either 'mag' or 'phase'.")
    if colourbar:
        cb = plt.colorbar(image, ax=axis, format="%.1f")
        cb.set_label("Fraction of maximum shift")


def plot_tec(axis, obsid, cmap="plasma", vlim=None, colourbar=True):
    if vlim is None:
        tec = axis.imshow(obsid.tec, extent=obsid.tec_extent,
                          cmap=cmap, origin="lower")
    else:
        tec = axis.imshow(obsid.tec, extent=obsid.tec_extent,
                          cmap=cmap, origin="lower",
                          vmin=vlim[0], vmax=vlim[1])
    label = "TEC [TECU]"
    if colourbar:
        cb = plt.colorbar(tec, ax=axis, format="%.2f")
        cb.set_label(label, fontsize=FONTSIZE+2, labelpad=30)

    axis.tick_params(axis="both", labelsize=FONTSIZE)
    axis.set_xlim(*obsid.tec_extent[0:2])
    axis.set_ylim(*obsid.tec_extent[2:4])
    return tec


def plot_power_spectrum(axis, obsid,
                        title="Power spectrum",
                        xlabel="$k_{RA}$ [deg$^{-1}$]",
                        ylabel="$k_{Dec}$ [deg$^{-1}$]",
                        freq_extent=None,
                        grid=True, colourbar=True, pca_arrows=False,
                        cmap="viridis"):
    setup_subplot(axis, title=title, xlabel=xlabel, ylabel=ylabel, grid=True)
    ps = obsid.ps

    if freq_extent is None:
        x_freq_extent = ps.shape[0]/(obsid.tec_extent[0]-obsid.tec_extent[1])/2
        y_freq_extent = ps.shape[1]/(obsid.tec_extent[2]-obsid.tec_extent[3])/2
        freq_extent = (-x_freq_extent, x_freq_extent, y_freq_extent, -y_freq_extent)

    fitted_ps_image = axis.imshow(np.arcsinh(fftshift(ps)), cmap=cmap,
                                  extent=freq_extent, origin="lower")
    if colourbar:
        cb = plt.colorbar(fitted_ps_image, ax=axis, format="%.1f")
        cb.set_label("arcsinh(Power)")

    if pca_arrows:
        try:
            obsid.pca_variance
        except AttributeError:
            obsid.pca()

        axis.arrow(0, 0,
                   obsid.pca_variance[0]*np.cos(obsid.pca_angle),
                   obsid.pca_variance[0]*np.sin(obsid.pca_angle),
                   color='r', width=0.02, head_width=0.1)
        axis.arrow(0, 0,
                   obsid.pca_variance[1]*np.cos(obsid.pca_angle-np.pi/2),
                   obsid.pca_variance[1]*np.sin(obsid.pca_angle-np.pi/2),
                   color='r', width=0.02, head_width=0.1)


# def plot_spatial_correlation(obsid, axis):
#     # import pysal as ps
#     # s = len(obsid.tec)
#     # n = s**2
#     # w = ps.lat2W(s, s, rook=False)
#     # # w.transform = 'R'
#     # e = np.random.random((n, 1))
#     # u = scipy.linalg.inv(np.eye(n) - 0.95 * w.full()[0])
#     # u = np.dot(u, e)
#     # ul = ps.lag_spatial(w, u)
#     # u = (u - u.mean()) / np.std(u)
#     # ul = (ul - ul.mean()) / np.std(ul)
#     # gu = u.reshape((s, s))

#     # # axis.matshow(gu, cmap=plt.cm.YlGn)
#     # axis.scatter(u, ul, linewidth=0)

#     # s = len(obsid.tec)
#     # w = ps.lat2W(s, s)
#     # y = obsid.tec.flatten()
#     # obsid.g = ps.Gamma(y, w).p_sim_g

#     corr = scipy.signal.correlate(obsid.tec, obsid.tec, mode="same")
#     axis.imshow(corr)


def generate_diagnostic_figure(obsid, verbosity=0, overwrite=False, filename=None,
                               directory=None, vlim=None):
    if not directory:
        directory = "plots"
    if not filename:
        filename = "%s/%s.png" % (directory, obsid.obsid)
    else:
        filename = "%s/%s" % (directory, filename)

    if not os.path.exists(directory):
        os.mkdir(directory)
    if not overwrite and os.path.exists(filename):
        if verbosity > 0:
            sys.stderr.write("Not overwriting and %s exists; no plot saved.\n" % filename)
        return

    fig, ax = plt.subplots(2, 2, figsize=(12, 9))
    plt.subplots_adjust(hspace=0.25, left=0.05, right=0.95, top=0.95, bottom=0.07)

    # The value in obsid.obsid may not actually be a 10-digit obsid. So, try to convert it to an int.
    try:
        obsid.obsid = int(obsid.obsid)
        title = "Obsid: %s (%s)\nMetric: %s" % (obsid.obsid, Time(obsid.obsid, format="gps").iso, "%.4f" % obsid.metric)
    except ValueError:
        title = "File: %s\nMetric: %s" % (obsid.obsid, obsid.metric)

    setup_subplot(ax[0, 0])
    ax[0, 0].set_title(title, fontsize=FONTSIZE)
    ax[0, 0].set_xlim([obsid.ra_centre+obsid.radius, obsid.ra_centre-obsid.radius])
    ax[0, 0].set_ylim([obsid.dec_centre-obsid.radius, obsid.dec_centre+obsid.radius])
    # plot_vector_arrows(ax[0, 0], obsid.fra, obsid.fdec, obsid.fra_shifts, obsid.fdec_shifts)
    plot_vector_arrows(ax[0, 0], obsid.fra, obsid.fdec, obsid.fra_shifts*60, obsid.fdec_shifts*60)

    setup_subplot(ax[0, 1], title="Power spectrum", xlabel="$k_{RA}$ [deg$^{-1}$]", ylabel="$k_{Dec}$ [deg$^{-1}$]")
    plot_power_spectrum(ax[0, 1], obsid)

    setup_subplot(ax[1, 0], title="Reconstructed TEC field")
    plot_vector_arrows(ax[1, 0], obsid.ra, obsid.dec, obsid.ra_shifts, obsid.dec_shifts, norm=False)
    if vlim is not None:
        plot_tec(ax[1, 0], obsid, vlim=vlim)
    else:
        plot_tec(ax[1, 0], obsid)

    fig.delaxes(ax[1, 1])

    def stat_plotter(value, desc, y_value, fontsize=12):
        plt.figtext(0.55, y_value, desc + ':', fontsize=FONTSIZE)
        if isinstance(value, float):
            plt.figtext(0.75, y_value, "%.4f" % value, fontsize=FONTSIZE)
        else:
            plt.figtext(0.75, y_value, value, fontsize=FONTSIZE)

    def weight_plotter(value, y_value, fontsize=12):
        if isinstance(value, float):
            plt.figtext(0.85, y_value, "%.4f" % value, fontsize=FONTSIZE)
        else:
            plt.figtext(0.85, y_value, value, fontsize=FONTSIZE)

    height = 0.45
    stat_plotter("$s_i$", "Statistic and weight", height, fontsize=FONTSIZE+2)
    weight_plotter("$w_i$", height, fontsize=FONTSIZE+2)
    height -= 0.03
    for i in range(len(obsid.metrics)):
        stat_plotter(obsid.metrics[i][0], obsid.metrics[i][1], height)
        weight_plotter(obsid.metric_weights[i], height)
        height -= 0.03

    stat_plotter(obsid.metric, "Metric", 0.15, fontsize=14)
    stat_plotter("$\sum_{i=1}^%s \/ w_i s_i$" % len(obsid.metrics), "Metric calculation",
                 0.08, fontsize=14)

    plt.savefig(filename, dpi=200)
    if verbosity > 0:
        print("Saved: "+filename)
    plt.close()


def raw_and_tec(obsid, verbosity=0, overwrite=False, filename=None, directory=None, title=None,
                norm_vectors=False, vlim=None):
    if not directory:
        directory = "raw_and_tec"
    if not filename:
        filename = "%s/%s.png" % (directory, obsid.obsid)
    else:
        filename = "%s/%s" % (directory, filename)

    if not os.path.exists(directory):
        os.mkdir(directory)
    if not overwrite and os.path.exists(filename):
        if verbosity > 0:
            sys.stderr.write("Not overwriting and %s exists; no plot saved.\n" % filename)
        return

    if not title:
        title = "Obsid: %s\nMetric: %.4f" % (obsid.obsid, obsid.metric)

    _, ax = plt.subplots(1, 2, figsize=(12, 4.5))
    plt.subplots_adjust(hspace=0.25, left=0.05, right=0.95, top=0.95, bottom=0.07)

    setup_subplot(ax[0], title)
    plot_vector_arrows(ax[0], obsid=obsid, norm=norm_vectors)
    if vlim is not None:
        plot_tec(ax[0], obsid, vlim=vlim)
    else:
        plot_tec(ax[0], obsid)

    plot_power_spectrum(ax[1], obsid)
    # try:
    #     ax[1].plot(np.arange(len(obsid.one_d_ps))*obsid.freq_res, obsid.one_d_ps)
    #     ax[1].plot(np.arange(len(obsid.one_d_ps))*obsid.freq_res, np.array(obsid.one_d_ps)/10, c='r', ls="--")
    #     ax[1].set_ylim(0, 50000)
    #     ax[1].set_ylabel("Power")
    #     ax[1].set_xlabel("deg$^{-1}$")
    # except AttributeError:
    #     pass

    plt.tight_layout()
    plt.savefig(filename, dpi=200)
    if verbosity > 0:
        print("Saved: "+filename)
    plt.close()


def tec_only(obsid, verbosity=0, overwrite=False, filename=None, directory=None, text=None,
             vectors=False, norm_vectors=False, axes=True, vlim=None):
    if not directory:
        directory = "tec_only"
    if not filename:
        filename = "%s/%s.png" % (directory, obsid.obsid)
    else:
        filename = "%s/%s" % (directory, filename)

    if not os.path.exists(directory):
        os.mkdir(directory)
    if not overwrite and os.path.exists(filename):
        if verbosity > 0:
            sys.stderr.write("Not overwriting and %s exists; no plot saved.\n" % filename)
        return

    _, ax = plt.subplots()

    ax.xaxis.set_ticks_position("both")
    ax.yaxis.set_ticks_position("both")

    if vectors:
        plot_vector_arrows(ax, obsid=obsid, norm=norm_vectors)

    if vlim is not None:
        plot_tec(ax, obsid, colourbar=False, vlim=vlim)
    else:
        plot_tec(ax, obsid, colourbar=False)

    if not axes:
        ax.xaxis.set_ticklabels([])
        ax.yaxis.set_ticklabels([])

    if text is not None:
        plt.figtext(0.07, 0.9, text)

    plt.tight_layout()
    plt.savefig(filename, dpi=200)
    if verbosity > 0:
        print("Saved: "+filename)
    plt.close()
