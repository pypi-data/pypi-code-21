"""Utilities for effective Area computation.

All energies in GeV.
"""
from __future__ import division, absolute_import, print_function

import numpy as np


def integrated_zenith(zen_min=0, zen_max=np.pi):
    """Integrate zenith."""
    # integrate zenith, but while in cosine
    return 2 * np.pi * np.abs(np.cos(zen_max) - np.cos(zen_min))


def event_ratio(fluxweight_pre, fluxweight_post):
    n_events_pre = np.sum(fluxweight_pre)
    n_events_post = np.sum(fluxweight_post)
    return n_events_post / n_events_pre


def event_ratio_1d(fluxweight_pre, fluxweight_post, binstat_pre,
                   binstat_post, bins):
    hist_pre, _ = np.histogram(binstat_pre, bins=bins,
                               weights=fluxweight_pre)
    hist_post, _ = np.histogram(binstat_post, bins=bins,
                                weights=fluxweight_post)
    return hist_post / hist_pre


def event_ratio_2d(fluxweight_pre, fluxweight_post, binstat_x_pre,
                   binstat_x_post, binstat_y_pre, binstat_y_post, xbins,
                   ybins):
    hist_pre, _, _ = np.histogram2d(binstat_x_pre, binstat_y_pre,
                                    bins=(xbins, ybins),
                                    weights=fluxweight_pre)
    hist_post, _, _ = np.histogram2d(binstat_x_post, binstat_y_post,
                                     bins=(xbins, ybins),
                                     weights=fluxweight_post)
    return hist_post / hist_pre


def effective_area(flux, w2_over_ngen, energy, solid_angle=4 * np.pi,
                   year_to_second=True, **integargs):
    """Effective Area.

    Compare the raw incoming flux (sans detector effects) to the
    events detected (including detector effects + cuts).

    This one assumes an isotropic flux.

    Raw flux: integral over e.g. the bare Honda flux.

    detected: corrected_w2 * flux (after cuts ifneedbe)

    Parameters
    ==========
    flux: km3flux.flux.BaseFlux (or subclass) instance
    w2_over_ngen:
        weight_w2, already corrected for total events generated.
        For gseagen, this is just `w2/ngen`, but
        for genhen, this is `w2 / (ngen * nfil)`.
    energy: array-like
    solid_angle: float [in rad], default=4pi
    year_to_second: bool, default=True
        divide by n_seconds_in_year
    """
    energy = np.atleast_1d(energy)
    w2_over_ngen = np.atleast_1d(w2_over_ngen)
    flux_samples = flux(energy)
    flux_integ = flux.integrate(**integargs)
    out = np.sum(w2_over_ngen * flux_samples) / (solid_angle * flux_integ)
    if year_to_second:
        out /= 365.25 * 24 * 60 * 60
    return out
