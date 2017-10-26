#!/usr/bin/env python
"""
An example of using the ``pypfilt`` package to predict the future sequence of
vowels and consonants, based on observing a sequence of characters.
"""

from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals

import argparse
import datetime
import h5py
import logging
import numpy as np
import os.path
import sys

from pypfilt import default_params, forecast
from pypfilt.model import Base
from pypfilt.summary import HDF5, ModelCIs, Obs
from pypfilt.text import to_unicode


# Chains to the West: Markov's Theory of Connected Events and Its Transmission
# to Western Europe
# doi:10.1017/S0269889706001062

# First links in the Markov Chain
# http://www.americanscientist.org/issues/pub/first-links-in-the-markov-chain/
# http://www.americanscientist.org/libraries/documents/201321152149545-2013-03Hayes.pdf


class VowelOrConsonant(Base):
    """
    A Markov chain model that admits two states: vowel (0) and consonant (1).
    """

    def __init__(self, p_c0):
        self.p_c0 = p_c0

    def state_size(self):
        return 3

    def priors(self, params):
        pv = 5 / 26  # The probability of a vowel following a consonant.
        pc = 21 / 26  # The probability of a consonant following a vowel.
        return {
            'alpha': lambda r, size=None: r.triangular(0, pv, 1, size=size),
            'beta': lambda r, size=None: r.triangular(0, pc, 1, size=size),
        }

    def init(self, params, vec):
        """Initialise any number of state vectors."""
        rnd = params['resample']['rnd']
        rnd_size = vec[..., 0].shape
        vec[..., 0] = rnd.binomial(n=1, p=self.p_c0, size=rnd_size)
        # Select alpha and beta according to the priors.
        vec[..., 1] = params['prior']['alpha'](rnd, size=rnd_size)
        vec[..., 2] = params['prior']['beta'](rnd, size=rnd_size)

    def update(self, params, t, dt, is_fs, prev, curr):
        """Perform a single time-step."""
        x, alpha, beta = prev[..., 0], prev[..., 1], prev[..., 2]
        curr[..., 1] = alpha
        curr[..., 2] = beta
        # x(t) = pr(consonant)
        #      = (1 - alpha) * x(t - 1) + beta * (1 - x(t - 1))
        curr[..., 0] = (1 - alpha) * x + beta * (1 - x)
        # TODO --- we can use rnd.uniform() and check rval <= prob
        #      --- this should be faster than using the binomial!
        # mask_v = x == 1
        # mask_c = x == 0
        # rnd = params['resample']['rnd']
        # rvals = rnd.uniform(size=x.shape)
        # v_to_c = np.logical_and(mask_v, rvals <= beta)
        # c_to_c = np.logical_and(mask_c, rvals <= (1 - alpha))
        # to_c = np.logical_or(v_to_c, c_to_c)
        # curr[..., 0] = 0
        # curr[..., 0][to_c] = 1

    def state_info(self):
        """Describe each state variable."""
        return [('x', 0)]

    def param_info(self):
        """Describe each model parameter."""
        return [('alpha', 1, True), ('beta', 2, True)]

    def param_bounds(self):
        """Return the lower and upper parameter bounds."""
        return [0, 0], [1, 1]

    def stat_info(self):
        """Describe each statistic that can be calculated by this model."""
        return []


def char_to_var(ch):
    if ch in ['a', 'e', 'i', 'o', 'u']:
        return 0
    else:
        return 1


def generate_obs(start):
    text = ("He was too young to have been blighted"
            "by the cold world's corrupt finnesse;"
            "his soul still blossomed out, and lighted"
            "at a friend's word, a girl's caress."
            "In heart's affairs, a sweet beginner,"
            "he fed on hope's deceptive dinner;"
            "the world's eclat, its thunder-roll,"
            "still captivated his young soul."
            "He sweetened up with fancy's icing"
            "the uncertainties within his heart;"
            "for him, the objective on life's chart"
            "was still mysterious and enticing -"
            "something to rack his brains about,"
            "suspecting wonders would come out.")

    chars = [char_to_var(ch) for ch in text if ch.isalnum]
    obs_list = []
    for ix, ch_val in enumerate(chars):
        obs_list.append({
            'date': start + datetime.timedelta(days=ix + 1),
            'value': np.float64(ch_val),
            'period': 1,
            'source': 'generate_obs()',
            'unit': 'is consonant',
        })
    return obs_list


def log_llhd(params, obs_list, curr, prev_dict):
    """Calculate the log-likelihood of the current observation(s)."""
    log_llhd = np.zeros(curr.shape[:-1])
    # The expected observation is x(t).
    exp = curr[..., 0]
    # TODO: make the likelihood depend on the previous state?
    for o in obs_list:
        val = o['value']
        # log_llhd[val != exp] -= 3
        if val == 0.0:
            log_llhd += np.log(1 - exp)
        elif val == 1.0:
            log_llhd += np.log(exp)
        else:
            raise ValueError("Invalid value {}".format(val))
    return log_llhd + 0.1


def main(args=None):
    logging.basicConfig(level=logging.INFO)

    p_consonant = 21 / 26
    model = VowelOrConsonant(p_consonant)
    params = default_params(model, px_count=1000)
    params['log_llhd_fn'] = log_llhd
    # Set a fixed PRNG seed.
    params['resample']['prng_seed'] = 42
    # Use the post-regularised particle filter.
    params['resample']['regularisation'] = True
    # Treat days as the unit of time.
    params['steps_per_day'] = 1
    params['out_dir'] = '.'
    params['tmp_dir'] = '.'

    start = datetime.datetime(1900, 1, 1)
    obs_list = generate_obs(start)
    fs_dates = [o['date'] for o in obs_list]
    until = max(fs_dates) + datetime.timedelta(days=1)

    # Define the summary tables to be saved to disk.
    summary = HDF5(params, obs_list, first_day=True)
    summary.add_tables(ModelCIs(probs=[0, 50, 95]), Obs())

    # Run the model estimation and forecasting simulations.
    out_file = 'output.hdf5'
    forecast(params, start, until, [obs_list], fs_dates, summary, out_file)
    return 0


if __name__ == "__main__":
    sys.exit(main())


def load_cis(in_file):
    with h5py.File(in_file) as f:
        cis = f['/data/model_cints'][()]
    return cis


def load_obs(in_file):
    with h5py.File(in_file) as f:
        obs = f['/data/obs'][()]
    return obs


def dt_col(np_col):
    return np.array(
        [datetime.datetime.strptime(to_unicode(d), '%Y-%m-%d %H:%M:%S')
         for d in np_col])


def colorbrewer_set2():
    return [
        '#8dd3c7', '#ffffb3', '#bebada', '#fb8072', '#80b1d3', '#fdb462',
        '#b3de69', '#fccde5', '#d9d9d9', '#bc80bd', '#ccebc5', '#ffed6f',
    ]


def fig_x_vs_obs(df, ci_lvls, obs, t0, ax):
    colours = colorbrewer_set2()
    ts_objs = []

    for ci in ci_lvls:
        df_x = df[df['prob'] == ci]
        dates = dt_col(df_x['date'])
        days = [(d - t0).days for d in dates]
        y_min = df_x['ymin']
        y_max = df_x['ymax']
        if ci > 0:
            ts = ax.fill_between(days, y_min, y_max, edgecolor='None',
                                 facecolor=colours.pop(0))
            ts.set_label("{}% CI".format(ci))
        else:
            ts = ax.plot(days, y_min, linestyle='-', color=colours.pop(0),
                         linewidth=1.5)[0]
            ts.set_label("Median")
        ts_objs.append(ts)

    obs_date = dt_col(obs['date'])
    obs_value = obs['value']
    obs_days = [(d - t0).days for d in obs_date]

    ts = ax.plot(obs_days, obs_value, 'ko')[0]
    ts.set_label('Observations')
    ts_objs.append(ts)

    ax.set_xlim(left=-0.25, right=max(obs_days) + 0.25)
    ax.set_ylim(bottom=0)

    return ts_objs


def fig_fs_vs_obs(df, ci_lvls, obs, t0):
    import matplotlib.pyplot as plt

    df_fs_date = dt_col(df['fs_date'])
    fs_dates = sorted(np.unique(df_fs_date))

    n_cols = 5
    n_rows = 2
    fig, subplots = plt.subplots(n_rows, n_cols, sharex=True, sharey=True)
    ix = 0
    ts = {}
    for cix, col in enumerate(subplots):
        for rix, ax in enumerate(col):
            fs_date = fs_dates[ix]
            ix += 1
            df_x = df[df_fs_date == fs_date]
            ts[ix] = fig_x_vs_obs(df_x, ci_lvls, obs, t0, ax)
            if ix == len(fs_dates):
                ax.set_title("Complete Estimation")
            else:
                ax.set_title("t = {}".format((fs_date - t0).days))

            if ix == 1:
                ax.legend(ts[ix], [t.get_label() for t in ts[ix]],
                          loc='best', frameon=False)

    return fig, subplots, ts


def fig_posterior(df, ci_lvls, t0, ax, obs=None):
    colours = colorbrewer_set2()
    ts_objs = []

    for ci in ci_lvls:
        df_x = df[df['prob'] == ci]
        dates = dt_col(df_x['date'])
        days = [(d - t0).days for d in dates]
        y_min = df_x['ymin']
        y_max = df_x['ymax']
        if ci > 0:
            ts = ax.fill_between(days, y_min, y_max, edgecolor='None',
                                 facecolor=colours.pop(0))
            ts.set_label("{}% CI".format(ci))
        else:
            ts = ax.plot(days, y_min, linestyle='-', color=colours.pop(0),
                         linewidth=1.5)[0]
            ts.set_label("Median")
        ts_objs.append(ts)

    if obs is not None:
        obs_date = dt_col(obs['date'])
        obs_value = obs['value']
        obs_days = [(d - t0).days for d in obs_date]

        ts = ax.plot(obs_days, obs_value, 'ko')[0]
        ts.set_label('Observations')
        ts_objs.append(ts)

    ax.set_xlim(left=-0.25, right=max(days) + 0.25)
    ax.set_ylim(bottom=0)

    return ts_objs


def fig_posteriors(df, ci_lvls, t0, obs):
    import matplotlib.pyplot as plt

    names = sorted(np.unique(df['name']))

    n_cols = 1
    n_rows = len(names)
    fig, subplots = plt.subplots(n_rows, n_cols, sharex=True, sharey=False)
    ts = {}
    for ix, ax in enumerate(subplots):
        name = names[ix]
        df_n = df[df['name'] == name]
        df_fs_dates = dt_col(df_n['fs_date'])
        df_n = df_n[df_fs_dates == max(df_fs_dates)]
        if to_unicode(name) == 'x':
            ts[ix] = fig_posterior(df_n, ci_lvls, t0, ax, obs)
        else:
            ts[ix] = fig_posterior(df_n, ci_lvls, t0, ax)
        ax.set_title(to_unicode(name))

        if ix == len(subplots) // 2:
            ax.legend(ts[ix], [t.get_label() for t in ts[ix]],
                      loc='best', frameon=False)
            ax.set_ylabel('Value')

        if ix == len(subplots) - 1:
            ax.set_xlabel('Time')

    return fig, subplots, ts


def plots_to_png(in_file, out_file):
    cis = load_cis(in_file)
    obs = load_obs(in_file)

    ci_lvls = sorted(np.unique(cis['prob']), reverse=True)
    ci_name = np.array([to_unicode(n) for n in cis['name']])
    ci_x = cis[ci_name == 'x']
    ci_fs_date = dt_col(ci_x['fs_date'])
    df_est = ci_x[ci_fs_date == max(ci_fs_date)]

    obs_date = dt_col(obs['date'])
    t0 = obs_date[0] - datetime.timedelta(days=1)

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    fig, subplots, ts = fig_fs_vs_obs(ci_x, ci_lvls, obs, t0)
    fig.set_figwidth(20)
    fig.set_figheight(12)
    fig.savefig('forecasts.png', dpi=300, format='png', transparent=True,
                bbox_inches='tight')

    fig, ax = plt.subplots(1)
    ts_objs = fig_x_vs_obs(df_est, ci_lvls, obs, t0, ax)
    ax.set_xlabel('Time')
    ax.set_ylabel('Position')
    ax.legend(ts_objs, [t.get_label() for t in ts_objs],
              loc='upper left', frameon=False)
    fig.set_figwidth(8)
    fig.set_figheight(6)
    fig.savefig('estimation.png', dpi=300, format='png', transparent=True,
                bbox_inches='tight')

    fig, subplots, ts = fig_posteriors(cis, ci_lvls, t0, obs)
    fig.set_figwidth(8)
    fig.set_figheight(6)
    fig.savefig('posteriors.png', dpi=300, format='png', transparent=True,
                bbox_inches='tight')


def get_parser():
    """Return the command-line argument parser for this script."""
    p = argparse.ArgumentParser()
    p.add_argument('data_file', help='The simulation output file')
    p.add_argument('plot_file', default=None, nargs='?',
                   help='The simulation output file')

    return p


def main(args=None):
    parser = get_parser()
    if args is None:
        args = vars(parser.parse_args())
    else:
        args = vars(parser.parse_args(args))

    in_file = args['data_file']
    out_file = args['plot_file']
    if out_file is None:
        out_file = "{}-%d.png".format(os.path.splitext(in_file)[0])

    plots_to_png(in_file, out_file)
    return 0


if __name__ == "__main__":
    sys.exit(main())
