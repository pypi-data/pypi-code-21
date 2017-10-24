#!python

# Python 2 and 3 compatibility
from __future__ import print_function

import os
import sys
import argparse
import multiprocessing as mp
import yaml
from yaml import CSafeLoader as Loader

import numpy as np

from cthulhu.reconstruct import Obsid
from cthulhu.unpack import unpack_data
from cthulhu.rts_log_tools import lm2radec
from cthulhu.plot_tools import generate_diagnostic_figure, raw_and_tec
from pyGrad2Surf.g2s import g2s, g2s_spectral, g2s_dirichlet, g2s_weighted


LOCK = mp.Lock()


def unpack_model_plot(data_file):
    if args.verbosity > 2:
        print("Attempting to unpack: %s" % data_file)

    unpacked = unpack_data(data_file, verbosity=args.verbosity)
    # Check if there's any data in the file; otherwise, print to stderr.
    if len(unpacked["sources"]) == 0:
        print("%s: No data contained." % data_file, file=sys.stderr)
        return

    if args.field:
        mean_ra = np.mean([unpacked["sources"][s]["ra"] for s in unpacked["sources"]])
        mean_dec = np.mean([unpacked["sources"][s]["dec"] for s in unpacked["sources"]])

        if args.field.lower() == "eor0":
            if abs(mean_ra + 0) > args.field_tol or abs(mean_dec + 27) > args.field_tol:
                print("%s: Not EoR0, skipping." % data_file, file=sys.stderr)
                return
        if args.field.lower() == "eor1":
            if abs(mean_ra - 60) > args.field_tol or abs(mean_dec + 27) > args.field_tol:
                print("%s: Not EoR1, skipping." % data_file, file=sys.stderr)
                return

    # # If we've specified the number of sources to include, check we're not doing too few.
    # if len(unpacked["sources"]) < args.number_of_sources:
        # If so, we need to re-assign the values used in reconstruction.

    if os.path.exists("bias.yaml"):
        with open("bias.yaml", 'r') as f:
            biases = yaml.load(f, Loader=Loader)
    else:
        biases = {}

    if args.directional_cosines:
        x_pos = "l"
        y_pos = "m"
        x_shift = "l_shifts"
        y_shift = "m_shifts"
    else:
        x_pos = "ra"
        y_pos = "dec"
        x_shift = "ra_shifts"
        y_shift = "dec_shifts"

    # Average all data, excepting the amount to be flagged.
    if not args.high_res:
        x, y, x_shifts, y_shifts = [], [], [], []
        sources, flux_densities = [], []
        l_bias, m_bias = [], []
        for s in unpacked["sources"]:
            # if int(unpacked["sources"][s]["source_number"]) > args.number_of_sources:
            #     continue

            x.append(unpacked["sources"][s][x_pos])
            y.append(unpacked["sources"][s][y_pos])

            if args.flag_end == 0:
                x_shifts.append(np.nanmean(unpacked["sources"][s][x_shift][args.flag_front:]))
                y_shifts.append(np.nanmean(unpacked["sources"][s][y_shift][args.flag_front:]))
            else:
                x_shifts.append(np.nanmean(unpacked["sources"][s][x_shift][args.flag_front:-args.flag_end]))
                y_shifts.append(np.nanmean(unpacked["sources"][s][y_shift][args.flag_front:-args.flag_end]))
            sources.append(s)
            flux_densities.append(unpacked["sources"][s]["flux_density"])

            if biases is None or s not in biases:
                l_bias.append(0.)
                m_bias.append(0.)
            else:
                l_bias.append(biases[s][0])
                m_bias.append(biases[s][1])

        if args.directional_cosines:
            x_bias = np.array(l_bias)
            y_bias = np.array(m_bias)
        else:
            x_bias, y_bias = lm2radec(x, y, np.array(l_bias), np.array(m_bias),
                                      unpacked["metadata"])

        obs = Obsid((x, y,
                     np.array(x_shifts)-x_bias,
                     np.array(y_shifts)-y_bias),
                    obsid=unpacked["metadata"]["obsid"],
                    sources=sources,
                    flux_densities=flux_densities,
                    radius=args.radius)
        # print(obs.radius, args.radius)
        obs.pca()
        obs.obsid_metric()

        if args.plots:
            obs.reconstruct_tec(g2s_method=g2s_method)
            obs.save_tec_fits(comment="Average of %s %ss intervals" %
                              (unpacked["metadata"]["iterations"]-args.flag_front-args.flag_end,
                               unpacked["metadata"]["cadence"]),
                              verbosity=args.verbosity, overwrite=args.overwrite)
            generate_diagnostic_figure(obs, verbosity=args.verbosity, overwrite=args.overwrite)
            raw_and_tec(obs, verbosity=args.verbosity, overwrite=args.overwrite,
                        title="Obsid: %s (Average of %s %ss intervals)\nMetric: %.4f PCA eigenvalue: %.4f" %
                        (obs.obsid, unpacked["metadata"]["iterations"]-args.flag_front-args.flag_end,
                         unpacked["metadata"]["cadence"], obs.metric, obs.pca_variance[0]))

        string = str(obs.obsid)
        for x in obs.metrics:
            string += " %.4f" % x[0]

        with LOCK:
            print(string)

    # For each epoch (timestamp) in the data, bundle the ionospheric shifts and pass them
    # to cthulhu.
    else:
        for i, t in enumerate(unpacked["metadata"]["timestamps"]):
            if i < args.flag_front or i + args.flag_end > len(unpacked["metadata"]["timestamps"]) - 1:
                continue
            x, y, x_shifts, y_shifts = [], [], [], []
            sources, flux_densities = [], []
            l_bias, m_bias = [], []
            for s in unpacked["sources"]:
                # if int(unpacked["sources"][s]["source_number"]) > args.number_of_sources:
                #     continue

                try:
                    x_s = unpacked["sources"][s][x_shift][i]
                    y_s = unpacked["sources"][s][y_shift][i]
                    if np.isfinite(x_s):
                        x.append(unpacked["sources"][s][x_pos])
                        y.append(unpacked["sources"][s][y_pos])
                        x_shifts.append(x_s)
                        y_shifts.append(y_s)
                        sources.append(s)
                        flux_densities.append(unpacked["sources"][s]["flux_density"])

                        if biases is None or s not in biases:
                            l_bias.append(0.)
                            m_bias.append(0.)
                        else:
                            l_bias.append(biases[s][0])
                            m_bias.append(biases[s][1])

                except IndexError:
                    # Maybe something went wrong in writing this file?
                    return

            if len(x) < 500:
                print("%s: Too few sources, skipping." % t, file=sys.stderr)
                continue

            if args.directional_cosines:
                x_bias = np.array(l_bias)
                y_bias = np.array(m_bias)
            else:
                x_bias, y_bias = lm2radec(x, y, np.array(l_bias), np.array(m_bias),
                                          unpacked["metadata"])

            obs = Obsid((x, y,
                         np.array(x_shifts)-x_bias,
                         np.array(y_shifts)-y_bias),
                        obsid=t, sources=sources,
                        flux_densities=flux_densities,
                        radius=args.radius)
            # obs.obsid = unpacked["metadata"]["obsid"]
            obs.pca()
            obs.obsid_metric()

            if args.plots:
                obs.reconstruct_tec(g2s_method=g2s_method)
                generate_diagnostic_figure(obs, verbosity=args.verbosity, overwrite=args.overwrite,
                                           filename="%s.png" % t, directory="plots_8s")
                raw_and_tec(obs, verbosity=args.verbosity, overwrite=args.overwrite,
                            filename="%s.png" % t, directory="raw_and_tec_8s",
                            title="Obsid: %s + %ss (%ss cadence)\nMetric: %.4f PCA eigenvalue: %.4f" % (obs.obsid, t - obs.obsid,
                                                                                                        unpacked["metadata"]["cadence"],
                                                                                                        obs.metric, obs.pca_variance[0]))

            if args.fits:
                # If plotting is disabled, then we need to reconstruct the TEC.
                if not args.plots:
                    obs.reconstruct_tec(g2s_method=g2s_method)

                # To ensure that the dimensions of the an output fits file are exactly the same,
                # overwrite the tec_extent with something consistent.
                # This works by utilising a variable "tec_extent" within this for loop. If it does
                # not already exist, we create it from the tec_extent attribute already in use.
                try:
                    obs.tec_extent = tec_extent
                except NameError:
                    tec_extent = obs.tec_extent
                obs.save_tec_fits(comment="%ss interval snapshot" % unpacked["metadata"]["cadence"],
                                  filename="%s.fits" % t, directory="fits_files_8s",
                                  verbosity=args.verbosity, overwrite=args.overwrite)

            string = str(t)
            for x in obs.metrics:
                string += " %.4f" % x[0]

            with LOCK:
                print(string)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbosity", action="count", default=0,
                        help="Level of verbosity.")
    parser.add_argument("-o", "--overwrite", action="store_true",
                        help="Ignore the presence of an existing file.")
    parser.add_argument("-d", "--directional_cosines", action="store_true",
                        help="Use (l,m) coordinates for calculations.")
    # parser.add_argument("-n", "--number_of_sources", default=10000, type=int,
    #                     help="Include only sources numbered n or lower.")
    parser.add_argument("--high_res", action="store_true",
                        help="Use each epoch of the data, rather than an average of the data. Default: %(default)s")
    parser.add_argument("-f", "--flag_front", default=1, type=int,
                        help="Flag this many epochs at the front of each file. Default: %(default)s")
    parser.add_argument("-e", "--flag_end", default=1, type=int,
                        help="Flag this many epochs at the end of each file. Default: %(default)s")
    parser.add_argument("-r", "--radius", type=float,
                        help="Specify the radius to include sources.")
    parser.add_argument("-p", "--plots", action="store_true",
                        help="Produce plots from the data. Default: %(default)s")
    parser.add_argument("--fits", action="store_true",
                        help="Produce fits images of the reconstructed TEC. Default: %(default)s")
    parser.add_argument("--field", type=str,
                        help="Only accept data from the field specified. "
                        "Currently only works for 'EoR0' or 'EoR1'. By default, no data is rejected.")
    parser.add_argument("--field_tol", default=10, type=float,
                        help="Tolerance on the location of the specified field. Default: %(default)s")
    parser.add_argument("--g2s_method", default="g2s",
                        help="Method to use for TEC reconstruction. Default: %(default)s")
    parser.add_argument("files", nargs='*', help="Files to be processed. "
                        "See cthulhu.unpack_data for appropriate formats.")
    args = parser.parse_args()

    # Check that field arguments are sane.
    if args.field and args.field.lower() not in ["eor0", "eor1"]:
        print("Unknown field specified (%s)." % args.field, file=sys.stderr)
        exit(1)

    if args.g2s_method.lower() == "g2s":
        g2s_method = g2s
    elif args.g2s_method.lower() == "g2s_spectral":
        g2s_method = g2s_spectral
    elif args.g2s_method.lower() == "g2s_dirichlet":
        g2s_method = g2s_dirichlet
    elif args.g2s_method.lower() == "g2s_weighted":
        g2s_method = g2s_weighted
    else:
        print("Unknown g2s method specified (%s)." % args.g2s_method, file=sys.stderr)
        exit(1)

    if args.verbosity > 1 or len(args.files) == 1:
        for f in args.files:
            unpack_model_plot(f)
    else:
        mp.Pool().map(unpack_model_plot, args.files)
