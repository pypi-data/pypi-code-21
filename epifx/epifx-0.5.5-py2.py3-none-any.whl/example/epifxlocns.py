"""Local settings for epidemic forecasting."""

import epifx
import epifx.obs
import errno
import numpy as np
import os.path
import pypfilt


def get_params(locn_settings):
    px_count = 15000
    prng_seed = 3001
    popn = locn_settings['popn']
    model = epifx.SEIR()
    time = pypfilt.Datetime()

    params = epifx.default_params(px_count, model, time, popn, prng_seed)

    params['resample']['threshold'] = 0.25
    params['resample']['regularisation'] = True
    params['epifx']['stoch'] = False

    # Set the output and temporary directories.
    out_dir = locn_settings['out_dir']
    tmp_dir = locn_settings['tmp_dir']
    for reqd_dir in [out_dir, tmp_dir]:
        if not os.path.isdir(reqd_dir):
            # Create the directory (and missing parents) with mode -rwxr-x---.
            try:
                os.makedirs(reqd_dir, mode=0o750)
            except OSError as e:
                # Potential race condition with multiple script instances.
                if e.errno != errno.EEXIST:
                    print("Warning: could not create {}".format(reqd_dir))
                    print(e)

    params['out_dir'] = out_dir
    params['tmp_dir'] = tmp_dir

    # Keep eta fixed at 1 (i.e., enforce homogeneous mixing).
    params['prior']['eta'] = lambda r, size=None: 1.0
    params['param_min'][7] = 1.0
    params['param_max'][7] = 1.0

    # Seed the initial exposure in the first 50 days of the simulation.
    # Note: this is actually the default value.
    params['param_min'][9] = 0
    params['param_max'][9] = 50
    params['prior']['t0'] = lambda r, size=None: r.uniform(0, 50, size=size)

    return params


def local_settings(locn_id=None):
    """
    Return location-specific forecasting parameters, either for all known
    locations (default, indexed by location ID) or for a single location, as
    identified by ``locn_id``.

    These parameters comprise:
    - id: used to identify each location, must be unique.
    - name: the pretty-printed version of the location ID.
    - popn: the size of the population in this location.
    - obs_model: the observation model instance.
    - obs_file: the filename of the observations file.
    - obs_filter: a function used to filter out, e.g., outliers.
    - obs_axis_lbl: the axis label for the observations.
    - obs_axis_prec: the decimal precision of axis ticks for the observations.
    - obs_datum_lbl: the label for individual observations.
    - obs_datum_prec: the decimal precision of individual observations.
    - from_file_args: a dictionary of keyword arguments to use when loading
        data from the observations files.
    - scan_years: the years for which observations are available.
    - scan: a dictionary that maps observation model parameter names to one or
        more values for that parameter (either a scalar value, a list, or a
        dictionary that maps years to scalar values or lists), for performing
        retrospective forecasting scans.
    - forecast: a dictionary that maps observation model parameter names to
        one or more values (as per scan, above) for performing live forecasts.
    - om_format: a dictionary that maps observation model parameter names to
        format specifiers used to include parameter values in output file
        names.
    - om_name: a dictionary that maps observation model parameter names to
        strings used to identify these parameters in output file names.
    - out_dir: the directory to which output files will be written.
    - json_dir: the directory to which JSON output files will be written.
    - tmp_dir: the directory to which temporary files will be written.
    - get_params: a function that accepts this dictionary as an argument and
      returns the simulation parameters dictionary.
    - extra_args: additional arguments for inclusion in parameter sweeps, can
      define any of the following:
      - start: a function that takes one argument, the season, and returns the
        start of the simulation period.
      - until: a function that takes one argument, the season, and returns the
        end of the simulation period.
      - live_fs_dates: a function that takes two arguments, the season and an
        (optional) initial forecasting date, and returns a list of dates for
        which live forecasts should be generated.
      - scan_fs_date: a function that takes two arguments, the season and the
        list of observations for that season, and returns the dates for which
        retrospective forecasts should be generated.

    :param locn_id: The ID of a single location (optional).
    """

    # Determine the default directory for temporary files and output files.
    # This may be host-dependent.
    data_dir = '.'

    # Default values for parameters that rarely need to be changed.
    defaults = {
        'from_file_args': {},
        'out_dir': data_dir,
        'tmp_dir': data_dir,
        'json_dir': 'www',
        'get_params': get_params,
    }

    # The dictionary of location-specific settings.
    settings = {
        'gft-vic': {
            'name': 'Victoria (GFT)',
            'popn': 4108541,
            'obs_model': epifx.obs.PopnCounts("Notifications", 7),
            'obs_file': 'google-flu-trends-aus.ssv',
            'obs_axis_lbl': 'ILI Cases per 100,000 GP visits',
            'obs_axis_prec': 0,
            'obs_datum_lbl': 'ILI Cases per 100,000',
            'obs_datum_prec': 2,
            'from_file_args': {'date_col': 'Date', 'value_col': 'VIC'},
            'scan_years': [2006, 2007],  # [2010, 2011, 2012, 2013, 2014],
            'scan': {
                'bg_obs': 300,
                'bg_var': 10000,
                'pr_obs': np.linspace(0.005, 0.015, num=11),
                'disp': [10],
            },
            'forecast': {
                # No forecasting, live data are not available.
                'bg_obs': [],
                'bg_var': [],
                'pr_obs': [],
                'disp': [],
            },
            'om_format': {
                'bg_obs': '03.0f',
                'bg_var': '05.0f',
                'pr_obs': '0.5f',
                'disp': '03.0f',
            },
            'om_name': {
                'bg_obs': 'bg',
                'bg_var': 'var',
                'pr_obs': 'pr',
                'disp': 'disp',
            },
        },
    }

    # Finalise the settings for each location.
    for locn in settings:
        # Apply default settings to each location, as needed.
        for k in defaults:
            if k not in settings[locn]:
                settings[locn][k] = defaults[k]
        # Include the location identifier in the settings.
        settings[locn]['id'] = locn

    if locn_id is None:
        return(settings.keys())
    elif locn_id in settings:
        return(settings[locn_id])
    else:
        raise ValueError("Invalid forecasting location '{}'".format(locn_id))
